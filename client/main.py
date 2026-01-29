#Window testing configs
from kivy.config import Config
Config.set('graphics', 'width', '320')
Config.set('graphics', 'height', '580')
import time
#Imported to run the camera
import cv2
#Imported to run multiple scripts at once
import threading
#Making python speak
import pyttsx3
#Recording audio for transcription
import pyaudio
import wave
#Checks for paths
import os
#Images to arrays so we don't need to save peoples photos
import numpy as np
#Python Image Processing
from PIL import Image as PILImg
#You Only Look Once, Fast Accurate Object Detection
from ultralytics import YOLO
#offline voice recognition
from faster_whisper import WhisperModel

#Kivy App frontend components
from kivy.lang import Builder
from kivy.app import App;
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.camera import Camera
from kivy.clock import mainthread, Clock
from kivy.graphics.texture import Texture
from kivy.uix.scrollview import ScrollView

CHUNK = 1024
FORMAT = pyaudio.paInt16 # 16-bit audio
CHANNELS = 1             # Mono
RATE = 44100             # Sample rate (common standard)
RECORD_SECONDS = 5       # Duration of recording
WAVE_OUTPUT_FILENAME = "output.wav"

sm = ScreenManager()
p = pyaudio.PyAudio()
speech_model_path = "./ggml-tiny.en.bin"
try:
    speech_model = WhisperModel("small.en", device="cpu", compute_type="int8")
    stream = None
except Exception as e:
    print(e)
obj_model = YOLO("yolov8n.pt")
left_right_object_sort = []
up_down_object_sort = []
class_ids_horizontal = []
class_ids_vertical = []
transcribing = False
tts_engine = pyttsx3.init()

def open_stream():
    global transcribing
    transcribing = True

def close_stream():
    global transcribing
    transcribing = False
class MainApp(App):
    def build(self):
        home_page = ChatScreen(name = 'main')
        sm.add_widget(obstacle_detection)
        sm.add_widget(home_page)
        sm.add_widget(transcript)
        sm.current = 'main'
        return sm
    def on_request_close(self, **kwargs):
        App.get_running_app().stop()
        stream.stop_stream()
        stream.close()
        p.terminate()
        
class BackButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "Back"
        self.bind(on_press = lambda instance: change_screen('main'))

class CameraScreen(Screen):
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

class ChatScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        home_page = Screen(name = self.name)
        chat = GridLayout(cols=1)
        chat.add_widget(Label(text="Welcome to Clarity! How can we help you?"))
        chat.add_widget(Label())
        obstacle_button = Button(text="Obstacle Detection")
        obstacle_button.bind(on_press = lambda instance: change_screen('obstacle_detection'))
        chat.add_widget(obstacle_button)
        translate_button = Button(text="Transcription")
        translate_button.bind(on_press = lambda instance:change_screen('transcript'))
        chat.add_widget(translate_button)
        self.add_widget(chat)

class TranscriptScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sub_layout = TextList(cols=1, size_hint_y=None)
        open_stream_button = Button(text="Transcribe")
        open_stream_button.bind(on_press=lambda instance: open_stream())
        close_stream_button = Button(text="Stop transcribing")
        close_stream_button.bind(on_press=lambda instance: close_stream())
        layout = GridLayout(cols=1)
        scroll_view = ScrollView(size_hint=(1,1))
        scroll_view.add_widget(self.sub_layout)
        layout.add_widget(scroll_view)
        layout.add_widget(open_stream_button)
        layout.add_widget(close_stream_button)
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
    global stream
    while True:
        if transcribing:
            try:
                stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

                frames = []

                for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                    data = stream.read(CHUNK)
                    frames.append(data)

                stream.stop_stream()
                stream.close()

                with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(frames))
                segments, info = speech_model.transcribe('output.wav', beam_size=1, best_of=1) #beam size: the # of stored possibilities
                for segment in segments:
                    print(segment.text)
                    transcript.sub_layout.add_message(segment.text)
                time.sleep(0.01)
            except Exception as e:
                print("Could not understand voice")
                print(e)
                pass

#camera = cv2.VideoCapture(0) #0 means to use the default camera
def analyze_image():
    global class_ids
    global confident_class_ids_vertical
    img_data = obstacle_detection.get_img_data()
    success, encoded_img = cv2.imencode('.jpg', img_data)
    decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
    results = obj_model(decoded_img)
    left_right_object_sort = []
    up_down_object_sort = []
    class_ids_vertical = []
    for result in results:
        xy_box_coordinates = result.boxes.xyxy.cpu().numpy()
        xywh_box_coordinates = result.boxes.xyxy.cpu().numpy()
        j = 0
        for coordinates in xy_box_coordinates:
            left_right_object_sort.append(int(coordinates[0]))
            up_down_object_sort.append(int(xywh_box_coordinates[j][3]) + int(coordinates[1]))
            j += 1
        i = 0
        for box in result.boxes:
            item_dict = {'id': i, 'distance': up_down_object_sort[i], 'min_x': left_right_object_sort[i], 'name': obj_model.names[int(box.cls[0])], 'conf': f"{box.conf[0]:.2f}"}
            class_ids_vertical.append(item_dict)
            i += 1
        confident_class_ids_vertical = [item for item in class_ids_vertical if confidence(item)]
        class_ids = sort_distance(confident_class_ids_vertical)
        tts_engine.say(organize_for_speech(class_ids))
        tts_engine.runAndWait()

def confidence(item):
    return float(item['conf']) > 0.65

def organize_for_speech(array):
    text = "In front of you there is a "
    for item_list in array:
        for item in item_list:
            name = item['name']
            future_index = item_list.index(item) + 1
            if future_index < len(item_list):
                future_item = item_list[future_index]
            if item_list[-1] == item:
                if(array[-1] == item_list):
                    text += name + "."
                else:
                    text += name + ". "
            elif future_item['name'] == name:
                text += name + " next to another "
            else:
                text += name + " next to a "
        if not array[-1] == item_list:
            text += "Behind that is a "
    return text

def sort_distance(xy_list):
    class_ids = []
    used_list = []
    for i in range(len(xy_list)):
        if not xy_list[i] in used_list:
            class_ids.insert(i, [])
            temp_list = filter(lambda item: abs(xy_list[i]['distance'] - item['distance']) < 10, xy_list)
            for item in temp_list:
                class_ids[i].append(item)
                used_list.append(item)
    for i in range(len(class_ids)):
        class_ids[i - 1] = sorted(class_ids[i - 1], key=lambda item: item['min_x'])
    return class_ids


def change_screen(name):
    sm.current = name

if __name__ == "__main__":
    voice_thread = threading.Thread(target=listen_for_voice, args=(), daemon=True)
    voice_thread.start()
    MainApp().run()