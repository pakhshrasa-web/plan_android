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
DEFAULT_ADMIN_PASSWORD = "admin123"  # رمز پیش‌فرض

# ========== سیستم نمایش خطا ==========
class ErrorPopup:
    """نمایش خطا به صورت پنجره بازشو با قابلیت کپی متن"""
    
    @staticmethod
    def show_error(error_message, error_details=""):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
            
            title_label = Label(text="[b][color=ff3333]⚠️ خطا در برنامه[/color][/b]", 
                               markup=True, size_hint_y=None, height=dp(50), font_size=sp(18))
            content.add_widget(title_label)
            
            msg_label = Label(text=f"[b]خطا:[/b] {error_message}", 
                             markup=True, size_hint_y=None, height=dp(60), text_size=(dp(400), None), halign='left')
            content.add_widget(msg_label)
            
            if error_details:
                detail_label = Label(text=f"[b]جزئیات:[/b]\n{error_details}", 
                                     markup=True, size_hint_y=None, height=dp(300), 
                                     text_size=(dp(400), None), halign='left', font_size=sp(12))
                scroll = ScrollView(size_hint_y=None, height=dp(300))
                scroll.add_widget(detail_label)
                content.add_widget(scroll)
            else:
                content.add_widget(Label(text="", size_hint_y=None, height=dp(20)))
            
            btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
            copy_btn = Button(text='📋 کپی متن خطا', background_color=(0.2, 0.4, 0.8, 1), size_hint_y=None, height=dp(45))
            close_btn = Button(text='✖ بستن', background_color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=dp(45))
            
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

# ===
# ========== مدیریت مسیرها و فونت ==========
import os
from kivy.config import Config
from kivy.core.text import LabelBase
from kivy.utils import platform
from kivy.core.window import Window  # اضافه شد

def setup_font():
    """تنظیم فونت فارسی"""
    font_path = '/system/fonts/NotoNaskhArabic-Regular.ttf'
    
    if os.path.exists(font_path):
        try:
            LabelBase.register(name='PersianFont', fn_regular=font_path)
            print(f"✅ فونت ثبت شد: {font_path}")
            return True
        except Exception as e:
            print(f"⚠️ خطا در ثبت فونت: {e}")
    
    print("⚠️ فونت فارسی پیدا نشد")
    return False

# اجرای تنظیم فونت
setup_font()

if platform != 'android':
    Window.size = (400, 650)

