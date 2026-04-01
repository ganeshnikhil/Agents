import os
from subprocess import run, DEVNULL
from .get_env import EnvManager


class PrivateModeOpener:
    def __init__(self, topic: str):
        self.topic = topic
        self.search_url = f"https://www.google.com/search?q={self.topic}"
        self.os_name = EnvManager.check_os()

    def open_chrome_incognito(self) -> None:
        """Open Chrome in Incognito mode (Windows)."""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        chrome_path = next((path for path in possible_paths if os.path.exists(path)), None)

        if chrome_path:
            run([chrome_path, "--incognito", self.search_url], stdout=DEVNULL, stderr=DEVNULL)
        else:
            print("❌ Chrome not found. Please install Chrome or use another browser.")

    def open_firefox_private(self) -> None:
        """Open Firefox in Private mode (Windows)."""
        possible_paths = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ]
        firefox_path = next((path for path in possible_paths if os.path.exists(path)), None)

        if firefox_path:
            run([firefox_path, "-private-window", self.search_url], stdout=DEVNULL, stderr=DEVNULL)
        else:
            print("❌ Firefox not found. Trying Edge...")
            self.open_edge_private()

    def open_edge_private(self) -> None:
        """Open Microsoft Edge in InPrivate mode (Windows)."""
        edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        if os.path.exists(edge_path):
            run([edge_path, "--inprivate", self.search_url], stdout=DEVNULL, stderr=DEVNULL)
        else:
            print("❌ Edge not found. Please install a supported browser.")

    def linux_firefox(self) -> None:
        """Open Firefox in Private mode on Linux."""
        run(["firefox", "--private-window", self.search_url], stdout=DEVNULL, stderr=DEVNULL)

    def incog_mode_mac(self) -> None:
        """Open Safari in Private mode on macOS using AppleScript."""
        applescript_code = f'''
        tell application "Safari"
            activate
            tell application "System Events"
                keystroke "n" using {{command down, shift down}} -- Open Private Window
            end tell
            delay 1 -- Give time to open Private Window
            tell window 1
                set current tab to (make new tab with properties {{URL:"{self.search_url}"}})
            end tell
        end tell
        '''
        run(['osascript', '-e', applescript_code], stdout=DEVNULL, stderr=DEVNULL)

    def open_in_private_mode(self) -> None:
        """Open the specified topic in private/incognito mode."""
        if self.os_name == "Linux":
            self.linux_firefox()

        elif self.os_name == "Darwin":  # macOS
            self.incog_mode_mac()

        elif self.os_name == "Windows":
            try:
                self.open_chrome_incognito()
            except Exception:
                try:
                    self.open_firefox_private()
                except Exception:
                    self.open_edge_private()
        else:
            print("❌ Unsupported Operating System.")
            return "Error occurred in opening in private mode"
        
        return "Your browser is ready in private mode."


# Usage example
def private_mode(topic:str) -> bool:
    private_mode_opener = PrivateModeOpener("Artificial Intelligence")
    result = private_mode_opener.open_in_private_mode()
    return result

