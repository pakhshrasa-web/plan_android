"""
ویجت‌های RTL برای پشتیبانی از متن فارسی
"""

from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.metrics import dp

# ========== تنظیم فونت ==========
def get_available_font():
    """پیدا کردن فونت فارسی موجود"""
    font_options = ['PersianFont', 'Vazirmatn', 'CustomFont', 'Roboto']
    
    for font in font_options:
        if font in LabelBase._fonts:
            print(f"✅ فونت انتخاب شده: {font}")
            return font
    
    return 'Roboto'

FONT_NAME = get_available_font()


class RTLTextInput(TextInput):
    """TextInput با پشتیبانی از RTL و فونت فارسی"""
    
    def __init__(self, **kwargs):
        # تنظیمات پیش‌فرض
        kwargs.setdefault('font_name', FONT_NAME)
        kwargs.setdefault('halign', 'right')
        kwargs.setdefault('padding', (dp(10), dp(10), dp(10), dp(10)))
        kwargs.setdefault('write_tab', False)
        kwargs.setdefault('multiline', False)
        kwargs.setdefault('focus', True)  # مهم برای تاچ
        
        super().__init__(**kwargs)
        
        # رویدادها
        self.bind(text=self._on_text_change)
        self.bind(focus=self._on_focus)
    
    def _on_text_change(self, instance, value):
        """تنظیم خودکار جهت متن"""
        if value and self._is_rtl_text(value):
            self.halign = 'right'
        else:
            self.halign = 'left'
    
    def _on_focus(self, instance, value):
        """وقتی فیلد فوکوس می‌شود"""
        if value:
            # نمایش کیبورد
            self.show_keyboard()
            # مکان‌نما آخر متن
            if self.text:
                self.cursor = (len(self.text), 0)
    
    def _is_rtl_text(self, text):
        """تشخیص RTL بودن متن"""
        if not text:
            return False
        
        rtl_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        ltr_chars = sum(1 for c in text if c.isalpha() and not ('\u0600' <= c <= '\u06FF'))
        
        if rtl_chars == 0 and ltr_chars == 0:
            return False
        
        return rtl_chars > ltr_chars


class RTLSpinner(Spinner):
    """Spinner با پشتیبانی از RTL و فونت فارسی"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', FONT_NAME)
        kwargs.setdefault('halign', 'right')
        kwargs.setdefault('text_autoupdate', True)
        super().__init__(**kwargs)


class RTLLabel(Label):
    """Label با پشتیبانی از RTL و فونت فارسی"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', FONT_NAME)
        kwargs.setdefault('halign', 'right')
        kwargs.setdefault('valign', 'middle')
        super().__init__(**kwargs)
        
        self.bind(text=self._update_alignment)
    
    def _update_alignment(self, instance, value):
        if value and is_rtl_text(value):
            self.halign = 'right'
        else:
            self.halign = 'left'


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


def auto_align_textinput(textinput):
    """تنظیم خودکار alignment بر اساس متن"""
    if textinput.text and is_rtl_text(textinput.text):
        textinput.halign = 'right'
        textinput.padding = (10, 10, 10, 10)
    else:
        textinput.halign = 'left'
        textinput.padding = (10, 10, 10, 10)
