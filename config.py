"""漢方マニアック - ブログ固有設定

ツムラ番号で引ける漢方データベース × 体験ベースの深掘りレビュー
YMYL対策: エビデンス重視・出典明記・体験談ベース
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

BLOG_NAME = "漢方マニアック"
BLOG_DESCRIPTION = "証・体質・症状から引ける漢方データベース。ツムラ全128処方を徹底解説。エビデンスと体験で届ける、日本一マニアックな漢方ブログ"
BLOG_URL = "https://musclelove-777.github.io/kampo-maniac"
BLOG_LANGUAGE = "ja"
GITHUB_REPO = "MuscleLove-777/kampo-maniac"

TARGET_CATEGORIES = [
    "漢方の基礎知識",
    "症状別漢方ガイド",
    "体質別漢方",
    "ダイエット・美容×漢方",
    "商品レビュー・比較",
    "漢方マニアック深掘り",
    "ライフスタイル×漢方",
]

THEME = {
    "primary": "#2d6a4f",
    "accent": "#52b788",
    "gradient_start": "#2d6a4f",
    "gradient_end": "#40916c",
    "dark_bg": "#0a1f14",
    "dark_surface": "#132f1e",
    "light_bg": "#f0fdf4",
    "light_surface": "#ffffff",
}

MAX_ARTICLE_LENGTH = 3000
ARTICLES_PER_DAY = 3
SCHEDULE_HOURS = [7, 12, 19]

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-flash"

ENABLE_SEO_OPTIMIZATION = True
MIN_SEO_SCORE = 70
MIN_KEYWORD_DENSITY = 1.0
MAX_KEYWORD_DENSITY = 3.0
META_DESCRIPTION_LENGTH = 120
ENABLE_INTERNAL_LINKS = True

AFFILIATE_LINKS = {
    "漢方薬": [
        {"service": "Amazon 漢方薬", "url": "https://www.amazon.co.jp/s?k=%E6%BC%A2%E6%96%B9%E8%96%AC", "description": "ツムラ・クラシエ漢方薬が豊富"},
        {"service": "楽天 漢方薬", "url": "https://search.rakuten.co.jp/search/mall/%E6%BC%A2%E6%96%B9%E8%96%AC/", "description": "ポイント還元でお得に漢方薬を購入"},
    ],
    "漢方サプリ・健康食品": [
        {"service": "薬日本堂オンラインショップ", "url": "https://www.nihondo.co.jp/shop/", "description": "老舗漢方薬局の公式通販"},
        {"service": "クラシエ漢方オンラインショップ", "url": "https://kamposhop.kracie.co.jp/", "description": "クラシエ公式の漢方通販"},
    ],
    "書籍・学習": [
        {"service": "Amazon 漢方書籍", "url": "https://www.amazon.co.jp/s?k=%E6%BC%A2%E6%96%B9+%E5%85%A5%E9%96%80", "description": "漢方入門から専門書まで"},
        {"service": "楽天ブックス", "url": "https://books.rakuten.co.jp/search?sitem=%E6%BC%A2%E6%96%B9", "description": "漢方関連書籍をポイントで"},
    ],
    "オンライン相談": [
        {"service": "漢方のオンライン相談", "url": "https://www.nihondo.co.jp/", "description": "薬剤師に漢方相談ができるサービス"},
    ],
}
AFFILIATE_TAG = "musclelove07-22"

ADSENSE_CLIENT_ID = os.environ.get("ADSENSE_CLIENT_ID", "")
DASHBOARD_PORT = 8087

# Google Analytics (GA4)
GOOGLE_ANALYTICS_ID = "G-CSFVD34MKK"

# Google Search Console 認証ファイル
SITE_VERIFICATION_FILES = {
    "googlea31edabcec879415.html": "google-site-verification: googlea31edabcec879415.html",
}
