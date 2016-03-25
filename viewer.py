#!/usr/bin/env python
# -*- coding: utf8 -*-

__author__ = "Shashank Singla"
__copyright__ = "Copyright 2014, RIDS Technology"
__email__ = "shashank@rids.in"

from datetime import datetime, timedelta
from os import path, getenv, utime,system
from platform import machine
from requests import get as req_get
from time import sleep, time
import json
from signal import signal, SIGUSR1, SIGUSR2
import logging
import sh
from subprocess import check_output,Popen
from settings import settings
import html_templates
from utils import url_fails,get_node_ip
import assets_helper
from init_rsync import generate_rsync_file
from install_id import INSTALLATION_ID
import itertools
from version import VERSION
from api_url import RCA

SPLASH_DELAY = 10  # secs
EMPTY_PL_DELAY = 5  # secs

BLACK_PAGE = '/tmp/rids_html/black_page.html'
TICKER_SIDEBAR_PAGE = '/tmp/rids_html/ticker_sidebar_page.html'
SPLASH_PAGE = '/tmp/rids_html/splash_page.html'
WATCHDOG_PATH = '/tmp/rids.watchdog'
RIDS_HTML = '/tmp/rids_html/'
LOAD_SCREEN = '/ridsc/loading.jpg'  # relative to $HOME
UZBLRC = '/ridsc/misc/uzbl.rc'  # relative to $HOME

current_browser_url = None
browser = None
ticker_browser = None
sidebar_browser = None
full_browser = None
spec = {}
div_dic = {}
run = None
video_lock = False
VIDEO_TIMEOUT=20  # secs

def sigusr1(signum, frame):
    """
    The signal interrupts sleep() calls, so the currently playing web or image asset is skipped.
    omxplayer is killed to skip any currently playing video assets.
    """
    logging.info('USR1 received, skipping.')
    sh.killall('omxplayer.bin', _ok_code=[1])


def sigusr2(signum, frame):
    """Reload settings"""
    logging.info("USR2 received, reloading settings.")
    load_settings()


