from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner

# استفاده از فونت پیشفرض اگر Vazirmatn ثبت نشده باشه
try:
    from kivy.core.text import LabelBase
    FONT_NAME = 'Vazirmatn' if 'Vazirmatn' in LabelBase._fonts else 'Roboto'
except:
    FONT_NAME = 'Roboto'

class RTLTextInput(TextInput):
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', FONT_NAME)
        kwargs.setdefault('halign', 'right')
        kwargs.setdefault('padding', (10, 10, 10, 10))
        super().__init__(**kwargs)

class RTLSpinner(Spinner):
    def __init__(self, **kwargs):
        kwargs.setdefault('font_name', FONT_NAME)
        super().__init__(**kwargs)
