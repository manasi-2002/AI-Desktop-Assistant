import os
import struct
import subprocess
import time
import webbrowser
import platform
from shlex import quote
import eel
import re
import hugchat
import pvporcupine
import pyaudio
import pyautogui
import pywhatkit as kit
import pygame
import platform
import sqlite3
import pyperclip
import google.generativeai as genai
from pathlib import Path
from backend.command import speak
from backend.config import ASSISTANT_NAME
from backend.helper import extract_yt_term, remove_words
from dotenv import load_dotenv

# Load Gemini API key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')
chat = model.start_chat(history=[]) #Starts a fresh chat history for generative responses

if platform.system() == "Windows":
    ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY_WINDOWS")
else:
    ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY_MAC")

def clean_markdown(text):
    # Remove backslash and underscore markdown 
    text = re.sub(r'(\{1,2}|_{1,2})(.?)\1', r'\2', text)
    # Remove inline code (e.g., code)
    text = re.sub(r'(.*?)', r'\1', text)
    # Remove markdown headers (e.g., # Header)
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    # Remove remaining asterisks or undesired symbols
    text = text.replace('*', '')
    return text.strip() #Removes formatting (like bold, italic, headers) from chatbot responses before speaking/displaying them.

# SQLite Connection
conn = sqlite3.connect("sherlock.db")
cursor = conn.cursor()

# Initialize pygame mixer
pygame.mixer.init()

@eel.expose
def playAssistantSound():
    sound_file = r"frontend/assets/audio/frontend_assets_audio_start_sound.mp3"
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play() #Initializes Pygame mixer and plays a sound file when the assistant is activated.

def openCommand(query):
    query = query.lower()
    query = query.replace(ASSISTANT_NAME, "")

    # Clean filler words like "please", "quickly", etc.
    fillers = ["please", "can you", "would you", "kindly", "quickly", "just", "hey"]
    for word in fillers:
        query = query.replace(word, "")

    # Remove the word "open"
    query = query.replace("open", "").strip()

    app_name = query

    if not app_name:
        return

    try:
        cursor.execute('SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
        results = cursor.fetchall()

        if results:
            speak("Opening " + app_name)
            path = results[0][0]
            if platform.system() == "Windows":
                os.startfile(path) # (Windows)
            elif platform.system() == "Darwin":
                os.system(f'open "{path}"') #(macOS)
            else:
                os.system(f'xdg-open "{path}"') #(Linux)
        else:
            cursor.execute('SELECT url FROM web_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if results:
                speak("Opening " + app_name)
                webbrowser.open(results[0][0])
            else:
                speak("Opening " + app_name)
                if platform.system() == "Windows":
                    os.system(f'start {app_name}')
                elif platform.system() == "Darwin":
                    os.system(f'open -a "{app_name}"')
                else:
                    os.system(f'xdg-open "{app_name}"')

    except Exception as e:
        speak(f"Something went wrong: {str(e)}")


def playYoutube(query):
    search_term = extract_yt_term(query)
    speak(f"Playing {search_term} on YouTube")
    kit.playonyt(search_term) #Extracts keywords and plays the video on YouTube.

def hotword():
    
    # Project root folder (this file's directory)
    project_root = Path(__file__).parent
    # Choose the right keyword file based on OS
    if platform.system() == "Windows":
        keyword_file = project_root / "hotwords" / "sherlock_windows.ppn"
    else:
        keyword_file = project_root / "hotwords" / "sherlock_mac.ppn"

    # Convert Path object to string path
    keyword_path_str = str(keyword_file.resolve())
    print(f"Loaded hotword keyword file: {keyword_path_str}")
    porcupine = None
    paud = None
    audio_stream = None

    try:
        # Use your custom keyword file with access key
        porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keyword_paths=[keyword_path_str]
        )
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(rate=porcupine.sample_rate, channels=1,
                                 format=pyaudio.paInt16, input=True,
                                 frames_per_buffer=porcupine.frame_length)

        while True:
            keyword = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)

            if keyword_index >= 0:
                print("Hotword detected")

                if platform.system() == "Windows":
                    pyautogui.keyDown("win")
                    pyautogui.press("j")
                    time.sleep(2)
                    pyautogui.keyUp("win")
                else:
                    pyautogui.keyDown('command')
                    pyautogui.press('j')
                    time.sleep(2)
                    pyautogui.keyUp('command')

    except Exception as e:
        print("Error in hotword detection:", e)
    finally:
        if porcupine:
            porcupine.delete()
        if audio_stream:
            audio_stream.close()
        if paud:
            paud.terminate()