class Scheduler(object):
    def __init__(self, *args, **kwargs):
        logging.debug('Scheduler init')
        self.update_playlist()

    def get_next_asset(self,playlist_id):
        logging.debug('get_next_asset')
        self.refresh_playlist()
       
        if self.nassets[playlist_id] == 0:
            return None
        
        idx = self.index[playlist_id]
        
        if self.index[playlist_id]+1 == self.nassets[playlist_id]:
            self.counter[playlist_id] = (self.counter[playlist_id]+1)%12
        self.index[playlist_id] = (self.index[playlist_id] + 1) % self.nassets[playlist_id]

        logging.debug('Playlist %s: get_next_asset counter %s returning asset %s of %s', playlist_id, self.counter[playlist_id], idx + 1, self.nassets[playlist_id])

        return self.assets[playlist_id][idx]       


    def refresh_playlist(self):
        logging.debug('refresh_playlist')
        time_cur = datetime.utcnow()
        logging.debug('refresh: counter: (%s) deadline (%s) timecur (%s)', str(self.counter), self.deadline, time_cur)
        
        if self.get_db_mtime() > self.last_update_db_mtime:
            logging.debug('updating playlist due to database modification')
            self.update_playlist()            
        
        elif self.deadline and self.deadline <= time_cur:
            self.update_playlist()

        elif self.get_tw_mtime() > self.last_update_tw_mtime :
            logging.info('updating tweets due to tweets modification')
            self.update_playlist()

        elif self.get_fd_mtime() > self.last_update_fd_mtime :
            logging.info('updating feeds due to feeds modification')
            self.update_playlist()

        elif self.get_ip_mtime() > self.last_update_ip_mtime :
            logging.info('updating ipaddr due to ipaddr modification')
            self.update_playlist()

    def is_mediatype(self,mediatype,broadtype,location):
        if(mediatype[0]==broadtype and mediatype[2] in location):
            return True
        else:
            return False

    def is_not_mediatype(self,mediatype,broadtype,location):
        if mediatype[1] == "V":
            return True if settings['video_split_screen'] in location else False

        if(mediatype[0]!=broadtype and mediatype[2] in location):
            return True
        else:
            return False

    def update_playlist(self):
        split_map = ["P","S","T"]
        logging.debug('update_playlist')
        self.last_update_db_mtime = self.get_db_mtime()
        self.last_update_tw_mtime = self.get_tw_mtime()
        self.last_update_fd_mtime = self.get_fd_mtime()
        self.last_update_ip_mtime = self.get_ip_mtime()

        (self.assets, self.deadline) = generate_asset_list()
        self.counter = [0] * int(settings['split_screen']) #,0,0]
        self.index   = [0] * int(settings['split_screen']) #[0,0,0]
        now = int(time())
        self.go_next = [now ]* int(settings['split_screen']) #[0]
        
        ticker_content = "<span class='star'> &nbsp;*&nbsp; </span>".join([asset['ticker_content'] for asset in self.assets if self.is_mediatype(asset['media_type'],'T',['T','B'])])
        sidebar_content = "<|>".join([asset['ticker_content'] for asset in self.assets if self.is_mediatype(asset['media_type'],'T',['S','B'])])
        
        self.assets = [[asset for asset in self.assets if self.is_not_mediatype(asset['media_type'],'T',[split_map[i]]) ] for i in range(int(settings['split_screen']))]

        self.nassets = [len(a) for a in self.assets]

        # fetching link name from asset media type
        self.links = [[str(asset['name']) for asset in arr if asset['media_type'] == 'OLP' or asset['media_type'] == 'OLS' or asset['media_type'] == 'OLT' ] for arr in self.assets ]
        url_arr = [item for sublist in self.links for item in sublist]
        if len(url_arr):
            Popen(["/home/pi/ridsc/misc/download.sh %s" % "^".join(url_arr) ],shell=True)

        logging.debug('update_playlist done, count %s, counter %s, index %s,go_next %s, deadline %s', str(self.nassets), str(self.counter), str(self.index),str(self.go_next), self.deadline)
        logging.debug('updating ticker and sidebar now')

        if settings['show_twitter_on'] == 'S':
            tweets = "<|>".join(get_tweets())
            sidebar_content = sidebar_content +"<|>"+ tweets
        elif settings['show_twitter_on'] == 'T':
            tweets = "<span class='star'> &nbsp;*&nbsp; </span>".join(get_tweets())
            ticker_content = ticker_content + "<span class='star'> &nbsp;*&nbsp; </span>" + tweets

        if settings['show_rss_on'] == 'S':
            feeds = "<|>".join(get_feeds())
            sidebar_content = sidebar_content +"<|>"+ feeds

        elif settings['show_rss_on'] == 'T' :
            feeds = "<span class='star'> &nbsp;*&nbsp; </span>".join(get_feeds())
            ticker_content = ticker_content +"<span class='star'> &nbsp;*&nbsp; </span>"+ feeds

        set_sidebar_ticker(sidebar_content, ticker_content)

    def get_db_mtime(self):
        # get schedule.txt file last modification time
        try:
            return path.getmtime(settings['database'])
        except:
            return 0

    def get_tw_mtime(self):
        # get tweets.txt file last modification time
        try:
            return path.getmtime(settings['tweets'])
        except:
            return 0

    def get_fd_mtime(self):
        # get feeds.txt file last modification time
        try:
            return path.getmtime(settings['feeds'])
        except:
            return 0

    def get_ip_mtime(self):
        # get ipaddr.txt file last modification time
        try:
            return path.getmtime(settings['ipaddr'])
        except:
            return 0

def generate_asset_list():
    logging.info('Generating asset-list...')
    playlist = assets_helper.get_playlist(db_conn)
    complete_playlist = list(itertools.chain.from_iterable(playlist))

    deadline = sorted([asset['end_date'] for asset in playlist])[0] if len(playlist) > 0 else None
    logging.debug('generate_asset_list deadline: %s', deadline)

    return (playlist, deadline)