# ========== ایمپورت ماژول‌های برنامه ==========
try:
    from utils.rtl_widgets import RTLTextInput, RTLSpinner
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
    # from utils.pdf_exporter import export_to_pdf  # کامنت شد
    from utils.file_picker import FilePicker
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
            layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(40))
            
            header_layout = BoxLayout(size_hint_y=0.1, spacing=dp(10))
            settings_btn = Button(text='⚙️', size_hint_x=0.2, background_color=(0.3, 0.3, 0.3, 1), size_hint_y=None, height=dp(50))
            settings_btn.bind(on_press=self.open_settings)
            header_layout.add_widget(settings_btn)
            header_layout.add_widget(Label(text='', size_hint_x=0.6))
            header_layout.add_widget(Label(text='', size_hint_x=0.2))
            layout.add_widget(header_layout)
            
            title = Label(text=f('مدیریت فروش'), font_size=sp(28), size_hint_y=0.2)
            layout.add_widget(title)
            
            self.username = RTLTextInput(hint_text='نام کاربری', size_hint_y=None, height=dp(60))
            layout.add_widget(self.username)
            
            self.password = RTLTextInput(hint_text='رمز عبور', password=True, size_hint_y=None, height=dp(60))
            layout.add_widget(self.password)
            
            btn = Button(text=f('ورود'), size_hint_y=None, height=dp(55))
            btn.bind(on_press=self.check_login)
            layout.add_widget(btn)
            
            register_btn = Button(text=f('ثبت نام'), size_hint_y=None, height=dp(45), background_color=(0.3, 0.6, 0.3, 1))
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
            content.add_widget(Label(text=f(message), size_hint_y=None, height=dp(50)))
            btn = Button(text=f('باشه'), size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=f(title), content=content, size_hint=(0.8, 0.35))
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
            
            title = Label(text=f('ثبت نام کاربر جدید'), font_size=sp(24), size_hint_y=0.1)
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
            register_btn = Button(text=f('ثبت نام'), background_color=(0.2, 0.7, 0.2, 1), size_hint_y=None, height=dp(50))
            register_btn.bind(on_press=self.do_register)
            btn_layout.add_widget(register_btn)
            
            back_btn = Button(text=f('بازگشت'), background_color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(50))
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
            content.add_widget(Label(text=f(message), size_hint_y=None, height=dp(50)))
            btn = Button(text=f('باشه'), size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=f(title), content=content, size_hint=(0.8, 0.35))
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
            layout = BoxLayout(orientation='vertical')
            
            header = Label(text=f('تنظیمات سیستم'), size_hint_y=0.07, font_size=sp(20))
            layout.add_widget(header)
            
            tabs_layout = BoxLayout(size_hint_y=0.08, spacing=dp(2))
            
            btn_users = Button(text=f('مدیریت کاربران'), background_color=(0.3, 0.5, 0.8, 1), size_hint_y=None, height=dp(45))
            btn_users.bind(on_press=lambda x: self.switch_tab(0))
            tabs_layout.add_widget(btn_users)
            
            btn_codes = Button(text=f('کدهای ثبت نام'), background_color=(0.3, 0.5, 0.8, 0.6), size_hint_y=None, height=dp(45))
            btn_codes.bind(on_press=lambda x: self.switch_tab(1))
            tabs_layout.add_widget(btn_codes)
            
            btn_general = Button(text=f('تنظیمات عمومی'), background_color=(0.3, 0.5, 0.8, 0.6), size_hint_y=None, height=dp(45))
            btn_general.bind(on_press=lambda x: self.switch_tab(2))
            tabs_layout.add_widget(btn_general)
            
            btn_password = Button(text=f('تغییر رمز'), background_color=(0.3, 0.5, 0.8, 0.6), size_hint_y=None, height=dp(45))
            btn_password.bind(on_press=lambda x: self.switch_tab(3))
            tabs_layout.add_widget(btn_password)
            
            layout.add_widget(tabs_layout)
            
            self.content_area = BoxLayout(orientation='vertical')
            layout.add_widget(self.content_area)
            
            back_btn = Button(text=f('بازگشت'), background_color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(45))
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
            layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(15))
            
            layout.add_widget(Label(text=f('تغییر رمز عبور مدیر'), size_hint_y=None, height=dp(50), font_size=sp(18), bold=True))
            layout.add_widget(Label(text=f('رمز عبور فعلی:'), size_hint_y=None, height=dp(30)))
            self.old_password = RTLTextInput(password=True, multiline=False, size_hint_y=None, height=dp(50))
            layout.add_widget(self.old_password)
            
            layout.add_widget(Label(text=f('رمز عبور جدید:'), size_hint_y=None, height=dp(30)))
            self.new_password = RTLTextInput(password=True, multiline=False, size_hint_y=None, height=dp(50))
            layout.add_widget(self.new_password)
            
            layout.add_widget(Label(text=f('تکرار رمز عبور جدید:'), size_hint_y=None, height=dp(30)))
            self.confirm_password = RTLTextInput(password=True, multiline=False, size_hint_y=None, height=dp(50))
            layout.add_widget(self.confirm_password)
            
            btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50), padding=(0, dp(20), 0, 0))
            save_btn = Button(text=f('تغییر رمز'), background_color=(0.2, 0.7, 0.2, 1), size_hint_y=None, height=dp(45))
            save_btn.bind(on_press=self.change_password)
            btn_layout.add_widget(save_btn)
            
            clear_btn = Button(text=f('پاک کردن'), background_color=(0.8, 0.5, 0.2, 1), size_hint_y=None, height=dp(45))
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
            content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
            content.bind(minimum_height=content.setter('height'))
            
            content.add_widget(Label(text=f('📋 لیست کاربران'), size_hint_y=None, height=dp(40), font_size=sp(16), bold=True))
            
            for user in users:
                user_box = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(5))
                info = f"{user.get('username', '')}\n{user.get('name', '')}\n{user.get('role', '')}"
                user_info = Label(text=f(info), size_hint_x=0.7)
                user_box.add_widget(user_info)
                
                del_btn = Button(text=f('حذف'), size_hint_x=0.3, background_color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=dp(40))
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
            content.add_widget(Label(text=f(f'آیا از حذف کاربر "{username}" مطمئن هستید؟'), size_hint_y=None, height=dp(50)))
            
            btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
            yes_btn = Button(text=f('بله، حذف شود'), size_hint_y=None, height=dp(45))
            no_btn = Button(text=f('خیر، انصراف'), size_hint_y=None, height=dp(45))
            btn_layout.add_widget(yes_btn)
            btn_layout.add_widget(no_btn)
            content.add_widget(btn_layout)
            
            popup = Popup(title=f('تایید حذف'), content=content, size_hint=(0.8, 0.35))
            
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
            content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
            content.bind(minimum_height=content.setter('height'))
            
            content.add_widget(Label(text=f('➕ ایجاد کد جدید'), size_hint_y=None, height=dp(40), font_size=sp(16), bold=True))
            
            role_spinner = RTLSpinner(text=roles[0], values=roles, size_hint_y=None, height=dp(50))
            content.add_widget(role_spinner)
            
            name_input = RTLTextInput(hint_text='نام و نام خانوادگی', multiline=False, size_hint_y=None, height=dp(50))
            content.add_widget(name_input)
            
            create_btn = Button(text=f('ساخت کد'), size_hint_y=None, height=dp(50), background_color=(0.2, 0.7, 0.2, 1))
            content.add_widget(create_btn)
            
            content.add_widget(Label(text=f('📋 کدهای فعال'), size_hint_y=None, height=dp(40), font_size=sp(16), bold=True))
            
            codes = get_codes()
            for code_info in codes:
                if not code_info.get('used', False):
                    code_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
                    code_text = f"{code_info['code']} - {code_info['role']} - {code_info['name']}"
                    code_label = Label(text=f(code_text), size_hint_x=0.8)
                    code_box.add_widget(code_label)
                    content.add_widget(code_box)
            
            def do_create(instance):
                try:
                    code = create_code(role_spinner.text, name_input.text)
                    self.show_message('موفق', f'کد ساخته شد:\n{code}')
                    self.switch_tab(1)
                except Exception as e:
                    error_details = traceback.format_exc()
                    ErrorPopup.show_error(f"خطا در ساخت کد: {e}", error_details)
            
            create_btn.bind(on_press=do_create)
            
            layout.add_widget(content)
            self.content_area.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش کدها: {e}", error_details)
    
    def show_general_settings_tab(self):
        try:
            settings = get_settings()
            
            layout = ScrollView()
            content = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, padding=dp(10))
            content.bind(minimum_height=content.setter('height'))
            
            fields = [
                ('supervision_rate', 'درصد سرکشی', '0.3'),
                ('conversion_rate', 'نرخ تبدیل', '0.25'),
                ('avg_invoice_amount', 'میانگین مبلغ فاکتور', '1000000'),
                ('target_amount', 'تارگت ریالی', '50000000'),
                ('work_start_time', 'ساعت شروع کار', '08:00'),
                ('min_daily_hours', 'حداقل ساعت کاری', '6'),
            ]
            
            inputs = {}
            for key, label, default in fields:
                content.add_widget(Label(text=f(label + ':'), size_hint_y=None, height=dp(45)))
                input_field = RTLTextInput(text=str(settings.get(key, default)), multiline=False, size_hint_y=None, height=dp(50))
                content.add_widget(input_field)
                inputs[key] = input_field
            
            save_btn = Button(text=f('ذخیره تنظیمات'), size_hint_y=None, height=dp(50), background_color=(0.2, 0.6, 1, 1))
            content.add_widget(save_btn)
            
            layout.add_widget(content)
            self.content_area.add_widget(layout)
            save_btn.bind(on_press=lambda x: self.save_settings(inputs))
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش تنظیمات عمومی: {e}", error_details)
    
    def save_settings(self, inputs):
        try:
            settings = {}
            for key, input_field in inputs.items():
                value = input_field.text
                if key in ['supervision_rate', 'conversion_rate']:
                    try:
                        value = float(value)
                    except:
                        value = 0
                elif key in ['avg_invoice_amount', 'target_amount', 'min_daily_hours']:
                    try:
                        value = int(value)
                    except:
                        value = 0
                settings[key] = value
            update_settings(settings)
            self.show_message('موفق', 'تنظیمات ذخیره شد')
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ذخیره تنظیمات: {e}", error_details)
    
    def show_message(self, title, message):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(Label(text=f(message), size_hint_y=None, height=dp(50)))
            btn = Button(text=f('باشه'), size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=f(title), content=content, size_hint=(0.8, 0.35))
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
            main_layout = BoxLayout(orientation='vertical')
            
            header = Label(text=f('پنل مدیریت'), size_hint_y=0.07, font_size=sp(20))
            main_layout.add_widget(header)
            
            tabs_layout = BoxLayout(size_hint_y=0.08, spacing=dp(2))
            
            btn_agents = Button(text=f('عامل‌ها'), background_color=(0.3, 0.5, 0.8, 1), size_hint_y=None, height=dp(45))
            btn_agents.bind(on_press=lambda x: self.switch_tab(0))
            tabs_layout.add_widget(btn_agents)
            
            btn_routes = Button(text=f('مسیرها'), background_color=(0.3, 0.5, 0.8, 0.6), size_hint_y=None, height=dp(45))
            btn_routes.bind(on_press=lambda x: self.switch_tab(1))
            tabs_layout.add_widget(btn_routes)
            
            btn_customers = Button(text=f('مشتریان'), background_color=(0.3, 0.5, 0.8, 0.6), size_hint_y=None, height=dp(45))
            btn_customers.bind(on_press=lambda x: self.switch_tab(2))
            tabs_layout.add_widget(btn_customers)
            
            btn_settings = Button(text=f('⚙️ تنظیمات'), background_color=(0.3, 0.5, 0.8, 0.6), size_hint_y=None, height=dp(45))
            btn_settings.bind(on_press=lambda x: self.switch_tab(3))
            tabs_layout.add_widget(btn_settings)
            
            main_layout.add_widget(tabs_layout)
            
            self.content_area = BoxLayout(orientation='vertical')
            main_layout.add_widget(self.content_area)
            
            logout_btn = Button(text=f('خروج'), background_color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=dp(45))
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
            content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
            content.bind(minimum_height=content.setter('height'))
            
            content.add_widget(Label(text=f('➕ افزودن عامل جدید'), size_hint_y=None, height=dp(40), font_size=sp(16), bold=True))
            
            name_input = RTLTextInput(hint_text='نام کامل', multiline=False, size_hint_y=None, height=dp(50))
            content.add_widget(name_input)
            
            phone_input = RTLTextInput(hint_text='شماره تلفن', multiline=False, size_hint_y=None, height=dp(50))
            content.add_widget(phone_input)
            
            role_spinner = RTLSpinner(text=ROLES[0], values=ROLES, size_hint_y=None, height=dp(50))
            content.add_widget(role_spinner)
            
            email_input = RTLTextInput(hint_text='ایمیل', multiline=False, size_hint_y=None, height=dp(50))
            content.add_widget(email_input)
            
            add_btn = Button(text=f('افزودن'), size_hint_y=None, height=dp(50), background_color=(0.2, 0.7, 0.2, 1))
            content.add_widget(add_btn)
            
            content.add_widget(Label(text=f('📋 لیست عامل‌ها'), size_hint_y=None, height=dp(40), font_size=sp(16), bold=True))
            
            agents = get_agents()
            for agent in agents:
                agent_box = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
                agent_info = Label(text=f("{agent.get('name', '')}\n{agent.get('role', '')}"), size_hint_x=0.7)
                agent_box.add_widget(agent_info)
                del_btn = Button(text=f('حذف'), size_hint_x=0.3, background_color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=dp(40))
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
            layout = BoxLayout(orientation='vertical')
            
            tabs = BoxLayout(size_hint_y=0.08, spacing=dp(2))
            btn_manual = Button(text=f('مدیریت دستی'), background_color=(0.3, 0.5, 0.8, 1), size_hint_y=None, height=dp(45))
            btn_excel = Button(text=f('ورود از اکسل'), background_color=(0.3, 0.5, 0.8, 0.6), size_hint_y=None, height=dp(45))
            
            btn_manual.bind(on_press=lambda x: self.show_manual_routes())
            btn_excel.bind(on_press=lambda x: self.show_excel_routes())
            
            tabs.add_widget(btn_manual)
            tabs.add_widget(btn_excel)
            layout.add_widget(tabs)
            
            self.routes_content = BoxLayout(orientation='vertical')
            layout.add_widget(self.routes_content)
            
            self.show_manual_routes()
            self.content_area.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش مسیرها: {e}", error_details)
    
    def show_manual_routes(self):
        try:
            self.routes_content.clear_widgets()
            
            content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
            content.bind(minimum_height=content.setter('height'))
            
            content.add_widget(Label(text=f('➕ افزودن مسیر جدید'), size_hint_y=None, height=dp(40), font_size=sp(16), bold=True))
            
            self.route_name_input = RTLTextInput(hint_text='نام مسیر', multiline=False, size_hint_y=None, height=dp(50))
            content.add_widget(self.route_name_input)
            
            add_btn = Button(text=f('افزودن'), size_hint_y=None, height=dp(50), background_color=(0.2, 0.7, 0.2, 1))
            add_btn.bind(on_press=self.add_route_manual)
            content.add_widget(add_btn)
            
            content.add_widget(Label(text=f('🗺️ لیست مسیرها'), size_hint_y=None, height=dp(40), font_size=sp(16), bold=True))
            
            self.routes_list = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
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
            for route in routes:
                box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
                box.add_widget(Label(text=f(route.get('name', '')), size_hint_x=0.7))
                del_btn = Button(text=f('حذف'), size_hint_x=0.3, background_color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=dp(40))
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
            
            layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
            
            layout.add_widget(Label(text=f('📎 ورود مسیرها از فایل Excel'), font_size=sp(18), bold=True, size_hint_y=0.08))
            
            info = Label(text=f('فرمت فایل اکسل: ستون اول نام مسیر'), size_hint_y=None, height=dp(40))
            layout.add_widget(info)
            
            self.routes_file_picker = FilePicker(size_hint_y=None, height=dp(100))
            layout.add_widget(self.routes_file_picker)
            
            import_btn = Button(text=f('ورود به سیستم'), background_color=(0.2, 0.7, 0.2, 1), size_hint_y=None, height=dp(50))
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
            layout = BoxLayout(orientation='vertical')
            
            tabs = BoxLayout(size_hint_y=0.08, spacing=dp(2))
            btn_manual = Button(text=f('مدیریت دستی'), background_color=(0.3, 0.5, 0.8, 1), size_hint_y=None, height=dp(45))
            btn_excel = Button(text=f('ورود از اکسل'), background_color=(0.3, 0.5, 0.8, 0.6), size_hint_y=None, height=dp(45))
            
            btn_manual.bind(on_press=lambda x: self.show_manual_customers())
            btn_excel.bind(on_press=lambda x: self.show_excel_customers())
            
            tabs.add_widget(btn_manual)
            tabs.add_widget(btn_excel)
            layout.add_widget(tabs)
            
            self.customers_content = BoxLayout(orientation='vertical')
            layout.add_widget(self.customers_content)
            
            self.show_manual_customers()
            self.content_area.add_widget(layout)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش مشتریان: {e}", error_details)
    
    def show_manual_customers(self):
        try:
            self.customers_content.clear_widgets()
            
            content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
            content.bind(minimum_height=content.setter('height'))
            
            content.add_widget(Label(text=f('➕ افزودن مشتری جدید'), size_hint_y=None, height=dp(40), font_size=sp(16), bold=True))
            
            content.add_widget(Label(text=f('انتخاب مسیر:'), size_hint_y=None, height=dp(30)))
            routes = get_routes()
            route_names = [r.get('name', '') for r in routes] if routes else ['']
            self.customer_route_spinner = RTLSpinner(text=route_names[0] if route_names else '', values=route_names, size_hint_y=None, height=dp(50))
            content.add_widget(self.customer_route_spinner)
            
            self.customer_name_input = RTLTextInput(hint_text='نام مشتری', multiline=False, size_hint_y=None, height=dp(50))
            content.add_widget(self.customer_name_input)
            
            self.customer_store_input = RTLTextInput(hint_text='نام فروشگاه', multiline=False, size_hint_y=None, height=dp(50))
            content.add_widget(self.customer_store_input)
            
            self.customer_mobile_input = RTLTextInput(hint_text='موبایل', multiline=False, size_hint_y=None, height=dp(50))
            content.add_widget(self.customer_mobile_input)
            
            self.customer_address_input = RTLTextInput(hint_text='آدرس', multiline=False, size_hint_y=None, height=dp(50))
            content.add_widget(self.customer_address_input)
            
            add_btn = Button(text=f('افزودن مشتری'), size_hint_y=None, height=dp(50), background_color=(0.2, 0.7, 0.2, 1))
            add_btn.bind(on_press=self.add_customer_manual)
            content.add_widget(add_btn)
            
            content.add_widget(Label(text=f('📞 لیست مشتریان'), size_hint_y=None, height=dp(40), font_size=sp(16), bold=True))
            
            self.customers_list = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
            self.customers_list.bind(minimum_height=self.customers_list.setter('height'))
            content.add_widget(self.customers_list)
            
            filter_btn = Button(text=f('نمایش مشتریان این مسیر'), size_hint_y=None, height=dp(40), background_color=(0.4, 0.5, 0.6, 1))
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
                self.customers_list.add_widget(Label(text=f('هیچ مشتری در این مسیر وجود ندارد'), size_hint_y=None, height=dp(40)))
                return
            
            for customer in filtered:
                box = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
                info = f"{customer.get('name', '')}\n{customer.get('store_name', '')}\n{customer.get('mobile', '')}"
                box.add_widget(Label(text=f(info), size_hint_x=0.7))
                del_btn = Button(text=f('حذف'), size_hint_x=0.3, background_color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=dp(40))
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
            
            layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
            
            layout.add_widget(Label(text=f('📎 ورود مشتریان از فایل Excel'), font_size=sp(18), bold=True, size_hint_y=0.08))
            
            info = Label(text=f('فرمت فایل اکسل: name, store_name, route_name, mobile, address'), size_hint_y=None, height=dp(40))
            layout.add_widget(info)
            
            self.customers_file_picker = FilePicker(size_hint_y=None, height=dp(100))
            layout.add_widget(self.customers_file_picker)
            
            import_btn = Button(text=f('ورود به سیستم'), background_color=(0.2, 0.7, 0.2, 1), size_hint_y=None, height=dp(50))
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
            routes = get_routes()
            customers = get_customers()
            
            route_names = [r.get('name', '') for r in routes] if routes else ['']
            customer_names = [c.get('name', '') for c in customers] if customers else ['']
            
            layout = ScrollView()
            content = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, padding=dp(10))
            content.bind(minimum_height=content.setter('height'))
            
            fields = [
                ('supervision_rate', f('درصد سرکشی به مشتری'), '0.3', 'float'),
                ('conversion_rate', f('نرخ تبدیل سرکشی به فاکتور'), '0.25', 'float'),
                ('avg_invoice_amount', f('میانگین مبلغ فاکتور استاندارد'), '1000000', 'int'),
                ('target_amount', f('مبلغ تارگت ریالی'), '50000000', 'int'),
                ('target_count', f('میزان تارگت تعدادی'), '100', 'int'),
                ('target_invoice_count', f('میزان تارگت تعداد فاکتور'), '20', 'int'),
                ('target_customer_count', f('میزان تارگت تعداد مشتری'), '50', 'int'),
                ('target_new_customer_count', f('میزان تارگت مشتری جدید'), '10', 'int'),
                ('target_cash_sales', f('تارگت فروش و وصول نقدی'), '30000000', 'int'),
                ('target_credit_sales', f('تارگت فروش و وصول غیر نقدی'), '20000000', 'int'),
                ('first_customer_of_route', f('اولین مشتری مسیر روز'), settings.get('first_customer_of_route', ''), 'spinner_customer', customer_names),
                ('work_start_time', f('ساعت شروع به کار'), '08:00', 'time'),
                ('first_visit_time', f('ساعت اولین ویزیت'), '09:00', 'time'),
                ('min_daily_hours', f('حداقل ساعت کاری روزانه'), '6', 'int'),
            ]
            
            inputs = {}
            for item in fields:
                key = item[0]
                label = item[1]
                default = item[2]
                field_type = item[3]
                
                content.add_widget(Label(text=label + ':', size_hint_y=None, height=dp(45)))
                
                if field_type == 'float':
                    value = settings.get(key, default)
                    input_field = RTLTextInput(text=str(value), multiline=False, size_hint_y=None, height=dp(50), input_filter='float')
                elif field_type == 'int':
                    value = settings.get(key, default)
                    input_field = RTLTextInput(text=str(value), multiline=False, size_hint_y=None, height=dp(50), input_filter='int')
                elif field_type == 'time':
                    value = settings.get(key, default)
                    input_field = RTLTextInput(text=value, multiline=False, size_hint_y=None, height=dp(50), hint_text='HH:MM')
                elif field_type == 'spinner_customer':
                    values = item[4] if len(item) > 4 else ['']
                    value = settings.get(key, default)
                    input_field = RTLSpinner(text=value if value else (values[0] if values else ''), 
                                            values=values, size_hint_y=None, height=dp(50))
                else:
                    value = settings.get(key, default)
                    input_field = RTLTextInput(text=str(value), multiline=False, size_hint_y=None, height=dp(50))
                
                content.add_widget(input_field)
                inputs[key] = input_field
            
            content.add_widget(Label(size_hint_y=None, height=dp(10)))
            
            save_btn = Button(text=f('ذخیره تنظیمات'), size_hint_y=None, height=dp(50), background_color=(0.2, 0.6, 1, 1), size_hint_x=0.5)
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
                elif key in ['work_start_time', 'first_visit_time', 'first_customer_of_route']:
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
            content.add_widget(Label(text=f(message), size_hint_y=None, height=dp(50)))
            btn = Button(text=f('باشه'), size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=f(title), content=content, size_hint=(0.8, 0.35))
            btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش پیام: {e}", error_details)
    
    def logout(self, instance):
        self.manager.current = 'login'


