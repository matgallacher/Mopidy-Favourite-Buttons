import logging
import RPi.GPIO as GPIO
import sys

from mopidy import core

import pykka

logger = logging.getLogger(__name__)


class FavouriteButtons(pykka.ThreadingActor, core.CoreListener):

    def __init__(self, config, core):
        super(FavouriteButtons, self).__init__()
        self.playlist = config.get('favourite-buttons')['playlist']
        self.core = core
        self.gpio_manager = GPIOManager(self, core, config)
    	
    def playback_state_changed(self, old_state, new_state):
        self.gpio_manager.set_led(new_state)

class GPIOManager():

    def __init__(self, frontend, core, pins):
        self.frontend = frontend
        self.pressed = 0
        self.core = core
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            GPIO.add_event_detect(4, GPIO.FALLING, callback=self.click_channel, bouncetime=300)

            GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            GPIO.add_event_detect(18, GPIO.FALLING, callback=self.click_channel, bouncetime=300)

            GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            GPIO.add_event_detect(24, GPIO.FALLING, callback=self.click_channel, bouncetime=300)

            GPIO.setup(14, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            GPIO.add_event_detect(14, GPIO.FALLING, callback=self.click_on_off, bouncetime=1500)

            GPIO.setup(7, GPIO.IN, pull_up_down = GPIO.PUD_UP)
            GPIO.add_event_detect(7, GPIO.FALLING, callback=self.click_on_off, bouncetime=1500)

            GPIO.setup(13, GPIO.OUT)
            self.red = GPIO.PWM(13, 500)
            self.red.start(100)

            GPIO.setup(16, GPIO.OUT)
            self.green = GPIO.PWM(16, 500)
            self.green.start(0)

            GPIO.setup(19, GPIO.OUT)
            self.blue = GPIO.PWM(19, 500)
            self.blue.start(0)

        except RuntimeError, re:
            logger.exception(re)

    def click_on_off(self, channel):
        logger.info('Detected click ' + str(channel))
        if channel == 14:
            self.core.playback.previous()
        elif channel == 7:
            self.core.playback.next()


    def click_channel(self, channel):
        logger.debug('Detected click ' + str(channel))

        if self.pressed != channel:
            self.pressed = channel
            
            logger.info('Switched to ' + str(self.pressed))
            playlists = self.core.playlists.as_list().get()

            tracks = self.core.playlists.get_items('m3u:Buttons.m3u').get()
            uri = ""

            if tracks:
                if channel == 4 and len(tracks) > 0:
                    uri = tracks[0].uri
                    
                elif channel == 18 and len(tracks) > 1:
                    uri = tracks[1].uri

                elif channel == 24 and len(tracks) > 2:
                    uri = tracks[2].uri

                else:
                    logger.warn('No track found for channel ' + str(channel))
            
            else:
                logger.warn('No tracks found')
            
            if uri != "":
                try:
                    logger.info('Starting to play ' + uri)
                    self.core.tracklist.clear().get(timeout = 5)
                    self.core.tracklist.add(None,None,None,[uri]).get(timeout = 5)
                    self.core.playback.play()
                    logger.debug('Started')

                except Exception, e:
                    logger.exception(e)

    def set_led(self, state):
        logger.info('Detected state change ' + str(state))
        if state != core.PlaybackState.PLAYING:
            self.green.ChangeDutyCycle(0)
            self.red.ChangeDutyCycle(100)
        else:
            self.green.ChangeDutyCycle(100)
            self.red.ChangeDutyCycle(0)
