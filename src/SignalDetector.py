import pyaudio
import wave
import click
import os
import time
import numpy as np
import matplotlib.pyplot as pyplot
import pygame as pg
import aubio

from scipy.signal.windows import blackmanharris
from scipy.fftpack import rfft

from src.EventGenerator import EventGenerator

class SignalDetector:
    def __init__(self, chunk=1024, frmat=pyaudio.paFloat32, channels=1, rate=22050):
        self.CHUNK = chunk
        self.FORMAT = frmat
        self.CHANNELS = channels
        self.RATE = rate
        self.frames = []
        self.OUTPUT_FILENAME = "output.wav"
        self.tap_started_time = 0
        self.scratch_started_time = 0
        self.back_started_time = 0
        self.scratching = False
        self.backing = False

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
                data = stream.read(self.CHUNK, exception_on_overflow = False) #0.135s
                self.frames.append(data)
                self.detect_tap(p)
                self.detect_pitch(p, data)
                # self.freq_from_fft(p)

                if self.tap_started_time != 0 and time.time() - self.tap_started_time > 0.5:
                    a_up_event = pg.event.Event(pg.KEYUP, key=pg.K_a)
                    pg.event.post(a_up_event)
                if self.scratch_started_time != 0 and time.time() - self.scratch_started_time > 0.2:
                    arrow_up_event = pg.event.Event(pg.KEYUP, key=pg.K_RIGHT)
                    pg.event.post(arrow_up_event)
                    self.scratching = False
                if self.back_started_time != 0 and time.time() - self.back_started_time > 0.2:
                    arrow_up_event = pg.event.Event(pg.KEYUP, key=pg.K_LEFT)
                    pg.event.post(arrow_up_event)
                    self.backing = False
        except KeyboardInterrupt:
            print("* streaming stopped")
        
        stream.close()
        p.terminate()

    def detect_tap(self, p, threshold=0.5):
        # Debugging.
        # start_time = time.time()
        bits_per_sample = p.get_sample_size(self.FORMAT) * 8
        dtype = 'float{0}'.format(bits_per_sample)
        audio = np.frombuffer(b''.join(self.frames), dtype)
        if audio.max() > threshold:
            a_down_event = pg.event.Event(pg.KEYDOWN, key=pg.K_a)
            pg.event.post(a_down_event)
            self.tap_started_time = time.time()
            print('Tap detected!')               
        # print(audio.max())
        # end_time = time.time()
        # print(end_time - start_time) # 0.00015s

    # Reference: https://github.com/aubio/aubio/issues/6
    def detect_pitch(self, p, data):
        # Aubio's pitch detection.
        pDetection = aubio.pitch("default", 4096,
            1024, self.RATE)
        # Set unit.
        pDetection.set_unit("Hz")
        pDetection.set_tolerance(0.8)

        samples = np.fromstring(data,
                    dtype=aubio.float_type)
        pitch = pDetection(samples)[0]
        confidence = pDetection.get_confidence()
        print("{} / {}".format(pitch,confidence))
        if pitch > 700 and pitch < 1000:
            if self.scratching == False:
                arrow_down_event = pg.event.Event(pg.KEYDOWN, key=pg.K_RIGHT)
                pg.event.post(arrow_down_event)
                self.scratching = True
            self.scratch_started_time = time.time()
            # print(self.scratch_started_time) # Debugging
            print('Scratch detected!')
        if pitch > 4000 and confidence > 0.6 :
            if self.backing == False:
                arrow_down_event = pg.event.Event(pg.KEYDOWN, key=pg.K_LEFT)
                pg.event.post(arrow_down_event)
                self.backing = True
            self.back_started_time = time.time()
            # print(self.scratch_started_time) # Debugging
            print('Back detected!')


    # freq_from_fft is adapted from https://gist.github.com/endolith/255291
    def freq_from_fft(self, p, threshold=5000):
        """
        Estimate frequency from peak of FFT
        """
        # Debugging.
        # start_time = time.time()
        bits_per_sample = p.get_sample_size(self.FORMAT) * 8
        dtype = 'int{0}'.format(bits_per_sample)
        sig = np.frombuffer(b''.join(self.frames), dtype)
        fs = self.RATE

        # Compute Fourier transform of windowed signal
        windowed = sig * blackmanharris(len(sig))
        f = rfft(windowed)

        # Find the peak and interpolate to get a more accurate peak
        i = np.argmax(abs(f))  # Just use this for less-accurate, naive version
        true_i = self.parabolic(np.log(abs(f)), i)[0]

        # Convert to equivalent frequency
        if (fs * true_i / len(windowed)) > threshold:
            if self.scratching == False:
                print("Sent message!")
                arrow_down_event = pg.event.Event(pg.KEYDOWN, key=pg.K_RIGHT)
                pg.event.post(arrow_down_event)
                self.scratching = True
            self.scratch_started_time = time.time()
            # print(self.scratch_started_time) # Debugging
            print('Scratch detected!')
        print(fs * true_i / len(windowed))
        # end_time = time.time()
        # print(end_time - start_time) 

    def parabolic(self,f, x):
        """Quadratic interpolation for estimating the true position of an
        inter-sample maximum when nearby samples are known.
    
        f is a vector and x is an index for that vector.
    
        Returns (vx, vy), the coordinates of the vertex of a parabola that goes
        through point x and its two neighbors.
    
        Example:
        Defining a vector f with a local maximum at index 3 (= 6), find local
        maximum if points 2, 3, and 4 actually defined a parabola.
    
        In [3]: f = [2, 3, 1, 6, 4, 2, 3, 1]
    
        In [4]: parabolic(f, argmax(f))
        Out[4]: (3.2142857142857144, 6.1607142857142856)
    
        """
        xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
        yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
        return (xv, yv)

if __name__ == '__main__':
    stream = SignalDetector()
    # Start looping, which will be indefinite until 'q' is pressed.
    running = True
    while running:

        print('''
            Press a key to perform that operation...
            s: start streaming audio and detect tap/scratch (ctrl+c to stop streaming)
            q or Q: quit program
        ''')

        key = click.getchar()
        print(key)

        if key == 'q' or key == 'Q':
            running = False
        
        if key == 's':
            stream.start_streaming()