class UserScreen(Screen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.settings = get_settings()
            self.build_ui()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت UserScreen: {e}", error_details)
            raise
    
    def build_ui(self):
        try:
            layout = BoxLayout(orientation='vertical')
            
            header = Label(text=f('ثبت ویزیت روزانه'), size_hint_y=0.07, font_size=sp(20))
            layout.add_widget(header)
            
            self.form_layout = GridLayout(cols=3, spacing=dp(8), size_hint_y=None, padding=dp(10))
            self.form_layout.bind(minimum_height=self.form_layout.setter('height'))
            
            routes = get_routes()
            self.route_names = [r.get('name', '') for r in routes] if routes else ['']
            
            customers = get_customers()
            self.all_customer_names = [c.get('name', '') for c in customers] if customers else ['']
            
            # هدرها
            self.form_layout.add_widget(Label(text=f('آیتم'), size_hint_y=None, height=dp(35), bold=True, color=(0.2, 0.5, 0.8, 1)))
            self.form_layout.add_widget(Label(text=f('مقدار'), size_hint_y=None, height=dp(35), bold=True, color=(0.2, 0.5, 0.8, 1)))
            self.form_layout.add_widget(Label(text=f('هدف'), size_hint_y=None, height=dp(35), bold=True, color=(0.2, 0.5, 0.8, 1)))
            
            self.inputs = {}
            
            # تاریخ
            self.form_layout.add_widget(Label(text=f('تاریخ ویزیت'), size_hint_y=None, height=dp(40)))
            visit_date = RTLTextInput(text=get_today_jalali(), multiline=False, size_hint_y=None, height=dp(40))
            self.form_layout.add_widget(visit_date)
            self.form_layout.add_widget(Label(text='---', size_hint_y=None, height=dp(40), color=(0.5, 0.5, 0.5, 1)))
            self.inputs['visit_date'] = visit_date
            
            # مسیر
            self.form_layout.add_widget(Label(text=f('مسیر ویزیت'), size_hint_y=None, height=dp(40)))
            self.route_spinner = RTLSpinner(text=self.route_names[0] if self.route_names else '', values=self.route_names, size_hint_y=None, height=dp(40))
            self.route_spinner.bind(text=self.on_route_change)
            self.form_layout.add_widget(self.route_spinner)
            self.route_customers_target = Label(text='0', size_hint_y=None, height=dp(40), color=(0.6, 0.4, 0.2, 1))
            self.form_layout.add_widget(self.route_customers_target)
            self.inputs['route_name'] = self.route_spinner
            
            # ساعت شروع
            self.form_layout.add_widget(Label(text=f('ساعت شروع کار'), size_hint_y=None, height=dp(40)))
            clock_in = RTLTextInput(text=get_current_time(), multiline=False, size_hint_y=None, height=dp(40))
            self.form_layout.add_widget(clock_in)
            self.form_layout.add_widget(Label(text=f(self.settings.get('work_start_time', '08:00')), size_hint_y=None, height=dp(40), color=(0.6, 0.4, 0.2, 1)))
            self.inputs['clock_in'] = clock_in
            
            # ساعت اولین ویزیت
            self.form_layout.add_widget(Label(text=f('ساعت اولین ویزیت'), size_hint_y=None, height=dp(40)))
            first_visit_time = RTLTextInput(text='', multiline=False, size_hint_y=None, height=dp(40))
            self.form_layout.add_widget(first_visit_time)
            self.form_layout.add_widget(Label(text=f(self.settings.get('first_visit_time', '09:00')), size_hint_y=None, height=dp(40), color=(0.6, 0.4, 0.2, 1)))
            self.inputs['first_visit_time'] = first_visit_time
            
            # اولین مشتری
            self.form_layout.add_widget(Label(text=f('اولین مشتری'), size_hint_y=None, height=dp(40)))
            self.first_customer_spinner = RTLSpinner(text='', values=self.all_customer_names, size_hint_y=None, height=dp(40))
            self.form_layout.add_widget(self.first_customer_spinner)
            self.first_customer_target = Label(text=f(self.settings.get('first_customer_of_route', 'تعیین نشده')), size_hint_y=None, height=dp(40), color=(0.6, 0.4, 0.2, 1))
            self.form_layout.add_widget(self.first_customer_target)
            self.inputs['first_customer'] = self.first_customer_spinner
            
            # تعداد مشتری ویزیت شده
            self.form_layout.add_widget(Label(text=f('تعداد مشتری ویزیت شده'), size_hint_y=None, height=dp(40)))
            visited_count = RTLTextInput(text='0', multiline=False, size_hint_y=None, height=dp(40), input_filter='int')
            self.form_layout.add_widget(visited_count)
            self.visited_customers_target = Label(text='0', size_hint_y=None, height=dp(40), color=(0.6, 0.4, 0.2, 1))
            self.form_layout.add_widget(self.visited_customers_target)
            self.inputs['visited_customers_count'] = visited_count
            
            # تعداد فاکتور موفق
            self.form_layout.add_widget(Label(text=f('تعداد فاکتور موفق'), size_hint_y=None, height=dp(40)))
            invoices_count = RTLTextInput(text='0', multiline=False, size_hint_y=None, height=dp(40), input_filter='int')
            self.form_layout.add_widget(invoices_count)
            self.form_layout.add_widget(Label(text=f(str(self.settings.get('target_invoice_count', '20'))), size_hint_y=None, height=dp(40), color=(0.6, 0.4, 0.2, 1)))
            self.inputs['successful_invoices_count'] = invoices_count
            
            # تعداد واحد فروش موفق
            self.form_layout.add_widget(Label(text=f('تعداد واحد فروش موفق'), size_hint_y=None, height=dp(40)))
            units_count = RTLTextInput(text='0', multiline=False, size_hint_y=None, height=dp(40), input_filter='int')
            self.form_layout.add_widget(units_count)
            self.form_layout.add_widget(Label(text=f(str(self.settings.get('target_count', '100'))), size_hint_y=None, height=dp(40), color=(0.6, 0.4, 0.2, 1)))
            self.inputs['successful_units_count'] = units_count
            
            # مبلغ فروش موفق
            self.form_layout.add_widget(Label(text=f('مبلغ فروش موفق'), size_hint_y=None, height=dp(40)))
            sales_amount = RTLTextInput(text='0', multiline=False, size_hint_y=None, height=dp(40), input_filter='int')
            self.form_layout.add_widget(sales_amount)
            
            target_amount = self.settings.get('target_amount', 50000000)
            try:
                target_amount = int(target_amount)
            except:
                target_amount = 0
            self.form_layout.add_widget(Label(text=f("{:,}".format(target_amount)), size_hint_y=None, height=dp(40), color=(0.6, 0.4, 0.2, 1)))
            self.inputs['successful_sales_amount'] = sales_amount
            
            # ساعت آخرین ویزیت
            self.form_layout.add_widget(Label(text=f('ساعت آخرین ویزیت'), size_hint_y=None, height=dp(40)))
            last_visit_time = RTLTextInput(text='', multiline=False, size_hint_y=None, height=dp(40))
            self.form_layout.add_widget(last_visit_time)
            self.form_layout.add_widget(Label(text='---', size_hint_y=None, height=dp(40), color=(0.5, 0.5, 0.5, 1)))
            self.inputs['last_visit_time'] = last_visit_time
            
            # ساعت پایان کار
            self.form_layout.add_widget(Label(text=f('ساعت پایان کار'), size_hint_y=None, height=dp(40)))
            clock_out = RTLTextInput(text='', multiline=False, size_hint_y=None, height=dp(40))
            self.form_layout.add_widget(clock_out)
            self.form_layout.add_widget(Label(text='---', size_hint_y=None, height=dp(40), color=(0.5, 0.5, 0.5, 1)))
            self.inputs['clock_out'] = clock_out
            
            form_scroll = ScrollView()
            form_scroll.add_widget(self.form_layout)
            layout.add_widget(form_scroll)
            
            btn_layout = BoxLayout(size_hint_y=0.09, spacing=dp(10), padding=dp(10))
            
            save_btn = Button(text=f('💾 ذخیره'), background_color=(0.2, 0.7, 0.2, 1), size_hint_y=None, height=dp(50))
            save_btn.bind(on_press=self.save_log)
            btn_layout.add_widget(save_btn)
            
            report_btn = Button(text=f('📊 گزارش'), background_color=(0.2, 0.6, 1, 1), size_hint_y=None, height=dp(50))
            report_btn.bind(on_press=self.go_to_report)
            btn_layout.add_widget(report_btn)
            
            logout_btn = Button(text=f('🚪 خروج'), background_color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=dp(50))
            logout_btn.bind(on_press=self.logout)
            btn_layout.add_widget(logout_btn)
            
            layout.add_widget(btn_layout)
            self.add_widget(layout)
            
            self.update_route_info()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در ساخت UI UserScreen: {e}", error_details)
            raise
    
    def update_route_info(self):
        try:
            current_route = self.route_spinner.text
            
            if current_route:
                customers = get_customers()
                total_customers = len([c for c in customers if c.get('route_name') == current_route])
                self.route_customers_target.text = str(total_customers)
                
                supervision_rate = self.settings.get('supervision_rate', 0.3)
                target_visits = int(total_customers * supervision_rate)
                self.visited_customers_target.text = str(target_visits)
                
                first_customer_target = self.settings.get('first_customer_of_route', 'تعیین نشده')
                self.first_customer_target.text = f(first_customer_target)
                
                filtered_customers = [c.get('name', '') for c in customers if c.get('route_name') == current_route]
                self.first_customer_spinner.values = filtered_customers if filtered_customers else ['']
                if filtered_customers:
                    self.first_customer_spinner.text = filtered_customers[0]
            else:
                self.route_customers_target.text = '0'
                self.visited_customers_target.text = '0'
                self.first_customer_spinner.values = ['']
                self.first_customer_spinner.text = ''
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در بروزرسانی اطلاعات مسیر: {e}", error_details)
    
    def on_route_change(self, spinner, text):
        self.update_route_info()
    
    def save_log(self, instance):
        try:
            log_data = {}
            for key, input_field in self.inputs.items():
                log_data[key] = input_field.text
            
            if not log_data['visit_date']:
                self.show_message('خطا', 'تاریخ ویزیت الزامی است')
                return
            
            for key in ['visited_customers_count', 'successful_invoices_count', 'successful_units_count', 'successful_sales_amount']:
                if key in log_data and (log_data[key] == '' or log_data[key] == '0'):
                    log_data[key] = '0'
            
            all_logs = get_daily_logs()
            
            if log_data['visit_date'] in all_logs:
                content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
                content.add_widget(Label(text=f('ویزیتی با این تاریخ قبلاً ثبت شده است. آیا می‌خواهید جایگزین شود؟'), size_hint_y=None, height=dp(60)))
                
                btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(50))
                yes_btn = Button(text=f('بله، جایگزین شود'), size_hint_y=None, height=dp(45))
                no_btn = Button(text=f('خیر، انصراف'), size_hint_y=None, height=dp(45))
                btn_layout.add_widget(yes_btn)
                btn_layout.add_widget(no_btn)
                content.add_widget(btn_layout)
                
                popup = Popup(title=f('توجه'), content=content, size_hint=(0.85, 0.35))
                
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
            content.add_widget(Label(text=f(message), size_hint_y=None, height=dp(50)))
            btn = Button(text=f('باشه'), size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=f(title), content=content, size_hint=(0.8, 0.35))
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
            
            header = Label(text=f('📊 گزارش عملکرد'), size_hint_y=0.07, font_size=sp(20))
            layout.add_widget(header)
            
            stats_scroll = ScrollView(size_hint_y=0.5)
            self.stats_layout = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=dp(15))
            self.stats_layout.bind(minimum_height=self.stats_layout.setter('height'))
            stats_scroll.add_widget(self.stats_layout)
            layout.add_widget(stats_scroll)
            
            btn_layout = BoxLayout(size_hint_y=0.12, spacing=dp(10), padding=dp(10))
            
            refresh_btn = Button(text=f('🔄 تازه سازی'), background_color=(0.4, 0.4, 0.8, 1), size_hint_y=None, height=dp(45))
            refresh_btn.bind(on_press=self.refresh_stats)
            btn_layout.add_widget(refresh_btn)
            
            excel_btn = Button(text=f('📎 خروجی Excel'), background_color=(0.2, 0.6, 0.2, 1), size_hint_y=None, height=dp(45))
            excel_btn.bind(on_press=self.export_excel)
            btn_layout.add_widget(excel_btn)
            
            pdf_btn = Button(text=f('📄 خروجی PDF'), background_color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=dp(45))
            pdf_btn.bind(on_press=self.export_pdf)
            btn_layout.add_widget(pdf_btn)
            
            back_btn = Button(text=f('🔙 بازگشت'), background_color=(0.5, 0.5, 0.5, 1), size_hint_y=None, height=dp(45))
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
                self.stats_layout.add_widget(Label(text=f('📭 هیچ داده‌ای وجود ندارد'), size_hint_y=None, height=dp(50), font_size=sp(16)))
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
            
            self.stats_layout.add_widget(Label(text=f('📊 خلاصه آمار کل'), size_hint_y=None, height=dp(45), font_size=sp(18), bold=True))
            
            stats_row1 = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
            card1 = self.make_stat_card(f('💰 کل فروش'), f"{total_sales:,}", 'Rial', (0.2, 0.6, 0.2, 1))
            card2 = self.make_stat_card(f('🧾 فاکتورها'), str(total_invoices), '', (0.2, 0.5, 0.8, 1))
            stats_row1.add_widget(card1)
            stats_row1.add_widget(card2)
            self.stats_layout.add_widget(stats_row1)
            
            stats_row2 = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
            card3 = self.make_stat_card(f('👥 ویزیت‌ها'), str(total_visits), '', (0.8, 0.5, 0.2, 1))
            card4 = self.make_stat_card(f('📦 واحد فروش'), str(total_units), '', (0.6, 0.3, 0.7, 1))
            stats_row2.add_widget(card3)
            stats_row2.add_widget(card4)
            self.stats_layout.add_widget(stats_row2)
            
            stats_row3 = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
            card5 = self.make_stat_card(f('📅 روزهای کاری'), str(len(logs)), '', (0.3, 0.6, 0.6, 1))
            avg_sale = total_sales // total_invoices if total_invoices > 0 else 0
            card6 = self.make_stat_card(f('📈 میانگین فاکتور'), f"{avg_sale:,}", 'Rial', (0.7, 0.4, 0.4, 1))
            stats_row3.add_widget(card5)
            stats_row3.add_widget(card6)
            self.stats_layout.add_widget(stats_row3)
            
            if total_visits > 0:
                avg_per_visit = total_sales // total_visits
                stats_row4 = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
                card7 = self.make_stat_card(f('🎯 فروش هر ویزیت'), f"{avg_per_visit:,}", 'Rial', (0.4, 0.5, 0.3, 1))
                stats_row4.add_widget(card7)
                self.stats_layout.add_widget(stats_row4)
            
            self.stats_layout.add_widget(Label(text=f(''), size_hint_y=None, height=dp(10)))
            self.stats_layout.add_widget(Label(text=f('📋 لیست ویزیت‌های ثبت شده'), size_hint_y=None, height=dp(40), font_size=sp(16), bold=True))
            
            header_box = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(2))
            header_date = Button(text=f('تاریخ'), size_hint_x=0.25, background_color=(0.2, 0.5, 0.8, 1), color=(1, 1, 1, 1), size_hint_y=None, height=dp(35))
            header_visit = Button(text=f('ویزیت'), size_hint_x=0.25, background_color=(0.2, 0.5, 0.8, 1), color=(1, 1, 1, 1), size_hint_y=None, height=dp(35))
            header_invoice = Button(text=f('فاکتور'), size_hint_x=0.25, background_color=(0.2, 0.5, 0.8, 1), color=(1, 1, 1, 1), size_hint_y=None, height=dp(35))
            header_sales = Button(text=f('فروش (ریال)'), size_hint_x=0.25, background_color=(0.2, 0.5, 0.8, 1), color=(1, 1, 1, 1), size_hint_y=None, height=dp(35))
            header_box.add_widget(header_date)
            header_box.add_widget(header_visit)
            header_box.add_widget(header_invoice)
            header_box.add_widget(header_sales)
            self.stats_layout.add_widget(header_box)
            
            sorted_logs = sorted(logs.items(), key=lambda x: x[0], reverse=True)
            
            for idx, (date, log) in enumerate(sorted_logs):
                row_box = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(2))
                row_box.add_widget(Label(text=date, size_hint_x=0.25))
                row_box.add_widget(Label(text=log.get('visited_customers_count', '0'), size_hint_x=0.25))
                row_box.add_widget(Label(text=log.get('successful_invoices_count', '0'), size_hint_x=0.25))
                
                sales = log.get('successful_sales_amount', '0')
                sales_num = int(sales) if str(sales).isdigit() else 0
                row_box.add_widget(Label(text=f"{sales_num:,}", size_hint_x=0.25))
                
                self.stats_layout.add_widget(row_box)
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در به‌روزرسانی آمار: {e}", error_details)
    
    def make_stat_card(self, title, value, unit, color):
        try:
            card = BoxLayout(orientation='vertical', size_hint_x=0.5, size_hint_y=None, height=dp(60), padding=dp(5), spacing=dp(2))
            title_label = Label(text=title, size_hint_y=None, height=dp(20), font_size=sp(12))
            value_label = Label(text=f"{value} {unit}", size_hint_y=None, height=dp(30), font_size=sp(18), bold=True)
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
            return Label(text=f"{title}: {value}")
    
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
            content.add_widget(Label(text=message, size_hint_y=None, height=dp(50)))
            btn = Button(text='باشه', size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=f(title), content=content, size_hint=(0.8, 0.35))
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
            layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(40))
            
            title = Label(text=f('ورود به تنظیمات سیستم'), font_size=sp(24), size_hint_y=0.15)
            layout.add_widget(title)
            
            # نمایش ایمیل مدیر و رمز پیش‌فرض
            info_text = f'[size=14][color=666666]ایمیل مدیر: {ADMIN_EMAIL}\nرمز پیش‌فرض: admin123[/color][/size]'
            email_info = Label(
                text=info_text,
                markup=True,
                size_hint_y=0.15
            )
            layout.add_widget(email_info)
            
            self.password_input = RTLTextInput(
                hint_text='رمز عبور مدیر',
                password=True,
                multiline=False,
                size_hint_y=None,
                height=dp(55)
            )
            layout.add_widget(self.password_input)
            
            btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(55))
            login_btn = Button(
                text=f('ورود'),
                background_color=(0.2, 0.6, 1, 1),
                size_hint_y=None,
                height=dp(50)
            )
            login_btn.bind(on_press=self.check_login)
            btn_layout.add_widget(login_btn)
            
            back_btn = Button(
                text=f('بازگشت'),
                background_color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(50)
            )
            back_btn.bind(on_press=self.go_back)
            btn_layout.add_widget(back_btn)
            
            layout.add_widget(btn_layout)
            
            # دکمه تنظیم مجدد رمز
            reset_btn = Button(
                text=f('🔄 تنظیم مجدد رمز (admin123)'),
                size_hint_y=None,
                height=dp(40),
                background_color=(0.8, 0.5, 0.2, 0.8)
            )
            reset_btn.bind(on_press=self.reset_password)
            layout.add_widget(reset_btn)
            
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
            
            # اگر رمز وجود نداشت یا خالی بود، رمز پیش‌فرض رو تنظیم کن
            if not hashed:
                from utils.auth import hash_password
                set_admin_password('admin123')
                hashed = get_admin_password()
                self.show_message('توجه', 'رمز پیش‌فرض "admin123" تنظیم شد')
            
            # بررسی رمز
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
            content.add_widget(Label(text=f(message), size_hint_y=None, height=dp(50)))
            btn = Button(text=f('باشه'), size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=f(title), content=content, size_hint=(0.8, 0.35))
            btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            error_details = traceback.format_exc()
            ErrorPopup.show_error(f"خطا در نمایش پیام: {e}", error_details)


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
            
            # هش کردن رمز پیش‌فرض
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
                'admin_password.json': {'hashed_password': hashed_default}  # رمز پیش‌فرض
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
