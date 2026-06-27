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
        self._font_path = self._find_font()
        self._update_texture()
    
    def _update_texture(self):
        if not self._text:
            self.texture = None
            self.size = (0, 0)
            return
        
        try:
            reshaped = arabic_reshaper.reshape(self._text)
            bidi_text = get_display(reshaped)
            
            if self._font_path and os.path.exists(self._font_path):
                font = ImageFont.truetype(self._font_path, self._font_size)
            else:
                font = ImageFont.load_default()
            
            temp_img = PILImage.new('RGBA', (1, 1), (255, 255, 255, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), bidi_text, font=font)
            
            padding = 10
            width = bbox[2] - bbox[0] + (padding * 2)
            height = bbox[3] - bbox[1] + (padding * 2)
            
            img = PILImage.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            draw.text(
                (padding - bbox[0], padding - bbox[1]),
                bidi_text,
                font=font,
                fill=self._color
            )
            
            data = io.BytesIO()
            img.save(data, format='png')
            data.seek(0)
            
            texture = Texture.create(size=(width, height), colorfmt='rgba')
            texture.blit_buffer(data.getvalue(), colorfmt='rgba', bufferfmt='ubyte')
            
            self.texture = texture
            self.size = (width, height)
            
        except Exception as e:
            print(f"❌ خطا در ایجاد متن فارسی: {e}")
            self.texture = None
    
    def _find_font(self):
        font_paths = [
            '/system/fonts/NotoNaskhArabic-Regular.ttf',
            '/system/fonts/NotoSansArabic-Regular.ttf',
            '/system/fonts/DroidNaskh-Regular.ttf',
            '/system/fonts/DroidSansFallback.ttf',
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                return path
        return None
    
    def set_text(self, text):
        self._text = text
        self._update_texture()
    
    def set_font_size(self, size):
        self._font_size = size
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
