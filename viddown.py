from pytube import YouTube
from pytube.innertube import _default_clients
from pytube import cipher
import re
import os

# Update default clients to handle YouTube's changes
client_version = "19.08.35"
_default_clients["ANDROID"]["context"]["client"]["clientVersion"] = client_version
_default_clients["IOS"]["context"]["client"]["clientVersion"] = client_version
_default_clients["ANDROID_EMBED"]["context"]["client"]["clientVersion"] = client_version
_default_clients["IOS_EMBED"]["context"]["client"]["clientVersion"] = client_version
_default_clients["IOS_MUSIC"]["context"]["client"]["clientVersion"] = "6.41"
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

# Function to get the throttling function name from the JavaScript
def get_throttling_function_name(js: str) -> str:
    function_patterns = [
        r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])?\([a-z]\)',
        r'\([a-z]\s*=\s*([a-zA-Z0-9$]+)(\[\d+\])\([a-z]\)',
    ]
    
    for pattern in function_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(js)
        if function_match:
            if len(function_match.groups()) == 1:
                return function_match.group(1)
            idx = function_match.group(2)
            if idx:
                idx = idx.strip("[]")
                array = re.search(
                    r'var {nfunc}\s*=\s*(\[.+?\]);'.format(
                        nfunc=re.escape(function_match.group(1))
                    ),
                    js
                )
                if array:
                    array = array.group(1).strip("[]").split(",")
                    array = [x.strip() for x in array]
                    return array[int(idx)]
    
    raise Exception("Could not find throttling function name.")

# Override the original get_throttling_function_name with the updated one
cipher.get_throttling_function_name = get_throttling_function_name


def download_youtube_video(url):
    """Downloads a YouTube video and saves it as 'temp_video.mp4' in the 'temp_videos' folder."""
    try:
        # Define the path for the downloaded video
        temp_folder = "temp_videos"
        os.makedirs(temp_folder, exist_ok=True)
        temp_video_path = os.path.join(temp_folder, "temp_video.mp4")
        
        # Create a YouTube object
        yt = YouTube(url)
        
        # Get the highest resolution stream available
        stream = yt.streams.get_highest_resolution()
        
        # Download the video
        print(f"Downloading {yt.title}...")
        stream.download(output_path=temp_folder, filename="temp_video.mp4")
        print("Download completed!")
        
        return temp_video_path  # Return the path to the downloaded video
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None  # Return None if an error occurs
    
if __name__ == "__main__":
    url = input("Enter the YouTube video URL: ")
    download_youtube_video(url)
