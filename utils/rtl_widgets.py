# utils/rtl_widgets.py
"""
ویجت‌های RTL برای پشتیبانی از متن فارسی
- استفاده از Pillow برای نمایش متن فارسی
- پشتیبانی از کیبورد و ورودی
"""

import os
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
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

# ========== کتابخانه Pillow برای نمایش فارسی ==========
try:
    from utils.persian_text import PersianLabel, is_rtl_text, create_persian_label
    HAS_PILLOW = True
    print("✅ Pillow برای نمایش فارسی بارگذاری شد")
except ImportError:
    HAS_PILLOW = False
    print("⚠️ Pillow در دسترس نیست - از روش جایگزین استفاده می‌شود")


def reshape_text(text):
    """شکل‌دهی متن فارسی/عربی (فقط برای fallback)"""
    if not text or not HAS_RTL_LIBS:
        return text
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped)
        return bidi_text
    except:
        return text


class RTLTextInput(TextInput):
    """TextInput با پشتیبانی از RTL"""
    
    def __init__(self, **kwargs):
        kwargs['halign'] = 'right'
        kwargs['padding'] = (dp(15), dp(12), dp(15), dp(12))
        kwargs['write_tab'] = False
        kwargs['multiline'] = False
        kwargs['size_hint_y'] = None
        kwargs['height'] = dp(50)
        
        super().__init__(**kwargs)
        
        self.bind(focus=self._on_focus)
        self._keyboard = None
        
        # اگر متن اولیه فارسی است، alignment رو تنظیم کن
        if self.text and is_rtl_text(self.text):
            self.halign = 'right'
    
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
    
    def insert_text(self, substring, from_undo=False):
        """ورود متن با پشتیبانی از RTL"""
        if is_rtl_text(substring):
            # برای متن فارسی، direction رو تنظیم کن
            self.halign = 'right'
        return super().insert_text(substring, from_undo=from_undo)


class RTLSpinner(Spinner):
    """Spinner با پشتیبانی از RTL"""
    
    def __init__(self, **kwargs):
        kwargs['halign'] = 'right'
        kwargs['text_autoupdate'] = True
        kwargs['size_hint_y'] = None
        kwargs['height'] = dp(50)
        super().__init__(**kwargs)


class RTLLabel(BoxLayout):
    """
    Label با پشتیبانی از RTL
    - از Pillow برای نمایش متن فارسی استفاده می‌کند
    - در صورت عدم دسترسی به Pillow، از reshape_text استفاده می‌کند
    """
    
    def __init__(self, text="", font_size=24, color=(0, 0, 0, 1), **kwargs):
        super().__init__(**kwargs)
        
        self.size_hint = (1, None)
        self.height = dp(50)
        self.orientation = 'vertical'
        
        self._text = text
        self._font_size = font_size
        self._color = color
        self._label_widget = None
        
        # ساخت ویجت نمایش متن
        self._build_label()
    
    def _build_label(self):
        """ساخت ویجت مناسب برای نمایش متن"""
        # پاک کردن ویجت قبلی
        if self._label_widget:
            self.remove_widget(self._label_widget)
            self._label_widget = None
        
        # اگر متن فارسی است و Pillow موجود است
        if self._text and is_rtl_text(self._text) and HAS_PILLOW:
            # تبدیل رنگ از 0-1 به 0-255
            color_rgb = tuple(int(c * 255) for c in self._color[:3])
            if len(self._color) > 3:
                color_rgb = color_rgb + (int(self._color[3] * 255),)
            else:
                color_rgb = color_rgb + (255,)
            
            self._label_widget = PersianLabel(
                text=self._text,
                font_size=self._font_size,
                color=color_rgb,
                size_hint=(1, None),
                height=self._font_size + dp(20)
            )
            
        else:
            # استفاده از Label معمولی
            display_text = self._text
            if self._text and is_rtl_text(self._text):
                display_text = reshape_text(self._text)
            
            self._label_widget = Label(
                text=display_text,
                font_size=self._font_size,
                color=self._color,
                halign='center',
                valign='middle',
                size_hint=(1, None),
                height=self._font_size + dp(20),
                text_size=(self.width, None)
            )
        
        # اضافه کردن ویجت
        if self._label_widget:
            self.add_widget(self._label_widget)
    
    def set_text(self, text):
        """تغییر متن"""
        self._text = text
        self._build_label()
    
    def set_font_size(self, size):
        """تغییر اندازه فونت"""
        self._font_size = size
        self._build_label()
    
    def set_color(self, color):
        """تغییر رنگ"""
        self._color = color
        self._build_label()
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        self.set_text(str(value))


# ========== توابع کمکی ==========

def auto_align_textinput(textinput):
    """تنظیم خودکار alignment بر اساس متن"""
    if textinput.text and is_rtl_text(textinput.text):
        textinput.halign = 'right'
        textinput.padding = (15, 12, 15, 12)
    else:
        textinput.halign = 'left'
        textinput.padding = (15, 12, 15, 12)


def create_rtl_label(text, font_size=24, color=(0, 0, 0, 1)):
    """ساخت RTLLabel با تنظیمات پیش‌فرض"""
    return RTLLabel(text=text, font_size=font_size, color=color)
