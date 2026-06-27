# utils/persian_text.py
"""
تبدیل متن فارسی به تصویر با استفاده از Pillow
بدون وابستگی به arabic_reshaper و bidi (چون در اندروید مشکل دارند)
"""

from kivy.uix.image import Image
from kivy.core.image import Texture
from PIL import Image as PILImage, ImageDraw, ImageFont
import io
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
                    # استفاده از encoding و layout_engine برای پشتیبیت بهتر
                    font = ImageFont.truetype(self._font_path, self._font_size, encoding='utf-8')
                    print(f"✅ فونت با موفقیت بارگذاری شد: {self._font_path}")
                except Exception as e:
                    print(f"⚠️ خطا در بارگذاری {self._font_path}: {e}")
            
            if font is None:
                font = ImageFont.load_default()
                print("⚠️ استفاده از فونت پیش‌فرض PIL")
            
            # اندازه‌گیری متن
            temp_img = PILImage.new('RGBA', (1, 1), (255, 255, 255, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            
            # استفاده از textbbox برای اندازه‌گیری دقیق
            bbox = temp_draw.textbbox((0, 0), self._text, font=font)
            
            padding = 15
            width = max(bbox[2] - bbox[0] + (padding * 2), 50)
            height = max(bbox[3] - bbox[1] + (padding * 2), 30)
            
            # ایجاد تصویر با پس‌زمینه شفاف
            img = PILImage.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # رسم متن به صورت مستقیم
            draw.text(
                (padding - bbox[0], padding - bbox[1]),
                self._text,
                font=font,
                fill=self._color,
                # استفاده از direction برای RTL (اگر PIL پشتیبانی کنه)
                direction='rtl' if self._is_rtl(self._text) else 'ltr'
            )
            
            # تبدیل به Texture کیوی
            data = io.BytesIO()
            img.save(data, format='png')
            data.seek(0)
            
            texture = Texture.create(size=(width, height), colorfmt='rgba')
            texture.blit_buffer(data.getvalue(), colorfmt='rgba', bufferfmt='ubyte')
            
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
        # محدوده کاراکترهای فارسی و عربی
        rtl_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF' or '\uFB50' <= c <= '\uFDFF')
        ltr_chars = sum(1 for c in text if c.isalpha() and not ('\u0600' <= c <= '\u06FF'))
        if rtl_chars == 0 and ltr_chars == 0:
            return False
        return rtl_chars > ltr_chars
    
    def _find_font(self):
        """پیدا کردن بهترین فونت موجود - اولویت با فونت‌های داخلی"""
        
        # لیست کامل فونت‌ها
        font_list = [
            # فونت‌های داخلی برنامه (مسیرهای نسبی)
            'fonts/Amiri-Regular.ttf',
            'fonts/Lateef-Regular.ttf',
            'fonts/Vazirmatn-Regular.ttf',
            'fonts/NotoNasrArabic-Regular.ttf',
            
            # مسیرهای مطلق
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts', 'Amiri-Regular.ttf'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts', 'Lateef-Regular.ttf'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts', 'Vazirmatn-Regular.ttf'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts', 'NotoNasrArabic-Regular.ttf'),
            
            # فونت‌های سیستمی (آخرین اولویت)
            '/system/fonts/NotoNaskhArabic-Regular.ttf',
            '/system/fonts/NotoSansArabic-Regular.ttf',
            '/system/fonts/DroidNaskh-Regular.ttf',
            '/system/fonts/DroidSansFallback.ttf',
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