# return tweets from tweets.txt
def get_tweets():
    tweets = ""
    with file(settings['tweets']) as f: 
        tweets = eval(f.read())

    return tweets

# return feeds from feeds.txt
def get_feeds():
    feeds = ""
    with file(settings['feeds']) as f: 
        feeds = eval(f.read())

    return feeds

# return ip address from ipaddr.txt
def get_ip():
    IP = "0.0.0.0"
    with file(settings['ipaddr']) as f: 
        IP = f.read()
    return IP.strip('\n')

def watchdog():
    """Notify the watchdog file to be used with the watchdog-device."""
    if not path.isfile(WATCHDOG_PATH):
        open(WATCHDOG_PATH, 'w').close()
    else:
        utime(WATCHDOG_PATH, None)


def load_browser(url=None):
    global browser, current_browser_url, spec
    logging.info('Loading browser...')

    if browser:
        logging.info('killing previous uzbl %s', browser.pid)
        browser.process.kill()

    if not url is None:
        current_browser_url = url

    # --config=-       read commands (and config) from stdin
    # --print-events   print events to stdout
    geometry = spec['screen']

    browser = sh.Command('uzbl-browser')(print_events=True, config='-', uri=current_browser_url, _bg=True,geometry=geometry)
    logging.info('Browser loading %s. Running as PID %s. Screen Size %s', current_browser_url, browser.pid, geometry)

    uzbl_rc = 'ssl_verify {}\n'.format('1' if settings['verify_ssl'] else '0')
    with open(HOME + UZBLRC) as f:  # load uzbl.rc
        uzbl_rc = f.read() + uzbl_rc
    browser_send(uzbl_rc)

def browser_send(command, cb=lambda _: True):
    if not (browser is None) and browser.process.alive:
        while not browser.process._pipe_queue.empty():  # flush stdout
            browser.next()

        browser.process.stdin.put(command + '\n')
        while True:  # loop until cb returns True
            if cb(browser.next()):
                break
    else:
        logging.info('browser found dead, restarting')
        load_browser()


def load_full_browser(url=None):
    if settings['show_ticker'] or settings['show_sidebar']:
        global full_browser, spec
        logging.debug('Loading Full browser...')

        if full_browser:
            logging.debug('killing previous uzbl %s', full_browser.pid)
            full_browser.process.kill()
        
        if not url is None:
            current_browser_url = url

        spec['full'] = "%sx%s+%s+%s" % (spec['total_w'],spec['total_h'],0,0)
        geometry = spec['full']
        full_browser = sh.Command('uzbl-browser')(print_events=True, config='-', uri=url, _bg=True,geometry=geometry)
        logging.debug('Full Browser loading %s. Running as PID %s. Screen Size %s', url, full_browser.pid, geometry)
        uzbl_rc = 'ssl_verify {}\n'.format('1' if settings['verify_ssl'] else '0')
        with open(HOME + UZBLRC) as f:  # load uzbl.rc
            uzbl_rc = f.read() + uzbl_rc
        full_browser_send(uzbl_rc)


def full_browser_send(command, cb=lambda _: True):
    if not (full_browser is None) and full_browser.process.alive:
        while not full_browser.process._pipe_queue.empty():  # flush stdout
            full_browser.next()

        full_browser.process.stdin.put(command + '\n')
        while True:  # loop until cb returns True
            if cb(full_browser.next()):
                break
    else:
        logging.debug('Full browser found dead, restarting')
        load_full_browser()

