import os
import json
from kivy.utils import platform

_data_path = None

def init_data_path():
    global _data_path
    if _data_path is None:
        if platform == 'android':
            try:
                from android.storage import app_storage_path
                _data_path = os.path.join(app_storage_path(), 'MyApp')
            except:
                _data_path = os.path.join(os.getcwd(), 'MyApp')
        else:
            if platform == 'win':
                _data_path = os.path.join(os.environ.get('APPDATA', os.getcwd()), 'MyApp')
            else:
                _data_path = os.path.join(os.getcwd(), 'MyApp')
        os.makedirs(_data_path, exist_ok=True)
        os.makedirs(os.path.join(_data_path, 'reports'), exist_ok=True)
    return _data_path

def get_data_path():
    if _data_path is None:
        init_data_path()
    return _data_path

def load_json(filename):
    path = os.path.join(get_data_path(), filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    path = os.path.join(get_data_path(), filename)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
