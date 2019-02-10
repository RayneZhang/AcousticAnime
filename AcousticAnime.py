import click
from src.RecordAudio import RecordAudio
from src.SignalDetector import SignalDetector

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