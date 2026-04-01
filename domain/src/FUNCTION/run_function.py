from .Tools.link_op import search_youtube
from .Tools.weather import weather_report
from .Tools.news import news_headlines
from .Tools.youtube_downloader import yt_downloader
from .Tools.app_op import app_runner
from ..Brain.text_to_info import send_to_ai
from .Tools.incog import private_mode
from .Tools.Email_send import send_email
from .Tools.phone_call import make_a_call
from .Tools.internet_search import duckgo_search
from typing import Union
from datetime import datetime



function_map = {
            'search_youtube': search_youtube,
            'weather_report': weather_report,
            'news_headlines': news_headlines,
            'yt_download': yt_downloader,
            'app_runner': app_runner,
            'send_to_ai': send_to_ai,
            'private_mode': private_mode,
            'send_email': send_email,
            'make_a_call': make_a_call,
            'duckgo_search': duckgo_search,
}

class FunctionExecutor:
    def __init__(self):
        self.function_map = {
            'search_youtube': search_youtube,
            'weather_report': weather_report,
            'news_headlines': news_headlines,
            'yt_download': yt_downloader,
            'app_runner': app_runner,
            'send_to_ai': send_to_ai,
            'private_mode': private_mode,
            'send_email': send_email,
            'make_a_call': make_a_call,
            'duckgo_search': duckgo_search,
        }

    def execute(self, function_call: dict) -> Union[None, dict, list]:
        """
        Execute a function based on the function call dictionary

        :param function_call: Dictionary with 'name' and 'parameters' keys
        :return: Dictionary with status and result of function execution
        """
        output = None
        func_name = function_call.get('name')
        args = function_call.get('parameters')

        try:
            if not func_name:
                return None

            func = self.function_map.get(func_name)

            if not func:
                print("[!] No matching function found.")
                return None

            if args:
                all_parameters = [args[k] for k in args.keys()]
                output = func(*all_parameters)
            else:
                print("[*] No parameters provided.")
                output = func()

        except KeyError as e:
            print(f"[!] Missing key in function call: {e}")
        except Exception as e:
            print(f"[!] Error executing function: {e}")

        return {
            "status": "success" if output is not None else "failed",
            "function_name": func_name,
            "args": args,
            "output": output,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
