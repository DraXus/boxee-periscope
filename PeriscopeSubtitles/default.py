#!/usr/bin/python
from __future__ import division
import os, re, string, urllib, urllib2, time, xbmcgui, elementtree.ElementTree as XMLTree
import periscope

#====================================================================================================================
# Functions
#====================================================================================================================

def apicall(command, paramslist, timeout):
    url = apiurl + apikey + "/" + command
    for param in paramslist:
        url = url + "/" + urllib.quote_plus(param)
    if debug: print "Getting url: " + url
    try:
        response = urllib2.urlopen(url)
    except:
        okdialog = xbmcgui.Dialog()
        ok = okdialog.ok(getstring(30218), getstring(30219) % (url))
        if debug: print "Failed to get url: " + url
    else:
        try:
            xml = XMLTree.parse(response)
            status = gettextelements(xml, "response/status")
        except:
            okdialog = xbmcgui.Dialog()
            ok = okdialog.ok(getstring(30218), getstring(30220))
            if debug: print "Failed to parse xml response from Bierdopje"
            return None
        if status == "false":
            return None
        else:
            return xml

def gettextelements(xml, path):
    textelements = []
    try:
        elements = xml.findall(path)
    except:
        return
    for element in elements:
        textelements.append(element.text)
    return textelements

def processsubtitlesfolder(existingsubtitles, dirname, filenames):
    for filename in filenames:
        match = re.match("(.*)\.(.*)", filename)
        if match:
            base = match.group(1)
            extension = match.group(2)
            if string.lower(extension) in ["srt","sub","smi"]:
                subfilename = base, extension
                existingsubtitles.append(subfilename)
            else:
                pass # no subtitles or videofile
        else:
            pass # probably a subfolder

def processdir(movielist, dirname, filenames):
    movies = []
    subs = []
    for filename in filenames:
        match = re.match("(.*)\.(.*)", filename)
        if match:
            base = match.group(1)
            extension = match.group(2)
            if string.lower(extension) in ["mkv","avi","xvid","divx","wmv"]:
                moviefilename = base, extension
                movies.append(moviefilename)
            elif string.lower(extension) in ["srt","sub","smi"]:
                subfilename = base, extension
                subs.append(subfilename)
            else:
                pass # no subtitles or videofile
        else:
            pass # probably a subfolder
    if separatesubtitlesfolder == "":
        for movie in movies:
            subfound = False
            for sub in subs:
                if string.find(sub[0],movie[0]) > -1:
                    if debug: print movie[0] + "." + movie[1] + " has a sub"
                    subfound = True
                    break
            if not subfound:
                if debug: print "No sub found for " + movie[0] + "." + movie[1]
                movielist.append(os.path.join(dirname, movie[0] + "." + movie[1]))
    else:
        for movie in movies:
            subfound = False
            for sub in existingsubtitles:     
                if string.find(sub[0],movie[0]) > -1:
                    if debug: print movie[0] + "." + movie[1] + " has a sub"
                    subfound = True
                    break
            if not subfound:
                if debug: print "No sub found for " + movie[0] + "." + movie[1]
                movielist.append(os.path.join(dirname, movie[0] + "." + movie[1]))
            
        
