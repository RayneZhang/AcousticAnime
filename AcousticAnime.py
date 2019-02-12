import click
from src.RecordAudio import RecordAudio
from src.SignalDetector import SignalDetector

import sys
import pygame as pg
from src.vendor.Pygame.data.main import main

import multiprocessing
import threading

def start_streaming():
    stream = SignalDetector()
    stream.start_streaming()

def start_gaming():
    main()
    pg.quit()

if __name__ == '__main__':
    t1 = threading.Thread(target=start_streaming)
    t1.start()
    # t1.join()
    start_gaming()
    

# if __name__ == '__main__':
#     main()
#     pg.quit()

#     stream = SignalDetector()
#     # Start looping, which will be indefinite until 'q' is pressed.
#     running = True
#     while running:

#         print('''
#             Press a key to perform that operation...
#             s: start streaming audio and detect tap/scratch (ctrl+c to stop streaming)
#             q or Q: quit program
#         ''')

#         key = click.getchar()
#         print(key)

#         if key == 'q' or key == 'Q':
#             running = False
        
#         if key == 's':
#             stream.start_streaming()