# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcplugin, xbmcaddon, urllib2, urllib, re, string, sys, os, gzip, StringIO
import xunlei
import logging

try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs

# Plugin constants 
__addonname__ = "XunLei VOD"
__addonid__ = "plugin.video.xunlei"
__addon__ = xbmcaddon.Addon(id=__addonid__)
__addonicon__ = os.path.join( __addon__.getAddonInfo('path'), 'icon.png' )

# parameter keys
PARAMETER_KEY_MODE = "mode"
PARAMETER_KEY_URL = "url"
PARAMETER_KEY_NAME = "name"
PARAMETER_KEY_ID = "id"

USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_5) '
            'AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.218 Safari/535.1')

# plugin modes
MODE_PLAY = 10
MODE_LIST_BT = 20
 
# plugin handle
handle = int(sys.argv[1])

def get_xunlei():
    """Currently, we're using hard coded settings. Should use xbmc settings in the future"""
    username = ''
    password = ''
    cookie_file = ''
    return xunlei.Xunlei(username, password, cookie_file)

# UI builder functions
def show_root_menu():
    """List all tasks"""
    xunlei_obj = get_xunlei()
    items = xunlei_obj.dashboard()
    for item in items:
        if item['status'] == '2' and item['download_url']:
            addDirectoryItem(name=item['name'].encode('utf-8'), parameters={
                PARAMETER_KEY_MODE: MODE_PLAY,
                PARAMETER_KEY_URL: item['download_url'].encode('utf-8'),
                PARAMETER_KEY_NAME: item['name'].encode('utf-8'),
            }, isFolder=False)
        if item['status'] == '2' and (not item['download_url']) and item['bt_download_url'][:5] == 'bt://':
            addDirectoryItem(name=item['name'].encode('utf-8'), parameters={
                PARAMETER_KEY_MODE: MODE_LIST_BT,
                PARAMETER_KEY_URL: item['bt_download_url'].encode('utf-8'),
                PARAMETER_KEY_NAME: item['name'].encode('utf-8'),
                PARAMETER_KEY_ID: item['id'].encode('utf-8'),
            }, isFolder=True)
    xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

def play_video(params):
    """Play a giving video"""
    xunlei_obj = get_xunlei()
    url = params.get(PARAMETER_KEY_URL, None)
    if url:
        name = params.get(PARAMETER_KEY_NAME, 'Unknown')
        listitem = xbmcgui.ListItem(name)
        logging.error(url)
        data = {
            'User-Agent': USER_AGENT,
            'Cookie': xunlei_obj.get_cookie_string(url),
            'Referer': xunlei_obj.get_dashboard_url()
        }
        video_url = '%s|%s' % (url, urllib.urlencode(data))
        xbmc.Player().play(video_url, listitem)

def list_bt(params):
    """List files in a bittorrent task"""
    xunlei_obj = get_xunlei()
    url = params.get(PARAMETER_KEY_URL, None)
    task_id = params.get(PARAMETER_KEY_ID, None)
    if url and task_id:
        items = xunlei_obj.list_bt(url, task_id)
        for item in items:
            if item['download_status'] == '2' and item['downurl']:
                addDirectoryItem(name=item['title'].encode('utf-8'), parameters={
                    PARAMETER_KEY_MODE: MODE_PLAY,
                    PARAMETER_KEY_URL: item['downurl'].encode('utf-8'),
                    PARAMETER_KEY_NAME: item['title'].encode('utf-8'),
                }, isFolder=False)
        xbmcplugin.endOfDirectory(handle=handle, succeeded=True)

# utility functions
def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramDict = parse_qs(parameters[1:])
        for key, value in paramDict.iteritems():
            paramDict[key] = value[0]
    return paramDict
 
def addDirectoryItem(name, isFolder=True, parameters={}):
    ''' Add a list item to the XBMC UI.'''
    li = xbmcgui.ListItem(name)
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=isFolder)


params = parameters_string_to_dict(sys.argv[2])
mode = int(params.get(PARAMETER_KEY_MODE, "0"))

# Depending on the mode, call the appropriate function to build the UI.
if not sys.argv[2]:
    # new start
    ok = show_root_menu()
elif mode == MODE_PLAY:
    ok = play_video(params)
elif mode == MODE_LIST_BT:
    ok = list_bt(params)

