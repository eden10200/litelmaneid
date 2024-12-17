# littelmonaid


## 概要
- このプロジェクトは、出費の管理ができるアプリとなっています

主な機能は
  - レシートの読み取り
  - 使いどころ、日付、金額などの出費情報の入力
  - 出費情報の期間別確認


## 必要条件

このプロジェクトを動かすために必要なものをリストします。

- Python 3.8
- Django 4.2.16
- 依存ライブラリ

## インストール方法


```bash
# リポジトリをクローン
git clone https://github.com/username/repository.git

# ディレクトリに移動
cd repository

# 仮想環境を作成してアクティブ化
python -m venv venv
source venv/bin/activate   # Windowsの場合: venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt
```
## API-Keyの取得
```
#1. Google Cloud Platform アカウントの作成
![Google Cloud Platform](https://cloud.google.com/?hl=ja) にアクセスし、GCPアカウントを作成します。

#2. 新しいプロジェクトの作成
GCPコンソールから新しいプロジェクトを作成します。

#3. Vision API を有効化
作成したプロジェクトでGoogle Cloud Vision APIを有効にします。
#4. サービスアカウントキーの作成
サービスアカウントを作成し、サービスアカウントキーをダウンロードします。
```
## 環境変数の設定

このプロジェクトでは、機密情報（APIキーやデータベースの接続情報）を管理するために **`.env` ファイル**を使用します。

### **手順**
```
1. プロジェクトのルートディレクトリに`.env`ファイルを作成します。
bash
touch .env

# 環境変数の例
SECRET_KEY=your-secret-key
DEBUG=True
# APIキーなど機密情報
GOOGLE_CLOUD_KEY=your-google-cloud-api-key
2.さきにダウンロードした絶対パスを![GOOGLE_CLOUD_KEY]に記入します
```
## ライセンス

このプロジェクトはMITライセンスのもとで公開されています。
