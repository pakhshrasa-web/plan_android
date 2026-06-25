"""
ویجت‌های RTL برای پشتیبانی از متن فارسی
"""

from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.clock import Clock

# ========== تنظیم فونت ==========
def get_best_font():
    """پیدا کردن بهترین فونت موجود"""
    font_options = ['PersianFont', 'CustomFont', 'Vazirmatn', 'Roboto']
    
    for font in font_options:
        if font in LabelBase._fonts:
            print(f"✅ فونت انتخاب شده برای ویجت‌ها: {font}")
            return font
    
    print("⚠️ فونت فارسی پیدا نشد، استفاده از Roboto")
    return 'Roboto'

FONT_NAME = get_best_font()


class RTLTextInput(TextInput):
    """TextInput با پشتیبانی از RTL و فونت فارسی"""
    
    def __init__(self, **kwargs):
        # مسیر مستقیم فونت سیستمی
        font_path = '/system/fonts/NotoNaskhArabic-Regular.ttf'
        
        # فقط propertyهای معتبر
        kwargs['font_name'] = font_path
        kwargs['halign'] = 'right'
        kwargs['padding'] = (dp(15), dp(10), dp(15), dp(10))
        kwargs['write_tab'] = False
        kwargs['multiline'] = False
        
        # فقط input_type معتبر است
        if 'input_type' not in kwargs:
            kwargs['input_type'] = 'text'
        
        super().__init__(**kwargs)
        
        self.bind(text=self._on_text_change)
        self.bind(focus=self._on_focus)
    
    def on_touch_down(self, touch):
        """دریافت تاچ برای فوکوس"""
        if self.collide_point(*touch.pos):
            print(f"✅ تاچ روی فیلد: {touch.pos}")
            self.focus = True
            Clock.schedule_once(lambda dt: self.show_keyboard(), 0.1)
            return True
        return super().on_touch_down(touch)
    
    def _on_focus(self, instance, value):
        """هنگام فوکوس - نمایش کیبورد"""
        if value:
            print("✅ فیلد فوکوس شد")
            Clock.schedule_once(lambda dt: self.show_keyboard(), 0.1)
            if self.text:
                Clock.schedule_once(lambda dt: setattr(self, 'cursor', (len(self.text), 0)), 0.1)
    
    def _on_text_change(self, instance, value):
        """تنظیم جهت متن"""
        if value and self._is_rtl_text(value):
            self.halign = 'right'
        else:
            self.halign = 'left'
    
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
        kwargs['font_name'] = FONT_NAME
        kwargs['halign'] = 'right'
        kwargs['text_autoupdate'] = True
        super().__init__(**kwargs)


class RTLLabel(Label):
    """Label با پشتیبانی از RTL و فونت فارسی"""
    
    def __init__(self, **kwargs):
        kwargs['font_name'] = FONT_NAME
        kwargs['halign'] = 'right'
        kwargs['valign'] = 'middle'
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
