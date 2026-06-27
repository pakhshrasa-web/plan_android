# utils/persian_text.py
"""
تبدیل متن فارسی به تصویر با استفاده از Pillow
برای حل مشکل نمایش فونت در Kivy اندروید
"""

from kivy.uix.image import Image
from kivy.core.image import Texture
from PIL import Image as PILImage, ImageDraw, ImageFont
import io
import os
import arabic_reshaper
from bidi.algorithm import get_display

class PersianLabel(Image):
    """Label فارسی که به صورت تصویر نمایش داده می‌شود"""
    
    def __init__(self, text="", font_size=24, color=(0, 0, 0, 255), **kwargs):
        super().__init__(**kwargs)
        self._text = text
        self._font_size = font_size
        self._color = color
        self._font_path = self._find_font()
        self._update_texture()
    
    def _update_texture(self):
        """به‌روزرسانی تصویر با متن جدید"""
        if not self._text:
            self.texture = None
            self.size = (0, 0)
            return
        
        try:
            # 1. شکل‌دهی به متن فارسی
            reshaped = arabic_reshaper.reshape(self._text)
            bidi_text = get_display(reshaped)
            
            # 2. بارگذاری فونت
            if self._font_path and os.path.exists(self._font_path):
                font = ImageFont.truetype(self._font_path, self._font_size)
            else:
                font = ImageFont.load_default()
            
            # 3. اندازه‌گیری متن
            temp_img = PILImage.new('RGBA', (1, 1), (255, 255, 255, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), bidi_text, font=font)
            
            # 4. ایجاد تصویر نهایی با حاشیه
            padding = 10
            width = bbox[2] - bbox[0] + (padding * 2)
            height = bbox[3] - bbox[1] + (padding * 2)
            
            img = PILImage.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # 5. رسم متن
            draw.text(
                (padding - bbox[0], padding - bbox[1]),
                bidi_text,
                font=font,
                fill=self._color
            )
            
            # 6. تبدیل به Texture کیوی
            data = io.BytesIO()
            img.save(data, format='png')
            data.seek(0)
            
            texture = Texture.create(size=(width, height), colorfmt='rgba')
            texture.blit_buffer(data.getvalue(), colorfmt='rgba', bufferfmt='ubyte')
            
            self.texture = texture
            self.size = (width, height)
            
        except Exception as e:
            print(f"❌ خطا در ایجاد متن فارسی: {e}")
            # در صورت خطا، متن ساده نمایش داده شود
            self.texture = None
    
    def _find_font(self):
        """پیدا کردن فونت فارسی در سیستم"""
        font_paths = [
            '/system/fonts/NotoNaskhArabic-Regular.ttf',
            '/system/fonts/NotoSansArabic-Regular.ttf',
            '/system/fonts/DroidNaskh-Regular.ttf',
            '/system/fonts/DroidSansFallback.ttf',
            'fonts/Vazirmatn-Regular.ttf',
            'fonts/NotoNaskhArabic-Regular.ttf'
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                return path
        
        # اگر فونت فارسی پیدا نشد، فونت سیستمی رو امتحان کن
        try:
            import kivy.resources
            for path in kivy.resources.resource_find('fonts/*.ttf') or []:
                if os.path.exists(path):
                    return path
        except:
            pass
        
        return None
    
    def set_text(self, text):
        """تغییر متن"""
        self._text = text
        self._update_texture()
    
    def set_font_size(self, size):
        """تغییر اندازه فونت"""
        self._font_size = size
        self._update_texture()


def is_rtl_text(text):
    """تشخیص RTL بودن متن"""
    if not text:
        return False
    text = str(text)
    rtl_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    ltr_chars = sum(1 for c in text if c.isalpha() and not ('\u0600' <= c <= '\u06FF'))
    if rtl_chars == 0 and ltr_chars == 0:
        return False
    return rtl_chars > ltr_chars


def create_persian_label(text, font_size=24, color=(0, 0, 0, 255)):
    """ساخت PersianLabel از متن"""
    return PersianLabel(text=text, font_size=font_size, color=color)
