import io
import re
import os
from multiprocessing.managers import Value

from lib2to3.fixer_util import String

from google.cloud import vision
from google.oauth2 import service_account
from datetime import datetime



class ReceiptOcrClient:
    def __init__(self, credentials_path: str):
        """
        Google Cloud Vision APIのクライアントを初期化
        :param credentials_path: GoogleサービスアカウントのJSONファイルパス
        """

        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        self.client = vision.ImageAnnotatorClient(credentials=credentials)

    def ocr(self, target_image: bytes) -> dict:
        """
        Google Cloud Vision APIでOCRを実行
        :param target_image: 画像のバイナリデータ
        :return: OCR結果
        """
        image = vision.Image(content=target_image)
        response = self.client.text_detection(image=image)
        return response

    def parse_date(self, raw_date: str) -> str:
        """
        生の日付文字列を標準的な「YYYY-MM-DD」形式に変換
        """
        try:
            if "年" in raw_date and "月" in raw_date and "日" in raw_date:
                return datetime.strptime(raw_date, "%Y年%m月%d日").strftime("%Y-%m-%d")
            elif "/" in raw_date:
                return datetime.strptime(raw_date, "%Y/%m/%d").strftime("%Y-%m-%d")
            elif "-" in raw_date:
                return datetime.strptime(raw_date, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            return None
        return None

    def parse_amount(self, raw_amount: str) -> float:
        """
        金額文字列を数値形式に変換
        :param raw_amount: "¥1,234"や"$123.45"形式の金額
        :return: 数値形式の金額 (例: 1234.0)
        """
        try:
            # 金額文字列から「¥」「$」「,」を除去して数値化
            raw_amount.replace('.', ',')

            cleaned_amount = re.sub(r"\D", "", raw_amount)  # 数字と小数点以外を除去

            return int(cleaned_amount)
        except ValueError:
            return None

    def get_payment_info(self, file_name: str) -> dict:
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()

        response = self.ocr(target_image=content)
        texts = response.text_annotations

        if not texts:
            return {"date": None, "amount": None}

        full_text = texts[0].description



        # 不要な項目（税合計、消費税合計、割引合計）を削除する正規表現
        exclusion_keywords = [
            r"税合計\s*[:：]?\s*[\$¥]?[0-9,]+(?:\.[0-9]{1,2})?",  # 税合計
            r"消費税合計\s*[:：]?\s*[\$¥]?[0-9,]+(?:\.[0-9]{1,2})?",  # 消費税合計
            r"値引き合計\s*[:：]?\s*[\$¥]?[0-9,]+(?:\.[0-9]{1,2})?",
            r"値引合計\s*[:：]?\s*[\$¥]?[0-9,]+(?:\.[0-9]{1,2})?",  # 
            r"割引合計\s*[:：]?\s*[\$¥]?[0-9,]+(?:\.[0-9]{1,2})?"  # 割引合計
        ]

        # 不要な項目を削除（改行や空白を考慮）
        for pattern in exclusion_keywords:
            full_text = re.sub(pattern, '', full_text, flags=re.DOTALL)

        with open('output_text.txt', 'w', encoding='utf-8') as f:
            f.write(full_text)

        # 「合計」や「Total」に続く金額を抽出する正規表現
            # 合計金額を抽出する正規表現
        total_pattern = r"(合計|Total)\s*[:：]?\s*(?:[\\$¥])?([0-9,]+((?:\.[0-9,]{1,8})|\s?[0-9]+)?)"
        total_match = re.search(total_pattern, full_text)

            # 合計金額の抽出と処理
        total_amount = None
        print(total_match.group(2))
        if total_match:
            total_amount = self.parse_amount(total_match.group(2))  # 合計金額部分を数値に変換

        # 日付抽出
        date_pattern = r"(\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}年\d{1,2}月\d{1,2}日)"
        date_match = re.findall(date_pattern, full_text)
        date = self.parse_date(date_match[0]) if date_match else None

        return {"date": date, "amount": total_amount}

