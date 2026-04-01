import subprocess
from data.phone_details import PHONE_DIR
from .get_env import EnvManager

class ADBConnect:
    def __init__(self):
        self.L_PATH_ADB = "./src/FUNCTION/adb_connect.sh"
        self.W_PATH_ADB = "./src/FUNCTION/adb_connect.bat"

    def adb_connect(self):
        """Establish ADB connection over Wi-Fi."""
        os_name = EnvManager.check_os()
        
        try:
            if os_name == "Windows":
                subprocess.run(self.W_PATH_ADB, shell=True, check=True)
            else:
                subprocess.run(['bash', self.L_PATH_ADB], check=True)
        except subprocess.CalledProcessError:
            return "❌ Failed to run ADB connect script."

        connected_devices = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = connected_devices.stdout.strip().split('\n')[1:]
        
        if not any("device" in line for line in devices):
            return "❌ No device connected! Ensure ADB is running and the phone is connected."

        return True

class PhoneCall:
    def __init__(self, adb_connect_instance: ADBConnect):
        self.adb_connect_instance = adb_connect_instance

    def start_a_call(self, name: str) -> str:
        adb_response = self.adb_connect_instance.adb_connect()
        if adb_response is not True:
            return adb_response

        name = name.lower().strip()
        mobileNo = PHONE_DIR.get(name)

        if not mobileNo:
            subprocess.run(['adb', 'disconnect'], check=True)
            return f"❌ Contact '{name}' not found!"

        try:
            subprocess.run(['adb', 'shell', 'am', 'start', '-a', 'android.intent.action.CALL', '-d', f'tel:{mobileNo}'], check=True)
        except subprocess.CalledProcessError:
            return f"❌ Failed to initiate call to {name}."

        # Optionally keep Wi-Fi connection alive by skipping disconnect here
        subprocess.run(['adb', 'disconnect'], check=True)

        return f"📞 Phone call initiated to your friend **{name.capitalize()}**!"

# Usage Example:
def make_a_call(name:str) -> str:
    adb_instance = ADBConnect()
    phone_call_instance = PhoneCall(adb_instance)
    response = phone_call_instance.make_a_call(name)
    return response 

