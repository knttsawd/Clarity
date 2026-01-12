#Window testing configs
from kivy.config import Config
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '580')
#Imported to run the camera
import cv2
#Imported to recognize the voice prompts of blind people
import speech_recognition as sr
#Imported to run multiple scripts at once
import threading
#Making python speak
import pyttsx3

#Kivy App frontend components
from kivy.lang import Builder
from kivy.app import App;
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.camera import Camera

class MainApp(App):
    def build(self):
        home_page = ChatScreen(name = 'main')
        obstacle_detection = CameraScreen(name='obstacle_detection')
        sm.add_widget(obstacle_detection)
        sm.add_widget(home_page)
        sm.add_widget(transcript)
        sm.current = 'main'
        return sm
    def on_request_close(self, **kwargs):
        App.get_running_app().stop()
        
class BackButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "Back"
        self.bind(on_press = lambda instance: changeScreen('main'))

class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) #Makes sure we don't override kivy's code 
        camera_layout = GridLayout(cols=1)
        camera = Camera(play=True, resolution=(640,480))
        camera_layout.add_widget(camera)
        back_button = BackButton()
        camera_layout.add_widget(back_button)
        self.add_widget(camera_layout)

class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        home_page = Screen(name = self.name)
        chat = GridLayout(cols=1)
        chat.add_widget(Label(text="Welcome to Clarity! How can we help you?"))
        chat.add_widget(Label())
        obstacle_button = Button(text="Obstacle Detection")
        obstacle_button.bind(on_press = lambda instance: changeScreen('obstacle_detection'))
        chat.add_widget(obstacle_button)
        translate_button = Button(text="Transcription")
        translate_button.bind(on_press = lambda instance:changeScreen('transcript'))
        chat.add_widget(translate_button)
        self.add_widget(chat)

class TranscriptScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = GridLayout(cols=1)
        sub_layout = GridLayout(cols=1)
        layout.add_widget(sub_layout)
        layout.add_widget(BackButton())
        self.add_widget(layout)
    def add_message(self, message):
        text = Label(text=message)
        self.sub_layout.add_widget(text)
        print(text)
        print("Init")
        return True

sm = ScreenManager()
r = sr.Recognizer()
messages = []
transcript = TranscriptScreen(name='transcript')

def listen_for_voice():
    with sr.Microphone() as mic:
        r.adjust_for_ambient_noise(mic, duration=1)
        r.pause_threshold = 1
        while True:
            try:
                audio = r.listen(mic, 10)
                text = r.recognize_sphinx(audio)
                text = text.lower() #to ensure nothing interesting happens when comparing text
                print(text)
                transcript.add_message(text)
            except sr.WaitTimeoutError:
                print("Nothing has been said for a while. Would you like to stop?")
            except:
                print("Could not understand voice")
                pass
#camera = cv2.VideoCapture(0) #0 means to use the default camera

def changeScreen(name):
     sm.current = name

if __name__ == "__main__":
    voice_thread = threading.Thread(target=listen_for_voice, args=(), daemon=True)
    voice_thread.start()
    MainApp().run()