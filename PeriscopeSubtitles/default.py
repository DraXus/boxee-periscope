#!/usr/bin/python
from __future__ import division
import os, re, string, urllib, xbmcgui
import periscope

#====================================================================================================================
# Functions
#====================================================================================================================
        
def processmoviefile(moviefilepathname, language):
    global downloadcounter
    global notfoundcounter
    #print "moviefilepathname = %s" % moviefilepathname
    periscope_client = periscope.Periscope()
    sub = periscope_client.downloadSubtitle(moviefilepathname, [language, ])
    if sub:
       downloadcounter += 1
    else:
       notfoundcounter += 1


#====================================================================================================================
# The "main" section
#====================================================================================================================

# Get script settings

getstring = xbmc.Language(os.getcwd()).getLocalizedString
settings  = xbmc.Settings(path=os.getcwd()).getSetting

if (string.lower(settings("debug")) == "true"):
    debug = True
else:
    debug = False

# Define global variables

progressdialog = xbmcgui.DialogProgress()
downloadcounter = 0
notfoundcounter = 0

# construct main menu options
# check if a video file is playing
if xbmc.Player().isPlayingVideo() :
    moviefileplaying = xbmc.Player().getPlayingFile()
    choices = [getstring(30300), getstring(30301), getstring(30302), getstring(30303), getstring(30304), getstring(30305), getstring(30306), getstring(30307), getstring(30308), getstring(30309), getstring(30310)]
else:
    choices = [getstring(30002),getstring(30003)]



# show main menu options
selectdialog = xbmcgui.Dialog()
userselected = selectdialog.select(getstring(30001), choices)

# if a valid menu option was selected
if userselected >= 0:

    # get subtitles for playing video
	
	language_match = re.match("(.*)\[([a-z]+)\](.*)", choices[userselected])
	if language_match:
	    language = language_match.group(2)
        if not xbmc.getCondVisibility('Player.Paused') : xbmc.Player().pause() #Pause if not paused
        ret = progressdialog.create(getstring(30200))
        processmoviefile(moviefileplaying, language)
        progressdialog.close()
        okdialog = xbmcgui.Dialog()
        if downloadcounter == 1:
            ok = okdialog.ok(getstring(30214), getstring(30216))      
            match = re.match("(.*)\.", moviefileplaying)
            if match:
                subtitlesfilename = match.group(1) + ".srt"
                xbmc.Player().setSubtitles( subtitlesfilename )           
        elif notfoundcounter == 1:
            ok = okdialog.ok(getstring(30214), getstring(30208))
        if xbmc.getCondVisibility('Player.Paused'): xbmc.Player().pause() # if Paused, un-pause
	else:
	   ok = okdialog.ok(getstring(30214), getstring(30208))
