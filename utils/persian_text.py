# utils/persian_text.py
"""
تبدیل متن فارسی به تصویر با استفاده از Pillow
نسخهٔ بهینه‌شده و سازگار با اندروید و ویندوز
"""

from kivy.uix.image import Image
from kivy.core.image import Texture
from PIL import Image as PILImage, ImageDraw, ImageFont
import os

class PersianLabel(Image):
    def __init__(self, text="", font_size=24, color=(0, 0, 0, 255), **kwargs):
        super().__init__(**kwargs)
        self._text = text
        self._font_size = font_size
        self._color = color
        self._font_path = self._find_font()
        print(f"🔍 فونت انتخاب شده: {self._font_path}")
        self._update_texture()

    def _update_texture(self):
        if not self._text:
            self.texture = None
            self.size = (0, 0)
            return

        try:
            # بارگذاری فونت
            font = None
            if self._font_path and os.path.exists(self._font_path):
                try:
                    font = ImageFont.truetype(self._font_path, self._font_size)
                    print(f"✅ فونت با موفقیت بارگذاری شد: {self._font_path}")
                except Exception as e:
                    print(f"⚠️ خطا در بارگذاری {self._font_path}: {e}")

            if font is None:
                font = ImageFont.load_default()
                print("⚠️ استفاده از فونت پیش‌فرض PIL")

            # اندازه‌گیری دقیق متن
            temp_img = PILImage.new("RGBA", (1, 1), (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), self._text, font=font)

            padding = 12
            width = max((bbox[2] - bbox[0]) + padding * 2, 20)
            height = max((bbox[3] - bbox[1]) + padding * 2, 20)

            # ایجاد تصویر نهایی
            img = PILImage.new("RGBA", (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # رسم متن (بدون direction چون روی اندروید پشتیبانی نمی‌شود)
            draw.text(
                (padding - bbox[0], padding - bbox[1]),
                self._text,
                font=font,
                fill=self._color
            )

            # تبدیل تصویر به دادهٔ خام RGBA
            raw = img.tobytes()

            # ساخت Texture صحیح
            texture = Texture.create(size=(width, height), colorfmt="rgba")
            texture.blit_buffer(raw, colorfmt="rgba", bufferfmt="ubyte")
            texture.flip_vertical()

            self.texture = texture
            self.size = (width, height)

        except Exception as e:
            print(f"❌ خطا در ایجاد متن فارسی: {e}")
            import traceback
            traceback.print_exc()
            self.texture = None

    def _is_rtl(self, text):
        """تشخیص RTL بودن متن - بدون نیاز به کتابخانه خارجی"""
        if not text:
            return False
        rtl_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF' or '\uFB50' <= c <= '\uFDFF')
        ltr_chars = sum(1 for c in text if c.isalpha() and not ('\u0600' <= c <= '\u06FF'))
        if rtl_chars == 0 and ltr_chars == 0:
            return False
        return rtl_chars > ltr_chars

    def _find_font(self):
        """پیدا کردن بهترین فونت موجود - اولویت با فونت‌های داخلی"""

        font_list = [
            "fonts/Amiri-Regular.ttf",
            "fonts/Lateef-Regular.ttf",
            "fonts/Vazirmatn-Regular.ttf",
            "fonts/NotoNasrArabic-Regular.ttf",

            os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts", "Amiri-Regular.ttf"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts", "Lateef-Regular.ttf"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts", "Vazirmatn-Regular.ttf"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts", "NotoNasrArabic-Regular.ttf"),

            "/system/fonts/NotoNaskhArabic-Regular.ttf",
            "/system/fonts/NotoSansArabic-Regular.ttf",
            "/system/fonts/DroidNaskh-Regular.ttf",
            "/system/fonts/DroidSansFallback.ttf",
        ]

        for path in font_list:
            if os.path.exists(path):
                print(f"🔍 فونت پیدا شد: {path}")
                return path

        print("⚠️ هیچ فونت فارسی پیدا نشد!")
        return None

    def set_text(self, text):
        self._text = text
        self._update_texture()