def extract_name_season_episode(filename):
    # used regexp for tv-shows from XBMC:
    # http://wiki.xbmc.org/index.php?title=Advancedsettings.xml#.3Ctvshowmatching.3E
    showname = ""
    season = ""
    episode = ""
    pattern = "(.*)[\._ \-][Ss]([0-9]+)[\.\-]?[Ee]([0-9]+)" # foo, s01e01, foo.s01.e01, foo.s01-e01    
    match = re.search(pattern, filename)
    if match:
        showname = match.group(1)
        season   = match.group(2)
        episode  = match.group(3)
    else:
        pattern = "(.*)\[[Ss]([0-9]+)\][_\- \.]\[[Ee]([0-9]+)" # foo_[s01]_[e01]
        match = re.search(pattern, filename)
        if match:
            showname = match.group(1)
            season   = match.group(2)
            episode  = match.group(3)
        else:
            pattern = "(.*)[\._ \-]+([0-9]+)[xX]([0-9]+)" # foo.1x09
            match = re.search(pattern, filename)
            if match:
                showname = match.group(1)
                season   = match.group(2)
                episode  = match.group(3)
            else:
                pattern = "(.*)[\._ \-]([0-9]+)([0-9][0-9])" # foo.103
                match = re.search(pattern, filename)
                if match:
                    showname = match.group(1)
                    season   = match.group(2)
                    episode  = match.group(3)
    if showname != "" and season != "" and episode != "":
        showname = string.strip(showname) # remove leading and trailing whitespace
        showname = string.replace(showname,"."," ") # assume there should be no dots in a showname ?
        showname = string.replace(showname,"_"," ") # assume there should be no underscores in a showname ?
        showname = string.replace(showname,"-"," ") # assume there should be no hyphens in a showname ?
        showname = string.strip(showname) # remove leading and trailing whitespace
        if debug: print "showname = " + showname + ", season = " + season + ", episode = " + episode
        return [showname, season, episode]
    else:
        return None

def getshowid(showname):
    if showname not in showids:
        response = apicall("GetShowByName",[showname], timeout)
        if response is not None:
            showid = gettextelements(response,"response/showid")
            if len(showid) == 1:
                showids[showname] = str(showid[0])
                if debug: print "Show ID for " + showname + " is: " + showids[showname]
                return showids[showname]
            else:
                if debug: print "No exact matching show name found for " + showname
                response = apicall("FindShowByName", [showname], timeout)
                if progressdialog.iscanceled(): return
                if response is not None:
                    showidlist   = gettextelements(response,"response/results/result/showid")
                    shownamelist = gettextelements(response,"response/results/result/showname")
                    if len(showidlist) > 0:
                        selectdialog = xbmcgui.Dialog()
                        userinput = selectdialog.select(getstring(30005), shownamelist)
                        if userinput >= 0:
                            showids[showname] = str(showidlist[userinput])
                            if debug: print "Show name selected: " + shownamelist[userinput]
                            return showids[showname]
                        else:
                            if debug: print "No show name selected"
                            return -1
                    else:
                        if debug: print "No show name found"
                        return 0
                        pass
    else:
        if debug: print "Showid for " + showname + " was already found: " + showids[showname]
        return showids[showname]

def getallsubs(showid,season,episode,language):
    subsdata = []
    subsdatalist = []
    filenamelist = []
    downloadlist = []
    numdownloadslist = []
    response = apicall("GetAllSubsFor",[showid, season, episode, language], timeout)
    if response is not None:
        filenames = gettextelements(response,"response/results/result/filename")
        if len(filenames) == 0:
            if debug: print "No subtitles found on bierdopje"
            return None
        else:
            downloadlinks = gettextelements(response,"response/results/result/downloadlink")
            numdownloadss = gettextelements(response,"response/results/result/numdownloads") 
            for i in range(len(filenames)):
                subsdata = [filenames[i] + ".srt", downloadlinks[i], numdownloadss[i]]
                subsdatalist.append(subsdata)
            return subsdatalist
            if debug: print str(i) + " subtitles found on bierdopje"
    else:
        return None

def isexactmatch(subsfile, moviefile):
    match = re.match("(.*)\.", moviefile)
    if match:
        moviefile = string.lower(match.group(1))
        subsfile = string.lower(subsfile)
        if string.find(string.lower(subsfile),string.lower(moviefile)) > -1:
            return True
        else:
            return False
    else:
        return False
    
