import os
import time
import pygame
from gtts import gTTS
import streamlit as st
import speech_recognition as sr
from googletrans import LANGUAGES, Translator

# Initialize modules
translator = Translator()
pygame.mixer.init()

# Create a mapping between language names and language codes
language_mapping = {name: code for code, name in LANGUAGES.items()}

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)

def translator_function(spoken_text, from_language, to_language):
    return translator.translate(spoken_text, src=from_language, dest=to_language)

def text_to_voice(text_data, to_language):
    myobj = gTTS(text=text_data, lang=to_language, slow=False)
    myobj.save("cache_file.mp3")
    audio = pygame.mixer.Sound("cache_file.mp3")
    audio.play()
    os.remove("cache_file.mp3")

def main_process(output_placeholder, from_language, to_language):
    global isTranslateOn

    while isTranslateOn:
        rec = sr.Recognizer()
        with sr.Microphone() as source:
            output_placeholder.info("🎙️ Listening...")
            rec.pause_threshold = 1
            audio = rec.listen(source, phrase_time_limit=10)

        try:
            output_placeholder.info("⏳ Processing...")
            spoken_text = rec.recognize_google(audio, language=from_language)

            output_placeholder.info("🔄 Translating...")
            translated_text = translator_function(spoken_text, from_language, to_language)

            text_to_voice(translated_text.text, to_language)

            output_placeholder.success(f"✅ Translation: {translated_text.text}")

        except Exception as e:
            output_placeholder.error(f"⚠️ Error: {e}")

# Streamlit UI layout with enhanced design
st.set_page_config(page_title="Language Translator", page_icon="🌍", layout="wide")
st.title("🌍 Real-Time Language Translator")
st.markdown(
    """
    This app allows you to translate spoken language in real-time. Select the source and target languages,
    then click **Start** to begin. Press **Stop** to end the session.
    """
)

# Sidebar for language selection
st.sidebar.header("Language Settings")
from_language_name = st.sidebar.selectbox("Select Source Language:", list(LANGUAGES.values()), index=list(LANGUAGES.values()).index("english"))
to_language_name = st.sidebar.selectbox("Select Target Language:", list(LANGUAGES.values()), index=list(LANGUAGES.values()).index("spanish"))

# Convert language names to language codes
from_language = get_language_code(from_language_name)
to_language = get_language_code(to_language_name)

# Buttons for controlling the process
start_button = st.button("▶️ Start", use_container_width=True)
stop_button = st.button("⏹️ Stop", use_container_width=True)

# Output area
output_placeholder = st.empty()

# Manage translation state
isTranslateOn = False
if start_button:
    if not isTranslateOn:
        isTranslateOn = True
        main_process(output_placeholder, from_language, to_language)

if stop_button:
    isTranslateOn = False
    output_placeholder.warning("🛑 Translation stopped.")
