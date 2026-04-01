from .get_env import AppManager , EnvManager #load_app, check_os
from os import system

class AppRunner:
    def __init__(self, name: str):
        self.name = name
        self.os_name = EnvManager.check_os()
        self.path = AppManager().load_app(name)

    def start_app(self) -> bool:
        """Start the app based on the operating system."""
        if self.os_name == "Linux":
            system(f'"{self.path}"')
        elif self.os_name == "Darwin":
            system(f'open "{self.path}"')
        elif self.os_name == "Windows":
            system(f'start "{self.path}"')
        else:
            print("Invalid Operating system..")
            return False
        return True
    
    def run(self) -> str:
        """Runs the application and returns a message indicating success or failure."""
        if self.start_app():
            return f"{self.name} is Opened and running now"
        return f"Oops, some error occurred in opening {self.name}."


def app_runner(app_name:str) -> str:
    run_app = AppRunner(app_name)
    result = run_app.run()
    return result


# Example usage:
if __name__ == "__main__":
    app_name = input("Enter the name of the app to open: ")
    app_runner = AppRunner(app_name)
    result = app_runner.run()
    print(result)
