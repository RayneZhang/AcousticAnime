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
    