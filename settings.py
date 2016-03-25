#!/usr/bin/env python
# -*- coding: utf8 -*-

from os import path, getenv
from sys import exit
import ConfigParser
import logging
from UserDict import IterableUserDict

CONFIG_DIR = 'rids_assets'
CONFIG_FILE = 'rids.conf'
DEFAULTS = {
    'main': {
        'database': CONFIG_DIR + '/schedule.txt',
        'listen': '0.0.0.0:8080',
        'assetdir': CONFIG_DIR,
        'tweets':'/home/pi/rids_files/tweets.txt',
        'feeds':'/home/pi/rids_files/feeds.txt',
        'ipaddr':'/home/pi/rids_files/ipaddr.txt',
    },
    'viewer': {
        'show_splash': True,
        'audio_output': 'hdmi',
        'shuffle_playlist': False,
        'resolution': '1920x1080',
        'default_duration': '10',
        'debug_logging': False,
        'verify_ssl': True,
        'split_screen': '1',
        'outer_space':'0',
        'inner_space':'5',
        'video_split_screen':'P',
        'border_width':'2',
        'split_type':0,
        'left_width':50,
        'upper_height':50,
        'main_bg':'#ecf0f1',
        'display_rotate':0,
        'rids_x':95,
        'rids_y':95,
        'rids_logo':'/home/pi/ridsc/static/img/rids_boot.png',
        'is_enabled':True,
        'show_days':"1111111",
    },
    'tickr': {
        'clock_color': '#ecf0f1',
        'ticker_color': '#ecf0f1',
        'clock_format': '12',
        'ticker_height': '9',
        'clock_bg': '#34495e',
        'ticker_bg': '#34495e',
        'ticker_font_size':30,
        'ticker_font':'orbitron.woff',
        'ticker_speed': 4,
        'show_ticker':True,
    },
    'sidebar':{
        'sidebar_color':'#ecf0f1',
        'sidebar_width':'25',
        'sidebar_font_size':'32',
        'sidebar_font':'lato.ttf',
        'sidebar_bg':'#2980b9',
        'show_sidebar':True,
        'institute_logo':'/home/pi/ridsc/static/img/rids_boot.png',
    },
    'twitter':{
        'show_twitter_on':'N',
        'twitter_handle':'@ridstechnology',
        'no_of_tweets':10,
    },
    'rss_feed':{
        'rss_url':'http://www.thehindu.com/?service=rss',
        'show_rss_on':'N',
        'no_of_feeds':5,
    }

}

# Initiate logging
logging.basicConfig(level=logging.INFO,
                    filename='/tmp/rids_viewer.log',
                    format='%(asctime)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')

# Silence urllib info messages ('Starting new HTTP connection')
# that are triggered by the remote url availability check in view_web
requests_log = logging.getLogger("requests")
requests_log.setLevel(logging.WARNING)
    
logging.debug('Starting viewer.py')


class RIDSSettings(IterableUserDict):
    "RIDSC's Settings."

    def __init__(self, *args, **kwargs):
        rv = IterableUserDict.__init__(self, *args, **kwargs)
        self.home = getenv('HOME')
        self.conf_file = self.get_configfile()

        if not path.isfile(self.conf_file):
            logging.error('Config-file %s missing', self.conf_file)
            exit(1)
        else:
            self.load()
        return rv

    def _get(self, config, section, field, default):
        try:
            if isinstance(default, bool):
                self[field] = config.getboolean(section, field)
            elif isinstance(default, int):
                self[field] = config.getint(section, field)
            else:
                self[field] = config.get(section, field)
        except ConfigParser.Error as e:
            logging.debug("Could not parse setting '%s.%s': %s. Using default value: '%s'." % (section, field, unicode(e), default))
            self[field] = default
        if field in ['database', 'assetdir']:
            self[field] = str(path.join(self.home, self[field]))

    def _set(self, config, section, field, default):
        if isinstance(default, bool):
            config.set(section, field, self.get(field, default) and 'on' or 'off')
        else:
            config.set(section, field, unicode(self.get(field, default)))

    def load(self):
        "Loads the latest settings from rids.conf into memory."
        logging.debug('Reading config-file...')
        config = ConfigParser.ConfigParser()
        config.read(self.conf_file)

        for section, defaults in DEFAULTS.items():
            for field, default in defaults.items():
                self._get(config, section, field, default)
        try:
            self.get_listen_ip()
            int(self.get_listen_port())
        except ValueError as e:
            logging.info("Could not parse setting 'listen': %s. Using default value: '%s'." % (unicode(e), DEFAULTS['main']['listen']))
            self['listen'] = DEFAULTS['main']['listen']

    def save(self):
        # Write new settings to disk.
        config = ConfigParser.ConfigParser()
        for section, defaults in DEFAULTS.items():
            config.add_section(section)
            for field, default in defaults.items():
                self._set(config, section, field, default)
        with open(self.conf_file, "w") as f:
            config.write(f)
        self.load()

    def get_configdir(self):
        return path.join(self.home, CONFIG_DIR)

    def get_configfile(self):
        return path.join(self.home, CONFIG_DIR, CONFIG_FILE)

    def get_listen_ip(self):
        return self['listen'].split(':')[0]

    def get_listen_port(self):
        return self['listen'].split(':')[1]

settings = RIDSSettings()
