import pyaudio
import wave
import click
import os
import numpy as np
import matplotlib.pyplot as pyplot

class RecordAudio:
    def __init__(self, chunk=3024, frmat=pyaudio.paInt16, channels=1, rate=22050):
        self.CHUNK = chunk
        self.FORMAT = frmat
        self.CHANNELS = channels
        self.RATE = rate
        self.frames = []
        self.OUTPUT_FILENAME = "output.wav"

    def start_record(self):
        self.frames = []
        p=pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, 
                    channels=self.CHANNELS, 
                    rate=self.RATE, 
                    input=True, 
                    frames_per_buffer=self.CHUNK)

        try:
            print("* recording started, press ctrl+c to stop")
            while True:
                data = stream.read(self.CHUNK)
                self.frames.append(data)
        except KeyboardInterrupt:
            print("* recording stopped, save to {}".format(self.OUTPUT_FILENAME))
        
        stream.close()
        p.terminate()

        # Debugging.
        bits_per_sample = p.get_sample_size(self.FORMAT) * 8
        print(bits_per_sample)
        dtype = 'int{0}'.format(bits_per_sample)
        audio = np.frombuffer(b''.join(self.frames), dtype)
        print(audio.max())

        wf = wave.open(self.OUTPUT_FILENAME, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def play_record(self):
        wf = wave.open(self.OUTPUT_FILENAME, 'rb')

        p=pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
        
        data = wf.readframes(self.CHUNK)

        print("* replaying clip")
        while data:
            stream.write(data)
            data = wf.readframes(self.CHUNK)

        stream.close()
        p.terminate()

    def read_audio(self, filename):
        wf = wave.open(filename, 'rb')
        nframes = wf.getnframes()
        duration = nframes / float(self.RATE)
        bytes_per_sample = wf.getsampwidth()
        bits_per_sample = bytes_per_sample * 8
        dtype = 'int{0}'.format(bits_per_sample)
        audio = np.frombuffer(wf.readframes(int(duration*self.RATE*bytes_per_sample/self.CHANNELS)), dtype=dtype)

        return audio, duration, nframes

    def dB(self, a, base=1.0):
        return 10.0*np.log10(a/base)

    def display_record(self):
        audio, duration, frames = self.read_audio(self.OUTPUT_FILENAME)
        fs = self.RATE
        audio_fft = np.fft.fft(audio)
        freqs = np.fft.fftfreq(audio.shape[0], 1.0/fs) / 1000.0
        max_freq_kHz = freqs.max()

        fig = pyplot.figure(figsize=(8.5, 11))
        ax_time = fig.add_subplot(311)
        ax_spec_gram = fig.add_subplot(312)
        ax_fft = fig.add_subplot(313)
        pyplot.gcf().subplots_adjust(bottom=0.2)

        ax_time.plot(np.arange(frames)/self.RATE, audio/audio.max())
        ax_time.set_xlabel('Time (s)')
        ax_time.set_ylabel('Relative amplitude')
        ax_time.set_xlim(0, duration)

        ax_spec_gram.specgram(audio, Fs=fs, cmap='jet')
        ax_spec_gram.set_xlim(0, duration)
        ax_spec_gram.set_ylim(0, max_freq_kHz*1000.0)
        ax_spec_gram.set_ylabel('Frequency (Hz)')
        ax_spec_gram.set_xlabel('Time (s)')

        # ax_fft.plot(np.fft.fftshift(freqs), np.fft.fftshift(self.dB(audio_fft)))
        # ax_fft.set_xlim(0, max_freq_kHz)
        # ax_fft.set_xlabel('Frequency (kHz)')
        # ax_fft.set_ylabel('dB')

        ax_fft.plot(np.arange(frames)/self.RATE, audio)
        ax_fft.set_xlim(0, duration)
        ax_fft.set_xlabel('Time (s)')
        ax_fft.set_ylabel('Amplitude')

        pyplot.tight_layout()
        pyplot.show()

if __name__ == '__main__':
    record = RecordAudio()
    # Start looping, which will be indefinite until 'q' is pressed.
    running = True
    while running:

        print('''
            Press a key to perform that operation...
            r: record audio and save to file (ctrl+c to stop recording and save)
            p: replay audio file
            d: display the spectrogram of the audio file
            q or Q: quit program
        ''')

        key = click.getchar()
        print(key)

        if key == 'q' or key == 'Q':
            running = False
        
        if key == 'r':
            record.start_record()
            
        if key == 'p':
            record.play_record()

        if key == 'd':
            record.display_record()
