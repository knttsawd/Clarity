#Imported to run the camera
import cv2
#Imported to recognize the voice prompts of blind people
import speech_recognition as sr
#Imported to run multiple scripts at once
import threading
#Making python speak
import pyttsx3

#Kivy App frontend components
from kivy.app import App;
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.camera import Camera

sm = ScreenManager()
r = sr.Recognizer()

def listen_for_voice():
    while True:
        with sr.Microphone() as mic:
            try:
                r.adjust_for_ambient_noise(mic, duration=0.2)
                audio = r.listen(mic)
                text = r.recognize_google(audio)
                text = text.lower() #to ensure nothing interesting happens when comparing text
                print(text)
            except:
                print("Could not understand voice")
                pass
#camera = cv2.VideoCapture(0) #0 means to use the default camera

def changeScreen(name):
     sm.current = name


class MainApp(App):
    def build(self):
        home_page = ChatScreen(name = 'main')
        obstacle_detection = CameraScreen(name='obstacle_detection')
        sm.add_widget(obstacle_detection)
        sm.add_widget(home_page)
        sm.current = 'main'
        return sm
    def on_request_close(self, **kwargs):
        App.get_running_app().stop()
class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) #Makes sure we don't override kivy's code 
        camera = Camera(play=True)
        self.add_widget(camera)


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
        # translate_button = Button(text="Translate Sign Language")
        # translate_button.bind(on_press = changeScreen("translate_sign_language"))
        # chat.add_widget(translate_button)
        #chat.add_widget()
        #obstacle_button.bind(on_press = changeScreen("obstacle_detection"))
        home_page.add_widget(chat)
        self.add_widget(home_page)

if __name__ == "__main__":
    
    voice_thread = threading.Thread(target=listen_for_voice, args=(), daemon=True)
    voice_thread.start()
    MainApp().run()