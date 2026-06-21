"""
نسخه دیباگ برنامه - با ذخیره‌ی خطا در فایل
"""

import os
import sys
import traceback

# ========== ذخیره‌ی خطا در فایل (بدون هیچ وابستگی) ==========
def log_crash(error_msg, error_details):
    try:
        # تلاش برای ذخیره در حافظه داخلی
        with open('/sdcard/planandroid_crash_log.txt', 'a', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write(f"خطا: {error_msg}\n")
            f.write(f"جزئیات:\n{error_details}\n")
            f.write("="*60 + "\n\n")
        print("✅ خطا در /sdcard/planandroid_crash_log.txt ذخیره شد.")
    except:
        # اگر نتونست در sdcard ذخیره کنه، در پوشه‌ی فعلی ذخیره کن
        try:
            with open('crash_log.txt', 'a', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write(f"خطا: {error_msg}\n")
                f.write(f"جزئیات:\n{error_details}\n")
                f.write("="*60 + "\n\n")
            print("✅ خطا در crash_log.txt ذخیره شد.")
        except:
            print("❌ خطا در ذخیره‌سازی لاگ!")

# ========== هندلر سراسری خطا ==========
def global_exception_handler(exc_type, exc_value, exc_tb):
    error_msg = str(exc_value)
    error_details = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    log_crash(error_msg, error_details)

sys.excepthook = global_exception_handler

# ========== حالا برنامه اصلی رو اجرا کن ==========
try:
    print("🚀 شروع برنامه...")
    
    # ایمپورت برنامه اصلی
    from main import MainApp
    
    print("✅ برنامه اصلی با موفقیت وارد شد.")
    MainApp().run()
    
except Exception as e:
    error_msg = str(e)
    error_details = traceback.format_exc()
    log_crash(error_msg, error_details)
    print(f"❌ خطا در اجرای برنامه: {e}")
