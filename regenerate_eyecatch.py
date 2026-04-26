"""既存全記事のアイキャッチ画像＋セクション画像を一括再生成し、サイトを再ビルドするスクリプト"""
import json
import re
import sys
from pathlib import Path

# blog_engine をインポートできるようにパスを追加
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import importlib.util

# config.py を直接ロード
config_path = Path(__file__).parent / "config.py"
spec = importlib.util.spec_from_file_location("config", config_path)
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

from blog_engine.image_fetcher import ImageFetcher
from blog_engine.site_generator import SiteGenerator

# inject_section_images.py をロード
inject_script = ROOT / "inject_section_images.py"
inject_spec = importlib.util.spec_from_file_location("inject_section_images", str(inject_script))
inject_mod = importlib.util.module_from_spec(inject_spec)
inject_spec.loader.exec_module(inject_mod)


def main():
    articles_dir = Path(config.BASE_DIR) / "output" / "articles"
    images_dir = Path(config.BASE_DIR) / "output" / "site" / "images"
    section_images_dir = images_dir / "section_images"
    section_images_dir.mkdir(parents=True, exist_ok=True)

    fetcher = ImageFetcher(config)

    article_files = sorted(articles_dir.glob("*.json"))
    print(f"対象記事: {len(article_files)}件")

    # テーマカラー取得
    theme_colors = None
    theme = getattr(config, "THEME", {})
    if theme.get("primary") and theme.get("accent"):
        theme_colors = (theme["primary"], theme["accent"])

    # 1. アイキャッチ画像の生成
    print("\n=== アイキャッチ画像生成 ===")
    eyecatch_count = 0
    for af in article_files:
        with open(af, "r", encoding="utf-8") as f:
            article = json.load(f)

        slug = article.get("slug", "")
        print(f"  {slug}")

        eyecatch_url = fetcher.fetch_eyecatch(article)
        if eyecatch_url:
            article["eyecatch_url"] = eyecatch_url
            with open(af, "w", encoding="utf-8") as f:
                json.dump(article, f, ensure_ascii=False, indent=2)
            print(f"    → {eyecatch_url}")
            eyecatch_count += 1

    print(f"アイキャッチ: {eyecatch_count}/{len(article_files)}件")

    # 2. セクション画像の再生成（ファイルが欠落しているもののみ）
    print("\n=== セクション画像再生成 ===")
    section_count = 0
    for af in article_files:
        with open(af, "r", encoding="utf-8") as f:
            article = json.load(f)

        slug = article.get("slug", "")
        content = article.get("content", "")

        # コンテンツ内のセクション画像参照を抽出
        refs = re.findall(r'section_images/([^\)]+\.png)', content)
        if not refs:
            continue

        # H2見出しを抽出（画像生成に必要）
        h2_matches = list(re.finditer(r'^## .+', content, re.MULTILINE))

        for img_filename in refs:
            img_path = section_images_dir / img_filename
            if img_path.exists() and img_path.stat().st_size > 500:
                continue

            # section index を取得
            idx_match = re.search(r'_section_(\d+)\.png$', img_filename)
            section_idx = int(idx_match.group(1)) if idx_match else 0

            # 対応する見出しテキストを探す
            heading_text = f"## セクション{section_idx}"
            # contentから画像直後のH2を探す
            img_ref = f"section_images/{img_filename}"
            pos = content.find(img_ref)
            if pos >= 0:
                after = content[pos:]
                h2_m = re.search(r'^## .+', after, re.MULTILINE)
                if h2_m:
                    heading_text = h2_m.group()

            inject_mod.generate_section_image(
                heading_text=heading_text,
                section_idx=section_idx,
                slug=slug,
                theme_colors=theme_colors,
                save_path=img_path,
            )
            print(f"  再生成: {img_filename}")
            section_count += 1

    print(f"セクション画像: {section_count}枚再生成")

    # 3. サイト再ビルド
    print("\n=== サイト再ビルド ===")
    site_gen = SiteGenerator(config)
    site_gen.build_site()
    print("完了!")


if __name__ == "__main__":
    main()
