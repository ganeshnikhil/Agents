import re
from pytube import YouTube
from os import getcwd, mkdir, system
from os.path import join, exists
from .get_env import EnvManager

class YouTubeDownloader:
    def __init__(self, url: str):
        self.url = url
        self.save_path = EnvManager.load_variable("Yt_path")
        if not self.save_path:
            raise ValueError("Error: No save path specified.")
    
    def extract_id(self) -> str:
        """Extracts the video ID from the YouTube URL."""
        regex = r"(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/" \
                r"|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
        match = re.search(regex, self.url)
        if not match:
            raise ValueError("Invalid YouTube URL")
        return match.group(1)
    
    def download_video(self) -> str:
        """Download a YouTube video."""
        # Extract video ID from URL
        try:
            video_id = self.extract_id()
        except ValueError as e:
            return str(e)

        # Create filename
        file_name = f"{video_id}.mp4"

        # Download video
        try:
            # Create save path if it doesn't exist
            if not exists(self.save_path):
                mkdir(self.save_path)
            
            # Get the highest resolution video stream
            video = YouTube(self.url)
            highest_resolution_stream = video.streams.order_by('resolution').desc().first()
            
            # Download the video
            highest_resolution_stream.download(output_path=self.save_path, filename=file_name)

            return f"Downloaded video: {file_name}"
        except Exception as e:
            print(f"Error downloading video: {e}")
            return f"Error occurred while downloading video: {e}"

# Usage example:
def yt_downloader(url:str) -> str:
    downloader = YouTubeDownloader(url)
    result = downloader.download_video()
    return result


