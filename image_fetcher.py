"""image_fetcher - オリジナルアイキャッチ画像を自動生成するモジュール

記事のテーマ（絵文字+グラデーション+タイトル）から
OGP画像をPNG形式で自動生成する。

- 著作権問題ゼロ（完全オリジナル生成）
- 外部API不要
- コスト0
- Pillow のみ必要（pip install Pillow）
"""

import colorsys
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# OGP推奨サイズ
WIDTH = 1200
HEIGHT = 630

# 日本語フォント候補（優先順）
TEXT_FONT_CANDIDATES = [
    # Windows
    "C:/Windows/Fonts/YuGothB.ttc",
    "C:/Windows/Fonts/meiryob.ttc",
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
    # Linux / GitHub Actions
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    # Mac
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
]

EMOJI_FONT_CANDIDATES = [
    "C:/Windows/Fonts/seguiemj.ttf",
    "/usr/share/fonts/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/System/Library/Fonts/Apple Color Emoji.ttc",
]

try:
    from PIL import Image, ImageDraw, ImageFont

    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


class ImageFetcher:
    """記事テーマに基づくオリジナルアイキャッチ画像生成"""

    def __init__(self, config):
        self.config = config
        self.base_dir = Path(config.BASE_DIR)
        self.images_dir = self.base_dir / "output" / "site" / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.theme = getattr(config, "THEME", {})

        if HAS_PILLOW:
            self._text_font = self._find_font(TEXT_FONT_CANDIDATES)
            self._emoji_font = self._find_font(EMOJI_FONT_CANDIDATES)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_eyecatch(self, article: dict) -> str:
        """記事のアイキャッチ画像を生成してサイト相対パスを返す"""
        if not HAS_PILLOW:
            logger.warning("Pillow が未インストールです: pip install Pillow")
            return ""

        slug = article.get("slug", "untitled")
        filename = f"{slug}.png"
        image_path = self.images_dir / filename

        if image_path.exists() and image_path.stat().st_size > 1000:
            logger.info("既存画像を使用: %s", filename)
            return f"images/{filename}"

        try:
            self._generate(article, image_path)
            logger.info("画像生成完了: %s", filename)
            return f"images/{filename}"
        except Exception as e:
            logger.warning("画像生成失敗: %s", e)
            return ""

    # ------------------------------------------------------------------
    # Image generation
    # ------------------------------------------------------------------

    def _generate(self, article: dict, save_path: Path):
        title = article.get("title", "")
        emoji = article.get("hero_emoji", "")
        seed = article.get("keyword", "") or article.get("slug", "default")

        color1, color2 = self._get_colors(seed)

        # 1. グラデーション背景
        img = self._create_gradient(color1, color2)
        img = img.convert("RGBA")

        # 2. 幾何学パターン
        self._add_pattern(img, seed)

        # 3. 絵文字
        if emoji:
            self._add_emoji(img, emoji)

        # 4. タイトル帯
        if title:
            self._add_title(img, title)

        # 5. ブログ名
        blog_name = getattr(self.config, "BLOG_NAME", "")
        if blog_name:
            self._add_watermark(img, blog_name)

        save_path.parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(str(save_path), "PNG", optimize=True)

    # ------------------------------------------------------------------
    # Color helpers
    # ------------------------------------------------------------------

    def _get_colors(self, seed: str):
        """テーマカラー or キーワードハッシュから2色を生成"""
        primary = self.theme.get("primary", "")
        accent = self.theme.get("accent", "")
        if primary and accent:
            return self._hex_to_rgb(primary), self._hex_to_rgb(accent)

        h = int(hashlib.md5(seed.encode()).hexdigest()[:8], 16)
        hue1 = (h % 360) / 360.0
        hue2 = ((h // 360) % 360) / 360.0
        if abs(hue1 - hue2) < 0.15:
            hue2 = (hue1 + 0.3) % 1.0

        r1, g1, b1 = colorsys.hls_to_rgb(hue1, 0.42, 0.75)
        r2, g2, b2 = colorsys.hls_to_rgb(hue2, 0.35, 0.80)
        return (
            (int(r1 * 255), int(g1 * 255), int(b1 * 255)),
            (int(r2 * 255), int(g2 * 255), int(b2 * 255)),
        )

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _create_gradient(c1, c2):
        """高速な水平グラデーション（1px 列ペースト方式）"""
        base = Image.new("RGB", (WIDTH, HEIGHT), c1)
        end = Image.new("RGB", (WIDTH, HEIGHT), c2)
        mask = Image.new("L", (WIDTH, HEIGHT))
        for x in range(WIDTH):
            mask.paste(int(255 * x / WIDTH), (x, 0, x + 1, HEIGHT))
        return Image.composite(end, base, mask)

    @staticmethod
    def _add_pattern(img, seed):
        """幾何学パターンオーバーレイ"""
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        h = int(hashlib.md5(seed.encode()).hexdigest()[:4], 16)
        style = h % 3
        c = (255, 255, 255, 25)

        if style == 0:
            # ドットパターン
            for y in range(0, HEIGHT, 40):
                for x in range(0, WIDTH, 40):
                    draw.ellipse([x - 3, y - 3, x + 3, y + 3], fill=c)
        elif style == 1:
            # 斜線パターン
            for i in range(-HEIGHT, WIDTH + HEIGHT, 50):
                draw.line([(i, 0), (i + HEIGHT, HEIGHT)], fill=c, width=1)
        else:
            # 同心円パターン
            cx, cy = WIDTH // 2, HEIGHT // 2
            for r in range(50, max(WIDTH, HEIGHT), 70):
                draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c, width=1)

        img.alpha_composite(overlay)

    def _add_emoji(self, img, emoji):
        """中央上部に絵文字を大きく配置"""
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        font = self._load_font(self._emoji_font or self._text_font, 100)

        try:
            bbox = draw.textbbox((0, 0), emoji, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        except Exception:
            return

        x = (WIDTH - tw) // 2
        y = HEIGHT // 2 - th - 60

        # 背景円
        cr = max(tw, th) // 2 + 35
        cx, cy = WIDTH // 2, y + th // 2
        draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(0, 0, 0, 50))
        draw.text((x, y), emoji, font=font, fill=(255, 255, 255, 230))

        img.alpha_composite(overlay)

    def _add_title(self, img, title):
        """半透明帯の上にタイトルを描画"""
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        font = self._load_font(self._text_font, 38)

        lines = self._wrap_text(draw, title, font, WIDTH - 120)[:3]
        lh = 52
        total_h = lh * len(lines)
        y0 = HEIGHT // 2 + 50

        # 半透明帯
        draw.rectangle([0, y0 - 20, WIDTH, y0 + total_h + 20], fill=(0, 0, 0, 100))

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            x = (WIDTH - tw) // 2
            y = y0 + i * lh
            # 影
            draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, 150))
            # 本文
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 245))

        img.alpha_composite(overlay)

    def _add_watermark(self, img, text):
        """右下にブログ名"""
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        font = self._load_font(self._text_font, 18)

        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = WIDTH - tw - 25
        y = HEIGHT - 40

        draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 120))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 180))

        img.alpha_composite(overlay)

    # ------------------------------------------------------------------
    # Font helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_font(path, size):
        if path:
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
        try:
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            return ImageFont.load_default()

    @staticmethod
    def _find_font(candidates):
        for p in candidates:
            if Path(p).exists():
                return p
        return None

    @staticmethod
    def _wrap_text(draw, text, font, max_w):
        lines = []
        cur = ""
        for ch in text:
            test = cur + ch
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] - bbox[0] > max_w:
                if cur:
                    lines.append(cur)
                cur = ch
            else:
                cur = test
        if cur:
            lines.append(cur)
        return lines

    @staticmethod
    def _hex_to_rgb(h):
        h = h.lstrip("#")
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))
