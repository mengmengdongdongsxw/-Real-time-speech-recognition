
import Speech_Recognition

def audio() :
    file_path = r"音频存储位置input.wav"
    client = Speech_Recognition.Client()
    client.send(file_path)
audio()