"""
اپلیکیشن مدیریت ویزیت و فروش - نسخه نهایی با نمایش خطا به صورت پاپ‌آپ
"""

# ========== تنظیم فونت و مسیرها (اصلاح شده برای اندروید) ==========
import os
import json
import sys
import traceback
from kivy.config import Config
from kivy.core.text import LabelBase
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.utils import platform
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.properties import StringProperty 
# ========== هندلر خطا ==========
def exception_handler(exc_type, exc_value, exc_tb):
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    
    paths = [
        '/storage/emulated/0/planandroid_crash.txt',
        '/sdcard/planandroid_crash.txt',
        '/data/data/org.pakhshrasa.planandroid/files/crash.txt',
    ]
    
    for path in paths:
        try:
            dir_path = os.path.dirname(path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("❌ CRASH ERROR:\n")
                f.write("="*60 + "\n")
                f.write(error_msg)
                f.write("="*60 + "\n")
            print(f"✅ Crash log saved to: {path}")
            break
        except Exception as e:
            print(f"Could not write to {path}: {e}")
            continue
    
    print("="*60)
    print("❌ CRASH ERROR:")
    print(error_msg)
    print("="*60)

sys.excepthook = exception_handler

# ========== تنظیمات مدیر ==========
ADMIN_EMAIL = "pakhshrasa@gmail.com"
DEFAULT_ADMIN_PASSWORD = "admin123"

# ========== سیستم نمایش خطا ==========
class ErrorPopup:
    """نمایش خطا به صورت پنجره بازشو با قابلیت کپی متن"""
    
    @staticmethod
    def show_error(error_message, error_details=""):
        try:
            from utils.rtl_widgets import RTLLabel, PersianButton
            
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
            
            title_label = RTLLabel(
                text="[b][color=ff3333]⚠️ خطا در برنامه[/color][/b]",
                markup=True,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(18)
            )
            content.add_widget(title_label)
            
            msg_label = RTLLabel(
                text=f"[b]خطا:[/b] {error_message}",
                markup=True,
                size_hint_y=None,
                height=dp(60),
                text_size=(dp(400), None),
                halign='left'
            )
            content.add_widget(msg_label)
            
            if error_details:
                detail_label = RTLLabel(
                    text=f"[b]جزئیات:[/b]\n{error_details}",
                    markup=True,
                    size_hint_y=None,
                    height=dp(300),
                    text_size=(dp(400), None),
                    halign='left',
                    font_size=sp(12)
                )
                scroll = ScrollView(size_hint_y=None, height=dp(300))
                scroll.add_widget(detail_label)
                content.add_widget(scroll)
            else:
                content.add_widget(RTLLabel(
                    text="",
                    size_hint_y=None,
                    height=dp(20)
                ))
            
            btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
            copy_btn = PersianButton(text='📋 کپی متن خطا', background_color=(0.2, 0.4, 0.8, 1), size_hint_y=None, height=dp(45))
            close_btn = PersianButton(text='✖ بستن', background_color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=dp(45))
            
            btn_layout.add_widget(copy_btn)
            btn_layout.add_widget(close_btn)
            content.add_widget(btn_layout)
            
            popup = Popup(title='⚠️ گزارش خطا', 
                          content=content, 
                          size_hint=(0.92, 0.75),
                          auto_dismiss=False)
            
            def copy_error(instance):
                full_text = f"خطا: {error_message}\n\nجزئیات:\n{error_details}"
                try:
                    from kivy.core.clipboard import Clipboard
                    Clipboard.copy(full_text)
                    copy_btn.text = '✅ کپی شد!'
                    Clock.schedule_once(lambda dt: setattr(copy_btn, 'text', '📋 کپی متن خطا'), 2)
                except:
                    copy_btn.text = '⚠️ دستی کپی کن'
            
            def close_popup(instance):
                popup.dismiss()
            
            copy_btn.bind(on_press=copy_error)
            close_btn.bind(on_press=close_popup)
            
            popup.open()
            
            print("="*60)
            print(f"❌ خطا: {error_message}")
            print(f"📋 جزئیات:\n{error_details}")
            print("="*60)
            
            try:
                from utils.storage import get_data_path
                data_path = get_data_path()
                log_dir = os.path.join(data_path, 'logs')
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(log_dir, 'crash_report.txt')
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(f"خطا: {error_message}\n\n")
                    f.write(f"جزئیات:\n{error_details}\n")
                    f.write("="*60 + "\n")
            except:
                try:
                    with open('/sdcard/planandroid_error.txt', 'w', encoding='utf-8') as f:
                        f.write(f"خطا: {error_message}\n\n")
                        f.write(f"جزئیات:\n{error_details}\n")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ خطا در نمایش پاپ‌آپ: {e}")

# ========== هندلر سراسری خطا ==========
def global_exception_handler(exc_type, exc_value, exc_tb):
    error_msg = str(exc_value)
    error_details = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    ErrorPopup.show_error(error_msg, error_details)

sys.excepthook = global_exception_handler

# ========== مدیریت مسیرها و فونت ==========
def get_app_root():
    from kivy.utils import platform
    if platform == 'android':
        try:
            from android.storage import app_storage_path
            return app_storage_path()
        except ImportError:
            return os.getcwd()
    else:
        return os.getcwd()

def setup_font():
    """تنظیم فونت فارسی + دیباگ کامل"""

    print("\n" + "=" * 60)
    print("شروع بررسی فونت")
    print("=" * 60)

    print("Current Working Directory:")
    print(os.getcwd())

    print("\nRoot files:")
    try:
        print(os.listdir("."))
    except Exception as e:
        print("خطا:", e)

    print("\nFonts directory:")
    try:
        print(os.listdir("fonts"))
    except Exception as e:
        print("خطا:", e)

    print("=" * 60)

    font_paths = [
        "fonts/Amiri-Regular.ttf",
        "fonts/Lateef-Regular.ttf",
        "fonts/NotoNasrArabic-Regular.ttf",
        "fonts/Vazirmatn-Regular.ttf",
        os.path.join(os.path.dirname(__file__), "fonts", "Amiri-Regular.ttf"),
        os.path.join(os.path.dirname(__file__), "fonts", "Lateef-Regular.ttf"),
        os.path.join(os.path.dirname(__file__), "fonts", "NotoNasrArabic-Regular.ttf"),
        os.path.join(os.path.dirname(__file__), "fonts", "Vazirmatn-Regular.ttf"),
    ]

    font_path = None

    print("\nبررسی مسیرهای فونت:\n")

    for path in font_paths:
        exists = os.path.exists(path)
        print(f"{path}   --->   {exists}")

        if exists:
            font_path = path
            break

    if font_path:
        print("\n✅ فونت انتخاب شد:")
        print(font_path)

        try:
            LabelBase.register(
                name="PersianFont",
                fn_regular=font_path
            )
            print("✅ فونت با نام 'PersianFont' ثبت شد.")

            Config.set('kivy', 'default_font', ['PersianFont', 'Roboto'])
            print("✅ فونت پیش‌فرض تنظیم شد.")

            return True

        except Exception as e:
            print("❌ خطا در ثبت فونت:")
            print(e)
            Config.set('kivy', 'default_font', ['Roboto'])
            return False

    else:
        print("\n❌ هیچ فونتی پیدا نشد.")
        Config.set('kivy', 'default_font', ['Roboto'])
        return False

setup_font()

if platform != 'android':
    Window.size = (400, 650)
    
# ========== ایمپورت ماژول‌های برنامه ==========
try:
    from utils.rtl_widgets import RTLTextInput, RTLSpinner, PersianComboBox, PersianButton, RTLLabel
    from utils.persian_text import PersianLabel
    from utils.text_helper import f
    from utils.storage import get_data_path, init_data_path
    from utils.file_manager import (
        get_agents, add_agent, delete_agent,
        get_routes, add_route, delete_route,
        get_customers, add_customer, delete_customer,
        get_settings, update_settings,
        get_daily_logs, save_daily_log
    )
    from utils.jalali_date import get_today_jalali, get_current_time
    from utils.user_manager import login, register_user, get_users, delete_user_by_id, get_codes, create_code
    from utils.auth import get_admin_password, set_admin_password, verify_password
    from utils.excel_importer import import_routes_from_excel, import_customers_from_excel
    from utils.excel_exporter import export_to_excel
    from utils.file_picker import FilePicker

    RTLLabel = PersianLabel
    
except Exception as e:
    error_details = traceback.format_exc()
    ErrorPopup.show_error(f"خطا در بارگذاری ماژول‌ها: {e}", error_details)

# ========== تعریف نقش‌ها ==========
ROLES = ['بازاریاب', 'سوپروایزر', 'سرپرست', 'مدیر', 'حسابدار', 'موزع', 'راننده', 'انباردار', 'سایر']

# ========== صفحات برنامه ==========

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.build_ui()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت LoginScreen: {e}", error_details)
            raise
    
    def build_ui(self):
        try:
            layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(5))
            
            # ========== دکمه مدیریت (سمت چپ بالا) ==========
            header_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
            settings_btn = PersianButton(
                text='مدیریت',
                size_hint_x=0.2,
                background_color=(0.3, 0.3, 0.3, 1),
                size_hint_y=None,
                height=dp(36)
            )
            settings_btn.bind(on_press=self.open_settings)
            header_layout.add_widget(settings_btn)
            header_layout.add_widget(Label(text='', size_hint_x=0.8))
            layout.add_widget(header_layout)
            
            # ========== فاصله ۱ سانت ==========
            layout.add_widget(Label(size_hint_y=None, height=dp(10)))
            
            # ========== عنوان مدیریت فروش ==========
            title = RTLLabel(
                text='مدیریت فروش',
                font_size=sp(32),
                size_hint_y=None,
                height=dp(50)
            )
            layout.add_widget(title)
            
            # ========== فاصله ۱ سانت ==========
            layout.add_widget(Label(size_hint_y=None, height=dp(10)))
            
            # ========== فیلد نام کاربری ==========
            self.username = RTLTextInput(
                hint_text='نام کاربری',
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            layout.add_widget(self.username)
            
            # ========== فاصله ۲ میلیمتر ==========
            layout.add_widget(Label(size_hint_y=None, height=dp(2)))
            
            # ========== فیلد رمز عبور ==========
            self.password = RTLTextInput(
                hint_text='رمز عبور',
                password=True,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            layout.add_widget(self.password)
            
            # ========== فاصله ۳ میلیمتر ==========
            layout.add_widget(Label(size_hint_y=None, height=dp(3)))
            
            # ========== دکمه ورود ==========
            btn = PersianButton(
                text='ورود',
                size_hint_y=None,
                height=dp(45)
            )
            btn.bind(on_press=self.check_login)
            layout.add_widget(btn)
            
            # ========== فاصله ۳ میلیمتر ==========
            layout.add_widget(Label(size_hint_y=None, height=dp(3)))
            
            # ========== دکمه ثبت نام ==========
            register_btn = PersianButton(
                text='ثبت نام',
                size_hint_y=None,
                height=dp(40),
                background_color=(0.3, 0.6, 0.3, 1)
            )
            register_btn.bind(on_press=self.open_register)
            layout.add_widget(register_btn)
            
            self.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت UI LoginScreen: {e}", error_details)
            raise
    
    def open_settings(self, instance):
        self.manager.current = 'settings_login'
    
    def open_register(self, instance):
        self.manager.current = 'register'
    
    def check_login(self, instance):
        try:
            user = login(self.username.text, self.password.text)
            if user:
                if user.get('role') == 'مدیر':
                    self.manager.current = 'admin'
                else:
                    self.manager.current = 'user'
            else:
                self.show_message('خطا', 'نام کاربری یا رمز عبور اشتباه است')
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ورود: {e}", error_details)
    
    def show_message(self, title, message):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(RTLLabel(
                text=message,
                size_hint_y=None,
                height=dp(50),
            ))
            btn = PersianButton(text='باشه', size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=title, content=content, size_hint=(0.8, 0.35))
            btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش پیام: {e}", error_details)


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.build_ui()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت RegisterScreen: {e}", error_details)
            raise
    
    def build_ui(self):
        try:
            layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(40))
            
            title = RTLLabel(
                text='ثبت نام کاربر جدید',
                font_size=sp(24),
                size_hint_y=0.1,
            )
            layout.add_widget(title)
            
            self.code_input = RTLTextInput(hint_text='کد ثبت نام', multiline=False, size_hint_y=None, height=dp(55))
            layout.add_widget(self.code_input)
            
            self.username = RTLTextInput(hint_text='نام کاربری', multiline=False, size_hint_y=None, height=dp(55))
            layout.add_widget(self.username)
            
            self.password = RTLTextInput(hint_text='رمز عبور', password=True, multiline=False, size_hint_y=None, height=dp(55))
            layout.add_widget(self.password)
            
            self.confirm_password = RTLTextInput(hint_text='تکرار رمز عبور', password=True, multiline=False, size_hint_y=None, height=dp(55))
            layout.add_widget(self.confirm_password)
            
            self.phone = RTLTextInput(hint_text='شماره تلفن', multiline=False, size_hint_y=None, height=dp(55))
            layout.add_widget(self.phone)
            
            self.email = RTLTextInput(hint_text='ایمیل', multiline=False, size_hint_y=None, height=dp(55))
            layout.add_widget(self.email)
            
            btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(55))
            register_btn = PersianButton(text='ثبت نام', background_color=(0.2, 0.7, 0.2, 1), size_hint_y=None, height=dp(50))
            register_btn.bind(on_press=self.do_register)
            btn_layout.add_widget(register_btn)
            
            back_btn = PersianButton(text='بازگشت', background_color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(50))
            back_btn.bind(on_press=self.go_back)
            btn_layout.add_widget(back_btn)
            
            layout.add_widget(btn_layout)
            self.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت UI RegisterScreen: {e}", error_details)
            raise
    
    def do_register(self, instance):
        try:
            if self.password.text != self.confirm_password.text:
                self.show_message('خطا', 'رمز عبور و تکرار آن مطابقت ندارند')
                return
            
            success, message = register_user(
                self.code_input.text,
                self.username.text,
                self.password.text,
                self.phone.text,
                self.email.text
            )
            
            if success:
                self.show_message('موفق', message)
                self.manager.current = 'login'
            else:
                self.show_message('خطا', message)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ثبت نام: {e}", error_details)
    
    def go_back(self, instance):
        self.manager.current = 'login'
    
    def show_message(self, title, message):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(RTLLabel(
                text=message,
                size_hint_y=None,
                height=dp(50),
            ))
            btn = PersianButton(text='باشه', size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=title, content=content, size_hint=(0.8, 0.35))
            btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش پیام: {e}", error_details)


