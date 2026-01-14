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
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDRaisedButton
from kivy.uix.widget import Widget



class RoundedButton(MDRaisedButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint_x=1
        self.size_hint_y=1

        self.md_bg_color = (0.4, 0.6, 1, 1)
        self.text_color = (1, 1, 1, 1)

        self.radius = [40, 40, 40, 40]

        self.font_style = "Button"
        self.font_size = 30

        self.padding = [10, 10]

       


class MainApp(MDApp):
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
        self.background_normal=""
        self.background_color=(0.4, 0.6, 1, 1)
        self.font_size=35
        self.font_style="Button"

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            Color(0.05, 0.1, 0.2, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self.update_bg, size=self.update_bg)
        
    def update_bg(self, *args):
        self.bg_rect.pos=self.pos
        self.bg_rect.size=self.size


class CameraScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) #Makes sure we don't override kivy's code 
        camera_layout = GridLayout(cols=1)
        camera = Camera(play=True, resolution=(640,480))
        camera_layout.add_widget(camera)
        back_button = BackButton()
        camera_layout.add_widget(back_button)
        self.add_widget(camera_layout)

class ChatScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        home_page = Screen(name = self.name)
        chat = GridLayout(cols=1)

        chat.add_widget(Widget(size_hint_y=None, height=30))
        # chat.add_widget(Label(text="Welcome to Clarity! How can we help you?"))
        chat.add_widget(
            MDCard(
                orientation="vertical",
                padding=15,
                size_hint_y=None,
                pos_hint={"right": 1},
                height=100,
                radius=[20, 20, 20, 20],
                md_bg_color=(0.3, 0.5, 1, 1),
                elevation=5
            )
        )
        chat.children[0].add_widget(
            MDLabel(
                text="Welcome to Clarity! How can we help you?",
                halign="left",
                font_style="H6",
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1)
            )
        )
        chat.add_widget(Label())
        obstacle_button = RoundedButton(text="Obstacle Detection")
        obstacle_button.bind(on_press = lambda instance: changeScreen('obstacle_detection'))
        chat.add_widget(obstacle_button)
        translate_button = RoundedButton(text="Transcription")
        translate_button.bind(on_press = lambda instance:changeScreen('transcript'))
        chat.add_widget(translate_button)
        self.add_widget(chat)


class TranscriptScreen(BaseScreen):
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