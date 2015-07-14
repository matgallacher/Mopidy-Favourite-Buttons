from __future__ import unicode_literals

import os

import logging

from mopidy import config, ext


__version__ = '0.1.0'

# TODO: If you need to log, use loggers named after the current Python module
logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = 'Mopidy-Favourite-Buttons'
    ext_name = 'favourite-buttons'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['playlist'] = config.String()
        return schema

    def setup(self, registry):
        from .frontend import FavouriteButtons
        registry.add('frontend', FavouriteButtons)

        registry.add('http:app', {
            #'name': self.ext_name,
            'name': 'favourite-buttons',
            'factory': websettings_app_factory,
        })


def websettings_app_factory(config, core):
    from .web import WebFavouritesRequestHandler
    return [
        ('/', WebFavouritesRequestHandler, {'core': core, 'config': config})
    ]
