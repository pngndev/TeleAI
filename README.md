[TeleAI Showcase.webm](https://github.com/user-attachments/assets/1f9f4019-ccba-4a36-a547-633432492c5f)
# TeleAI

**TeleAI** is a video processing chatbot that allows users to upload a video and chat about its content. Built using Streamlit, Google Generative AI, and dotenv, TeleAI provides an intuitive interface where users can ask questions, get insights, and interact with video content in a conversational manner.

__website:__ *https://tele-ai.streamlit.app/*
## Features

- **Video Upload:** Users can upload a video and have it processed by the chatbot.
- **Conversational AI:** Leverages Google Generative AI to answer questions and provide insights based on the video content.
- **Streamlit Interface:** A sleek and professional-looking UI for easy interaction.
- **Environment Management:** Uses `dotenv` to manage environment variables securely.

## Installation

Follow these steps to set up and run TeleAI on your local machine.

### Prerequisites

Ensure you have the following installed:

- **Python 3.7 or higher**
- **pip** (Python package installer)
- **A Google Generative AI API key**

### Step 1: Clone the Repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/pngnev/TeleAI.git
cd TeleAI
```
### Step 2: Set Up a Virtual Environment (Optional but Recommended)
It’s recommended to create a virtual environment to keep your dependencies isolated:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```
### Step 3: Install Required Packages
Install the necessary packages listed in requirements.txt:

```bash
pip install -r requirements.txt
```
### Step 4: Configure Environment Variables
Create a .env file in the project root directory and add your Google Generative AI API key:

```bash
touch .env
```
Add the following line to your .env file:
```bash
GEMINI_API_KEY=your-google-generative-ai-api-key
```
### Step 5: Run the Application
Start the Streamlit app by running the following command:
```bash
streamlit run TeleAI.py
```
Once the app is running, streamlit will automatically open a tab with the application.

### Step 6: Upload a Video and Chat

Upload a Video: Upload your video file using the provided interface.
Start Chatting: Ask questions or chat with the AI about the video content.
## Troubleshooting
If you encounter any issues, make sure your environment is properly set up and that your API key is correct.
## License
This repo is licensed under GPL v2.0 `(General Public License v2.0)`
