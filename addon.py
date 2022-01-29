from os import preadv
import xbmc
import xbmcaddon
import xbmcgui
from datetime import datetime, timedelta
import time
import json

ADDON = xbmcaddon.Addon()
ADDONID = ADDON.getAddonInfo('id')
ADDONNAME = ADDON.getAddonInfo('name')
SETTINGS = xbmcaddon.Addon().getSettings()
LANGUAGE = ADDON.getLocalizedString
DIALOG = xbmcgui.Dialog()

# read settings
active = SETTINGS.getBool('active')
dryrun = SETTINGS.getBool('dryrun')
number_of_days = SETTINGS.getInt('numberofdays')
prevent = SETTINGS.getBool('preventdialog')

if not active:
    DIALOG.ok(ADDONNAME, LANGUAGE(32001))
    exit()
else:
    if not dryrun and not prevent:
        ret = DIALOG.yesno(LANGUAGE(32005), LANGUAGE(32006))
        if not ret:
            exit()

if dryrun and not prevent:
    DIALOG.ok(ADDONNAME, LANGUAGE(32002))

now = datetime.now()
#kodi_time = now.strftime("%Y-%m-%d %H:%M:%S")

# this is the json we work with
# the output contains movielabel, movie-id, lastplayed and playcount
response = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": { "properties" : [ "lastplayed", "playcount" ], "sort": { "order": "ascending", "method": "label", "ignorearticle": true } }, "id": "libMovies"}')
data = json.loads(response)

list_of_movies=()

# for every movie item
# that`s not the movie-id
for movie in data['result']['movies']:
    # get lastplayed date and modify it
    last_p = movie['lastplayed']
    # get movie-id
    movieid = movie['movieid']
    # get movie label
    label = movie['label']

    # if lastplayed value is not empty
    xbmc.log("Checking: " + label, level=xbmc.LOGDEBUG)     
    if not last_p:
        continue
    xbmc.log("last: " + last_p, level=xbmc.LOGDEBUG)
    # format string to date
    try:
        last_date = datetime.strptime(last_p, "%Y-%m-%d %H:%M:%S")
    except TypeError:
        last_date = datetime(*(time.strptime(last_p, "%Y-%m-%d %H:%M:%S")[0:6]))
    # add 365 to lasteplayed date
    lastp_plus_year = last_date + timedelta(days=number_of_days)
    xbmc.log("plus one year: " + str(lastp_plus_year), level=xbmc.LOGDEBUG)
    # check if lastplayed + 'number_of_days' is lower than then the current date
    if lastp_plus_year < now:
        xbmc.log("added: " + str(movie['label']), level=xbmc.LOGDEBUG)
        #ans=movie['label']
        list_of_movies = list_of_movies + (movie['label'], )
        if not dryrun:
            set = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": { "movieid": %d, "playcount": 0, "lastplayed": "" }, "id": "libMovies"}' %movieid)
            xbmc.log(str(set), level=LOGDEBUG)
    else:
        xbmc.log("no movie added", level=xbmc.LOGDEBUG)

if not list_of_movies:
    if not prevent:
        DIALOG.ok(ADDONNAME, LANGUAGE(32003))
    else:
        exit()
else:
    DIALOG.ok(ADDONNAME, LANGUAGE(32004) +str(list_of_movies))
