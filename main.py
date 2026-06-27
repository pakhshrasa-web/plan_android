"""
اپلیکیشن مدیریت ویزیت و فروش - نسخه نهایی سازگار با persian_text و rtl_widgets
"""

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

ADMIN_EMAIL = "pakhshrasa@gmail.com"
DEFAULT_ADMIN_PASSWORD = "admin123"

class ErrorPopup:
    @staticmethod
    def show_error(error_message, error_details=""):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
            
            title_label = Label(
                text="[b][color=ff3333]⚠️ خطا در برنامه[/color][/b]",
                markup=True,
                size_hint_y=None,
                height=dp(50),
                font_size=sp(18)
            )
            content.add_widget(title_label)
            
            msg_label = Label(
                text=f"[b]خطا:[/b] {error_message}",
                markup=True,
                size_hint_y=None,
                height=dp(60),
                text_size=(dp(400), None),
                halign='left'
            )
            content.add_widget(msg_label)
            
            if error_details:
                detail_label = Label(
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
                content.add_widget(Label(text="", size_hint_y=None, height=dp(20)))
            
            btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
            copy_btn = Button(
                text='📋 کپی متن خطا',
                background_color=(0.2, 0.4, 0.8, 1),
                size_hint_y=None,
                height=dp(45)
            )
            close_btn = Button(
                text='✖ بستن',
                background_color=(0.8, 0.2, 0.2, 1),
                size_hint_y=None,
                height=dp(45)
            )
            
            btn_layout.add_widget(copy_btn)
            btn_layout.add_widget(close_btn)
            content.add_widget(btn_layout)
            
            popup = Popup(
                title='⚠️ گزارش خطا',
                content=content,
                size_hint=(0.92, 0.75),
                auto_dismiss=False
            )
            
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

def global_exception_handler(exc_type, exc_value, exc_tb):
    error_msg = str(exc_value)
    error_details = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
    ErrorPopup.show_error(error_msg, error_details)

sys.excepthook = global_exception_handler

def setup_font():
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
            Config.set(
                "kivy",
                "default_font",
                [font_path, "Roboto"]
            )
            print("✅ فونت با موفقیت ثبت شد.")
            return True
        except Exception as e:
            print("❌ خطا در ثبت فونت:")
            print(e)
    else:
        print("\n❌ هیچ فونتی پیدا نشد.")

    Config.set("kivy", "default_font", ["Roboto"])
    return False

setup_font()

if platform != 'android':
    Window.size = (400, 650)

# ========== ایمپورت ماژول‌های برنامه ==========
try:
    from utils.rtl_widgets import RTLTextInput, RTLSpinner, RTLLabel
    from utils.persian_text import f
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
except Exception as e:
    error_details = traceback.format_exc()
    ErrorPopup.show_error(f"خطا در بارگذاری ماژول‌ها: {e}", error_details)

ROLES = ['بازاریاب', 'سوپروایزر', 'سرپرست', 'مدیر', 'حسابدار', 'موزع', 'راننده', 'انباردار', 'سایر']

# ========== صفحات برنامه ==========

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.build_ui()
        except Exception as e:
            ErrorPopup.show_error(f"خطا در ساخت LoginScreen: {e}", traceback.format_exc())
            raise
    
    def build_ui(self):
        try:
            layout = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(40))
            
            header_layout = BoxLayout(size_hint_y=0.1, spacing=dp(10))
            settings_btn = Button(
                text='⚙️',
                size_hint_x=0.2,
                background_color=(0.3, 0.3, 0.3, 1),
                size_hint_y=None,
                height=dp(50)
            )
            settings_btn.bind(on_press=self.open_settings)
            header_layout.add_widget(settings_btn)
            header_layout.add_widget(Label(text='', size_hint_x=0.6))
            header_layout.add_widget(Label(text='', size_hint_x=0.2))
            layout.add_widget(header_layout)
            
            title = RTLLabel(text=f('مدیریت فروش'), font_size=sp(28), size_hint_y=0.2)
            layout.add_widget(title)
            
            self.username = RTLTextInput(hint_text='نام کاربری', size_hint_y=None, height=dp(60))
            layout.add_widget(self.username)
            
            self.password = RTLTextInput(hint_text='رمز عبور', password=True, size_hint_y=None, height=dp(60))
            layout.add_widget(self.password)
            
            btn = Button(text=f('ورود'), size_hint_y=None, height=dp(55))
            btn.bind(on_press=self.check_login)
            layout.add_widget(btn)
            
            register_btn = Button(
                text=f('ثبت نام'),
                size_hint_y=None,
                height=dp(45),
                background_color=(0.3, 0.6, 0.3, 1)
            )
            register_btn.bind(on_press=self.open_register)
            layout.add_widget(register_btn)
            
            self.add_widget(layout)
        except Exception as e:
            ErrorPopup.show_error(f"خطا در ساخت UI LoginScreen: {e}", traceback.format_exc())
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
            ErrorPopup.show_error(f"خطا در ورود: {e}", traceback.format_exc())
    
    def show_message(self, title, message):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(RTLLabel(text=f(message), size_hint_y=None, height=dp(50)))
            btn = Button(text=f('باشه'), size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=f(title), content=content, size_hint=(0.8, 0.35))
            btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            ErrorPopup.show_error(f"خطا در نمایش پیام: {e}", traceback.format_exc())


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.build_ui()
        except Exception as e:
            ErrorPopup.show_error(f"خطا در ساخت RegisterScreen: {e}", traceback.format_exc())
            raise
    
    def build_ui(self):
        try:
            layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(40))
            
            title = RTLLabel(text=f('ثبت نام کاربر جدید'), font_size=sp(24), size_hint_y=0.1)
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
            register_btn = Button(
                text=f('ثبت نام'),
                background_color=(0.2, 0.7, 0.2, 1),
                size_hint_y=None,
                height=dp(50)
            )
            register_btn.bind(on_press=self.do_register)
            btn_layout.add_widget(register_btn)
            
            back_btn = Button(
                text=f('بازگشت'),
                background_color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(50)
            )
            back_btn.bind(on_press=self.go_back)
            btn_layout.add_widget(back_btn)
            
            layout.add_widget(btn_layout)
            self.add_widget(layout)
        except Exception as e:
            ErrorPopup.show_error(f"خطا در ساخت UI RegisterScreen: {e}", traceback.format_exc())
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
            ErrorPopup.show_error(f"خطا در ثبت نام: {e}", traceback.format_exc())
    
    def go_back(self, instance):
        self.manager.current = 'login'
    
    def show_message(self, title, message):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(RTLLabel(text=f(message), size_hint_y=None, height=dp(50)))
            btn = Button(text=f('باشه'), size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=f(title), content=content, size_hint=(0.8, 0.35))
            btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            ErrorPopup.show_error(f"خطا در نمایش پیام: {e}", traceback.format_exc())