class AdminSettingsScreen(Screen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.build_ui()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت AdminSettingsScreen: {e}", error_details)
            raise
    
    def build_ui(self):
        try:
            layout = BoxLayout(orientation='vertical', padding=[dp(5), dp(5), dp(5), dp(5)])
            
            # ❌ هدر حذف شد
            
            # ========== تب‌ها (از راست به چپ) ==========
            tabs_layout = BoxLayout(
                size_hint_y=None,
                height=dp(38),
                spacing=dp(2)
            )
            
            btn_password = PersianButton(
                text='تغییر رمز',
                background_color=(0.3, 0.5, 0.8, 0.6),
                size_hint_y=None,
                height=dp(34)
            )
            btn_password.bind(on_press=lambda x: self.switch_tab(3))
            tabs_layout.add_widget(btn_password)
            
            btn_codes = PersianButton(
                text='کدهای ثبت نام',
                background_color=(0.3, 0.5, 0.8, 0.6),
                size_hint_y=None,
                height=dp(34)
            )
            btn_codes.bind(on_press=lambda x: self.switch_tab(1))
            tabs_layout.add_widget(btn_codes)
            
            btn_users = PersianButton(
                text='مدیریت کاربران',
                background_color=(0.3, 0.5, 0.8, 1),
                size_hint_y=None,
                height=dp(34)
            )
            btn_users.bind(on_press=lambda x: self.switch_tab(0))
            tabs_layout.add_widget(btn_users)
            
            # ❌ تب تنظیمات عمومی حذف شد
            
            layout.add_widget(tabs_layout)
            
            # ========== محتوای تب‌ها ==========
            self.content_area = BoxLayout(orientation='vertical')
            layout.add_widget(self.content_area)
            
            # ========== دکمه بازگشت ==========
            back_btn = PersianButton(
                text='بازگشت',
                background_color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(36)
            )
            back_btn.bind(on_press=self.go_back)
            layout.add_widget(back_btn)
            
            self.add_widget(layout)
            self.switch_tab(0)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت UI AdminSettingsScreen: {e}", error_details)
            raise
    
    def switch_tab(self, tab_id):
        try:
            self.content_area.clear_widgets()
            
            if tab_id == 0:
                self.show_users_tab()
            elif tab_id == 1:
                self.show_codes_tab()
            elif tab_id == 2:
                self.show_general_settings_tab()
            elif tab_id == 3:
                self.show_change_password_tab()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در تغییر تب: {e}", error_details)
    
    def show_change_password_tab(self):
        try:
            layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
            
            # عنوان
            layout.add_widget(RTLLabel(
                text='تغییر رمز عبور مدیر',
                size_hint_y=None,
                height=dp(40),
                font_size=sp(18),
                bold=True,
                color=(0.2, 0.5, 0.8, 1)
            ))
            
            # رمز فعلی
            layout.add_widget(RTLLabel(
                text='رمز عبور فعلی:',
                size_hint_y=None,
                height=dp(28),
                font_size=sp(14)
            ))
            self.old_password = RTLTextInput(
                password=True,
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36),
                hint_text='رمز عبور فعلی را وارد کنید'
            )
            layout.add_widget(self.old_password)
            
            # رمز جدید
            layout.add_widget(RTLLabel(
                text='رمز عبور جدید:',
                size_hint_y=None,
                height=dp(28),
                font_size=sp(14)
            ))
            self.new_password = RTLTextInput(
                password=True,
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36),
                hint_text='رمز عبور جدید را وارد کنید'
            )
            layout.add_widget(self.new_password)
            
            # تکرار رمز جدید
            layout.add_widget(RTLLabel(
                text='تکرار رمز عبور جدید:',
                size_hint_y=None,
                height=dp(28),
                font_size=sp(14)
            ))
            self.confirm_password = RTLTextInput(
                password=True,
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36),
                hint_text='تکرار رمز عبور جدید'
            )
            layout.add_widget(self.confirm_password)
            
            # دکمه‌ها
            btn_layout = BoxLayout(
                spacing=dp(10),
                size_hint_y=None,
                height=dp(48),
                padding=(0, dp(8), 0, 0)
            )
            
            save_btn = PersianButton(
                text='تغییر رمز',
                background_color=(0.2, 0.7, 0.2, 1),
                size_hint_y=None,
                height=dp(42)
            )
            save_btn.bind(on_press=self.change_password)
            btn_layout.add_widget(save_btn)
            
            clear_btn = PersianButton(
                text='پاک کردن',
                background_color=(0.8, 0.5, 0.2, 1),
                size_hint_y=None,
                height=dp(42)
            )
            clear_btn.bind(on_press=self.clear_password_fields)
            btn_layout.add_widget(clear_btn)
            
            layout.add_widget(btn_layout)
            self.content_area.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش تب تغییر رمز: {e}", error_details)
    
    def change_password(self, instance):
        try:
            old = self.old_password.text
            new = self.new_password.text
            confirm = self.confirm_password.text
            
            hashed = get_admin_password()
            if not hashed or not verify_password(old, hashed):
                self.show_message('خطا', 'رمز عبور فعلی اشتباه است')
                return
            
            if len(new) < 6:
                self.show_message('خطا', 'رمز عبور جدید باید حداقل 6 کاراکتر باشد')
                return
            
            if new != confirm:
                self.show_message('خطا', 'رمز عبور جدید و تکرار آن مطابقت ندارند')
                return
            
            set_admin_password(new)
            self.clear_password_fields(instance)
            self.show_message('موفق', 'رمز عبور با موفقیت تغییر کرد')
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در تغییر رمز: {e}", error_details)
    
    def clear_password_fields(self, instance):
        self.old_password.text = ''
        self.new_password.text = ''
        self.confirm_password.text = ''
    
    def show_users_tab(self):
        try:
            users = get_users()
            
            layout = ScrollView()
            content = GridLayout(
                cols=1,
                spacing=dp(5),
                size_hint_y=None,
                padding=dp(5)
            )
            content.bind(minimum_height=content.setter('height'))
            
            # ========== فاصله ۵ میلیمتر از تب ==========
            content.add_widget(Label(size_hint_y=None, height=dp(5)))
            
            # ========== عنوان ==========
            content.add_widget(RTLLabel(
                text='📋 لیست کاربران',
                size_hint_y=None,
                height=dp(32),
                font_size=sp(16),
                bold=True,
                color=(0.2, 0.5, 0.8, 1)
            ))
            
            if not users:
                content.add_widget(RTLLabel(
                    text='هیچ کاربری ثبت نشده است',
                    size_hint_y=None,
                    height=dp(32),
                    font_size=sp(14),
                    color=(0.5, 0.5, 0.5, 1)
                ))
            
            for user in users:
                user_box = BoxLayout(
                    size_hint_y=None,
                    height=dp(50),
                    spacing=dp(5)
                )
                
                info = f"{user.get('username', '')} | {user.get('name', '')} | {user.get('role', '')}"
                user_info = RTLLabel(
                    text=info,
                    size_hint_x=0.7,
                    font_size=sp(13)
                )
                user_box.add_widget(user_info)
                
                del_btn = PersianButton(
                    text='حذف',
                    size_hint_x=0.3,
                    background_color=(0.8, 0.2, 0.2, 1),
                    size_hint_y=None,
                    height=dp(32)
                )
                del_btn.bind(on_press=lambda x, uid=user.get('id'): self.delete_user(uid))
                user_box.add_widget(del_btn)
                content.add_widget(user_box)
            
            layout.add_widget(content)
            self.content_area.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش کاربران: {e}", error_details)
    
    def delete_user(self, user_id):
        try:
            users = get_users()
            username = ""
            for user in users:
                if user.get('id') == user_id:
                    username = user.get('username', '')
                    break
            
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
            content.add_widget(RTLLabel(
                text=f'آیا از حذف کاربر "{username}" مطمئن هستید؟',
                size_hint_y=None,
                height=dp(45),
                font_size=sp(16)
            ))
            
            btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))
            yes_btn = PersianButton(
                text='بله، حذف شود',
                size_hint_y=None,
                height=dp(40)
            )
            no_btn = PersianButton(
                text='خیر، انصراف',
                size_hint_y=None,
                height=dp(40)
            )
            btn_layout.add_widget(yes_btn)
            btn_layout.add_widget(no_btn)
            content.add_widget(btn_layout)
            
            popup = Popup(title='تایید حذف', content=content, size_hint=(0.8, 0.35))
            
            def do_delete(instance):
                delete_user_by_id(user_id)
                popup.dismiss()
                self.show_message('موفق', f'کاربر "{username}" با موفقیت حذف شد')
                self.switch_tab(0)
            
            def cancel_delete(instance):
                popup.dismiss()
            
            yes_btn.bind(on_press=do_delete)
            no_btn.bind(on_press=cancel_delete)
            popup.open()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در حذف کاربر: {e}", error_details)
    
    def show_codes_tab(self):
        try:
            roles = ['مدیر', 'ادمین', 'سوپروایزر', 'بازاریاب', 'حسابدار', 'موزع', 'راننده', 'انباردار', 'سایر']
            
            layout = ScrollView()
            content = GridLayout(
                cols=1,
                spacing=dp(4),
                size_hint_y=None,
                padding=dp(5)
            )
            content.bind(minimum_height=content.setter('height'))
            
            content.add_widget(Label(size_hint_y=None, height=dp(5)))
            
            # ✅ استفاده از PersianComboBox و ذخیره در self
            self.role_spinner = PersianComboBox(
                text='مدیر',
                values=roles,
                height=dp(45)
            )
            content.add_widget(self.role_spinner)
            
            content.add_widget(Label(size_hint_y=None, height=dp(2)))
            
            self.code_name_input = RTLTextInput(
                hint_text='نام و نام خانوادگی',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            content.add_widget(self.code_name_input)
            
            create_btn = PersianButton(
                text='ساخت کد',
                size_hint_y=None,
                height=dp(45),
                background_color=(0.2, 0.7, 0.2, 1)
            )
            content.add_widget(create_btn)
            
            def do_create(instance):
                try:
                    # ✅ گرفتن نقش درست از کمبوباکس
                    selected_role = self.role_spinner.text
                    name = self.code_name_input.text
                    
                    if not name:
                        self.show_message('خطا', 'لطفاً نام و نام خانوادگی را وارد کنید')
                        return
                    
                    code = create_code(selected_role, name)
                    self.show_message('موفق', f'کد ساخته شد:\n{code}')
                    self.code_name_input.text = ''
                    self.switch_tab(1)
                except Exception as e:
                    error_details = traceback.format_exc()
                    ErrorPopup.show_error(f"خطا در ساخت کد: {e}", error_details)
            
            create_btn.bind(on_press=do_create)
          
            # ========== لیست کدهای فعال ==========
            content.add_widget(RTLLabel(
                text='📋 کدهای فعال',
                size_hint_y=None,
                height=dp(35),
                font_size=sp(16),
                bold=True,
                color=(0.2, 0.5, 0.8, 1)
            ))
            
            codes = get_codes()
            has_codes = False
            for code_info in codes:
                if not code_info.get('used', False):
                    has_codes = True
                    code_box = BoxLayout(
                        size_hint_y=None,
                        height=dp(35),
                        spacing=dp(5)
                    )
                    code_text = f"{code_info['code']} - {code_info['role']} - {code_info['name']}"
                    code_label = RTLLabel(
                        text=code_text,
                        size_hint_x=1,
                        font_size=sp(14)
                    )
                    code_box.add_widget(code_label)
                    content.add_widget(code_box)
            
            if not has_codes:
                content.add_widget(RTLLabel(
                    text='هیچ کد فعالی وجود ندارد',
                    size_hint_y=None,
                    height=dp(35),
                    font_size=sp(14),
                    color=(0.5, 0.5, 0.5, 1)
                ))
            
            layout.add_widget(content)
            self.content_area.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش کدها: {e}", error_details)
   
    
    def show_message(self, title, message):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(RTLLabel(
                text=message,
                size_hint_y=None,
                height=dp(45),
                font_size=sp(16)
            ))
            btn = PersianButton(
                text='باشه',
                size_hint_y=None,
                height=dp(40)
            )
            content.add_widget(btn)
            popup = Popup(title=title, content=content, size_hint=(0.8, 0.35))
            btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش پیام: {e}", error_details)
    
    def go_back(self, instance):
        self.manager.current = 'login'


class AdminScreen(Screen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.current_tab = 0
            self.build_ui()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت AdminScreen: {e}", error_details)
            raise
    
    def build_ui(self):
        try:
            main_layout = BoxLayout(orientation='vertical', padding=[dp(5), dp(5), dp(5), dp(5)])
            
            # ❌ هدر حذف شد
            
            # ========== تب‌ها (در بالا) ==========
            tabs_layout = BoxLayout(
                size_hint_y=None,
                height=dp(38),
                spacing=dp(2)
            )
            
            btn_settings = PersianButton(
                text='⚙️ تنظیمات',
                background_color=(0.3, 0.5, 0.8, 0.6),
                size_hint_y=None,
                height=dp(34)
            )
            btn_settings.bind(on_press=lambda x: self.switch_tab(3))
            tabs_layout.add_widget(btn_settings)
            
            btn_customers = PersianButton(
                text='مشتریان',
                background_color=(0.3, 0.5, 0.8, 0.6),
                size_hint_y=None,
                height=dp(34)
            )
            btn_customers.bind(on_press=lambda x: self.switch_tab(2))
            tabs_layout.add_widget(btn_customers)
            
            btn_routes = PersianButton(
                text='مسیرها',
                background_color=(0.3, 0.5, 0.8, 0.6),
                size_hint_y=None,
                height=dp(34)
            )
            btn_routes.bind(on_press=lambda x: self.switch_tab(1))
            tabs_layout.add_widget(btn_routes)
            
            btn_agents = PersianButton(
                text='عامل‌ها',
                background_color=(0.3, 0.5, 0.8, 1),
                size_hint_y=None,
                height=dp(34)
            )
            btn_agents.bind(on_press=lambda x: self.switch_tab(0))
            tabs_layout.add_widget(btn_agents)
            
            main_layout.add_widget(tabs_layout)
            
            # ========== محتوای تب‌ها ==========
            self.content_area = BoxLayout(orientation='vertical')
            main_layout.add_widget(self.content_area)
            
            # ========== دکمه خروج ==========
            logout_btn = PersianButton(
                text='خروج',
                background_color=(0.8, 0.2, 0.2, 1),
                size_hint_y=None,
                height=dp(36)
            )
            logout_btn.bind(on_press=self.logout)
            main_layout.add_widget(logout_btn)
            
            self.add_widget(main_layout)
            self.switch_tab(0)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت UI AdminScreen: {e}", error_details)
            raise
    
    def switch_tab(self, tab_id):
        try:
            self.current_tab = tab_id
            self.content_area.clear_widgets()
            
            if tab_id == 0:
                self.show_agents_tab()
            elif tab_id == 1:
                self.show_routes_tab()
            elif tab_id == 2:
                self.show_customers_tab()
            elif tab_id == 3:
                self.show_settings_tab()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در تغییر تب: {e}", error_details)
    
    def show_agents_tab(self):
        try:
            layout = ScrollView()
            content = GridLayout(
                cols=1,
                spacing=dp(8),
                size_hint_y=None,
                padding=dp(10)
            )
            content.bind(minimum_height=content.setter('height'))
            
            # عنوان
            content.add_widget(RTLLabel(
                text='➕ افزودن عامل جدید',
                size_hint_y=None,
                height=dp(38),
                font_size=sp(16),
                bold=True,
                color=(0.2, 0.5, 0.8, 1)
            ))
            
            # فیلدها
            name_input = RTLTextInput(
                hint_text='نام کامل',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            content.add_widget(name_input)
            
            phone_input = RTLTextInput(
                hint_text='شماره تلفن',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            content.add_widget(phone_input)
            
            # ✅ استفاده از PersianComboBox
            role_spinner = PersianComboBox(
                text=ROLES[0],
                values=ROLES,
                size_hint_y=None,
                height=dp(50)
            )
            content.add_widget(role_spinner)
            
            email_input = RTLTextInput(
                hint_text='ایمیل',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            content.add_widget(email_input)
            
            
            add_btn = PersianButton(
                text='افزودن',
                size_hint_y=None,
                height=dp(45),
                background_color=(0.2, 0.7, 0.2, 1)
            )
            content.add_widget(add_btn)
            
            # لیست عامل‌ها
            content.add_widget(RTLLabel(
                text='📋 لیست عامل‌ها',
                size_hint_y=None,
                height=dp(38),
                font_size=sp(16),
                bold=True,
                color=(0.2, 0.5, 0.8, 1)
            ))
            
            agents = get_agents()
            if not agents:
                content.add_widget(RTLLabel(
                    text='هیچ عاملی ثبت نشده است',
                    size_hint_y=None,
                    height=dp(35),
                    font_size=sp(13),
                    color=(0.5, 0.5, 0.5, 1)
                ))
            
            for agent in agents:
                agent_box = BoxLayout(
                    size_hint_y=None,
                    height=dp(50),
                    spacing=dp(5),
                    padding=[dp(5), dp(5), dp(5), dp(5)]
                )
                agent_info = RTLLabel(
                    text=f"{agent.get('name', '')}\n{agent.get('role', '')}",
                    size_hint_x=0.7,
                    font_size=sp(13)
                )
                agent_box.add_widget(agent_info)
                del_btn = PersianButton(
                    text='حذف',
                    size_hint_x=0.3,
                    background_color=(0.8, 0.2, 0.2, 1),
                    size_hint_y=None,
                    height=dp(35)
                )
                del_btn.bind(on_press=lambda x, a=agent: self.delete_agent_and_refresh(a.get('id')))
                agent_box.add_widget(del_btn)
                content.add_widget(agent_box)
            
            add_btn.bind(on_press=lambda x: self.add_agent_and_refresh(name_input, phone_input, role_spinner, email_input))
            
            layout.add_widget(content)
            self.content_area.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش عامل‌ها: {e}", error_details)
    
    def add_agent_and_refresh(self, name_input, phone_input, role_spinner, email_input):
        try:
            if name_input.text:
                agent = {
                    'name': name_input.text,
                    'phone': phone_input.text,
                    'role': role_spinner.text,
                    'email': email_input.text,
                    'hire_date': get_today_jalali()
                }
                add_agent(agent)
                name_input.text = ''
                phone_input.text = ''
                email_input.text = ''
                self.show_message('موفق', 'عامل با موفقیت اضافه شد')
                self.switch_tab(0)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در افزودن عامل: {e}", error_details)
    
    def delete_agent_and_refresh(self, agent_id):
        try:
            delete_agent(agent_id)
            self.show_message('موفق', 'عامل با موفقیت حذف شد')
            self.switch_tab(0)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در حذف عامل: {e}", error_details)
    
    def show_routes_tab(self):
        try:
            layout = BoxLayout(orientation='vertical', padding=[dp(5), dp(5), dp(5), dp(5)])
            
            # تب‌های داخلی مسیرها
            tabs = BoxLayout(
                size_hint_y=None,
                height=dp(45),
                spacing=dp(3),
                padding=[dp(5), dp(5), dp(5), dp(5)]
            )
            
            btn_manual = PersianButton(
                text='مدیریت دستی',
                background_color=(0.3, 0.5, 0.8, 1),
                size_hint_y=None,
                height=dp(40)
            )
            btn_manual.bind(on_press=lambda x: self.show_manual_routes())
            tabs.add_widget(btn_manual)
            
            btn_excel = PersianButton(
                text='ورود از اکسل',
                background_color=(0.3, 0.5, 0.8, 0.6),
                size_hint_y=None,
                height=dp(40)
            )
            btn_excel.bind(on_press=lambda x: self.show_excel_routes())
            tabs.add_widget(btn_excel)
            
            layout.add_widget(tabs)
            
            # محتوای مسیرها
            self.routes_content = BoxLayout(orientation='vertical', padding=[dp(10), dp(10), dp(10), dp(10)])
            layout.add_widget(self.routes_content)
            
            self.show_manual_routes()
            self.content_area.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش مسیرها: {e}", error_details)
    
    def show_manual_routes(self):
        try:
            self.routes_content.clear_widgets()
            
            content = GridLayout(
                cols=1,
                spacing=dp(8),
                size_hint_y=None,
                padding=dp(10)
            )
            content.bind(minimum_height=content.setter('height'))
            
            # عنوان
            content.add_widget(RTLLabel(
                text='➕ افزودن مسیر جدید',
                size_hint_y=None,
                height=dp(38),
                font_size=sp(16),
                bold=True,
                color=(0.2, 0.5, 0.8, 1)
            ))
            
            self.route_name_input = RTLTextInput(
                hint_text='نام مسیر',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            content.add_widget(self.route_name_input)
            
            add_btn = PersianButton(
                text='افزودن',
                size_hint_y=None,
                height=dp(45),
                background_color=(0.2, 0.7, 0.2, 1)
            )
            add_btn.bind(on_press=self.add_route_manual)
            content.add_widget(add_btn)
            
            # لیست مسیرها
            content.add_widget(RTLLabel(
                text='🗺️ لیست مسیرها',
                size_hint_y=None,
                height=dp(38),
                font_size=sp(16),
                bold=True,
                color=(0.2, 0.5, 0.8, 1)
            ))
            
            self.routes_list = GridLayout(
                cols=1,
                spacing=dp(5),
                size_hint_y=None
            )
            self.routes_list.bind(minimum_height=self.routes_list.setter('height'))
            content.add_widget(self.routes_list)
            
            scroll = ScrollView()
            scroll.add_widget(content)
            self.routes_content.add_widget(scroll)
            
            self.refresh_routes_list()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش مسیرهای دستی: {e}", error_details)
    
    def refresh_routes_list(self):
        try:
            self.routes_list.clear_widgets()
            routes = get_routes()
            
            if not routes:
                self.routes_list.add_widget(RTLLabel(
                    text='هیچ مسیری ثبت نشده است',
                    size_hint_y=None,
                    height=dp(35),
                    font_size=sp(13),
                    color=(0.5, 0.5, 0.5, 1)
                ))
            
            for route in routes:
                box = BoxLayout(
                    size_hint_y=None,
                    height=dp(38),
                    spacing=dp(5),
                    padding=[dp(5), dp(5), dp(5), dp(5)]
                )
                box.add_widget(RTLLabel(
                    text=route.get('name', ''),
                    size_hint_x=0.7,
                    font_size=sp(14)
                ))
                del_btn = PersianButton(
                    text='حذف',
                    size_hint_x=0.3,
                    background_color=(0.8, 0.2, 0.2, 1),
                    size_hint_y=None,
                    height=dp(35)
                )
                del_btn.bind(on_press=lambda x, r=route: self.delete_route_and_refresh(r.get('id')))
                box.add_widget(del_btn)
                self.routes_list.add_widget(box)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در به‌روزرسانی لیست مسیرها: {e}", error_details)
    
    def add_route_manual(self, instance):
        try:
            if self.route_name_input.text:
                add_route({'name': self.route_name_input.text})
                self.route_name_input.text = ''
                self.refresh_routes_list()
                self.show_message('موفق', 'مسیر با موفقیت اضافه شد')
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در افزودن مسیر: {e}", error_details)
    
    def delete_route_and_refresh(self, route_id):
        try:
            delete_route(route_id)
            self.refresh_routes_list()
            self.show_message('موفق', 'مسیر با موفقیت حذف شد')
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در حذف مسیر: {e}", error_details)
    
    def show_excel_routes(self):
        try:
            self.routes_content.clear_widgets()
            
            layout = BoxLayout(
                orientation='vertical',
                padding=dp(15),
                spacing=dp(12)
            )
            
            # ✅ عنوان با PersianLabel
            title_label = PersianLabel(
                text='📎 ورود مسیرها از فایل Excel',
                font_size=sp(18),
                color=(255, 255, 255, 255),
                size_hint_y=None,
                height=dp(40),
                halign='right'
            )
            layout.add_widget(title_label)
            
            # ✅ متن راهنما با PersianLabel
            info_label = PersianLabel(
                text='فرمت فایل اکسل: ستون اول نام مسیر',
                font_size=sp(14),
                color=(200, 200, 200, 255),
                size_hint_y=None,
                height=dp(35),
                halign='right'
            )
            layout.add_widget(info_label)
            
            self.routes_file_picker = FilePicker(
                size_hint_y=None,
                height=dp(100)
            )
            layout.add_widget(self.routes_file_picker)
            
            import_btn = PersianButton(
                text='ورود به سیستم',
                background_color=(0.2, 0.7, 0.2, 1),
                size_hint_y=None,
                height=dp(45)
            )
            import_btn.bind(on_press=self.import_routes_from_excel)
            layout.add_widget(import_btn)
            
            self.routes_content.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش ورود اکسل مسیرها: {e}", error_details)
    
    def import_routes_from_excel(self, instance):
        try:
            filepath = self.routes_file_picker.get_file()
            if not filepath:
                self.show_message('خطا', 'لطفاً ابتدا فایل را انتخاب کنید')
                return
            
            success, message = import_routes_from_excel(filepath)
            self.show_message('موفق' if success else 'خطا', message)
            
            if success:
                self.show_manual_routes()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ورود مسیرها از اکسل: {e}", error_details)
    
    def show_customers_tab(self):
        try:
            layout = BoxLayout(orientation='vertical', padding=[dp(5), dp(5), dp(5), dp(5)])
            
            # تب‌های داخلی مشتریان
            tabs = BoxLayout(
                size_hint_y=None,
                height=dp(45),
                spacing=dp(3),
                padding=[dp(5), dp(5), dp(5), dp(5)]
            )
            
            btn_manual = PersianButton(
                text='مدیریت دستی',
                background_color=(0.3, 0.5, 0.8, 1),
                size_hint_y=None,
                height=dp(40)
            )
            btn_manual.bind(on_press=lambda x: self.show_manual_customers())
            tabs.add_widget(btn_manual)
            
            btn_excel = PersianButton(
                text='ورود از اکسل',
                background_color=(0.3, 0.5, 0.8, 0.6),
                size_hint_y=None,
                height=dp(40)
            )
            btn_excel.bind(on_press=lambda x: self.show_excel_customers())
            tabs.add_widget(btn_excel)
            
            layout.add_widget(tabs)
            
            # محتوای مشتریان
            self.customers_content = BoxLayout(orientation='vertical', padding=[dp(10), dp(10), dp(10), dp(10)])
            layout.add_widget(self.customers_content)
            
            self.show_manual_customers()
            self.content_area.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش مشتریان: {e}", error_details)
    
    def show_manual_customers(self):
        try:
            self.customers_content.clear_widgets()
            
            content = GridLayout(
                cols=1,
                spacing=dp(8),
                size_hint_y=None,
                padding=dp(10)
            )
            content.bind(minimum_height=content.setter('height'))
            
            # عنوان
            content.add_widget(RTLLabel(
                text='➕ افزودن مشتری جدید',
                size_hint_y=None,
                height=dp(38),
                font_size=sp(16),
                bold=True,
                color=(0.2, 0.5, 0.8, 1)
            ))
            
            # انتخاب مسیر
            content.add_widget(RTLLabel(
                text='انتخاب مسیر:',
                size_hint_y=None,
                height=dp(28),
                font_size=sp(14)
            ))
            routes = get_routes()
            route_names = [r.get('name', '') for r in routes] if routes else ['']
            self.customer_route_spinner = PersianComboBox(
                text=route_names[0] if route_names else '',
                values=route_names,
                size_hint_y=None,
                height=dp(50)
            )
            content.add_widget(self.customer_route_spinner)
            
            # فیلدهای مشتری
            self.customer_name_input = RTLTextInput(
                hint_text='نام مشتری',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            content.add_widget(self.customer_name_input)
            
            self.customer_store_input = RTLTextInput(
                hint_text='نام فروشگاه',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            content.add_widget(self.customer_store_input)
            
            self.customer_mobile_input = RTLTextInput(
                hint_text='موبایل',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            content.add_widget(self.customer_mobile_input)
            
            self.customer_address_input = RTLTextInput(
                hint_text='آدرس',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            content.add_widget(self.customer_address_input)
            
            add_btn = PersianButton(
                text='افزودن مشتری',
                size_hint_y=None,
                height=dp(45),
                background_color=(0.2, 0.7, 0.2, 1)
            )
            add_btn.bind(on_press=self.add_customer_manual)
            content.add_widget(add_btn)
            
            # لیست مشتریان
            content.add_widget(RTLLabel(
                text='📞 لیست مشتریان',
                size_hint_y=None,
                height=dp(38),
                font_size=sp(16),
                bold=True,
                color=(0.2, 0.5, 0.8, 1)
            ))
            
            self.customers_list = GridLayout(
                cols=1,
                spacing=dp(5),
                size_hint_y=None
            )
            self.customers_list.bind(minimum_height=self.customers_list.setter('height'))
            content.add_widget(self.customers_list)
            
            filter_btn = PersianButton(
                text='نمایش مشتریان این مسیر',
                size_hint_y=None,
                height=dp(40),
                background_color=(0.4, 0.5, 0.6, 1)
            )
            filter_btn.bind(on_press=self.refresh_customers_list)
            content.add_widget(filter_btn)
            
            scroll = ScrollView()
            scroll.add_widget(content)
            self.customers_content.add_widget(scroll)
            
            self.refresh_customers_list()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش مشتریان دستی: {e}", error_details)
    
    def refresh_customers_list(self, instance=None):
        try:
            self.customers_list.clear_widgets()
            
            selected_route = self.customer_route_spinner.text
            all_customers = get_customers()
            
            filtered = [c for c in all_customers if c.get('route_name') == selected_route]
            
            if not filtered:
                self.customers_list.add_widget(RTLLabel(
                    text='هیچ مشتری در این مسیر وجود ندارد',
                    size_hint_y=None,
                    height=dp(35),
                    font_size=sp(13),
                    color=(0.5, 0.5, 0.5, 1)
                ))
                return
            
            for customer in filtered:
                box = BoxLayout(
                    size_hint_y=None,
                    height=dp(50),
                    spacing=dp(5),
                    padding=[dp(5), dp(5), dp(5), dp(5)]
                )
                info = f"{customer.get('name', '')}\n{customer.get('store_name', '')}\n{customer.get('mobile', '')}"
                box.add_widget(RTLLabel(
                    text=info,
                    size_hint_x=0.7,
                    font_size=sp(12)
                ))
                del_btn = PersianButton(
                    text='حذف',
                    size_hint_x=0.3,
                    background_color=(0.8, 0.2, 0.2, 1),
                    size_hint_y=None,
                    height=dp(35)
                )
                del_btn.bind(on_press=lambda x, c=customer: self.delete_customer_and_refresh(c.get('id')))
                box.add_widget(del_btn)
                self.customers_list.add_widget(box)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در به‌روزرسانی لیست مشتریان: {e}", error_details)
    
    def add_customer_manual(self, instance):
        try:
            route_name = self.customer_route_spinner.text
            name = self.customer_name_input.text
            store = self.customer_store_input.text
            mobile = self.customer_mobile_input.text
            address = self.customer_address_input.text
            
            if not route_name:
                self.show_message('خطا', 'لطفاً ابتدا مسیر را انتخاب کنید')
                return
            
            if not name:
                self.show_message('خطا', 'نام مشتری الزامی است')
                return
            
            customer = {
                'name': name,
                'store_name': store,
                'route_name': route_name,
                'mobile': mobile,
                'address': address
            }
            add_customer(customer)
            
            self.customer_name_input.text = ''
            self.customer_store_input.text = ''
            self.customer_mobile_input.text = ''
            self.customer_address_input.text = ''
            
            self.refresh_customers_list()
            self.show_message('موفق', 'مشتری با موفقیت اضافه شد')
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در افزودن مشتری: {e}", error_details)
    
    def delete_customer_and_refresh(self, customer_id):
        try:
            delete_customer(customer_id)
            self.refresh_customers_list()
            self.show_message('موفق', 'مشتری با موفقیت حذف شد')
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در حذف مشتری: {e}", error_details)
    
    def show_excel_customers(self):
        try:
            self.customers_content.clear_widgets()
            
            layout = BoxLayout(
                orientation='vertical',
                padding=dp(15),
                spacing=dp(12)
            )
            
            # ✅ عنوان با PersianLabel
            title_label = PersianLabel(
                text='📎 ورود مشتریان از فایل Excel',
                font_size=sp(18),
                color=(255, 255, 255, 255),
                size_hint_y=None,
                height=dp(40),
                halign='right'
            )
            layout.add_widget(title_label)
            
            # ✅ متن راهنما با PersianLabel
            info_label = PersianLabel(
                text='فرمت فایل اکسل: name, store_name, route_name, mobile, address',
                font_size=sp(14),
                color=(200, 200, 200, 255),
                size_hint_y=None,
                height=dp(35),
                halign='right'
            )
            layout.add_widget(info_label)
            
            self.customers_file_picker = FilePicker(
                size_hint_y=None,
                height=dp(100)
            )
            layout.add_widget(self.customers_file_picker)
            
            import_btn = PersianButton(
                text='ورود به سیستم',
                background_color=(0.2, 0.7, 0.2, 1),
                size_hint_y=None,
                height=dp(45)
            )
            import_btn.bind(on_press=self.import_customers_from_excel)
            layout.add_widget(import_btn)
            
            self.customers_content.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش ورود اکسل مشتریان: {e}", error_details)
    
    def import_customers_from_excel(self, instance):
        try:
            filepath = self.customers_file_picker.get_file()
            if not filepath:
                self.show_message('خطا', 'لطفاً ابتدا فایل را انتخاب کنید')
                return
            
            success, message = import_customers_from_excel(filepath)
            self.show_message('موفق' if success else 'خطا', message)
            
            if success:
                self.show_manual_customers()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ورود مشتریان از اکسل: {e}", error_details)
    
    def show_settings_tab(self):
        try:
            settings = get_settings()
            
            layout = ScrollView()
            content = GridLayout(
                cols=2,
                spacing=dp(8),
                size_hint_y=None,
                padding=dp(10)
            )
            content.bind(minimum_height=content.setter('height'))
            
            fields = [
                ('supervision_rate', 'درصد سرکشی به مشتری', '0.3', 'float'),
                ('conversion_rate', 'نرخ تبدیل سرکشی به فاکتور', '0.25', 'float'),
                ('avg_invoice_amount', 'میانگین مبلغ فاکتور', '1000000', 'int'),
                ('target_amount', 'مبلغ تارگت ریالی', '50000000', 'int'),
                ('target_count', 'میزان تارگت تعدادی', '100', 'int'),
                ('target_invoice_count', 'میزان تارگت تعداد فاکتور', '20', 'int'),
                ('target_customer_count', 'میزان تارگت تعداد مشتری', '50', 'int'),
                ('target_new_customer_count', 'میزان تارگت مشتری جدید', '10', 'int'),
                ('target_cash_sales', 'تارگت فروش نقدی', '30000000', 'int'),
                ('target_credit_sales', 'تارگت فروش غیر نقدی', '20000000', 'int'),
                ('work_start_time', 'ساعت شروع به کار', '08:00', 'time'),
                ('first_visit_time', 'ساعت اولین ویزیت', '09:00', 'time'),
                ('min_daily_hours', 'حداقل ساعت کاری روزانه', '6', 'int'),
            ]
            
            inputs = {}
            for item in fields:
                key = item[0]
                label = item[1]
                default = item[2]
                field_type = item[3]
                
                # لیبل
                content.add_widget(RTLLabel(
                    text=label + ':',
                    size_hint_y=None,
                    height=dp(38),
                    font_size=sp(14)
                ))
                
                # فیلد
                value = settings.get(key, default)
                if field_type == 'float':
                    input_field = RTLTextInput(
                        text=str(value),
                        multiline=False,
                        size_hint_y=None,
                        height=dp(50),
                        input_filter='float',
                        font_size=sp(36)
                    )
                elif field_type == 'int':
                    input_field = RTLTextInput(
                        text=str(value),
                        multiline=False,
                        size_hint_y=None,
                        height=dp(50),
                        input_filter='int',
                        font_size=sp(36)
                    )
                elif field_type == 'time':
                    input_field = RTLTextInput(
                        text=value,
                        multiline=False,
                        size_hint_y=None,
                        height=dp(50),
                        hint_text='HH:MM',
                        font_size=sp(36)
                    )
                else:
                    input_field = RTLTextInput(
                        text=str(value),
                        multiline=False,
                        size_hint_y=None,
                        height=dp(50),
                        font_size=sp(36)
                    )
                
                content.add_widget(input_field)
                inputs[key] = input_field
            
            # دکمه ذخیره
            save_btn = PersianButton(
                text='ذخیره تنظیمات',
                size_hint_y=None,
                height=dp(45),
                background_color=(0.2, 0.6, 1, 1),
                size_hint_x=0.5
            )
            save_btn.bind(on_press=lambda x: self.save_settings(inputs))
            content.add_widget(save_btn)
            
            layout.add_widget(content)
            self.content_area.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش تنظیمات: {e}", error_details)
    
    def save_settings(self, inputs):
        try:
            settings = {}
            for key, input_field in inputs.items():
                value = input_field.text
                
                if key in ['supervision_rate', 'conversion_rate']:
                    try:
                        value = float(value)
                    except:
                        value = 0.0
                elif key in ['avg_invoice_amount', 'target_amount', 'target_count', 'target_invoice_count', 
                            'target_customer_count', 'target_new_customer_count', 'target_cash_sales', 
                            'target_credit_sales', 'min_daily_hours']:
                    try:
                        value = int(value)
                    except:
                        value = 0
                elif key in ['work_start_time', 'first_visit_time']:
                    pass
                
                settings[key] = value
            
            update_settings(settings)
            self.show_message('موفق', 'تنظیمات با موفقیت ذخیره شد')
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ذخیره تنظیمات: {e}", error_details)
    
    def show_message(self, title, message):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(RTLLabel(
                text=message,
                size_hint_y=None,
                height=dp(45),
                font_size=sp(16)
            ))
            btn = PersianButton(
                text='باشه',
                size_hint_y=None,
                height=dp(40)
            )
            content.add_widget(btn)
            popup = Popup(title=title, content=content, size_hint=(0.8, 0.35))
            btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش پیام: {e}", error_details)
    
    def logout(self, instance):
        self.manager.current = 'login'

from kivy.uix.label import Label  # ✅ اضافه کن

class UserScreen(Screen):
    route_count = StringProperty('0') 
    
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.settings = get_settings()
            self._last_route_text = ''
            self.build_ui()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت UserScreen: {e}", error_details)
            raise
    
    def build_ui(self):
        try:
            layout = BoxLayout(orientation='vertical', padding=[dp(5), dp(5), dp(5), dp(5)])
            
            self.form_layout = GridLayout(
                cols=3,
                spacing=dp(4),
                size_hint_y=None,
                padding=dp(5)
            )
            self.form_layout.bind(minimum_height=self.form_layout.setter('height'))
            
            routes = get_routes()
            self.route_names = [r.get('name', '') for r in routes] if routes else ['']
            
            customers = get_customers()
            self.all_customer_names = [c.get('name', '') for c in customers] if customers else ['']
            
            # ========== هدرها ==========
            self.form_layout.add_widget(RTLLabel(
                text='آیتم',
                size_hint_y=None,
                height=dp(30),
                bold=True,
                color=(0.2, 0.5, 0.8, 1),
                font_size=sp(15)
            ))
            self.form_layout.add_widget(RTLLabel(
                text='مقدار',
                size_hint_y=None,
                height=dp(30),
                bold=True,
                color=(0.2, 0.5, 0.8, 1),
                font_size=sp(15)
            ))
            self.form_layout.add_widget(RTLLabel(
                text='هدف',
                size_hint_y=None,
                height=dp(30),
                bold=True,
                color=(0.2, 0.5, 0.8, 1),
                font_size=sp(15)
            ))
            
            self.inputs = {}
            
            # ========== تاریخ ویزیت ==========
            self.form_layout.add_widget(RTLLabel(
                text='تاریخ ویزیت',
                size_hint_y=None,
                height=dp(35),
                font_size=sp(14)
            ))
            visit_date = RTLTextInput(
                text=get_today_jalali(),
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(42)
            )
            self.form_layout.add_widget(visit_date)
            self.form_layout.add_widget(RTLLabel(
                text='---',
                size_hint_y=None,
                height=dp(35),
                color=(0.5, 0.5, 0.5, 1),
                font_size=sp(22)
            ))
            self.inputs['visit_date'] = visit_date
            
            # ========== مسیر ویزیت ==========
            self.form_layout.add_widget(RTLLabel(
                text='مسیر ویزیت',
                size_hint_y=None,
                height=dp(35),
                font_size=sp(14)
            ))

            self.route_spinner = PersianComboBox(
                text=self.route_names[0] if self.route_names else '',
                values=self.route_names,
                height=dp(50)
            )
            self.route_spinner.main_btn.background_color = (1, 1, 1, 1)
            self.route_spinner.main_btn.color = (0, 0, 0, 1)
            self.route_spinner.main_btn.font_size = sp(18)
            self.form_layout.add_widget(self.route_spinner)

            # ✅ تغییر: استفاده از Label به جای RTLLabel
            from kivy.uix.label import Label
            self.route_customers_target = Label(
                text=self.route_count,
                size_hint_y=None,
                height=dp(35),
                color=(1, 0.8, 0.2, 1),  # زرد طلایی
                font_size=sp(24),
                font_name='PersianFont',
                halign='center',
                valign='middle'
            )
            self.form_layout.add_widget(self.route_customers_target)
            
            self.inputs['route_name'] = self.route_spinner
            
            self._last_route_text = self.route_spinner.text
            Clock.schedule_interval(self._check_route_change, 0.5)
            
            # ========== ساعت شروع کار ==========
            self.form_layout.add_widget(RTLLabel(
                text='ساعت شروع کار',
                size_hint_y=None,
                height=dp(35),
                font_size=sp(14)
            ))
            clock_in = RTLTextInput(
                text=get_current_time(),
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            self.form_layout.add_widget(clock_in)
            self.form_layout.add_widget(RTLLabel(
                text=self.settings.get('work_start_time', '08:00'),
                size_hint_y=None,
                height=dp(35),
                color=(255, 255, 255, 255),
                font_size=sp(14)
            ))
            self.inputs['clock_in'] = clock_in
            
            # ========== ساعت اولین ویزیت ==========
            self.form_layout.add_widget(RTLLabel(
                text='ساعت اولین ویزیت',
                size_hint_y=None,
                height=dp(35),
                font_size=sp(14)
            ))
            first_visit_time = RTLTextInput(
                text='',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            self.form_layout.add_widget(first_visit_time)
            self.form_layout.add_widget(RTLLabel(
                text=self.settings.get('first_visit_time', '09:00'),
                size_hint_y=None,
                height=dp(35),
                color=(255, 255, 255, 255),
                font_size=sp(14)
            ))
            self.inputs['first_visit_time'] = first_visit_time
            
            # ========== اولین مشتری ==========
            self.form_layout.add_widget(RTLLabel(
                text='اولین مشتری',
                size_hint_y=None,
                height=dp(35),
                font_size=sp(14)
            ))

            self.first_customer_spinner = PersianComboBox(
                text='',
                values=[''],
                height=dp(60)
            )
            self.first_customer_spinner.main_btn.background_color = (1, 1, 1, 1)
            self.first_customer_spinner.main_btn.color = (0, 0, 0, 1)
            self.first_customer_spinner.main_btn.font_size = sp(14)
            self.form_layout.add_widget(self.first_customer_spinner)

            self.first_customer_target = RTLTextInput(
                text='',
                multiline=False,
                size_hint_y=None,
                height=dp(45),
                font_size=sp(14),
                hint_text='نام مشتری'
            )
            self.form_layout.add_widget(self.first_customer_target)

            self.inputs['first_customer'] = self.first_customer_target
            
            # ========== تعداد مشتری ویزیت شده ==========
            self.form_layout.add_widget(RTLLabel(
                text='تعداد مشتری ویزیت شده',
                size_hint_y=None,
                height=dp(35),
                font_size=sp(14)
            ))
            visited_count = RTLTextInput(
                text='0',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                input_filter='int',
                font_size=sp(36)
            )
            self.form_layout.add_widget(visited_count)
            
            self.visited_customers_target = RTLLabel(
                text='0',
                size_hint_y=None,
                height=dp(35),
                color=(255, 255, 255, 255),
                font_size=sp(14)
            )
            self.form_layout.add_widget(self.visited_customers_target)
            self.inputs['visited_customers_count'] = visited_count
            
            # ========== تعداد فاکتور موفق ==========
            self.form_layout.add_widget(RTLLabel(
                text='تعداد فاکتور موفق',
                size_hint_y=None,
                height=dp(35),
                font_size=sp(14)
            ))
            invoices_count = RTLTextInput(
                text='0',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                input_filter='int',
                font_size=sp(36)
            )
            self.form_layout.add_widget(invoices_count)
            self.form_layout.add_widget(RTLLabel(
                text=str(self.settings.get('target_invoice_count', '20')),
                size_hint_y=None,
                height=dp(35),
                color=(255, 255, 255, 255),
                font_size=sp(14)
            ))
            self.inputs['successful_invoices_count'] = invoices_count
            
            # ========== تعداد واحد فروش موفق ==========
            self.form_layout.add_widget(RTLLabel(
                text='تعداد واحد فروش موفق',
                size_hint_y=None,
                height=dp(35),
                font_size=sp(14)
            ))
            units_count = RTLTextInput(
                text='0',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                input_filter='int',
                font_size=sp(36)
            )
            self.form_layout.add_widget(units_count)
            self.form_layout.add_widget(RTLLabel(
                text=str(self.settings.get('target_count', '100')),
                size_hint_y=None,
                height=dp(35),
                color=(255, 255, 255, 255),
                font_size=sp(14)
            ))
            self.inputs['successful_units_count'] = units_count
            
            # ========== مبلغ فروش موفق ==========
            self.form_layout.add_widget(RTLLabel(
                text='مبلغ فروش موفق',
                size_hint_y=None,
                height=dp(35),
                font_size=sp(14)
            ))
            sales_amount = RTLTextInput(
                text='0',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                input_filter='int',
                font_size=sp(36)
            )
            self.form_layout.add_widget(sales_amount)
            
            target_amount = self.settings.get('target_amount', 50000000)
            try:
                target_amount = int(target_amount)
            except:
                target_amount = 0
            self.form_layout.add_widget(RTLLabel(
                text="{:,}".format(target_amount),
                size_hint_y=None,
                height=dp(35),
                color=(255, 255, 255, 255),
                font_size=sp(14)
            ))
            self.inputs['successful_sales_amount'] = sales_amount
            
            # ========== ساعت آخرین ویزیت ==========
            self.form_layout.add_widget(RTLLabel(
                text='ساعت آخرین ویزیت',
                size_hint_y=None,
                height=dp(35),
                font_size=sp(14)
            ))
            last_visit_time = RTLTextInput(
                text='',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            self.form_layout.add_widget(last_visit_time)
            self.form_layout.add_widget(RTLLabel(
                text='---',
                size_hint_y=None,
                height=dp(35),
                color=(0.5, 0.5, 0.5, 1),
                font_size=sp(14)
            ))
            self.inputs['last_visit_time'] = last_visit_time
            
            # ========== ساعت پایان کار ==========
            self.form_layout.add_widget(RTLLabel(
                text='ساعت پایان کار',
                size_hint_y=None,
                height=dp(35),
                font_size=sp(14)
            ))
            clock_out = RTLTextInput(
                text='',
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            self.form_layout.add_widget(clock_out)
            self.form_layout.add_widget(RTLLabel(
                text='---',
                size_hint_y=None,
                height=dp(35),
                color=(0.5, 0.5, 0.5, 1),
                font_size=sp(14)
            ))
            self.inputs['clock_out'] = clock_out
            
            # ========== ScrollView ==========
            form_scroll = ScrollView()
            form_scroll.add_widget(self.form_layout)
            layout.add_widget(form_scroll)
            
            # ========== دکمه‌ها ==========
            btn_layout = BoxLayout(
                size_hint_y=None,
                height=dp(42),
                spacing=dp(5),
                padding=dp(5)
            )
            
            save_btn = PersianButton(
                text='💾 ذخیره',
                background_color=(0.2, 0.7, 0.2, 1),
                size_hint_y=None,
                height=dp(38)
            )
            save_btn.bind(on_press=self.save_log)
            btn_layout.add_widget(save_btn)
            
            report_btn = PersianButton(
                text='📊 گزارش',
                background_color=(0.2, 0.6, 1, 1),
                size_hint_y=None,
                height=dp(38)
            )
            report_btn.bind(on_press=self.go_to_report)
            btn_layout.add_widget(report_btn)
            
            logout_btn = PersianButton(
                text='🚪 خروج',
                background_color=(0.8, 0.2, 0.2, 1),
                size_hint_y=None,
                height=dp(38)
            )
            logout_btn.bind(on_press=self.logout)
            btn_layout.add_widget(logout_btn)
            
            layout.add_widget(btn_layout)
            self.add_widget(layout)
            
            Clock.schedule_once(lambda dt: self.update_route_info(), 0.5)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت UI UserScreen: {e}", error_details)
            raise
    
    def _check_route_change(self, dt):
        if hasattr(self, 'route_spinner'):
            current_text = self.route_spinner.text
            if current_text != self._last_route_text:
                self._last_route_text = current_text
                self.update_route_info()
    
    def update_route_info(self):
        try:
            current_route = self.route_spinner.text
            
            if current_route and current_route not in ['', '⚠️ مسیری انتخاب نشده']:
                customers = get_customers()
                
                total_customers = 0
                filtered_customers = []
                
                for c in customers:
                    route_name = c.get('route_name', '').strip()
                    if route_name == current_route.strip():
                        total_customers += 1
                        filtered_customers.append(c.get('name', ''))
                
                # ✅ آپدیت با Clock برای اطمینان
                Clock.schedule_once(lambda dt: self._update_ui(str(total_customers), filtered_customers), 0)
                
            else:
                Clock.schedule_once(lambda dt: self._update_ui('0', []), 0)
                
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در بروزرسانی اطلاعات مسیر: {e}", error_details)

    def _update_ui(self, count, customers_list):
        """آپدیت امن UI در ترد اصلی"""
        try:
            # آپدیت تعداد مشتریان
            self.route_count = count
            self.route_customers_target.text = count
            
            # آپدیت کمبوباکس اولین مشتری
            if customers_list:
                self.first_customer_spinner.values = customers_list
                self.first_customer_spinner.text = customers_list[0]
            else:
                self.first_customer_spinner.values = ['⚠️ مشتری‌ای یافت نشد']
                self.first_customer_spinner.text = '⚠️ مشتری‌ای یافت نشد'
            
            # آپدیت مشتری هدف
            first_customer_target = self.settings.get('first_customer_of_route', '')
            self.first_customer_target.text = first_customer_target
            
            # آپدیت تعداد ویزیت هدف
            supervision_rate = self.settings.get('supervision_rate', 0.3)
            target_visits = int(int(count) * supervision_rate)
            self.visited_customers_target.text = str(target_visits)
            
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در آپدیت UI: {e}", error_details)
    
    def save_log(self, instance):
        try:
            log_data = {}
            for key, input_field in self.inputs.items():
                log_data[key] = input_field.text
            
            if 'route_name' in self.inputs:
                log_data['route_name'] = self.inputs['route_name'].text
            if 'first_customer' in self.inputs:
                log_data['first_customer'] = self.inputs['first_customer'].text
            
            if not log_data.get('visit_date'):
                self.show_message('خطا', 'تاریخ ویزیت الزامی است')
                return
            
            for key in ['visited_customers_count', 'successful_invoices_count', 'successful_units_count', 'successful_sales_amount']:
                if key in log_data and (log_data[key] == '' or log_data[key] == '0'):
                    log_data[key] = '0'
            
            all_logs = get_daily_logs()
            
            if log_data.get('visit_date') in all_logs:
                content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
                content.add_widget(RTLLabel(
                    text='ویزیتی با این تاریخ قبلاً ثبت شده است. آیا می‌خواهید جایگزین شود؟',
                    size_hint_y=None,
                    height=dp(60),
                ))
                
                btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
                yes_btn = PersianButton(text='بله، جایگزین شود', size_hint_y=None, height=dp(45))
                no_btn = PersianButton(text='خیر، انصراف', size_hint_y=None, height=dp(45))
                btn_layout.add_widget(yes_btn)
                btn_layout.add_widget(no_btn)
                content.add_widget(btn_layout)
                
                popup = Popup(title='توجه', content=content, size_hint=(0.85, 0.35))
                
                def replace(instance):
                    save_daily_log(log_data['visit_date'], log_data)
                    popup.dismiss()
                    self.show_message('موفق', 'اطلاعات ویزیت با موفقیت جایگزین شد')
                    self.clear_form()
                
                def cancel(instance):
                    popup.dismiss()
                
                yes_btn.bind(on_press=replace)
                no_btn.bind(on_press=cancel)
                popup.open()
            else:
                save_daily_log(log_data['visit_date'], log_data)
                self.show_message('موفق', 'اطلاعات ویزیت با موفقیت ذخیره شد')
                self.clear_form()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ذخیره ویزیت: {e}", error_details)
    
    def clear_form(self):
        for key in ['first_visit_time', 'last_visit_time', 'clock_out']:
            if key in self.inputs:
                self.inputs[key].text = ''
        
        for key in ['visited_customers_count', 'successful_invoices_count', 'successful_units_count', 'successful_sales_amount']:
            if key in self.inputs:
                self.inputs[key].text = '0'
    
    def go_to_report(self, instance):
        self.manager.current = 'report'
    
    def logout(self, instance):
        self.manager.current = 'login'
    
    def show_message(self, title, message):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(RTLLabel(
                text=message,
                size_hint_y=None,
                height=dp(50),
            ))
            btn = PersianButton(text='باشه', size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=title, content=content, size_hint=(0.8, 0.35))
            btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش پیام: {e}", error_details)


class ReportScreen(Screen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.build_ui()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت ReportScreen: {e}", error_details)
            raise
    
    def build_ui(self):
        try:
            layout = BoxLayout(orientation='vertical')
            
            header = RTLLabel(
                text='📊 گزارش عملکرد',
                size_hint_y=0.07,
                font_size=sp(20),
            )
            layout.add_widget(header)
            
            stats_scroll = ScrollView(size_hint_y=0.5)
            self.stats_layout = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=dp(15))
            self.stats_layout.bind(minimum_height=self.stats_layout.setter('height'))
            stats_scroll.add_widget(self.stats_layout)
            layout.add_widget(stats_scroll)
            
            btn_layout = BoxLayout(size_hint_y=0.12, spacing=dp(10), padding=dp(10))
            
            refresh_btn = PersianButton(text='🔄 تازه سازی', background_color=(0.4, 0.4, 0.8, 1), size_hint_y=None, height=dp(45))
            refresh_btn.bind(on_press=self.refresh_stats)
            btn_layout.add_widget(refresh_btn)
            
            excel_btn = PersianButton(text='📎 خروجی Excel', background_color=(0.2, 0.6, 0.2, 1), size_hint_y=None, height=dp(45))
            excel_btn.bind(on_press=self.export_excel)
            btn_layout.add_widget(excel_btn)
            
            pdf_btn = PersianButton(text='📄 خروجی PDF', background_color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=dp(45))
            pdf_btn.bind(on_press=self.export_pdf)
            btn_layout.add_widget(pdf_btn)
            
            back_btn = PersianButton(text='🔙 بازگشت', background_color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(45))
            back_btn.bind(on_press=self.go_back)
            btn_layout.add_widget(back_btn)
            
            layout.add_widget(btn_layout)
            self.add_widget(layout)
            
            self.refresh_stats(None)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت UI ReportScreen: {e}", error_details)
            raise
    
    def refresh_stats(self, instance):
        try:
            self.stats_layout.clear_widgets()
            
            logs = get_daily_logs()
            
            if not logs:
                self.stats_layout.add_widget(RTLLabel(
                    text='📭 هیچ داده‌ای وجود ندارد',
                    size_hint_y=None,
                    height=dp(50),
                    font_size=sp(16),
                ))
                return
            
            total_sales = 0
            total_invoices = 0
            total_visits = 0
            total_units = 0
            
            for date, log in logs.items():
                try:
                    sales_val = log.get('successful_sales_amount', '0')
                    total_sales += int(sales_val) if str(sales_val).isdigit() else 0
                    total_invoices += int(log.get('successful_invoices_count', '0')) if str(log.get('successful_invoices_count', '0')).isdigit() else 0
                    total_visits += int(log.get('visited_customers_count', '0')) if str(log.get('visited_customers_count', '0')).isdigit() else 0
                    total_units += int(log.get('successful_units_count', '0')) if str(log.get('successful_units_count', '0')).isdigit() else 0
                except:
                    pass
            
            self.stats_layout.add_widget(RTLLabel(
                text='📊 خلاصه آمار کل',
                size_hint_y=None,
                height=dp(45),
                font_size=sp(18),
                bold=True,
            ))
            
            stats_row1 = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
            card1 = self.make_stat_card('💰 کل فروش', f"{total_sales:,}", 'Rial', (0.2, 0.6, 0.2, 1))
            card2 = self.make_stat_card('🧾 فاکتورها', str(total_invoices), '', (0.2, 0.5, 0.8, 1))
            stats_row1.add_widget(card1)
            stats_row1.add_widget(card2)
            self.stats_layout.add_widget(stats_row1)
            
            stats_row2 = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
            card3 = self.make_stat_card('👥 ویزیت‌ها', str(total_visits), '', (0.8, 0.5, 0.2, 1))
            card4 = self.make_stat_card('📦 واحد فروش', str(total_units), '', (0.6, 0.3, 0.7, 1))
            stats_row2.add_widget(card3)
            stats_row2.add_widget(card4)
            self.stats_layout.add_widget(stats_row2)
            
            stats_row3 = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
            card5 = self.make_stat_card('📅 روزهای کاری', str(len(logs)), '', (0.3, 0.6, 0.6, 1))
            avg_sale = total_sales // total_invoices if total_invoices > 0 else 0
            card6 = self.make_stat_card('📈 میانگین فاکتور', f"{avg_sale:,}", 'Rial', (0.7, 0.4, 0.4, 1))
            stats_row3.add_widget(card5)
            stats_row3.add_widget(card6)
            self.stats_layout.add_widget(stats_row3)
            
            if total_visits > 0:
                avg_per_visit = total_sales // total_visits
                stats_row4 = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
                card7 = self.make_stat_card('🎯 فروش هر ویزیت', f"{avg_per_visit:,}", 'Rial', (0.4, 0.5, 0.3, 1))
                stats_row4.add_widget(card7)
                self.stats_layout.add_widget(stats_row4)
            
            self.stats_layout.add_widget(Label(text='', size_hint_y=None, height=dp(10)))
            self.stats_layout.add_widget(RTLLabel(
                text='📋 لیست ویزیت‌های ثبت شده',
                size_hint_y=None,
                height=dp(40),
                font_size=sp(16),
                bold=True,
            ))
            
            header_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(2))
            header_date = PersianButton(text='تاریخ', size_hint_x=0.25, background_color=(0.2, 0.5, 0.8, 1), color=(1, 1, 1, 1), size_hint_y=None, height=dp(35))
            header_visit = PersianButton(text='ویزیت', size_hint_x=0.25, background_color=(0.2, 0.5, 0.8, 1), color=(1, 1, 1, 1), size_hint_y=None, height=dp(35))
            header_invoice = PersianButton(text='فاکتور', size_hint_x=0.25, background_color=(0.2, 0.5, 0.8, 1), color=(1, 1, 1, 1), size_hint_y=None, height=dp(35))
            header_sales = PersianButton(text='فروش (ریال)', size_hint_x=0.25, background_color=(0.2, 0.5, 0.8, 1), color=(1, 1, 1, 1), size_hint_y=None, height=dp(35))
            header_box.add_widget(header_date)
            header_box.add_widget(header_visit)
            header_box.add_widget(header_invoice)
            header_box.add_widget(header_sales)
            self.stats_layout.add_widget(header_box)
            
            sorted_logs = sorted(logs.items(), key=lambda x: x[0], reverse=True)
            
            for idx, (date, log) in enumerate(sorted_logs):
                row_box = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(2))
                row_box.add_widget(RTLLabel(
                    text=date,
                    size_hint_x=0.25,
                ))
                row_box.add_widget(RTLLabel(
                    text=log.get('visited_customers_count', '0'),
                    size_hint_x=0.25,
                ))
                row_box.add_widget(RTLLabel(
                    text=log.get('successful_invoices_count', '0'),
                    size_hint_x=0.25,
                ))
                
                sales = log.get('successful_sales_amount', '0')
                sales_num = int(sales) if str(sales).isdigit() else 0
                row_box.add_widget(RTLLabel(
                    text=f"{sales_num:,}",
                    size_hint_x=0.25,
                ))
                
                self.stats_layout.add_widget(row_box)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در به‌روزرسانی آمار: {e}", error_details)
    
    def make_stat_card(self, title, value, unit, color):
        try:
            card = BoxLayout(
                orientation='vertical',
                size_hint_x=0.5,
                size_hint_y=None,
                height=dp(60),
                padding=dp(5),
                spacing=dp(2)
            )
            
            title_label = RTLLabel(
                text=title,
                size_hint_y=None,
                height=dp(20),
                font_size=sp(12),
            )
            value_label = RTLLabel(
                text=f"{value} {unit}",
                size_hint_y=None,
                height=dp(30),
                font_size=sp(18),
                bold=True,
            )
            card.add_widget(title_label)
            card.add_widget(value_label)
            
            with card.canvas.before:
                Color(*color)
                self.bg_rect = Rectangle(pos=card.pos, size=card.size)
                card.bind(pos=self.update_bg, size=self.update_bg)
                card.bg_color = color
                card.bg_rect = self.bg_rect
            return card
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت کارت آماری: {e}", error_details)
            return RTLLabel(
                text=f"{title}: {value}",
            )
    
    def update_bg(self, instance, value):
        try:
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
        except:
            pass
    
    def export_excel(self, instance):
        try:
            filepath = export_to_excel()
            if filepath:
                self.show_message('موفق', 'فایل Excel ذخیره شد')
            else:
                self.show_message('خطا', 'هیچ داده‌ای وجود ندارد')
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در خروجی Excel: {e}", error_details)
    
    def export_pdf(self, instance):
        self.show_message('توجه', 'قابلیت خروجی PDF در این نسخه موقتاً غیرفعال است')
    
    def go_back(self, instance):
        self.manager.current = 'user'
    
    def show_message(self, title, message):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(RTLLabel(
                text=message,
                size_hint_y=None,
                height=dp(50),
            ))
            btn = PersianButton(text='باشه', size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=title, content=content, size_hint=(0.8, 0.35))
            btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش پیام: {e}", error_details)


class SettingsLoginScreen(Screen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.build_ui()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت SettingsLoginScreen: {e}", error_details)
            raise
    
    def build_ui(self):
        try:
            layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(8))
            
            # ========== فاصله ۲ سانت از بالا ==========
            layout.add_widget(Label(size_hint_y=None, height=dp(20)))
            
            # ========== عنوان ==========
            title = RTLLabel(
                text='ورود به تنظیمات سیستم',
                font_size=sp(24),
                size_hint_y=None,
                height=dp(45)
            )
            layout.add_widget(title)
            
            # ========== فاصله ۳ میلیمتر ==========
            layout.add_widget(Label(size_hint_y=None, height=dp(3)))
            
            # ========== فیلد رمز مدیر (ارتفاع ۱ سانت) ==========
            self.password_input = RTLTextInput(
                hint_text='رمز عبور مدیر',
                password=True,
                multiline=False,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(36)
            )
            layout.add_widget(self.password_input)
            
            # ========== فاصله ۳ میلیمتر ==========
            layout.add_widget(Label(size_hint_y=None, height=dp(3)))
            
            # ========== دکمه‌ها (کنار هم) ==========
            btn_layout = BoxLayout(
                spacing=dp(5),
                size_hint_y=None,
                height=dp(42)
            )
            
            login_btn = PersianButton(
                text='ورود',
                background_color=(0.2, 0.6, 1, 1),
                size_hint_y=None,
                height=dp(38)
            )
            login_btn.bind(on_press=self.check_login)
            btn_layout.add_widget(login_btn)
            
            back_btn = PersianButton(
                text='بازگشت',
                background_color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(38)
            )
            back_btn.bind(on_press=self.go_back)
            btn_layout.add_widget(back_btn)
            
            layout.add_widget(btn_layout)
            
            # ❌ دکمه تنظیم مجدد رمز حذف شد (امنیت)
            
            self.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت UI SettingsLoginScreen: {e}", error_details)
            raise
    
    def reset_password(self, instance):
        """تنظیم مجدد رمز به admin123"""
        try:
            from utils.auth import hash_password
            set_admin_password('admin123')
            self.show_message('موفق', 'رمز با موفقیت به "admin123" تنظیم شد')
            self.password_input.text = ''
        except Exception as e:
            self.show_message('خطا', f'خطا در تنظیم رمز: {e}')
    
    def check_login(self, instance):
        try:
            hashed = get_admin_password()
            
            if not hashed:
                from utils.auth import hash_password
                set_admin_password('admin123')
                hashed = get_admin_password()
                self.show_message('توجه', 'رمز پیش‌فرض "admin123" تنظیم شد')
            
            if verify_password(self.password_input.text, hashed):
                self.manager.current = 'admin_settings'
            else:
                self.show_message('خطا', 'رمز عبور اشتباه است')
                self.password_input.text = ''
                
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ورود به تنظیمات: {e}", error_details)
    
    def forgot_password(self, instance):
        """بازیابی رمز عبور از طریق ایمیل"""
        try:
            from plyer import email
            email.send(
                recipient=ADMIN_EMAIL,
                subject='درخواست بازیابی رمز عبور مدیر',
                text=f'''
سلام مدیر گرامی

درخواست بازیابی رمز عبور پنل مدیریت از طرف شما ثبت شده است.

رمز عبور پیش‌فرض شما: admin123

لطفاً پس از ورود، رمز عبور خود را تغییر دهید.

با احترام
سیستم مدیریت فروش
                '''
            )
            self.show_message(
                'موفق',
                f'ایمیل بازیابی رمز به {ADMIN_EMAIL} ارسال شد.\nرمز پیش‌فرض: admin123'
            )
        except Exception as e:
            self.show_message(
                '🔑 بازیابی رمز',
                f'رمز پیش‌فرض مدیر: admin123\nلطفاً پس از ورود، رمز را تغییر دهید.'
            )
    
    def go_back(self, instance):
        self.manager.current = 'login'
    
    def show_message(self, title, message):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(RTLLabel(
                text=message,
                size_hint_y=None,
                height=dp(50),
            ))
            btn = PersianButton(text='باشه', size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=title, content=content, size_hint=(0.8, 0.35))
            btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش پیام: {e}", error_details)


class DebugScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20))
        
        font_paths = [
            '/system/fonts/NotoNaskhArabic-Regular.ttf',
            '/system/fonts/NotoSansArabic-Regular.ttf',
            '/system/fonts/DroidSansFallback.ttf',
        ]
        
        for path in font_paths:
            exists = os.path.exists(path)
            layout.add_widget(RTLLabel(
                text=f"{path}: {'✅' if exists else '❌'}",
            ))
        
        internal_paths = [
            os.path.join(os.path.dirname(__file__), 'fonts', 'Vazirmatn-Regular.ttf'),
            os.path.join(os.path.dirname(__file__), 'Vazirmatn-Regular.ttf'),
        ]
        
        for path in internal_paths:
            exists = os.path.exists(path)
            layout.add_widget(RTLLabel(
                text=f"{path}: {'✅' if exists else '❌'}",
            ))
        
        layout.add_widget(RTLLabel(
            text="📋 فونت‌های ثبت شده:",
        ))
        for name in LabelBase._fonts.keys():
            layout.add_widget(RTLLabel(
                text=f"  - {name}",
            ))
        
        layout.add_widget(RTLLabel(
            text="تست فارسی با Roboto",
            font_name='Roboto'
        ))
        layout.add_widget(RTLLabel(
            text="تست فارسی با PersianFont",
            font_name='PersianFont'
        ))
        
        back_btn = PersianButton(text='بازگشت', size_hint_y=None, height=dp(50))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))
        layout.add_widget(back_btn)
        
        self.add_widget(layout)


class ScreenManagement(ScreenManager):
    pass


class MainApp(App):
    def build(self):
        try:
            self.data_path = init_data_path()
            os.makedirs(os.path.join(self.data_path, 'reports'), exist_ok=True)
            
            self.init_json_files()
            
            sm = ScreenManagement()
            sm.add_widget(LoginScreen(name='login'))
            sm.add_widget(AdminScreen(name='admin'))
            sm.add_widget(UserScreen(name='user'))
            sm.add_widget(ReportScreen(name='report'))
            sm.add_widget(RegisterScreen(name='register'))
            sm.add_widget(AdminSettingsScreen(name='admin_settings'))
            sm.add_widget(SettingsLoginScreen(name='settings_login'))
            
            from kivy.core.window import Window
            Window.bind(on_keyboard=self.on_keyboard)
            
            return sm
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در راه‌اندازی برنامه: {e}", error_details)
            return ScreenManager()
    
    def on_keyboard(self, window, key, *args):
        if key == 27:
            current_screen = self.root.current
            
            if current_screen == 'login':
                self.stop()
                return True
            elif current_screen == 'admin_settings':
                self.root.current = 'settings_login'
                return True
            elif current_screen == 'settings_login':
                self.root.current = 'login'
                return True
            elif current_screen == 'register':
                self.root.current = 'login'
                return True
            elif current_screen == 'admin':
                self.root.current = 'login'
                return True
            elif current_screen == 'user':
                self.root.current = 'login'
                return True
            elif current_screen == 'report':
                self.root.current = 'user'
                return True
        
        return False
    
    def init_json_files(self):
        try:
            from utils.auth import hash_password
            
            hashed_default = hash_password(DEFAULT_ADMIN_PASSWORD)
            
            default_data = {
                'definitions.json': {
                    'agents': [],
                    'routes': [],
                    'customers': []
                },
                'settings.json': {
                    'supervision_rate': 0.3,
                    'conversion_rate': 0.25,
                    'avg_invoice_amount': 1000000,
                    'target_amount': 50000000,
                    'target_count': 100,
                    'target_invoice_count': 20,
                    'target_customer_count': 50,
                    'target_new_customer_count': 10,
                    'target_cash_sales': 30000000,
                    'target_credit_sales': 20000000,
                    'work_start_time': '08:00',
                    'first_visit_time': '09:00',
                    'min_daily_hours': 6,
                    'first_customer_of_route': ''
                },
                'daily_log.json': {},
                'users.json': {'users': []},
                'codes.json': {'codes': []},
                'admin_password.json': {'hashed_password': hashed_default}
            }
            
            from utils.storage import get_data_path
            data_path = get_data_path()
            
            for filename, default_content in default_data.items():
                filepath = os.path.join(data_path, filename)
                if not os.path.exists(filepath):
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(default_content, f, ensure_ascii=False, indent=2)
                    print(f"✅ فایل {filename} ایجاد شد")
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ایجاد فایل‌های اولیه: {e}", error_details)
            raise


if __name__ == '__main__':
    try:
        MainApp().run()
    except Exception as e:
        error_details = traceback.format_exc()
        try:
            from kivy.uix.popup import Popup
            from kivy.uix.label import Label
            from kivy.uix.button import Button
            from kivy.uix.boxlayout import BoxLayout
            from kivy.app import App
            
            class EmergencyApp(App):
                def build(self):
                    content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
                    content.add_widget(Label(text=f"خطای بحرانی:\n{str(e)}", size_hint_y=None, height=dp(200)))
                    btn = Button(text='بستن', size_hint_y=None, height=dp(50))
                    content.add_widget(btn)
                    popup = Popup(title='⚠️ خطا', content=content, size_hint=(0.9, 0.6), auto_dismiss=False)
                    btn.bind(on_press=popup.dismiss)
                    popup.open()
                    return BoxLayout()
            
            EmergencyApp().run()
        except:
            print("="*60)
            print(f"❌ خطای بحرانی: {e}")
            print(error_details)
            print("="*60)
