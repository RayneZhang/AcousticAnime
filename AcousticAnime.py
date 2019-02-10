import click
from src.RecordAudio import RecordAudio

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