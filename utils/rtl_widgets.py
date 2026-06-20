from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner

class RTLTextInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = (10, 10, 10, 10)
        self.font_name = 'Vazirmatn'
        self.halign = 'right'

class RTLSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'Vazirmatn'
