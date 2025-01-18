from flask import Flask, render_template, request, jsonify
import os
import time
import threading
import pygame
from gtts import gTTS
import speech_recognition as sr
from googletrans import LANGUAGES, Translator

app = Flask(__name__)

# Initialize global variables
isTranslateOn = False
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

def main_process(output_callback, from_language, to_language):
    global isTranslateOn

    rec = sr.Recognizer()
    while isTranslateOn:
        try:
            with sr.Microphone() as source:
                output_callback("Listening...")
                rec.pause_threshold = 1
                audio = rec.listen(source, phrase_time_limit=10)

            output_callback("Processing...")
            spoken_text = rec.recognize_google(audio, language=from_language)

            output_callback("Translating...")
            translated_text = translator_function(spoken_text, from_language, to_language)

            text_to_voice(translated_text.text, to_language)
            output_callback(f"Translated: {translated_text.text}")

        except Exception as e:
            output_callback(f"Error: {str(e)}")
            break

@app.route('/', methods=['GET', 'POST'])
def index():
    global isTranslateOn

    if 'start' in request.form:
        from_language_name = request.form['from_language']
        to_language_name = request.form['to_language']

        from_language = get_language_code(from_language_name)
        to_language = get_language_code(to_language_name)

        if not isTranslateOn:
            isTranslateOn = True
            threading.Thread(
                target=main_process,
                args=(lambda msg: print(msg), from_language, to_language),
                daemon=True
            ).start()

    elif 'stop' in request.form:
        isTranslateOn = False

    return render_template('index.html', languages=LANGUAGES.values())

if __name__ == '__main__':
    app.run(debug=True)