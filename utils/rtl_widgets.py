"""
ویجت‌های RTL برای پشتیبانی از متن فارسی
"""

from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window

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
FONT_PATH = '/system/fonts/NotoNaskhArabic-Regular.ttf'


class RTLTextInput(TextInput):
    """
    TextInput با پشتیبانی از RTL و فونت فارسی
    - استفاده از مسیر مستقیم فونت سیستمی
    - پشتیبانی از تاچ و کیبورد در اندروید
    """
    
    def __init__(self, **kwargs):
        # تنظیمات اجباری
        kwargs['font_name'] = FONT_PATH  # استفاده از مسیر مستقیم فونت
        kwargs['halign'] = 'right'
        kwargs['padding'] = (dp(15), dp(12), dp(15), dp(12))
        kwargs['write_tab'] = False
        kwargs['multiline'] = False
        kwargs['size_hint_y'] = None
        kwargs['height'] = dp(50)
        
        super().__init__(**kwargs)
        
        # رویدادها
        self.bind(focus=self._on_focus)
        self.bind(text=self._on_text_change)
        
        # متغیر برای کیبورد
        self._keyboard = None
    
    def on_touch_down(self, touch):
        """دریافت تاچ برای فوکوس و نمایش کیبورد"""
        if self.collide_point(*touch.pos):
            print(f"✅ تاچ روی فیلد: {touch.pos}")
            # فوکوس را تنظیم کن
            self.focus = True
            # نمایش کیبورد با تأخیر
            Clock.schedule_once(lambda dt: self._show_keyboard(), 0.1)
            return True
        return super().on_touch_down(touch)
    
    def _show_keyboard(self):
        """نمایش کیبورد با استفاده از Window.request_keyboard"""
        if self.focus:
            try:
                # روش مطمئن‌تر برای نمایش کیبورد در اندروید
                self._keyboard = Window.request_keyboard(
                    self._keyboard_closed, 
                    self, 
                    'text'
                )
                if self._keyboard:
                    self._keyboard.bind(on_key_down=self._on_key_down)
                    print("✅ کیبورد با موفقیت نمایش داده شد")
            except Exception as e:
                print(f"⚠️ خطا در نمایش کیبورد: {e}")
                # روش جایگزین
                try:
                    self.show_keyboard()
                except:
                    pass
    
    def _on_focus(self, instance, value):
        """هنگام فوکوس - نمایش کیبورد"""
        if value:
            print("✅ فیلد فوکوس شد")
            Clock.schedule_once(lambda dt: self._show_keyboard(), 0.1)
            # مکان‌نما در انتهای متن
            if self.text:
                Clock.schedule_once(
                    lambda dt: setattr(self, 'cursor', (len(self.text), 0)), 
                    0.1
                )
        else:
            # وقتی فوکوس از دست می‌رود
            if self._keyboard:
                self._keyboard.unbind(on_key_down=self._on_key_down)
                self._keyboard = None
    
    def _on_key_down(self, keyboard, keycode, text, modifiers):
        """دریافت رویدادهای کیبورد"""
        if keycode[1] == 'enter':
            if not self.multiline:
                self.focus = False
        return True
    
    def _keyboard_closed(self):
        """وقتی کیبورد بسته می‌شود"""
        print("🔑 کیبورد بسته شد")
        self._keyboard = None
    
    def _on_text_change(self, instance, value):
        """تنظیم جهت متن بر اساس محتوا"""
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
        kwargs['font_name'] = FONT_PATH  # استفاده از مسیر مستقیم
        kwargs['halign'] = 'right'
        kwargs['text_autoupdate'] = True
        kwargs['size_hint_y'] = None
        kwargs['height'] = dp(50)
        super().__init__(**kwargs)


class RTLLabel(Label):
    """Label با پشتیبانی از RTL و فونت فارسی"""
    
    def __init__(self, **kwargs):
        kwargs['font_name'] = FONT_PATH  # استفاده از مسیر مستقیم
        kwargs['halign'] = 'right'
        kwargs['valign'] = 'middle'
        super().__init__(**kwargs)
        
        self.bind(text=self._update_alignment)
    
    def _update_alignment(self, instance, value):
        """به‌روزرسانی alignment بر اساس متن"""
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
        textinput.padding = (15, 12, 15, 12)
    else:
        textinput.halign = 'left'
        textinput.padding = (15, 12, 15, 12)