def findContact(query):
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wsapp', 'video']
    query = remove_words(query, words_to_remove).strip().lower()

    try:
        cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", 
                       ('%' + query + '%', query + '%'))
        results = cursor.fetchall()

        if results:
            mobile_number_str = str(results[0][0])
            if not mobile_number_str.startswith('+91'):
                mobile_number_str = '+91' + mobile_number_str
            return mobile_number_str, query
        else:
            speak('Contact not found')
            return 0, 0
    except:
        speak('Contact not found')
        return 0, 0

def whatsApp(Phone, message, flag, name):
    system_platform = platform.system()
    

    try:
        if system_platform == "Windows":
            # Open WhatsApp UWP Desktop
            subprocess.Popen([
                "explorer.exe",
                "shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App"
            ])
            time.sleep(7)

            # Focus search bar
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)

            # Paste contact name
            pyperclip.copy(name)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(2)

            # Click on first result — Adjust coordinates as needed
            pyautogui.click(x=250, y=260)
            time.sleep(2)

            if flag == 'message':
                sherlock_message = f"Message sent successfully to {name}"
                pyperclip.copy(message)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(1)
                pyautogui.press('enter')
                speak(sherlock_message)

            elif flag == 'call':
                sherlock_message = f"Calling {name}"
                speak(sherlock_message)
                time.sleep(2)
                pyautogui.click(x=1790, y=95)  # Adjust this to actual 📞 position

            elif flag == 'video':
                sherlock_message = f"Starting video call with {name}"
                speak(sherlock_message)
                time.sleep(2)
                pyautogui.click(x=1730, y=95)  # Adjust this to 📹 button position

        elif system_platform == "Darwin":  # macOS
            # Open WhatsApp app on Mac
            subprocess.Popen(["open", "-a", "WhatsApp"])
            time.sleep(7)

            # Click on Search bar (adjust this x, y based on your screen)
            pyautogui.click(x=100, y=80)
            time.sleep(1)

            # Paste contact name
            pyperclip.copy(name)
            pyautogui.hotkey('command', 'v')
            time.sleep(2)

            # Click first result (adjust coordinates as needed)
            pyautogui.click(x=150, y=200)
            time.sleep(2)

            if flag == 'message':
                sherlock_message = f"Message sent successfully to {name}"
                pyperclip.copy(message)
                pyautogui.hotkey('command', 'v')
                time.sleep(1)
                pyautogui.press('enter')
                speak(sherlock_message)

            elif flag == 'call':
                sherlock_message = f"Calling {name}"
                speak(sherlock_message)
                time.sleep(2)
                pyautogui.click(x=1250, y=70)  # Voice call on mac (adjust as needed)

            elif flag == 'video':
                sherlock_message = f"Starting video call with {name}"
                speak(sherlock_message)
                time.sleep(2)
                pyautogui.click(x=1200, y=70)  # Video call on mac (adjust as needed)

        else:
            speak("Unsupported OS for WhatsApp automation.")

    except Exception as e:
        speak(f"Error interacting with WhatsApp: {str(e)}")

def gemini_chatbot(prompt):
    try:
        start = time.time()

        response = chat.send_message(prompt)

        end = time.time()
        print(f"Gemini response time: {end - start:.2f} seconds")

        response_text = clean_markdown(response.text.strip())

        print(f"Gemini: {response_text}")
        return response_text

    except Exception as e:
        return f"Gemini Error: {str(e)}"

@eel.expose
def chatBot(query):
    try:
        eel.DisplayMessage(query)  # Show user's question once
        response = gemini_chatbot(query)
        print(f"Gemini: {response}")

        eel.DisplayMessage("Sherlock", response)  # Show assistant's response once

        # Speak only if word count is <= 50
        if len(response.split()) <= 50:
            speak(response)

    except Exception as e:
        print(f"Gemini ChatBot Error: {e}")
        speak("Sorry, I couldn't answer that.")

# @eel.expose
# def chatBot(query):
#     try:
#         eel.DisplayMessage(query)  # Show user's question once
#         response = gemini_chatbot(query)
#         print(f"Gemini: {response}")

#         words = response.split()
#         word_count = len(words)

#         # Condition-wise handling
#         if word_count <= 50:
#             eel.DisplayMessage(response)
#             speak(response)

#         elif word_count <= 150:
#             eel.DisplayMessage(response)
#             time.sleep(30)

#         else:
#             trimmed = ' '.join(words[:150]) + "..."
#             eel.DisplayMessage(trimmed)
            

#     except Exception as e:
#         print(f"Gemini ChatBot Error: {e}")
#         speak("Sorry, I couldn't answer that.")
