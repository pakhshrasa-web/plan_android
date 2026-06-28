"""
ویجت‌های RTL برای پشتیبانی از متن فارسی
"""

from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.core.text import LabelBase
from kivy.graphics import Color, Rectangle, RoundedRectangle

# ========== کتابخانه Pillow برای نمایش فارسی ==========
try:
    from utils.persian_text import PersianLabel
    HAS_PILLOW = True
    print("✅ Pillow برای نمایش فارسی بارگذاری شد")
except ImportError as e:
    HAS_PILLOW = False
    print(f"⚠️ Pillow در دسترس نیست: {e}")


def is_rtl_text(text):
    """تشخیص RTL بودن متن"""
    if not text:
        return False
    text = str(text)
    rtl_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF' or '\uFB50' <= c <= '\uFDFF')
    ltr_chars = sum(1 for c in text if c.isalpha() and not ('\u0600' <= c <= '\u06FF'))
    if rtl_chars == 0 and ltr_chars == 0:
        return False
    return rtl_chars > ltr_chars


class RTLTextInput(BoxLayout):
    """
    ✅ فیلد ورودی با پشتیبانی از RTL و فونت فارسی
    """
    def __init__(self, **kwargs):
        # استخراج پارامترها
        self._hint_text = kwargs.pop('hint_text', '')
        self._password = kwargs.pop('password', False)
        self._multiline = kwargs.pop('multiline', False)
        self._text = kwargs.pop('text', '')
        self._font_size = kwargs.pop('font_size', dp(24))
        self._input_filter = kwargs.pop('input_filter', None)
        
        # تنظیمات ظاهری
        height = kwargs.pop('height', dp(55))
        size_hint_y = kwargs.pop('size_hint_y', None)
        
        super().__init__(**kwargs)
        
        self.orientation = 'vertical'
        if size_hint_y is not None:
            self.size_hint_y = size_hint_y
        self.height = height
        self.padding = dp(10)
        
        # ذخیره کردن رنگ‌های پس‌زمینه و حاشیه
        self.bg_color = (1, 1, 1, 1)
        self.border_color = (0.7, 0.7, 0.7, 1)
        self.border_color_focus = (0.2, 0.5, 0.8, 1)
        
        # پس‌زمینه و حاشیه با Canvas
        with self.canvas.before:
            # پس‌زمینه سفید
            self.bg_color_inst = Color(*self.bg_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )
            # حاشیه
            self.border_color_inst = Color(*self.border_color)
            self.border_rect = RoundedRectangle(
                pos=(self.x + 1, self.y + 1),
                size=(self.width - 2, self.height - 2),
                radius=[dp(7)]
            )
        
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # TextInput مخفی برای دریافت ورودی
        self._hidden_input = TextInput(
            text=self._text,
            password=self._password,
            multiline=self._multiline,
            font_size=self._font_size,
            size_hint=(1, 1),
            opacity=0,
            disabled=False,
            input_filter=self._input_filter,
            background_color=(0, 0, 0, 0),
            foreground_color=(0, 0, 0, 1),
            cursor_color=(0.2, 0.5, 0.8, 1),
            halign='right'
        )
        self._hidden_input.bind(text=self._on_text_change)
        self._hidden_input.bind(focus=self._on_focus)
        
        # PersianLabel برای نمایش متن
        display_text = self._text if self._text else self._hint_text
        is_hint = not self._text
        
        # تبدیل رنگ برای PersianLabel
        color = (0.5, 0.5, 0.5, 1) if is_hint else (0, 0, 0, 1)
        color_rgb = tuple(int(c * 255) for c in color)
        
        self.label = PersianLabel(
            text=display_text,
            font_size=self._font_size,
            color=color_rgb,
            size_hint=(1, 1),
            halign='right'
        )
        
        # ترتیب اضافه کردن: اول PersianLabel، سپس TextInput
        self.add_widget(self.label)
        self.add_widget(self._hidden_input)
    
    def _update_rect(self, instance, value):
        """به‌روزرسانی پس‌زمینه و حاشیه"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border_rect.pos = (self.x + 1, self.y + 1)
        self.border_rect.size = (self.width - 2, self.height - 2)
    
    def _on_focus(self, instance, value):
        """وقتی فوکوس تغییر میکنه، رنگ حاشیه رو عوض کن"""
        self.canvas.before.remove(self.border_color_inst)
        
        if value:
            self.border_color_inst = Color(*self.border_color_focus)
        else:
            self.border_color_inst = Color(*self.border_color)
        
        self.canvas.before.add(self.border_color_inst)
        if self.border_rect in self.canvas.before.children:
            self.canvas.before.remove(self.border_rect)
        self.canvas.before.add(self.border_rect)
    
    def _on_text_change(self, instance, value):
        """وقتی متن تغییر میکنه، PersianLabel رو به‌روز کن"""
        self._text = value
        if value:
            color = (0, 0, 0, 1)
            color_rgb = tuple(int(c * 255) for c in color)
            self.label.set_text(value)
            self.label.color = color_rgb
            self.label._update_texture()
        else:
            color = (0.5, 0.5, 0.5, 1)
            color_rgb = tuple(int(c * 255) for c in color)
            self.label.set_text(self._hint_text)
            self.label.color = color_rgb
            self.label._update_texture()
    
    def get_text(self):
        return self._hidden_input.text
    
    @property
    def text(self):
        return self._hidden_input.text
    
    @text.setter
    def text(self, value):
        self._text = value
        self._hidden_input.text = value
        self._on_text_change(self._hidden_input, value)


class RTLSpinner(Spinner):
    """Spinner با پشتیبانی از RTL و فونت فارسی"""
    
    def __init__(self, **kwargs):
        if 'font_name' not in kwargs:
            kwargs['font_name'] = 'PersianFont'
        kwargs['halign'] = 'right'
        kwargs['text_autoupdate'] = True
        kwargs['size_hint_y'] = None
        kwargs['height'] = dp(50)
        super().__init__(**kwargs)


# RTLLabel - با تبدیل درست رنگ
class RTLLabel(PersianLabel):
    """
    RTLLabel - با پشتیبانی از رنگ‌های float و int
    """
    def __init__(self, **kwargs):
        kwargs.pop('bold', None)
        kwargs.pop('markup', None)
        kwargs.pop('halign', None)
        kwargs.pop('valign', None)
        kwargs.pop('text_size', None)
        kwargs.pop('font_name', None)
        kwargs.pop('size_hint_x', None)
        kwargs.pop('size_hint_y', None)
        
        text = kwargs.pop('text', '')
        font_size = kwargs.pop('font_size', 24)
        
        color = kwargs.pop('color', (0, 0, 0, 1))
        
        def to_int(val):
            try:
                if isinstance(val, float):
                    return int(val * 255) if val <= 1 else int(val)
                return int(val)
            except:
                return 0
        
        if isinstance(color, (tuple, list)):
            if len(color) >= 3:
                r = to_int(color[0])
                g = to_int(color[1])
                b = to_int(color[2])
                a = to_int(color[3]) if len(color) >= 4 else 255
                color = (r, g, b, a)
            else:
                color = (0, 0, 0, 255)
        else:
            try:
                val = to_int(color)
                color = (val, val, val, 255)
            except:
                color = (0, 0, 0, 255)
        
        color = tuple(int(c) for c in color)
        
        super().__init__(text=text, font_size=font_size, color=color, **kwargs)


# ✅ PersianButton جدید - با استفاده از PersianLabel
class PersianButton(Button):
    """دکمه با پشتیبانی از متن فارسی - با استفاده از PersianLabel"""
    def __init__(self, **kwargs):
        # استخراج متن
        text = kwargs.pop('text', '')
        font_size = kwargs.pop('font_size', sp(18))
        
        # حذف پارامترهای اضافی
        kwargs.pop('font_name', None)
        kwargs.pop('halign', None)
        kwargs.pop('valign', None)
        kwargs.pop('markup', None)
        kwargs.pop('text_size', None)
        kwargs.pop('bold', None)
        
        super().__init__(**kwargs)
        
        # ساخت PersianLabel برای نمایش متن
        self.label = PersianLabel(
            text=text,
            font_size=font_size,
            color=(255, 255, 255, 255),
            size_hint=(1, 1),
            halign='center'
        )
        self.add_widget(self.label)
        
        # وقتی دکمه تغییر اندازه میده، label هم تغییر کنه
        self.bind(size=self._update_label, pos=self._update_label)
        self._update_label()
    
    def _update_label(self, *args):
        self.label.size = self.size
        self.label.pos = self.pos
    
    def set_text(self, text):
        self.label.set_text(text)