import io
import re
import os

from google.cloud import vision
from google.oauth2 import service_account

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

    def get_payment_info(self, file_name: str) -> dict:
        """
        レシート画像から金額と日付を抽出
        :param file_name: レシート画像のファイルパス
        :return: 抽出された金額と日付
        """
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()

        response = self.ocr(target_image=content)
        texts = response.text_annotations

        if not texts:
            return {"date": None, "amount": None}

        full_text = texts[0].description

        # 金額を正規表現で抽出（例：¥1,234や$123.45）
        amount_pattern = r"([\$¥]?[\d,]+\.?\d{0,2})"
        amount_match = re.findall(amount_pattern, full_text)

        # 日付を正規表現で抽出（例：2023/12/25や25-12-2023）
        date_pattern = r"(\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})"
        date_match = re.findall(date_pattern, full_text)

        # 最初の一致を返す（精度向上のための処理は必要に応じて追加）
        amount = amount_match[0] if amount_match else None
        date = date_match[0] if date_match else None

        return {"date": date, "amount": amount}



