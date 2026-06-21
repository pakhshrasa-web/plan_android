"""
کمک‌کننده برای نمایش صحیح متن فارسی
"""

import arabic_reshaper
from bidi.algorithm import get_display

# کش برای بهبود عملکرد
_reshape_cache = {}

def f(text):
    """تبدیل متن فارسی به شکل صحیح برای نمایش در Kivy"""
    if not text or not isinstance(text, str):
        return text
    
    # اگر در کش وجود داره
    if text in _reshape_cache:
        return _reshape_cache[text]
    
    try:
        result = get_display(arabic_reshaper.reshape(text))
        # ذخیره در کش (با محدودیت)
        if len(_reshape_cache) < 200:
            _reshape_cache[text] = result
        return result
    except:
        return text

def clear_cache():
    """پاک کردن کش"""
    global _reshape_cache
    _reshape_cache = {}
