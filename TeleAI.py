import os
import time
import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from pytube import YouTube
from pytube.innertube import _default_clients
from pytube import cipher
import re

# Load environment variables
load_dotenv()

# Configure the Gemini API with your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Ensure the temp folder exists
temp_folder = "temp_videos"
os.makedirs(temp_folder, exist_ok=True)

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

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini and returns the file object."""
    file = genai.upload_file(path, mime_type=mime_type)
    st.success(f"Uploaded '{file.display_name}' successfully!")
    return file

def wait_for_files_active(files):
    """Waits for the given files to be processed and active."""
    with st.spinner("Processing video, please wait..."):
        for file in files:
            while file.state.name == "PROCESSING":
                time.sleep(5)  # Reduced sleep time for faster checking
                file = genai.get_file(file.name)
            if file.state.name != "ACTIVE":
                st.error(f"File {file.name} failed to process")
                raise Exception(f"File {file.name} failed to process")
    st.success("Video processed successfully!")

# Set up the configuration for the model generation
generation_config = {
    "temperature": 2,
    "top_p": 0.9,
    "top_k": 50,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Create the generative model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="nice and formal tone, as you are a professional TeleAI bot which allows users to get information about their uploaded video, you provide to the point answers with exact details"
)

# Streamlit app UI
st.set_page_config(page_title="TeleAI", page_icon="🤖", layout="wide")

st.title("Welcome to TeleAI 🤖")
st.subheader("Your AI-powered video assistant")

# Initialize session state for file and chat history
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# "Back" button to reset the session state
if st.session_state.uploaded_file:
    if st.button("Back"):
        # Clear the session state to reset the app
        st.session_state.uploaded_file = None
        st.session_state.chat_history = []
        st.query_params = {}  # Reset the query parameters to refresh the app

# Layout with two columns: video preview on the left, chat on the right
col1, col2 = st.columns([1, 2])

with col1:
    if st.session_state.uploaded_file is None:
        st.subheader("Upload or Download Video")
        
        # Input for YouTube URL
        youtube_url = st.text_input("Enter YouTube video URL (or leave empty to upload file):")
        
        if youtube_url:
            # Download the YouTube video
            temp_video_path = download_youtube_video(youtube_url)
            if temp_video_path:
                st.session_state.uploaded_file = temp_video_path

                # Upload the video and wait for it to be processed
                files = [upload_to_gemini(temp_video_path, mime_type="video/mp4")]
                wait_for_files_active(files)

                # Start a chat session with the model and store the file reference
                st.session_state.chat_session = model.start_chat(
                    history=[
                        {"role": "user", "parts": [files[0]]},
                        {"role": "user", "parts": ["Describe the content of the video."]},
                    ]
                )
        else:
            # File uploader if no YouTube URL is provided
            uploaded_file = st.file_uploader("Or upload a video file to start", type=["mp4"], help="Supported format: .mp4")
            if uploaded_file is not None:
                # Save the uploaded file to the temp folder
                temp_video_path = os.path.join(temp_folder, "temp_video.mp4")
                with open(temp_video_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.session_state.uploaded_file = temp_video_path

                # Upload the video and wait for it to be processed
                files = [upload_to_gemini(temp_video_path, mime_type="video/mp4")]
                wait_for_files_active(files)

                # Start a chat session with the model and store the file reference
                st.session_state.chat_session = model.start_chat(
                    history=[
                        {"role": "user", "parts": [files[0]]},
                        {"role": "user", "parts": ["Describe the content of the video."]},
                    ]
                )
    else:
        st.video(st.session_state.uploaded_file)
        st.write("Video already uploaded. You can start chatting with TeleAI.")

with col2:
    if st.session_state.uploaded_file:
        # Chatbot loop in Streamlit
        user_input = st.text_input("You:", placeholder="Ask something...", key="user_input")

        if user_input:
            if user_input.lower() == "exit":
                st.write("Ending session.")
            else:
                with st.spinner("TeleAI is thinking..."):
                    response = st.session_state.chat_session.send_message(user_input)
                st.session_state.chat_history.insert(0, {"user": user_input, "bot": response.text})

        # Display chat history with latest messages on top
        for chat in st.session_state.chat_history:
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                <div style="max-width: 70%; background-color: #0084ff; color: white; padding: 10px; border-radius: 10px; border-top-right-radius: 0px;">
                    {chat['user']}
                </div>
            </div>
            <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                <div style="max-width: 70%; background-color: #f1f0f0; color: black; padding: 10px; border-radius: 10px; border-top-left-radius: 0px;">
                    {chat['bot']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Include a button to clear chat history
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
