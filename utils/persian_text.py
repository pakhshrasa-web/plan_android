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
        self.text = text
        self.font_size = font_size
        self.color = color
        self._update_texture()
    
    def _update_texture(self):
        if not self.text:
            return
        
        # 1. شکل‌دهی به متن فارسی
        reshaped_text = arabic_reshaper.reshape(self.text)
        bidi_text = get_display(reshaped_text)
        
        # 2. پیدا کردن فونت
        font_path = self._find_font()
        
        # 3. ایجاد تصویر با PIL
        try:
            # ایجاد تصویر موقت برای اندازه‌گیری
            temp_img = PILImage.new('RGBA', (1, 1), (255, 255, 255, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            
            if font_path:
                font = ImageFont.truetype(font_path, self.font_size)
            else:
                font = ImageFont.load_default()
            
            # اندازه‌گیری متن
            bbox = temp_draw.textbbox((0, 0), bidi_text, font=font)
            width = bbox[2] - bbox[0] + 20
            height = bbox[3] - bbox[1] + 20
            
            # ایجاد تصویر نهایی
            img = PILImage.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # رسم متن
            draw.text((10, 10), bidi_text, font=font, fill=self.color)
            
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
    
    def _find_font(self):
        # لیست مسیرهای احتمالی فونت
        font_paths = [
            '/system/fonts/NotoNaskhArabic-Regular.ttf',
            '/system/fonts/NotoSansArabic-Regular.ttf',
            '/system/fonts/DroidNaskh-Regular.ttf',
            'fonts/Vazirmatn-Regular.ttf'
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                return path
        return None
    
    def set_text(self, text):
        self.text = text
        self._update_texture()
