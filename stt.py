import speech_recognition as sr 
import pyttsx3
import pythoncom

def recognize_and_speak():

    pythoncom.CoInitialize() 

    recognizer = sr.Recognizer()
    engine = pyttsx3.init()

    def speech_text(command):
        engine.say(command)
        engine.runAndWait()

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source=source, duration=0.5)
            audio = recognizer.listen(source=source)
            
           
            text = recognizer.recognize_google(audio_data=audio)
            text = text.lower()

            speech_text(text)
            return text  
        
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None

    except sr.UnknownValueError:
        print("Unknown error occurred")
        return None
