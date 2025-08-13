import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from openai import OpenAI
from gtts import gTTS
import pygame
import os
import time

newsapi = "<YOUR_NEWSAPI_KEY>"
openai_api_key = "<YOUR_OPENAI_KEY>"

recognizer = sr.Recognizer()
engine = pyttsx3.init()

def speak_old(text):
    engine.say(text)
    engine.runAndWait()

def speak(text):
    try:
        tts = gTTS(text)
        tts.save('temp.mp3')
        pygame.mixer.init()
        pygame.mixer.music.load('temp.mp3')
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()
        os.remove("temp.mp3")
    except Exception as e:
        print(f"Speech error: {e}")
        speak_old(text)

def aiProcess(command):
    try:
        client = OpenAI(api_key=openai_api_key)
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a virtual assistant named Jarvis skilled in general tasks like Alexa. Give short responses."},
                {"role": "user", "content": command}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"AI Error: {e}"

def processCommand(c):
    c = c.lower()
    if "open google" in c:
        webbrowser.open("https://google.com")
    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")
    elif c.startswith("play"):
        parts = c.split(" ", 1)
        if len(parts) > 1:
            song = parts[1]
            if song in musicLibrary.music:
                webbrowser.open(musicLibrary.music[song])
            else:
                speak("Sorry, I don't have that song.")
        else:
            speak("Please say the song name after play.")
    elif "search youtube for" in c:
        query = c.replace("search youtube for", "").strip()
        if query:
            speak(f"Searching YouTube for {query}")
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(url)
        else:
            speak("Please say the search term after 'search YouTube for'.")
    elif "news" in c:
        try:
            r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}")
            if r.status_code == 200:
                articles = r.json().get('articles', [])
                for article in articles[:5]:
                    speak(article['title'])
            else:
                speak("Failed to fetch news.")
        except Exception as e:
            speak(f"News fetch error: {e}")
    else:
        output = aiProcess(c)
        speak(output)

if __name__ == "__main__":
    speak("Initializing hey google....")
    while True:
        try:
            print("Listening for wake word...")
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=3)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            word = recognizer.recognize_google(audio).lower()
            if word == "hey google":
                speak("Yes?")
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=5)
                    command = recognizer.recognize_google(audio)
                    processCommand(command)
        except sr.WaitTimeoutError:
            pass
        except Exception as e:
            print(f"Error: {e}")
