"""
ویجت‌های RTL برای پشتیبانی از متن فارسی
"""

from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label

# استفاده از فونت پیشفرض اگر Vazirmatn ثبت نشده باشه
try:
    from kivy.core.text import LabelBase
    FONT_NAME = 'Vazirmatn' if 'Vazirmatn' in LabelBase._fonts else 'Roboto'
except:
    FONT_NAME = 'Roboto'


class RTLTextInput(TextInput):
    """
    TextInput با پشتیبانی از RTL و فونت فارسی
    """
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', FONT_NAME)
        kwargs.setdefault('halign', 'right')
        kwargs.setdefault('padding', (10, 10, 10, 10))
        kwargs.setdefault('write_tab', False)
        super().__init__(**kwargs)


class RTLSpinner(Spinner):
    """
    Spinner با پشتیبانی از RTL و فونت فارسی
    """
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', FONT_NAME)
        kwargs.setdefault('halign', 'right')
        kwargs.setdefault('text_autoupdate', True)
        super().__init__(**kwargs)


class RTLLabel(Label):
    """
    Label با پشتیبانی از RTL و فونت فارسی
    """
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', FONT_NAME)
        kwargs.setdefault('halign', 'right')
        kwargs.setdefault('valign', 'middle')
        super().__init__(**kwargs)


def is_rtl_text(text):
    """
    تشخیص RTL بودن متن
    """
    if not text:
        return False
    
    text = str(text)
    rtl_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    ltr_chars = sum(1 for c in text if c.isalpha() and not ('\u0600' <= c <= '\u06FF'))
    
    if rtl_chars == 0 and ltr_chars == 0:
        return False
    
    return rtl_chars > ltr_chars


def auto_align_textinput(textinput):
    """
    تنظیم خودکار alignment بر اساس متن
    """
    if textinput.text and is_rtl_text(textinput.text):
        textinput.halign = 'right'
        textinput.padding = (10, 10, 10, 10)
    else:
        textinput.halign = 'left'
        textinput.padding = (10, 10, 10, 10)
