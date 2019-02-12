import pyaudio
import wave
import click
import os
import time
import numpy as np
import matplotlib.pyplot as pyplot

from scipy.signal.windows import blackmanharris
from scipy.fftpack import rfft

import pygame as pg

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
                self.freq_from_fft(p)
                # time.sleep(0.1)
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
            a_down_event = pg.event.Event(pg.KEYDOWN, key=pg.K_a)
            pg.event.post(a_down_event)
            print('Tap detected!')
            time.sleep(0.2)
            a_up_event = pg.event.Event(pg.KEYUP, key=pg.K_a)
            pg.event.post(a_up_event)
        # end_time = time.time()
        # print(end_time - start_time) # 0.00015s

    # freq_from_fft is adapted from https://gist.github.com/endolith/255291
    def freq_from_fft(self, p):
        """
        Estimate frequency from peak of FFT
        """
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
        # print(fs * true_i / len(windowed))
        # return fs * true_i / len(windowed)

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