def set_sidebar_ticker(sidebar,ticker):
    """ 
    function sets sidebar and ticker on full browser
    """

    if settings['show_sidebar'] and not settings['show_ticker']:    # if there is only sidebar
        command = 'js window.set_sidebar("{0}")'.format(sidebar.encode('utf-8'))    
        full_browser_send(command, cb=lambda b: 'COMMAND_EXECUTED' in b and 'set_sidebar' in b)
    
    elif not settings['show_sidebar'] and settings['show_ticker']:  # if there is only ticker
        command = 'js window.set_ticker("{0}")'.format(ticker.encode('utf-8'))
        full_browser_send(command, cb=lambda b: 'COMMAND_EXECUTED' in b and 'set_ticker' in b)

    else :  # if both sidebar and ticker 
        command = 'js window.set_sidebar_ticker("{0}","{1}")'.format(sidebar.encode('utf-8'),ticker.encode('utf-8')) 
        full_browser_send(command, cb=lambda b: 'COMMAND_EXECUTED' in b and 'set_sidebar_ticker' in b)

# clear screen in each split with the background color
def browser_screen_clear(playlist_id,frame):

    browser_send('js window.screen_black("{0}","{1}")'.format(playlist_id,frame), cb=lambda b: 'COMMAND_EXECUTED' in b and 'screen_black' in b)

# clear iframe before setting image or video 
def iframe_clear(playlist_id):
    browser_send('js window.iframe_clear("{0}")'.format(playlist_id), cb=lambda b: 'COMMAND_EXECUTED' in b and 'iframe_clear' in b)

# loads the browser with the background color
def browser_clear(force=False):
    """Load a black page. Default cb waits for the page to load."""
    browser_url('file://' + BLACK_PAGE, force=force, cb=lambda buf: 'LOAD_FINISH' in buf and BLACK_PAGE in buf)

def browser_url(url, cb=lambda _: True, force=False):
    global current_browser_url

    if url == current_browser_url and not force:
        pass# logging.debug('Already showing %s, keeping it.', current_browser_url)
    else:
        current_browser_url = url
        browser_send('uri ' + current_browser_url, cb=cb)
        logging.info('current url is %s', current_browser_url)

# set the html_template into an iframe 
def set_iframe(uri,playlist_id):
    iframe_clear(playlist_id)
    browser_send('js window.set_iframe("{0}","{1}")'.format(uri,playlist_id), cb=lambda b: 'COMMAND_EXECUTED' in b and 'set_iframe' in b)

def view_image(uri,playlist_id):
    iframe_clear(playlist_id)
    browser_clear()
    browser_send('js window.setimg("{0}","{1}","{2}")'.format(uri,playlist_id,get_ip()), cb=lambda b: 'COMMAND_EXECUTED' in b and 'setimg' in b)

def view_video(uri, duration,playlist_id,frame):
    global spec, run, video_lock
    geometry = spec['video']
    logging.debug('Displaying video %s for %s, Screen Size: %s ', uri, duration,geometry)

    if arch == 'armv6l':        
        player_args = ['omxplayer', uri]
        player_kwargs = {'o': settings['audio_output'], '_bg': True, '_ok_code': [0, 124],'win':geometry}
        # player_kwargs['_ok_code'] = [0, 124]
    else:
        player_args = ['mplayer', uri, '-nosound']
        player_kwargs = {'_bg': True}

    if duration and duration != 'N/A':
        player_args = ['timeout', VIDEO_TIMEOUT + int(duration.split('.')[0])] + player_args

    # logging.debug('In video run with video_lock value : %d' % video_lock)
    if video_lock:
        # run1 = sh.Command(player_args[0])(*player_args[1:], **player_kwargs) 
        # watchdog()
        
        while run.process.alive:
            sleep(1)
            
        # run = sh.Command(player_args[0])(*player_args[1:], **player_kwargs)
        # run = None
        # run = run1
    # else:
    run = sh.Command(player_args[0])(*player_args[1:], **player_kwargs)   
    sleep(1)
    browser_screen_clear(playlist_id,frame) 
    # browser_screen_clear(playlist_id)
    
    # if run.exit_code == 124:
    #     logging.error('omxplayer timed out')

