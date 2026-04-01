from geopy.geocoders import Nominatim
from requests import get
from .get_env import EnvManager
from ...Brain.text_to_info import send_to_ai

class WeatherService:
    def __init__(self, city: str):
        self.city = city
        self.api_key = EnvManager.load_variable("Weather_api")
        self.geolocator = Nominatim(user_agent="your_app_name")
        self.latitude, self.longitude = self.get_lat_lng(city)

    def get_lat_lng(self, name: str) -> tuple:
        """Get the latitude and longitude of a given place."""
        location = self.geolocator.geocode(name)
        if location:
            latitude = round(location.latitude, 3)
            longitude = round(location.longitude, 3)
            return latitude, longitude
        return 0, 0

    def weather_data(self) -> str:
        """Get the current weather report for the city."""
        report = {}
        url = "https://weatherapi-com.p.rapidapi.com/current.json"
        querystring = {"q": f"{self.latitude},{self.longitude}"}
        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "weatherapi-com.p.rapidapi.com"
        }

        response = get(url, headers=headers, params=querystring)
        
        all_data = response.json()
        
        report["datetime"] = all_data["current"]["last_updated"]
        report["temp"] = all_data["current"]["temp_c"]
        report["condition"] = all_data["current"]["condition"]["text"]
        report["wind"] = all_data["current"]["wind_kph"]
        report["humidity"] = all_data["current"]["humidity"]
        report["cloud"] = all_data["current"]["cloud"]
        report["feels_like"] = all_data["current"]["feelslike_c"]
        report["uv"] = all_data["current"]["uv"]
        
        if report:
            summarize_text = send_to_ai(f"{report} please summarize given data in less than 20 words without using numerical data.")
            return summarize_text
        return "No weather data found."

#Usage example:
def weather_report(city) -> str:
    weather_service = WeatherService(city)
    weather_summary = weather_service.weather_report()
    return weather_summary

