"""
ابزارهای نمایش متن فارسی با استفاده از PIL
"""

from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from io import BytesIO
from PIL import Image as PILImage, ImageDraw, ImageFont
import os

def create_persian_label(text, font_size=24, color=(0, 0, 0, 255), bg_color=(255, 255, 255, 0)):
    """
    ایجاد یک Image widget با متن فارسی
    """
    try:
        # پیدا کردن فونت
        font_paths = [
            '/system/fonts/DroidSansFallback.ttf',
            '/system/fonts/NotoNaskhArabic-Regular.ttf',
            '/system/fonts/NotoSansArabic-Regular.ttf',
        ]
        
        font = None
        for path in font_paths:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, font_size)
                    print(f"✅ فونت برای PIL پیدا شد: {path}")
                    break
                except:
                    continue
        
        if font is None:
            font = ImageFont.load_default()
            print("⚠️ استفاده از فونت پیش‌فرض PIL")
        
        # اندازه‌گیری متن
        bbox = font.getbbox(text)
        width = bbox[2] - bbox[0] + 20
        height = bbox[3] - bbox[1] + 20
        
        # ایجاد تصویر
        img = PILImage.new('RGBA', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), text, font=font, fill=color)
        
        # تبدیل به BytesIO
        buffer = BytesIO()
        img.save(buffer, format='png')
        buffer.seek(0)
        
        # ایجاد Image widget
        return Image(texture=CoreImage(buffer, ext='png').texture)
    
    except Exception as e:
        print(f"⚠️ خطا در ایجاد متن فارسی: {e}")
        from kivy.uix.label import Label
        return Label(text=text)