def check_update():
    """
    Check if there is a later version of RIDS
    available. Only do this update once per day.

    Return True if up to date was written to disk,
    False if no update needed and None if unable to check.
    """

    sha_file = path.join('/home/pi/rids_files/', 'latest_rids_sha')

    if path.isfile(sha_file):
        sha_file_mtime = path.getmtime(sha_file)
        last_update = datetime.fromtimestamp(sha_file_mtime)
    else:
        last_update = None

    # logging.debug('Last update: %s' % str(last_update))

    if last_update is None or last_update < (datetime.now() - timedelta(days=1)):

        if get_ip() != '0.0.0.0' and not url_fails("http://www.google.com"):
            Popen(["/home/pi/ridsc/misc/run_upgrade.sh"],shell=True)
            with open(sha_file, 'w') as f:
                f.write(VERSION)
            return True    
        else:
            logging.debug('Unable to retreive latest RIDS')
            return
    else:
        return False

def load_settings():
    """Load settings and set the log level."""
    settings.load()
    logging.getLogger().setLevel(logging.DEBUG if settings['debug_logging'] else logging.INFO)

def asset_loop(scheduler):
    check_update()
    global run, video_lock
    SLEEP_DELAY = 1

    if scheduler.assets[0] is None and scheduler.assets[1] is None and scheduler.assets[2] is None :
        logging.info('All Playlist are empty. Sleeping for %s seconds', 1)
    
    split_map = ["P","S","T"]

    mylist = range(int(settings['split_screen']))

    logging.info('Status for Playlist %s: index %s,  nassets %s, go_next %s', str(mylist), str(scheduler.index), str(scheduler.nassets), str(scheduler.go_next))
    frame = ""
    for i in mylist:

        skip = False      
        if video_lock and split_map[i] == settings["video_split_screen"]:
            if run.process.alive:
                watchdog()
                # Skip next loop only if go_next time logic says, not on video_lock logic
                if scheduler.go_next[i]>int(time()):
                    skip = True
            else:
                video_lock = False
                # scheduler.go_next[i] = int(time())

                scheduler.go_next[i] = int(time()) + int(scheduler.assets[i][((scheduler.index[i]-1)%scheduler.nassets[i])]['duration'])   
            
            # if scheduler.assets[i][((scheduler.index[i-1])%scheduler.nassets[i])]['mimetype'] == 'video':
            #     frame =  scheduler.assets[i][((scheduler.index[i-1])%scheduler.nassets[i])]['filename']
            #     frame = frame.split(".")[0]+".jpeg"

        if scheduler.go_next[i]> int(time()): #0
            logging.debug('Playlist %s: Asset id %s is still running.', i,scheduler.index[i])
        elif not skip:
            asset = scheduler.get_next_asset(i)

            while asset is not None and (scheduler.counter[i]+1) % int(asset['modulo']) != 0 :
                asset = scheduler.get_next_asset(i)

            if asset is None:
                logging.info('Playlist %s is empty', i)
                view_image(HOME + LOAD_SCREEN,i)
                scheduler.go_next[i] = int(time()) + 1

            elif path.isfile(asset['uri']) or not url_fails(asset['uri']):
                name, mime, uri = asset['name'], asset['mimetype'], asset['uri']
                logging.info('Playlist %s: Showing asset %s (%s)', i, name, mime)
                # logging.debug('Asset URI %s', uri)
                watchdog()
                dur = int(asset['duration'])
                if 'image' in mime:
                    view_image(uri,i)
                elif 'Html' in mime:
                    set_iframe(uri,i)
                elif 'video' in mime:
                    frame = asset['filename'].split(".")[0]+".jpeg"
                    view_video(uri, asset['duration'],i,frame)
                    video_lock = True             
                    dur = int(dur*1-1)
                elif 'web' in mime:
                    frame = asset['filename'].split(".")[0]+".jpeg"
                    view_video(uri, asset['duration'],i,frame)
                    video_lock = True
                    dur = int(dur)
                else:
                    logging.error('Unknown MimeType %s', mime)

                #Should be below the above code
                scheduler.go_next[i] =  int(time()) + dur
                    
            else:
                # scheduler.go_next[i] =  int(asset['duration'])
                logging.info('Asset %s at %s is not available, skipping.', asset['name'], asset['uri'])
                sleep(0.5)
    
    if video_lock:
        SLEEP_DELAY = 1
    else:  
        # SLEEP_DELAY = int(min(scheduler.go_next))
        SLEEP_DELAY = max(1,int(min([ x - int(time()) for x in scheduler.go_next])))

    logging.info('Sleeping for %s, go_next - %s, current_time - %s', SLEEP_DELAY,str(scheduler.go_next),str(int(time())))
    sleep(SLEEP_DELAY)  
    # scheduler.go_next = [dur-SLEEP_DELAY for dur in scheduler.go_next]


