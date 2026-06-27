"""
ابزارهای نمایش متن فارسی با استفاده از Pillow
"""

from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage
from io import BytesIO
from PIL import Image as PILImage, ImageDraw, ImageFont
import os

# پیدا کردن بهترین فونت برای PIL
def get_pil_font(font_size=24):
    font_paths = [
        '/system/fonts/NotoNaskhArabic-Regular.ttf',
        '/system/fonts/DroidSansFallback.ttf',
        '/system/fonts/NotoSansArabic-Regular.ttf',
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, font_size)
            except:
                continue
    
    return ImageFont.load_default()


def create_persian_label(text, font_size=24, color=(0, 0, 0, 255), bg_color=(255, 255, 255, 0)):
    """ایجاد Image widget با متن فارسی"""
    try:
        font = get_pil_font(font_size)
        
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


def create_persian_button(text, font_size=20, color=(1, 1, 1, 1), bg_color=(0.2, 0.6, 0.2, 1)):
    """ایجاد دکمه با متن فارسی"""
    from kivy.uix.button import Button
    
    # ایجاد تصویر با رنگ پس‌زمینه
    img = create_persian_label(text, font_size, color, bg_color)
    
    # قرار دادن تصویر در دکمه
    btn = Button()
    btn.add_widget(img)
    
    return btn