class AdminSettingsScreen(Screen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.build_ui()
        except Exception as e:
            ErrorPopup.show_error(f"خطا در ساخت AdminSettingsScreen: {e}", traceback.format_exc())
            raise
    
    def build_ui(self):
        try:
            layout = BoxLayout(orientation='vertical')
            
            header = RTLLabel(text=f('تنظیمات سیستم'), size_hint_y=0.07, font_size=sp(20))
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
            ErrorPopup.show_error(f"خطا در ساخت UI AdminSettingsScreen: {e}", traceback.format_exc())
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
            ErrorPopup.show_error(f"خطا در تغییر تب: {e}", traceback.format_exc())
    
    def show_change_password_tab(self):
        try:
            layout = BoxLayout(orientation='vertical', padding=dp(30), spacing=dp(15))
            
            layout.add_widget(RTLLabel(text=f('تغییر رمز عبور مدیر'), size_hint_y=None, height=dp(50), font_size=sp(18)))
            layout.add_widget(RTLLabel(text=f('رمز عبور فعلی:'), size_hint_y=None, height=dp(30)))
            self.old_password = RTLTextInput(password=True, multiline=False, size_hint_y=None, height=dp(50))
            layout.add_widget(self.old_password)
            
            layout.add_widget(RTLLabel(text=f('رمز عبور جدید:'), size_hint_y=None, height=dp(30)))
            self.new_password = RTLTextInput(password=True, multiline=False, size_hint_y=None, height=dp(50))
            layout.add_widget(self.new_password)
            
            layout.add_widget(RTLLabel(text=f('تکرار رمز عبور جدید:'), size_hint_y=None, height=dp(30)))
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
            ErrorPopup.show_error(f"خطا در نمایش تب تغییر رمز: {e}", traceback.format_exc())
    
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
            ErrorPopup.show_error(f"خطا در تغییر رمز: {e}", traceback.format_exc())
    
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
            
            content.add_widget(RTLLabel(text=f('📋 لیست کاربران'), size_hint_y=None, height=dp(40), font_size=sp(16)))
            
            for user in users:
                user_box = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(5))
                info = f"{user.get('username', '')}\n{user.get('name', '')}\n{user.get('role', '')}"
                user_info = RTLLabel(text=f(info), size_hint_x=0.7)
                user_box.add_widget(user_info)
                
                del_btn = Button(text=f('حذف'), size_hint_x=0.3, background_color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=dp(40))
                del_btn.bind(on_press=lambda x, uid=user.get('id'): self.delete_user(uid))
                user_box.add_widget(del_btn)
                content.add_widget(user_box)
            
            layout.add_widget(content)
            self.content_area.add_widget(layout)
        except Exception as e:
            ErrorPopup.show_error(f"خطا در نمایش کاربران: {e}", traceback.format_exc())
    
    def delete_user(self, user_id):
        try:
            users = get_users()
            username = ""
            for user in users:
                if user.get('id') == user_id:
                    username = user.get('username', '')
                    break
            
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
            content.add_widget(RTLLabel(text=f(f'آیا از حذف کاربر "{username}" مطمئن هستید؟'), size_hint_y=None, height=dp(50)))
            
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
            ErrorPopup.show_error(f"خطا در حذف کاربر: {e}", traceback.format_exc())
    
    def show_codes_tab(self):
        try:
            roles = ['مدیر', 'ادمین', 'سوپروایزر', 'بازاریاب', 'حسابدار', 'موزع', 'راننده', 'انباردار', 'سایر']
            
            layout = ScrollView()
            content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
            content.bind(minimum_height=content.setter('height'))
            
            content.add_widget(RTLLabel(text=f('➕ ایجاد کد جدید'), size_hint_y=None, height=dp(40), font_size=sp(16)))
            
            role_spinner = RTLSpinner(text=roles[0], values=roles, size_hint_y=None, height=dp(50))
            content.add_widget(role_spinner)
            
            name_input = RTLTextInput(hint_text='نام و نام خانوادگی', multiline=False, size_hint_y=None, height=dp(50))
            content.add_widget(name_input)
            
            create_btn = Button(text=f('ساخت کد'), size_hint_y=None, height=dp(50), background_color=(0.2, 0.7, 0.2, 1))
            content.add_widget(create_btn)
            
            content.add_widget(RTLLabel(text=f('📋 کدهای فعال'), size_hint_y=None, height=dp(40), font_size=sp(16)))
            
            codes = get_codes()
            for code_info in codes:
                if not code_info.get('used', False):
                    code_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
                    code_text = f"{code_info['code']} - {code_info['role']} - {code_info['name']}"
                    code_label = RTLLabel(text=f(code_text), size_hint_x=0.8)
                    code_box.add_widget(code_label)
                    content.add_widget(code_box)
            
            def do_create(instance):
                try:
                    code = create_code(role_spinner.text, name_input.text)
                    self.show_message('موفق', f'کد ساخته شد:\n{code}')
                    self.switch_tab(1)
                except Exception as e:
                    ErrorPopup.show_error(f"خطا در ساخت کد: {e}", traceback.format_exc())
            
            create_btn.bind(on_press=do_create)
            
            layout.add_widget(content)
            self.content_area.add_widget(layout)
        except Exception as e:
            ErrorPopup.show_error(f"خطا در نمایش کدها: {e}", traceback.format_exc())
    
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
                content.add_widget(RTLLabel(text=f(label + ':'), size_hint_y=None, height=dp(45)))
                input_field = RTLTextInput(text=str(settings.get(key, default)), multiline=False, size_hint_y=None, height=dp(50))
                content.add_widget(input_field)
                inputs[key] = input_field
            
            save_btn = Button(text=f('ذخیره تنظیمات'), size_hint_y=None, height=dp(50), background_color=(0.2, 0.6, 1, 1))
            content.add_widget(save_btn)
            
            layout.add_widget(content)
            self.content_area.add_widget(layout)
            save_btn.bind(on_press=lambda x: self.save_settings(inputs))
        except Exception as e:
            ErrorPopup.show_error(f"خطا در نمایش تنظیمات عمومی: {e}", traceback.format_exc())
    
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
            ErrorPopup.show_error(f"خطا در ذخیره تنظیمات: {e}", traceback.format_exc())
    
    def show_message(self, title, message):
        try:
            content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
            content.add_widget(RTLLabel(text=f(message), size_hint_y=None, height=dp(50)))
            btn = Button(text=f('باشه'), size_hint_y=None, height=dp(40))
            content.add_widget(btn)
            popup = Popup(title=f(title), content=content, size_hint=(0.8, 0.35))
            btn.bind(on_press=popup.dismiss)
            popup.open()
        except Exception as e:
            ErrorPopup.show_error(f"خطا در نمایش پیام: {e}", traceback.format_exc())
    
    def go_back(self, instance):
        self.manager.current = 'login'


