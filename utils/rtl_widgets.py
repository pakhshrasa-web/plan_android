"""
ویجت‌های RTL برای پشتیبانی از متن فارسی
- استفاده از arabic_reshaper برای شکل‌دهی متن
"""

import os
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.text import LabelBase

# ========== کتابخانه‌های RTL ==========
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_RTL_LIBS = True
    print("✅ کتابخانه‌های RTL بارگذاری شدند")
except ImportError:
    HAS_RTL_LIBS = False
    print("⚠️ کتابخانه‌های RTL در دسترس نیستند")

# ========== تنظیم فونت ==========
# پیدا کردن فونت
def get_font():
    font_paths = [
        '/system/fonts/DroidSansFallback.ttf',
        '/system/fonts/NotoNaskhArabic-Regular.ttf',
        '/system/fonts/NotoSansArabic-Regular.ttf',
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            return path
    
    return 'Roboto'

FONT_PATH = get_font()
print(f"📁 فونت استفاده شده: {FONT_PATH}")


def reshape_text(text):
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
    """TextInput با پشتیبانی از RTL"""
    
    def __init__(self, **kwargs):
        kwargs['font_name'] = FONT_PATH if FONT_PATH != 'Roboto' else 'Roboto'
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
    """Spinner با پشتیبانی از RTL"""
    
    def __init__(self, **kwargs):
        kwargs['font_name'] = FONT_PATH if FONT_PATH != 'Roboto' else 'Roboto'
        kwargs['halign'] = 'right'
        kwargs['text_autoupdate'] = True
        kwargs['size_hint_y'] = None
        kwargs['height'] = dp(50)
        super().__init__(**kwargs)


class RTLLabel(Label):
    """Label با پشتیبانی از RTL - استفاده از Pillow برای نمایش فارسی"""
    
    def __init__(self, **kwargs):
        # ذخیره متن اصلی
        self._original_text = kwargs.get('text', '')
        self._font_size = kwargs.get('font_size', 24)
        
        # اگر متن فارسی است، از Pillow استفاده کن
        if self._original_text and is_rtl_text(self._original_text):
            try:
                from utils.persian_text import create_persian_label
                # جایگزینی Label با Image
                img_label = create_persian_label(
                    self._original_text,
                    self._font_size
                )
                # حذف این Label و اضافه کردن Image
                if kwargs.get('parent'):
                    kwargs['parent'].remove_widget(self)
                    kwargs['parent'].add_widget(img_label)
                    return
            except Exception as e:
                print(f"⚠️ خطا در ایجاد متن فارسی: {e}")
        
        # اگر فارسی نبود یا خطا داشت، از Label معمولی استفاده کن
        kwargs['font_name'] = FONT_PATH if FONT_PATH != 'Roboto' else 'Roboto'
        kwargs['halign'] = 'right'
        kwargs['valign'] = 'middle'
        
        super().__init__(**kwargs)
        self.bind(text=self._on_text_set)
    
    def _on_text_set(self, instance, value):
        """وقتی متن تغییر می‌کند"""
        self._original_text = value
        if value and is_rtl_text(value):
            # برای تغییرات پویا، از روش جایگزینی استفاده کن
            try:
                from utils.persian_text import create_persian_label
                # اینجا باید جایگزینی انجام شود
                # ولی برای سادگی، فعلاً از reshape_text استفاده کن
                self.text = reshape_text(value)
            except:
                self.text = value
        else:
            self.text = value


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
