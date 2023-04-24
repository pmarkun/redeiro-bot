import os
from dotenv import load_dotenv
import hashlib
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from moviepy.editor import *

load_dotenv()


def create_video_with_audio(image_path, audio_path, output_path):
    audio_clip = AudioFileClip(audio_path)
    image_clip = ImageClip(image_path, duration=audio_clip.duration)
    image_clip.fps = 24
    image_clip = image_clip.set_audio(audio_clip)
    image_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

def synthesize_text_with_watson(text):
    # Load Watson TTS credentials from environment variables
    api_key = os.getenv("WATSON_TTS_API_KEY")
    url = os.getenv("WATSON_TTS_URL")
    voice= os.getenv("WATSON_TTS_VOICE")


    # Create a hash of the text to generate a unique filename
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    audio_file_path = f"./tmp/out/{text_hash}.ogg"

    # Check if the audio file already exists
    if not os.path.isfile(audio_file_path):
        # Set up the Watson Text to Speech client
        authenticator = IAMAuthenticator(api_key)
        tts = TextToSpeechV1(authenticator=authenticator)
        tts.set_service_url(url)

        # Synthesize text to audio
        audio_format = "audio/ogg"
        response = tts.synthesize(
            text,
            accept=audio_format,
            voice=voice,
            timeout=60
        ).get_result()

        # Save the audio file
        with open(audio_file_path, "wb") as audio_file:
            audio_file.write(response.content)
        
         # Create a video file with a static image and the synthesized audio
        image_path = "./static/bot.png"  # Replace with the path to your static image
        video_file_path = audio_file_path.replace(".ogg", ".mp4")
        create_video_with_audio(image_path, audio_file_path, video_file_path)

    return video_file_path