# utils/persian_text.py
from kivy.uix.image import Image
from kivy.core.image import Texture
from PIL import Image as PILImage, ImageDraw, ImageFont
import io
import os
import arabic_reshaper
from bidi.algorithm import get_display

class PersianLabel(Image):
    def __init__(self, text="", font_size=24, color=(0, 0, 0, 255), **kwargs):
        super().__init__(**kwargs)
        self._text = text
        self._font_size = font_size
        self._color = color
        self._font_path = self._find_best_font()
        print(f"✅ فونت انتخاب شده: {self._font_path}")
        self._update_texture()
    
    def _update_texture(self):
        if not self._text:
            self.texture = None
            self.size = (0, 0)
            return
        
        try:
            # شکل‌دهی به متن فارسی
            reshaped = arabic_reshaper.reshape(self._text)
            bidi_text = get_display(reshaped)
            
            # بارگذاری فونت
            font = None
            if self._font_path and os.path.exists(self._font_path):
                try:
                    font = ImageFont.truetype(self._font_path, self._font_size)
                    print(f"✅ فونت با موفقیت بارگذاری شد: {self._font_path}")
                except Exception as e:
                    print(f"⚠️ خطا در بارگذاری {self._font_path}: {e}")
            
            # اگر فونت کار نکرد، فونت‌های جایگزین رو امتحان کن
            if font is None:
                fallback_fonts = [
                    'fonts/Amiri-Regular.ttf',
                    'fonts/Lateef-Regular.ttf',
                    'fonts/NotoNasrArabic-Regular.ttf',
                    'fonts/Vazirmatn-Regular.ttf',
                    '/system/fonts/NotoNaskhArabic-Regular.ttf',
                    '/system/fonts/DroidSansFallback.ttf',
                ]
                
                for fb_path in fallback_fonts:
                    if os.path.exists(fb_path):
                        try:
                            font = ImageFont.truetype(fb_path, self._font_size)
                            print(f"✅ فونت جایگزین بارگذاری شد: {fb_path}")
                            break
                        except:
                            continue
            
            # اگر هیچ فونتی کار نکرد، از فونت پیش‌فرض PIL استفاده کن
            if font is None:
                font = ImageFont.load_default()
                print(f"⚠️ استفاده از فونت پیش‌فرض PIL")
            
            # اندازه‌گیری متن
            temp_img = PILImage.new('RGBA', (1, 1), (255, 255, 255, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), bidi_text, font=font)
            
            padding = 10
            width = max(bbox[2] - bbox[0] + (padding * 2), 50)
            height = max(bbox[3] - bbox[1] + (padding * 2), 30)
            
            # ایجاد تصویر با پس‌زمینه شفاف
            img = PILImage.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # رسم متن
            draw.text(
                (padding - bbox[0], padding - bbox[1]),
                bidi_text,
                font=font,
                fill=self._color
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
    
    def _find_best_font(self):
        """پیدا کردن بهترین فونت موجود"""
        
        # لیست کامل فونت‌ها با اولویت
        font_list = [
            # فونت‌های داخلی برنامه (اولویت با Amiri)
            'fonts/Amiri-Regular.ttf',
            'fonts/Lateef-Regular.ttf',
            'fonts/NotoNasrArabic-Regular.ttf',
            'fonts/Vazirmatn-Regular.ttf',
            
            # مسیرهای مطلق (برای اطمینان)
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts', 'Amiri-Regular.ttf'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts', 'Lateef-Regular.ttf'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts', 'NotoNasrArabic-Regular.ttf'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'fonts', 'Vazirmatn-Regular.ttf'),
            
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


def is_rtl_text(text):
    if not text:
        return False
    text = str(text)
    rtl_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    ltr_chars = sum(1 for c in text if c.isalpha() and not ('\u0600' <= c <= '\u06FF'))
    if rtl_chars == 0 and ltr_chars == 0:
        return False
    return rtl_chars > ltr_chars
