import logging

from mopidy import core

import pykka

logger = logging.getLogger(__name__)


class FavouriteButtons(pykka.ThreadingActor, core.CoreListener):

    def __init__(self, config, core):
        super(FavouriteButtons, self).__init__()
        self.playlist = config.get('favourite-buttons')['playlist']
        self.core = core
        self.gpio_manager = GPIOManager(self, config)
    

class GPIOManager():

    def __init__(self, frontend, pins):
        self.frontend = frontend
