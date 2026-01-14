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
#offline quick speech recognition
import vosk
#Checks for paths
import os
#Images to arrays so we don't need to save peoples photos
import numpy as np
#Python Image Processing
from PIL import Image as PILImg
#You Only Look Once, Fast Accurate Object Detection
from ultralytics import YOLO

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
from kivy.clock import mainthread, Clock
from kivy.graphics.texture import Texture



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

path = "../venv/Lib/site-packages/speech_recognition/vosk"
sm = ScreenManager()
r = sr.Recognizer()
r.vosk_model_path = path
model = YOLO("yolov8n.pt")

class MainApp(MDApp):
    def build(self):
        home_page = ChatScreen(name = 'main')
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
        self.bind(on_press = lambda instance: change_screen('main'))
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
        self.camera = Camera(play=True, resolution=(640,480))
        camera_layout.add_widget(self.camera)
        analyze_button = Button(text="Describe_Image")
        analyze_button.bind(on_press = lambda instance: analyze_image())
        camera_layout.add_widget(analyze_button)
        back_button = BackButton()
        camera_layout.add_widget(back_button)
        self.add_widget(camera_layout)
    def get_img_data(self, **kwargs):
        texture = self.camera.texture
        if texture:
            raw_rgba_img = PILImg.frombytes("RGBA", size=texture.size, data=texture.pixels) 
            frame = np.array(raw_rgba_img)
            raw_bgra_frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)#BGRA stands for Blue, Green, Red, Alpha. It's like RGB, but more compatible with opencv(image processing)
            return raw_bgra_frame
        else:
            return

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
        obstacle_button.bind(on_press = lambda instance: change_screen('obstacle_detection'))
        chat.add_widget(obstacle_button)
        translate_button = RoundedButton(text="Transcription")
        translate_button.bind(on_press = lambda instance:change_screen('transcript'))
        chat.add_widget(translate_button)
        self.add_widget(chat)


class TranscriptScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sub_layout = TextList(cols=1)
        layout = GridLayout(cols=1)
        layout.add_widget(self.sub_layout)
        layout.add_widget(BackButton())
        self.add_widget(layout)
    
class TextList(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    @mainthread
    def add_message(self, message):
        text = Label(text=message)
        self.add_widget(text)
        return True

transcript = TranscriptScreen(name='transcript')
obstacle_detection = CameraScreen(name='obstacle_detection')

def listen_for_voice():
    with sr.Microphone() as mic:
        r.adjust_for_ambient_noise(mic, duration=1)
        r.pause_threshold = 1
        while True:
            try:
                audio = r.listen(mic, 10)
                text = r.recognize_vosk(audio)
                text = text.lower() #to ensure nothing interesting happens when comparing text
                transcript.sub_layout.add_message(text)
            except sr.WaitTimeoutError:
                print("Nothing has been said for a while. Would you like to stop?")
            except Exception as e:
                print("Could not understand voice")
                print(e)
                pass

#camera = cv2.VideoCapture(0) #0 means to use the default camera
def analyze_image():
    img_data = obstacle_detection.get_img_data()
    success, encoded_img = cv2.imencode('.jpg', img_data)
    decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
    results = model(decoded_img)
    for result in results:
        for box in result.boxes:
            print("CLS: ", result.names[int(box.cls)])
        print("LEN: ", len(result.boxes))


def change_screen(name):
     sm.current = name

if __name__ == "__main__":
    voice_thread = threading.Thread(target=listen_for_voice, args=(), daemon=True)
    voice_thread.start()
    MainApp().run()