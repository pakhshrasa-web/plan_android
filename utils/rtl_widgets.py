# utils/rtl_widgets.py
"""
ویجت‌های RTL برای پشتیبانی از متن فارسی
- استفاده از Pillow برای نمایش متن فارسی (بدون arabic_reshaper)
"""

from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window

# ========== تشخیص RTL ==========
def is_rtl_text(text):
    """تشخیص RTL بودن متن - بدون وابستگی به کتابخانه خارجی"""
    if not text:
        return False
    text = str(text)
    rtl_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF' or '\uFB50' <= c <= '\uFDFF')
    ltr_chars = sum(1 for c in text if c.isalpha() and not ('\u0600' <= c <= '\u06FF'))
    if rtl_chars == 0 and ltr_chars == 0:
        return False
    return rtl_chars > ltr_chars

# ========== کتابخانه Pillow ==========
try:
    from utils.persian_text import PersianLabel
    HAS_PILLOW = True
    print("✅ Pillow برای نمایش فارسی بارگذاری شد")
except ImportError as e:
    HAS_PILLOW = False
    print(f"⚠️ Pillow در دسترس نیست: {e}")


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
    ✅ نسخه RTLLabel - بدون وابستگی به arabic_reshaper
    - از Pillow برای نمایش متن فارسی استفاده می‌کند
    """
    
    def __init__(self, **kwargs):
        # استخراج پارامترهای مورد نیاز
        text = kwargs.pop('text', '')
        font_size = kwargs.pop('font_size', 24)
        color = kwargs.pop('color', (0, 0, 0, 1))
        size_hint_y = kwargs.pop('size_hint_y', None)
        height = kwargs.pop('height', dp(50))
        
        # حذف پارامترهای مزاحم
        kwargs.pop('bold', None)
        kwargs.pop('markup', None)
        kwargs.pop('halign', None)
        kwargs.pop('valign', None)
        kwargs.pop('text_size', None)
        
        super().__init__(**kwargs)
        
        self.orientation = 'vertical'
        if size_hint_y is not None:
            self.size_hint_y = size_hint_y
        if height:
            self.height = height
        
        self._text = text
        self._font_size = font_size
        self._color = color
        self._label_widget = None
        
        self._build_label()
    
    def _build_label(self):
        """ساخت ویجت نمایش متن"""
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
            
            try:
                self._label_widget = PersianLabel(
                    text=self._text,
                    font_size=self._font_size,
                    color=color_rgb,
                    size_hint=(1, None),
                    height=self._font_size + dp(20)
                )
                print(f"✅ PersianLabel ساخته شد برای: {self._text[:20]}...")
            except Exception as e:
                print(f"⚠️ خطا در ساخت PersianLabel: {e}")
                self._label_widget = None
        
        # اگر Pillow کار نکرد، از Label معمولی استفاده کن
        if self._label_widget is None:
            self._label_widget = Label(
                text=self._text or "",
                font_size=self._font_size,
                color=self._color,
                halign='center',
                valign='middle',
                size_hint=(1, None),
                height=self._font_size + dp(20),
                text_size=(self.width, None)
            )
            # برای اینکه halign/valign درست کار کند
            self._label_widget.bind(size=self._update_text_size)
        
        if self._label_widget:
            self.add_widget(self._label_widget)
    
    def _update_text_size(self, instance, value):
        """به‌روزرسانی text_size برای Label معمولی"""
        instance.text_size = (instance.width, None)
    
    def set_text(self, text):
        self._text = text
        self._build_label()
    
    @property
    def text(self):
        return self._text
    
    @text.setter
    def text(self, value):
        self.set_text(str(value) if value else "")
