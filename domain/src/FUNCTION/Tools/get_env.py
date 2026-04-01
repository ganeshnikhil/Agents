from dotenv import load_dotenv
from os import environ
from typing import Union
import json
import os
import platform
from fuzzywuzzy import process
from data.Domain import websites
import shutil


# Load environment variables from .env file
load_dotenv()
APP_JSON_PATH = "./DATA/app.json"


class EnvManager:
    """Handles environment variable loading."""
    
    @staticmethod
    def load_variable(variable_name: str) -> Union[str, None]:
        """Load environment variable."""
        try:
            variable = environ.get(variable_name.strip())
            return variable
        except Exception as e:
            print(f"Error: {e}")
        return None
    
    @staticmethod
    def check_os() -> str:
        """Check the operating system and return the name."""
        os_name = platform.system()
        if os_name == "Windows":
            return "Windows"
        elif os_name == "Darwin":
            return "Darwin"
        elif os_name == "Linux":
            return "Linux"
        else:
            return "Unknown"


class AppManager:
    """Handles application management tasks such as checking OS, installed apps, and updating the app list."""

    @staticmethod
    def is_app_installed(path: str) -> bool:
        """Check if an application is installed by verifying its path."""
        
        # Check if it's in the system PATH (for built-in apps like Notepad, Calculator)
        if shutil.which(path):
            return True
        
        # Check if the direct path exists (for installed applications)
        return os.path.exists(path)

    @staticmethod
    def get_url(website_name: str) -> str:
        """Retrieve website URL with exact or fuzzy matching."""
        if not website_name:
            print("❌ Website name cannot be empty.")
            return ""

        # Normalize input
        website_name = website_name.strip().lower()

        # Exact match
        if website_name in websites:
            return websites[website_name]

        # Fuzzy matching
        closest_match, score = process.extractOne(website_name, websites.keys())
        if score >= 80:
            return websites[closest_match]

        print(f"❌ Website '{website_name}' not found.")
        return ""

    @staticmethod
    def get_app_path(app_name, app_data):
        """Retrieve app path with exact match and fuzzy matching."""
        # ✅ Strip and lowercase app_name (just in case)
        app_name = app_name.strip().lower()
        # ✅ Check for exact match (since app_data is already normalized)
        if app_name in app_data and AppManager.is_app_installed(app_data.get(app_name)):
            return app_data.get(app_name)

        # ✅ Fuzzy match for closest name in normalized keys
        closest_match, score = process.extractOne(app_name, app_data.keys())
        
        # ✅ Set a threshold for match confidence (e.g., 80)
        if score >= 80 and AppManager.is_app_installed(closest_match):  # High confidence match
            return app_data[closest_match]
        
        # if no app found, fallback to website search
        link = AppManager.get_url(app_name)
        if link:
            return link
        
        # ❌ No match found
        print(f"❌ Application or web '{app_name}' not found.")
        return ""

    @staticmethod
    def load_app(app_name: str) -> str:
        """Load the path of the application from app.json."""
        if not os.path.exists(APP_JSON_PATH) or os.path.getsize(APP_JSON_PATH) == 0:
            print("app.json is empty or does not exist. Fetching apps...")
            AppManager.update_app_list()

        with open(APP_JSON_PATH, "r", encoding="utf-8") as f:
            app_data = json.load(f)
        
        return AppManager.get_app_path(app_name , app_data)

    @staticmethod
    def update_app_list():
        """Get the list of installed apps and store them in app.json."""
        os_name = EnvManager.check_os()
        apps = []

        if os_name == "Windows":
            apps = AppManager.get_installed_apps_windows()
        elif os_name == "Darwin":
            apps = AppManager.get_installed_apps_mac()
        elif os_name == "Linux":
            apps = AppManager.get_installed_apps_linux()

        # Store in app.json
        app_dict = {app["name"].lower(): app["path"] for app in apps}
        
        with open(APP_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(app_dict, f, indent=4)
        
        print(f"{len(app_dict)} applications found and stored in app.json.")

    @staticmethod
    def get_installed_apps_windows():
        """Get installed applications on Windows."""
        import winreg
        apps = []
        reg_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
        ]
        
        for reg_path in reg_paths:
            try:
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                for i in range(winreg.QueryInfoKey(reg_key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(reg_key, i)
                        subkey = winreg.OpenKey(reg_key, subkey_name)
                        name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                        path, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                        if name and path:
                            apps.append({"name": name, "path": path})
                    except (FileNotFoundError, OSError, ValueError):
                        continue
            except FileNotFoundError:
                continue
        return apps

    @staticmethod
    def get_installed_apps_mac():
        """Get installed applications on macOS."""
        app_paths = [
            "/Applications",
            os.path.expanduser("~/Applications"),
            "/System/Applications",  # System apps
        ]
        apps = []

        for path in app_paths:
            if os.path.exists(path):
                for app in os.listdir(path):
                    if app.endswith(".app"):
                        apps.append({"name": app.replace(".app", ""), "path": os.path.join(path, app)})

        return apps

    @staticmethod
    def get_installed_apps_linux():
        """Get installed applications on Linux."""
        import glob
        app_paths = ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]
        apps = []

        for path in app_paths:
            if os.path.exists(path):
                for file in glob.glob(f"{path}/*.desktop"):
                    with open(file, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        name, exec_path = None, None
                        for line in lines:
                            if line.startswith("Name="):
                                name = line.split("=", 1)[1].strip()
                            elif line.startswith("Exec="):
                                exec_path = line.split("=", 1)[1].strip()
                        if name and exec_path:
                            apps.append({"name": name, "path": exec_path.split()[0]})

        return apps
