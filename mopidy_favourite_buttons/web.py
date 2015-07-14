import logging
import os
import tornado.web
import jinja2

from mopidy import core

template_file = os.path.join(os.path.dirname(__file__), 'index.html')

logger = logging.getLogger(__name__)

class WebFavouritesRequestHandler(tornado.web.RequestHandler):

    def initialize(self, core, config):
        self.playlist = config.get('favourite-buttons')['playlist']
        self.core = core

    def get(self):
        templateLoader = jinja2.FileSystemLoader( searchpath = "/" )
        templateEnv = jinja2.Environment( loader=templateLoader )
        template = templateEnv.get_template(template_file)
        error = ''
        
        model = {
            "error": error,
            "playlists": self.core.playlists.as_list().get()
        }

        tracks = self.core.playlists.get_items("m3u:Buttons.m3u").get()

        if tracks:
            if len(tracks) > 0:
                model["mw_name"] = tracks[0].name
                model["mw_uri"] = tracks[0].uri
                
            if len(tracks) > 1:
                model["lw_name"] = tracks[1].name
                model["lw_uri"] = tracks[1].uri
                
            if len(tracks) > 2:
                model["vhf_name"] = tracks[2].name
                model["vhf_uri"] = tracks[2].uri

        self.write(template.render ( model ) )

        
    def post(self):
        error = ''

        f = open(self.playlist, "w")
        f.write("#EXTM3U\n")
        f.write("\n")
        f.write("#EXTINF:1000," + self.get_argument("mw_name", "NOT SET") + "\n")
        f.write(self.get_argument("mw_uri", "file:///music/not-set.mp3") + "\n")
        f.write("#EXTINF:1000," + self.get_argument("lw_name", "NOT SET") + "\n")
        f.write(self.get_argument("lw_uri", "file:///music/not-set.mp3") + "\n")
        f.write("#EXTINF:1000," + self.get_argument("vhf_name", "NOT SET") + "\n")
        f.write(self.get_argument("vhf_uri", "file:///music/not-set.mp3") + "\n")
        f.close()

        self.core.playlists.refresh("m3u")

        self.get()
