#!/usr/bin/env python3
"""漢方マニアック - GitHub Actions用一括実行スクリプト

キーワード選定 → 記事生成 → アフィリエイト挿入 → SEOチェック → サイトビルド
を一括で実行する。ツムラ全128処方を徹底解説する漢方特化ブログ。
"""
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# ローカル開発: blog_engine が親ディレクトリにある
# GitHub Actions: blog_engine ファイルがワークフローでコピー済み
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

import config
import prompts


def _try_import(module_name, class_name):
    """blog_engine パッケージまたはローカルファイルからインポートを試みる"""
    # まず blog_engine パッケージから試行
    try:
        mod = __import__(f"blog_engine.{module_name}", fromlist=[class_name])
        return getattr(mod, class_name)
    except ImportError:
        pass
    # ローカルファイルからフォールバック
    mod = __import__(module_name, fromlist=[class_name])
    return getattr(mod, class_name)


def run(cfg=None, prm=None):
    """メイン処理: キーワード選定 → 記事生成 → アフィリエイト → サイトビルド"""
    cfg = cfg or config
    prm = prm or prompts

    logger.info("=== %s 自動生成開始 ===", cfg.BLOG_NAME)
    start_time = datetime.now()

    # 出力ディレクトリ作成
    for attr in ["OUTPUT_DIR", "ARTICLES_DIR", "SITE_DIR"]:
        d = getattr(cfg, attr, None)
        if d:
            Path(d).mkdir(parents=True, exist_ok=True)

    # ステップ1: キーワード選定
    logger.info("ステップ1: キーワード選定")
    try:
        from google import genai

        if not cfg.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY が設定されていません")
            sys.exit(1)

        client = genai.Client(api_key=cfg.GEMINI_API_KEY)

        if prm and hasattr(prm, "build_keyword_prompt"):
            prompt = prm.build_keyword_prompt(cfg)
        else:
            categories_text = "\n".join(f"- {cat}" for cat in cfg.TARGET_CATEGORIES)
            prompt = (
                f"{cfg.BLOG_NAME}用のキーワードを選定してください。\n\n"
                f"カテゴリ一覧:\n{categories_text}\n\n"
                'JSON形式のみ: {"category": "カテゴリ名", "keyword": "キーワード"}'
            )

        response = client.models.generate_content(
            model=cfg.GEMINI_MODEL, contents=prompt
        )
        response_text = response.text.strip()

        # コードブロック内のJSONを抽出
        if "```" in response_text:
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        data = json.loads(response_text)
        category = data["category"]
        keyword = data["keyword"]
        logger.info("選定結果 - カテゴリ: %s, キーワード: %s", category, keyword)

    except Exception as e:
        logger.error("キーワード選定失敗: %s", e)
        sys.exit(1)

    # ステップ2: 記事生成
    logger.info("ステップ2: 記事生成")
    try:
        ArticleGenerator = _try_import("article_generator", "ArticleGenerator")
        SEOOptimizer = _try_import("seo_optimizer", "SEOOptimizer")

        generator = ArticleGenerator(cfg)
        article = generator.generate_article(
            keyword=keyword, category=category, prompts=prm
        )
        logger.info("記事生成完了: %s", article.get("title", "不明"))

        optimizer = SEOOptimizer(cfg)
        seo_result = optimizer.check_seo_score(article)
        logger.info(
            "SEOスコア: %d/100 (グレード: %s)",
            seo_result.get("total_score", 0),
            seo_result.get("grade", "?"),
        )

    except Exception as e:
        logger.error("記事生成失敗: %s", e)
        sys.exit(1)

    # ステップ2.5: アフィリエイトリンク挿入
    logger.info("ステップ2.5: アフィリエイトリンク挿入")
    try:
        AffiliateManager = _try_import("affiliate", "AffiliateManager")
        aff = AffiliateManager(cfg, prm)
        article = aff.insert_affiliate_links(article)
        logger.info("アフィリエイト: %d件挿入", article.get("affiliate_count", 0))
    except Exception as e:
        logger.warning("アフィリエイト挿入スキップ: %s", e)

    # ステップ3: サイトビルド
    logger.info("ステップ3: サイトビルド")
    try:
        SiteGenerator = _try_import("site_generator", "SiteGenerator")
        site_gen = SiteGenerator(cfg)
        site_gen.build_site()
        logger.info("サイトビルド完了")
    except Exception as e:
        logger.error("サイトビルド失敗: %s", e)
        sys.exit(1)

    # 完了サマリー
    duration = (datetime.now() - start_time).total_seconds()
    logger.info("=== 自動生成完了（%.1f秒） ===", duration)
    logger.info("  カテゴリ: %s", category)
    logger.info("  キーワード: %s", keyword)
    logger.info("  タイトル: %s", article.get("title", "不明"))
    logger.info("  SEOスコア: %d/100", seo_result.get("total_score", 0))


if __name__ == "__main__":
    run()
