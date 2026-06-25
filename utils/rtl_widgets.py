"""
ویجت‌های RTL برای پشتیبانی از متن فارسی
"""

from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window

# ========== کتابخانه‌های RTL ==========
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_RTL_LIBS = True
    print("✅ کتابخانه‌های RTL بارگذاری شدند")
except ImportError:
    HAS_RTL_LIBS = False
    print("⚠️ کتابخانه‌های RTL در دسترس نیستند")

# مسیر فونت (اگر وجود داشت)
FONT_PATH = '/system/fonts/NotoNaskhArabic-Regular.ttf'
FALLBACK_FONT = 'Roboto'

def get_font():
    """پیدا کردن فونت مناسب"""
    if os.path.exists(FONT_PATH):
        return FONT_PATH
    return FALLBACK_FONT


def reshape_arabic(text):
    """شکل‌دهی متن فارسی/عربی"""
    if not text or not HAS_RTL_LIBS:
        return text
    try:
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)
        return bidi_text
    except:
        return text


class RTLTextInput(TextInput):
    """TextInput با پشتیبانی از RTL و فونت فارسی"""
    
    def __init__(self, **kwargs):
        # تنظیمات
        kwargs['font_name'] = get_font()
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
        
        self._keyboard = None
    
    def on_touch_down(self, touch):
        """دریافت تاچ برای فوکوس"""
        if self.collide_point(*touch.pos):
            self.focus = True
            return True
        return super().on_touch_down(touch)
    
    def _on_focus(self, instance, value):
        """هنگام فوکوس"""
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
        """نمایش کیبورد"""
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
        """پنهان کردن کیبورد"""
        if self._keyboard:
            self._keyboard.unbind(on_key_down=self._on_key_down)
            self._keyboard = None
            try:
                Window.release_all_keyboards()
            except:
                pass
    
    def _on_key_down(self, keyboard, keycode, text, modifiers):
        """پردازش کلیدها"""
        key_name = keycode[1]
        
        if key_name == 'enter' and not self.multiline:
            self.focus = False
            return True
        
        if key_name == 'backspace':
            if self.text:
                self.text = self.text[:-1]
            return True
        
        if text:
            # اضافه کردن متن با شکل‌دهی
            cursor_pos = self.cursor[0]
            old_text = self.text
            new_text = old_text[:cursor_pos] + text + old_text[cursor_pos:]
            self.text = new_text
            self.cursor = (cursor_pos + len(text), 0)
            return True
        
        return False
    
    def _keyboard_closed(self):
        """بسته شدن کیبورد"""
        self._keyboard = None
    
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
        kwargs['font_name'] = get_font()
        kwargs['halign'] = 'right'
        kwargs['text_autoupdate'] = True
        kwargs['size_hint_y'] = None
        kwargs['height'] = dp(50)
        super().__init__(**kwargs)


class RTLLabel(Label):
    """Label با پشتیبانی از RTL و فونت فارسی"""
    
    def __init__(self, **kwargs):
        kwargs['font_name'] = get_font()
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
        textinput.padding = (15, 12, 15, 12)
    else:
        textinput.halign = 'left'
        textinput.padding = (15, 12, 15, 12)