def downloadsubtitle(url, moviefilepathname, language, timeout):
    subtitlescontent = ""
    moviefile = os.path.basename(moviefilepathname)
    match = re.match("(.*)\.", moviefile)    
    if match:
        if separatesubtitlesfolder == "":
            subtitlesfilename = xbmc.translatePath( os.path.join(os.path.dirname(moviefilepathname), match.group(1) + "." + language + ".srt"))
        else:
            subtitlesfilename = xbmc.translatePath( os.path.join(separatesubtitlesfolder, match.group(1) + "." + language + ".srt"))
        if debug: print "Subtiles will be saved as: " + subtitlesfilename
        if debug: print "Getting url: " + url
        try:
            response = urllib2.urlopen(url)
        except urllib2.URLError, (err):
            okdialog = xbmcgui.Dialog()
            ok = okdialog.ok(getstring(30218), getstring(30219) % (url))            
            if debug: print "Failed to get url: " + url
            return False
        else:
            try:
                subfile = open(subtitlesfilename, "w" + "b")
                subtitlescontent = response.read()
                subfile.write(subtitlescontent)
                subfile.close()
                return True
            except:
                okdialog = xbmcgui.Dialog()
                ok = okdialog.ok(getstring(30218), getstring(30221) % (subtitlesfilename))
                if debug: print "Failed to save subtitles to: " + subtitlesfilename
                return False
        
def processmoviefile(moviefilepathname, progressdialog, count, total):
    global downloadcounter
    global notfoundcounter    
    #print "moviefilepathname = %s" % moviefilepathname
    periscope_client = periscope.Periscope()
    langs = ["es", ]
    sub = periscope_client.downloadSubtitle(moviefilepathname, langs)
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

if debug: print "Starting debug of script Bierdopje"

tvshowsrootpath = settings("tvshowsrootpath")
if debug: print "Tvshowsrootpath = " + settings("tvshowsrootpath")

if (string.lower(settings("separatesubtitlesfolder")) == "true"):
    if debug: print "Separate folder for subtitles = " + settings("subtitlesfolder")
    separatesubtitlesfolder = settings("subtitlesfolder")
else:
    separatesubtitlesfolder = ""
    if debug: print "No separate folder for subtitles"

if int(settings("language")) == 0:
    if debug: print "Language for subtitles is Dutch"
    languagecode = "nl"
    lookupnumber = int(settings("dutchsuffix"))
    #languagestring = getstring(lookupnumber) # this creates an access violation:
    # CThread::staticThread : Access violation at 0x77ac8c39: Writing location 0x00000014
    languagestring = ("Dutch", "Nederlands", "NL", "NLD", "dutch", "nederlands", "nl", "nld")[lookupnumber]
    if debug: print "Suffix languagestring = " + languagestring
elif int(settings("language")) == 1:
    if debug: print "Language for subtitles is English"
    languagecode = "en"   
    lookupnumber = int(settings("englishsuffix"))
    #languagestring = getstring(lookupnumber) # this creates an access violation:
    # CThread::staticThread : Access violation at 0x77ac8c39: Writing location 0x00000014
    languagestring = ("English", "Engels", "EN", "ENG", "english", "engels", "en", "eng")[lookupnumber]
    if debug: print "Suffix languagestring = " + languagestring

# Define global variables

apiurl = "http://api.bierdopje.com/"
apikey = "FBE81431599EBCAD"

existingsubtitles = []
timeout = 30 # useless in xbmc python version
progressdialog = xbmcgui.DialogProgress()
showids = {}
downloadcounter = 0
notfoundcounter = 0

# Find out if OpenSubtitles_OSD script is installed
if os.path.exists(xbmc.translatePath("special://home/scripts/OpenSubtitles_OSD/default.py")):
    OpenSubtitlesScript = xbmc.translatePath("special://home/scripts/OpenSubtitles_OSD/default.py")
elif os.path.exists(xbmc.translatePath(os.path.join(os.getcwd(),"..", "OpenSubtitles_OSD", "default.py"))):
    OpenSubtitlesScript = xbmc.translatePath(os.path.join(os.getcwd(),"..", "OpenSubtitles_OSD", "default.py"))
else:
    OpenSubtitlesScript = ""

# construct main menu options
# check if a video file is playing
if xbmc.Player().isPlayingVideo() :
    moviefileplaying = xbmc.Player().getPlayingFile()
    #choices = [getstring(30001),getstring(30002),getstring(30003)]
    choices = [getstring(30001)]
