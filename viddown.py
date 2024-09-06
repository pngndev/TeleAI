import os
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch the API key from environment variables
api_key = os.getenv('YOUTUBE_API_KEY')

# Path to the cookies file
cookies_file = "/cookies.txt"

def download_youtube_video(link):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join("temp_videos", "temp_video.mp4"),
        'api_key': api_key,
        'cookies': cookies_file  # Add the cookies file option here
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])

# Example usage
if __name__ == "__main__":
    link = input("Enter a YouTube video link: ")
    download_youtube_video(link)
