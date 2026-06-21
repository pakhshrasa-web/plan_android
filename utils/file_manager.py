"""
مدیریت فایل‌های JSON - نسخه کامل با پشتیبانی از اندروید
"""

import os
import json
from kivy.app import App
from kivy.utils import platform

def get_data_path():
    """
    دریافت مسیر پوشه دیتا
    پشتیبانی از اندروید و دسکتاپ
    """
    try:
        app = App.get_running_app()
        if app:
            # استفاده از user_data_dir که در اندروید کار میکنه
            if hasattr(app, 'user_data_dir'):
                path = app.user_data_dir
                os.makedirs(path, exist_ok=True)
                return path
            elif hasattr(app, 'data_path'):
                path = app.data_path
                os.makedirs(path, exist_ok=True)
                return path
    except:
        pass
    
    # Fallback برای اندروید
    if platform == 'android':
        try:
            from android.storage import app_storage_path
            path = app_storage_path()
            os.makedirs(path, exist_ok=True)
            return path
        except:
            pass
    
    # Fallback نهایی
    path = os.path.join(os.getcwd(), 'data')
    os.makedirs(path, exist_ok=True)
    return path

# ... بقیه توابع مثل قبل ...