class AdminScreen(Screen):
    def __init__(self, **kwargs):
        try:
            super().__init__(**kwargs)
            self.current_tab = 0
            self.build_ui()
        except Exception as e:
            ErrorPopup.show_error(f"خطا در ساخت AdminScreen: {e}", traceback.format_exc())
            raise
    
    def build_ui(self):
        try:
            main_layout = BoxLayout(orientation='vertical')
            
            header = RTLLabel(text=f('پنل مدیریت'), size_hint_y=0.07, font_size=sp(20))
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
            ErrorPopup.show_error(f"خطا در ساخت UI AdminScreen: {e}", traceback.format_exc())
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
            ErrorPopup.show_error(f"خطا در تغییر تب: {e}", traceback.format_exc())
    
    def show_agents_tab(self):
        try:
            layout = ScrollView()
            content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
            content.bind(minimum_height=content.setter('height'))
            
            content.add_widget(RTLLabel(text=f('➕ افزودن عامل جدید'), size_hint_y=None, height=dp(40), font_size=sp(16)))
            
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
            
            content.add_widget(RTLLabel(text=f('📋 لیست عامل‌ها'), size_hint_y=None, height=dp(40), font_size=sp(16)))
            
            agents = get_agents()
            for agent in agents:
                agent_box = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))
                agent_info = RTLLabel(text=f("{agent.get('name', '')}\n{agent.get('role', '')}"), size_hint_x=0.7)
                agent_box.add_widget(agent_info)
                del_btn = Button(text=f('حذف'), size_hint_x=0.3, background_color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=dp(40))
                del_btn.bind(on_press=lambda x, a=agent: self.delete_agent_and_refresh(a.get('id')))
                agent_box.add_widget(del_btn)
                content.add_widget(agent_box)
            
            add_btn.bind(on_press=lambda x: self.add_agent_and_refresh(name_input, phone_input, role_spinner, email_input))
            
            layout.add_widget(content)
            self.content_area.add_widget(layout)
        except Exception as e:
            ErrorPopup.show_error(f"خطا در نمایش عامل‌ها: {e}", traceback.format_exc())
    
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
            ErrorPopup.show_error(f"خطا در افزودن عامل: {e}", traceback.format_exc())
    
    def delete_agent_and_refresh(self, agent_id):
        try:
            delete_agent(agent_id)
            self.show_message('موفق', 'عامل با موفقیت حذف شد')
            self.switch_tab(0)
        except Exception as e:
            ErrorPopup.show_error(f"خطا در حذف عامل: {e}", traceback.format_exc())
    
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
            ErrorPopup.show_error(f"خطا در نمایش مسیرها: {e}", traceback.format_exc())
    
    def show_manual_routes(self):
        try:
            self.routes_content.clear_widgets()
            
            content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
            content.bind(minimum_height=content.setter('height'))
            
            content.add_widget(RTLLabel(text=f('➕ افزودن مسیر جدید'), size_hint_y=None, height=dp(40), font_size=sp(16)))
            
            self.route_name_input = RTLTextInput(hint_text='نام مسیر', multiline=False, size_hint_y=None, height=dp(50))
            content.add_widget(self.route_name_input)
            
            add_btn = Button(text=f('افزودن'), size_hint_y=None, height=dp(50), background_color=(0.2, 0.7, 0.2, 1))
            add_btn.bind(on_press=self.add_route_manual)
            content.add_widget(add_btn)
            
            content.add_widget(RTLLabel(text=f('🗺️ لیست مسیرها'), size_hint_y=None, height=dp(40), font_size=sp(16)))
            
            self.routes_list = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
            self.routes_list.bind(minimum_height=self.routes_list.setter('height'))
            content.add_widget(self.routes_list)
            
            scroll = ScrollView()
            scroll.add_widget(content)
            self.routes_content.add_widget(scroll)
            
            self.refresh_routes_list()
        except Exception as e:
            ErrorPopup.show_error(f"خطا در نمایش مسیرهای دستی: {e}", traceback.format_exc())
    
    def refresh_routes_list(self):
        try:
            self.routes_list.clear_widgets()
            routes = get_routes()
            for route in routes:
                box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
                box.add_widget(RTLLabel(text=f(route.get('name', '')), size_hint_x=0.7))
                del_btn = Button(text=f('حذف'), size_hint_x=0.3, background_color=(0.8, 0.2, 0.2, 1), size_hint_y=None, height=dp(40))
                del_btn.bind(on_press=lambda x, r=route: self.delete_route_and_refresh(r.get('id')))
                box.add_widget(del_btn)
                self.routes_list.add_widget(box)
        except Exception as e:
            ErrorPopup.show_error(f"خطا در به‌روزرسانی لیست مسیرها: {e}", traceback.format_exc())
    
    def add_route_manual(self, instance):
        try:
            if self.route_name_input.text:
                add_route({'name': self.route_name_input.text})
                self.route_name_input.text = ''
                self.refresh_routes_list()
                self.show_message('موفق', 'مسیر با موفقیت اضافه شد')
        except Exception as e:
            ErrorPopup.show_error(f"خطا در افزودن مسیر: {e}", traceback.format_exc())
    
    def delete_route_and_refresh(self, route_id):
        try:
            delete_route(route_id)
            self.refresh_routes_list()
            self.show_message('موفق', 'مسیر با موفقیت حذف شد')
        except Exception as e:
            ErrorPopup.show_error(f"خطا در حذف مسیر: {e}", traceback.format_exc())
    
    def show_excel_routes(self):
        try:
            self.routes_content.clear_widgets()
            
            layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
            
            layout.add_widget(RTLLabel(text=f('📎 ورود مسیرها از فایل Excel'), font_size=sp(18), size_hint_y=0.08))
            
            info = RTLLabel(text=f('فرمت فایل اکسل: ستون اول نام مسیر'), size_hint_y=None, height=dp(40))
            layout.add_widget(info)
            
            self.routes_file_picker = FilePicker(size_hint_y=None, height=dp(100))
            layout.add_widget(self.routes_file_picker)
            
            import_btn = Button(text=f('ورود به سیستم'), background_color=(0.2, 0.7, 0.2, 1), size_hint_y=None, height=dp(50))
            import_btn.bind(on_press=self.import_routes_from_excel)
            layout.add_widget(import_btn)
            
            self.routes_content.add_widget(layout)
        except Exception as e:
            ErrorPopup.show_error(f"خطا در نمایش ورود اکسل مسیرها: {e}", traceback.format_exc())
    
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
            ErrorPopup.show_error(f"خطا در ورود مسیرها از اکسل: {e}", traceback.format_exc())
    
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
            ErrorPopup.show_error(f"خطا در نمایش مشتریان: {e}", traceback.format_exc())
    
    def show_manual_customers(self):
        try:
            self.customers_content.clear_widgets()
            
            content = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(10))
            content.bind(minimum_height=content.setter('height'))
            
            content.add_widget(RTLLabel(text=f('➕ افزودن مشتری جدید'), size_hint_y=None, height=dp(40), font_size=sp(16)))
            
            content.add_widget(RTLLabel(text=f('انتخاب مسیر:'), size_hint_y=None, height=dp(30)))
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
            
            content.add_widget(RTLLabel(text=f('📞 لیست مشتریان'), size_hint_y=None, height=dp(40), font_size=sp(16)))
            
            self.customers_list = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
            self.customers_list.bind(minimum_height=self.customers_list.setter('height'))
            content.add_widget(self.customers_list)
            
            filter_btn = Button(text=f('نمایش مشتریان این مسیر'), size_hint_y=None, height=dp(40), background_color=(0.4, 0.5, 0.6, 1))
            filter_btn.bind(on_press=self.refresh_customers_list)
            content.add_widget(filter_btn)
            
            scroll = ScrollView()
            scroll.add_widget(content)
            self.customers_content.add_widget(scroll)
