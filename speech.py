import speech_recognition as sr
import asyncio, threading, uuid, os
import edge_tts
import playsound

VOICE = "en-IN-PrabhatNeural"

recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.6
mic = sr.Microphone()
listening = False

with mic as source:
    recognizer.adjust_for_ambient_noise(source, duration=1)

def speak(text):
    def _run():
        async def _tts():
            filename = f"nova_{uuid.uuid4()}.mp3"
            communicate = edge_tts.Communicate(text, VOICE)
            await communicate.save(filename)
            playsound.playsound(filename)
            os.remove(filename)
        asyncio.run(_tts())
    threading.Thread(target=_run, daemon=True).start()

def listen():
    global listening
    if listening:
        return ""
    listening = True
    try:
        with mic as source:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
            return recognizer.recognize_google(audio).lower()
    except:
        return ""
    finally:
        listening = False
