import time
import pygame as pg

class EventGenerator():
    def jumpEvent(self):
        a_down_event = pg.event.Event(pg.KEYDOWN, key=pg.K_a)
        pg.event.post(a_down_event)
        time.sleep(0.1)
        a_up_event = pg.event.Event(pg.KEYUP, key=pg.K_a)
        pg.event.post(a_up_event)
        