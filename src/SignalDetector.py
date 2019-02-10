import pyaudio
import wave
import click
import os
import time
import numpy as np
import matplotlib.pyplot as pyplot

class SignalDetector:
    def __init__(self, chunk=3024, frmat=pyaudio.paInt16, channels=1, rate=22050):
        self.CHUNK = chunk
        self.FORMAT = frmat
        self.CHANNELS = channels
        self.RATE = rate
        self.frames = []
        self.OUTPUT_FILENAME = "output.wav"

    def start_streaming(self):
        self.frames = []
        p=pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, 
                    channels=self.CHANNELS, 
                    rate=self.RATE, 
                    input=True, 
                    frames_per_buffer=self.CHUNK)

        try:
            print("* streaming started, press ctrl+c to stop")
            while True:
                self.frames = [] # Clear frames at each slice.
                data = stream.read(self.CHUNK) #0.135s
                self.frames.append(data)
                self.detect_tap(p)
        except KeyboardInterrupt:
            print("* streaming stopped")
        
        stream.close()
        p.terminate()

    def detect_tap(self, p, threshold=10000):
        # Debugging.
        # start_time = time.time()
        bits_per_sample = p.get_sample_size(self.FORMAT) * 8
        dtype = 'int{0}'.format(bits_per_sample)
        audio = np.frombuffer(b''.join(self.frames), dtype)
        if audio.max() > threshold:
            print('Tap detected!')
        # end_time = time.time()
        # print(end_time - start_time) # 0.00015s

if __name__ == '__main__':
    stream = SignalDetector()
    # Start looping, which will be indefinite until 'q' is pressed.
    running = True
    while running:

        print('''
            Press a key to perform that operation...
            s: start streaming audio and detect tap/scratch (ctrl+c to stop recording and save)
            q or Q: quit program
        ''')

        key = click.getchar()
        print(key)

        if key == 'q' or key == 'Q':
            running = False
        
        if key == 's':
            stream.start_streaming()