def set_spec(screen):
    """
    Sets the screen specification according to the rids.conf
    """
    global spec,div_dic
    spec['total_h'] = int(screen[1])
    spec['total_w'] = int(screen[0])   

    if settings['show_ticker']:
        spec['ticker_h'] = max(68,int(spec['total_h'] *int(settings['ticker_height'])/100))
    else:
        spec['ticker_h'] = 0

    spec['ticker_w'] = spec['total_w']    
    spec['sidebar_h'] = spec['total_h'] - spec['ticker_h'] - 4

    if settings['show_sidebar']:
        spec['sidebar_w'] = max(200,int(spec['total_w']*int(settings['sidebar_width'])/100))
    else:
        spec['sidebar_w'] = 0    
   
    spec['screen_h'] = spec['sidebar_h']
    spec['screen_w'] = spec['total_w'] - spec['sidebar_w']

    spec['ticker_x'] = 0
    spec['ticker_y'] = spec['sidebar_h'] + 4

    spec['sidebar_x'] = 0
    spec['sidebar_y'] = 0

    spec['screen_x'] = spec['sidebar_w']
    spec['screen_y'] = 0

    spec['screen'] = "%sx%s+%s+%s" % (spec['screen_w'],spec['screen_h'],spec['screen_x'],spec['screen_y'])
    spec['ticker'] = "%sx%s+%s+%s" % (spec['ticker_w'],spec['ticker_h'],spec['ticker_x'],spec['ticker_y'])
    spec['sidebar'] = "%sx%s+%s+%s" % (spec['sidebar_w'],spec['sidebar_h'],spec['sidebar_x'],spec['sidebar_y'])
    
    thick_border = int(settings['outer_space'])
    thin_border = int(settings['inner_space'])

    settings['border_width_h'] = 0
    settings['border_width_h'] = 0
    
    if settings['split_screen'] == "1" :
        thick_border = 0

    full_height = spec['screen_h'] - thick_border*2 #- int(settings['border_width'])*2
    upper_height = spec['screen_h']* int(settings['upper_height'])/100 - thick_border - thin_border #- int(settings['border_width'])*2 
    lower_height = full_height - upper_height
    full_width = spec['screen_w'] - thick_border*2 # - int(settings['border_width'])*2
    left_width = spec['screen_w']* int(settings['left_width'])/100 - thick_border - thin_border # - int(settings['border_width'])*2 
    right_width = full_width - left_width

    #Screen split in Primary,Second,Tertiary

    div_dic['P_div_t'] = thick_border     
    div_dic['P_div_l'] = thick_border

    if not settings['split_type']:  # if vertical
        div_dic['S_div_t'] = thick_border
        div_dic['S_div_l'] = thick_border + left_width + thin_border*2
        
    else:     # if horizontal
        div_dic['S_div_t'] = thick_border + upper_height + thin_border*2
        div_dic['S_div_l'] = thick_border
        settings['border_width_v'] = 0
    
    div_dic['T_div_t'] = thick_border + upper_height + thin_border*2  #+ int(settings['border_width'])*2
    div_dic['T_div_l'] = thick_border + left_width + thin_border*2
    
    #assuming one screen area    
    div_dic['P_div_h'] = full_height
    div_dic['P_div_w'] = full_width

    div_dic['S_div_w'] = 0
    div_dic['S_div_h'] = 0

    div_dic['T_div_w'] = 0 
    div_dic['T_div_h'] = 0
    
    if settings['split_screen'] != "1" : 
        if not settings['split_type']:
            div_dic['P_div_w'] = left_width
            div_dic['S_div_w'] = right_width
            div_dic['S_div_h'] = full_height if settings['split_screen'] == "2" else upper_height
            settings['border_width_v'] = settings['border_width']

        else:
            div_dic['P_div_h'] = upper_height
            div_dic['S_div_h'] = lower_height
            div_dic['S_div_w'] = full_width if settings['split_screen'] == "2" else left_width
            settings['border_width_h'] = settings['border_width']

    if settings['split_screen'] == "3":
        div_dic['T_div_w'] = right_width
        div_dic['T_div_h'] = lower_height
    
    video_x = spec['screen_x'] + div_dic[str(settings['video_split_screen'])+'_div_l'] + int(settings['border_width']) 
    video_y = spec['screen_y'] + div_dic[str(settings['video_split_screen'])+'_div_t'] + int(settings['border_width'])*2 
    video_w = video_x + div_dic[str(settings['video_split_screen'])+'_div_w'] - int(settings['border_width'])
    video_h = video_y + div_dic[str(settings['video_split_screen'])+'_div_h'] - int(settings['border_width'])
    spec['video'] = "%s %s %s %s" % (video_x,video_y,video_w,video_h)
    spec['event'] = spec['sidebar_h']/2
    spec['ticker_margin'] = spec['ticker_h']/2-40
    div_dic['logo_y'] = int(spec['screen_h'] * int(settings['rids_y'])/100.0)    # y-position of brought by logo
    div_dic['logo_x'] = int(spec['screen_w'] * int(settings['rids_x'])/100.0)    # x-position of brought by logo
    div_dic['status_x'] = div_dic['logo_x'] + 110
    div_dic['status_y'] = div_dic['logo_y'] + 25