else:
    choices = [getstring(30002),getstring(30003)]

# Add "run OpenSubtitles_OSD" to main menu if it is available and video is in full screen
if OpenSubtitlesScript != "" and xbmc.getCondVisibility('videoplayer.isfullscreen') :
    choices.append(getstring(30006) + " OpenSubtitles_OSD")

# show main menu options
selectdialog = xbmcgui.Dialog()
userselected = selectdialog.select(getstring(30000), choices)

# if a valid menu option was selected
if userselected >= 0:

    # get subtitles for playing video
    if choices[userselected] == getstring(30001):
        if not xbmc.getCondVisibility('Player.Paused') : xbmc.Player().pause() #Pause if not paused
        ret = progressdialog.create(getstring(30200))
        processmoviefile(moviefileplaying, progressdialog, 0, 1)
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

    # get subtitles for a single file
    elif choices[userselected] == getstring(30002):
        browsedialog = xbmcgui.Dialog()
        selectedfile = browsedialog.browse(1, getstring(30004), "video", ".mkv|.avi|.divx|.xvid|.wmv", False, False, "")
        if selectedfile != "":
            ret = progressdialog.create(getstring(30200))
            processmoviefile(selectedfile, progressdialog, 0, 1)
            print 4
            progressdialog.close()
            print 5
            okdialog = xbmcgui.Dialog()
            print 6
            if downloadcounter == 1:
                print 7
                ok = okdialog.ok(getstring(30214), getstring(30216))
            elif notfoundcounter == 1:
                print 8
                ok = okdialog.ok(getstring(30214), getstring(30215))

    # automatically get all missing subtitles for all tv shows
    elif choices[userselected] == getstring(30003):
        if string.find(tvshowsrootpath,"smb://") > -1:
            okdialog = xbmcgui.Dialog()
            ok = okdialog.ok(getstring(30218), getstring(30224))
            ok = okdialog.ok(getstring(30218), getstring(30225))
        elif os.path.exists(tvshowsrootpath):
            if separatesubtitlesfolder != "":
                if debug: print "Reading all existing subtitles in folder " + separatesubtitlesfolder
                os.path.walk(separatesubtitlesfolder, processsubtitlesfolder, existingsubtitles)
            if debug: print "Scanning " + tvshowsrootpath + " for movies without external subtitles ...\r\n"
            ret = progressdialog.create(getstring(30201))
            unsubbedmovielist = []
            os.path.walk(tvshowsrootpath, processdir, unsubbedmovielist)
            if debug: print "=" * 80
            showids = {} # dictionary for bierdopje's showid
            unsubbedmoviecounter = 0
            unsubbedmoviescount = len(unsubbedmovielist)   
            if unsubbedmoviescount > 0:
                ret = progressdialog.create(getstring(30202))
                if debug: print "Movies without external subtitles found, processing movies ..."
                for unsubbedmovie in unsubbedmovielist: # unsubbedmovie is movie filename with full path
                    processmoviefile(unsubbedmovie, progressdialog, unsubbedmoviecounter, unsubbedmoviescount)
                    unsubbedmoviecounter = unsubbedmoviecounter + 1                    
                    if progressdialog.iscanceled(): break
                progressdialog.close()
                okdialog = xbmcgui.Dialog()
                ok = okdialog.ok(getstring(30214), getstring(30217) % (str(downloadcounter), str(notfoundcounter)))
            else: # nothing to do, all tv show files have subtitles
                progressdialog.close()
                okdialog = xbmcgui.Dialog()
                ok = okdialog.ok(getstring(30214), getstring(30222))
        else: # path defined in settings does not exist
            okdialog = xbmcgui.Dialog()
            ok = okdialog.ok(getstring(30218), getstring(30223))

    # run OpenSubtitles_OSD
    elif choices[userselected] == getstring(30006) + " OpenSubtitles_OSD":
        xbmc.executescript(OpenSubtitlesScript)
