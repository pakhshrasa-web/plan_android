import arabic_reshaper
from bidi.algorithm import get_display

def f(text):
    if not text or not isinstance(text, str):
        return text
    try:
        return get_display(arabic_reshaper.reshape(text))
    except:
        return text