def setup():
    global HOME, arch, db_conn
    HOME = getenv('HOME', '/home/pi')
    arch = machine()

    signal(SIGUSR1, sigusr1)
    signal(SIGUSR2, sigusr2)

    load_settings()
    db_conn = settings['database']

    if not RCA:
        screen = check_output(['tvservice', '-s']).split(" ")[8]
    else:
        screen = check_output(['tvservice', '-s']).split(" ")[4]

    Popen(["/home/pi/ridsc/misc/display_rotate.sh %s" % settings['display_rotate']],shell=True)

    screen = screen.split("x")[1]+"x"+screen.split("x")[0] if int(settings['display_rotate']) else screen

    generate_rsync_file(screen)

    screen = screen.split("x")

    set_spec(screen)

    sh.mkdir(RIDS_HTML, p=True)
    my_ip = get_node_ip()
    if my_ip:
        ip_lookup = True
        url = "Your local ip is {}".format(my_ip)
    else:
        ip_lookup = False
        url = "Unable to look up your installation's IP address." 

    html_templates.black_page(BLACK_PAGE,settings,div_dic)
    html_templates.ticker_sidebar_page(TICKER_SIDEBAR_PAGE,settings,div_dic,spec)
    html_templates.splash_page(SPLASH_PAGE,url,INSTALLATION_ID,settings)


def main():
    setup()
    if not settings['is_enabled']:
        url = 'file://' + SPLASH_PAGE 
        load_full_browser(url=url)
        sleep(10000000)

    url = 'file://' + SPLASH_PAGE if settings['show_splash'] else 'file://' + BLACK_PAGE
    load_full_browser(url = 'file://' + TICKER_SIDEBAR_PAGE)
    load_browser(url=url)

    if settings['show_splash']:
        sleep(SPLASH_DELAY)

    scheduler = Scheduler()
    logging.debug('Entering infinite loop.')
    while True:
        asset_loop(scheduler)

if __name__ == "__main__":
    main()

