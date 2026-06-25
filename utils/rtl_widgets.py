"""
ویجت‌های RTL برای پشتیبانی از متن فارسی
"""

import os
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window

# ========== تنظیم فونت ==========
def get_font_path():
    """پیدا کردن مسیر فونت - اولویت با فونت داخلی"""
    # 1. فونت داخلی برنامه (Vazirmatn)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    internal_fonts = [
        os.path.join(base_dir, 'fonts', 'Vazirmatn-Regular.ttf'),
        os.path.join(base_dir, 'fonts', 'Vazirmatn.ttf'),
        os.path.join(base_dir, 'Vazirmatn-Regular.ttf'),
    ]
    
    for path in internal_fonts:
        if os.path.exists(path):
            print(f"✅ فونت داخلی پیدا شد: {path}")
            return path
    
    # 2. فونت سیستمی (در صورت نبود فونت داخلی)
    system_fonts = [
        '/system/fonts/NotoNaskhArabic-Regular.ttf',
        '/system/fonts/NotoSansArabic-Regular.ttf',
        '/system/fonts/DroidSansFallback.ttf',
    ]
    
    for path in system_fonts:
        if os.path.exists(path):
            print(f"✅ فونت سیستمی پیدا شد: {path}")
            return path
    
    print("⚠️ هیچ فونتی پیدا نشد، استفاده از Roboto")
    return 'Roboto'

# پیدا کردن فونت
FONT_PATH = get_font_path()
print(f"📁 فونت استفاده شده: {FONT_PATH}")

# ثبت فونت در LabelBase برای استفاده در ویجت‌ها
try:
    if FONT_PATH != 'Roboto' and os.path.exists(FONT_PATH):
        LabelBase.register(name='CustomFont', fn_regular=FONT_PATH)
        print(f"✅ فونت با نام CustomFont ثبت شد")
except Exception as e:
    print(f"⚠️ خطا در ثبت فونت: {e}")


class RTLTextInput(TextInput):
    """TextInput با پشتیبانی از RTL و فونت فارسی"""
    
    def __init__(self, **kwargs):
        # استفاده از فونت ثبت شده
        kwargs['font_name'] = 'CustomFont' if FONT_PATH != 'Roboto' else 'Roboto'
        kwargs['halign'] = 'right'
        kwargs['padding'] = (dp(15), dp(12), dp(15), dp(12))
        kwargs['write_tab'] = False
        kwargs['multiline'] = False
        kwargs['size_hint_y'] = None
        kwargs['height'] = dp(50)
        
        super().__init__(**kwargs)
        
        self.bind(focus=self._on_focus)
        self.bind(text=self._on_text_change)
        self._keyboard = None
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.focus = True
            return True
        return super().on_touch_down(touch)
    
    def _on_focus(self, instance, value):
        if value:
            Clock.schedule_once(lambda dt: self._show_keyboard(), 0.1)
            if self.text:
                Clock.schedule_once(
                    lambda dt: setattr(self, 'cursor', (len(self.text), 0)),
                    0.15
                )
        else:
            self._hide_keyboard()
    
    def _show_keyboard(self):
        if self.focus:
            try:
                self._keyboard = Window.request_keyboard(
                    self._keyboard_closed,
                    self,
                    'text'
                )
                if self._keyboard:
                    self._keyboard.bind(on_key_down=self._on_key_down)
            except Exception as e:
                print(f"⚠️ خطا در نمایش کیبورد: {e}")
    
    def _hide_keyboard(self):
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard = None
            try:
                Window.release_all_keyboards()
            except:
                pass
    
    def _on_key_down(self, keyboard, keycode, text, modifiers):
        key_name = keycode[1]
        
        if key_name == 'enter' and not self.multiline:
            self.focus = False
            return True
        
        if key_name == 'backspace':
            if self.text:
                self.text = self.text[:-1]
            return True
        
        if text:
            cursor_pos = self.cursor[0]
            old_text = self.text
            new_text = old_text[:cursor_pos] + text + old_text[cursor_pos:]
            self.text = new_text
            self.cursor = (cursor_pos + len(text), 0)
            return True
        
        return False
    
    def _keyboard_closed(self):
        self._keyboard = None
    
    def _on_text_change(self, instance, value):
        if value and self._is_rtl_text(value):
            self.halign = 'right'
        else:
            self.halign = 'left'
    
    def _is_rtl_text(self, text):
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
        kwargs['font_name'] = 'CustomFont' if FONT_PATH != 'Roboto' else 'Roboto'
        kwargs['halign'] = 'right'
        kwargs['text_autoupdate'] = True
        kwargs['size_hint_y'] = None
        kwargs['height'] = dp(50)
        super().__init__(**kwargs)


class RTLLabel(Label):
    """Label با پشتیبانی از RTL و فونت فارسی"""
    
    def __init__(self, **kwargs):
        kwargs['font_name'] = 'CustomFont' if FONT_PATH != 'Roboto' else 'Roboto'
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
    if not text:
        return False
    text = str(text)
    rtl_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    ltr_chars = sum(1 for c in text if c.isalpha() and not ('\u0600' <= c <= '\u06FF'))
    if rtl_chars == 0 and ltr_chars == 0:
        return False
    return rtl_chars > ltr_chars


def auto_align_textinput(textinput):
    if textinput.text and is_rtl_text(textinput.text):
        textinput.halign = 'right'
        textinput.padding = (15, 12, 15, 12)
    else:
        textinput.halign = 'left'
        textinput.padding = (15, 12, 15, 12)
