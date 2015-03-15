## STEPS ##

  1. Download the script and extract it to the boxee scripts folder.
    * The folder is probably at:
      * **Windows:** C:\Program Files\Boxee\scripts
      * **Mac OS X:** /Applications/Boxee.app/Contents/Resources/boxee/scripts/
      * **Linux:** /opt/boxee/scripts

> 2. Open the boxee\_video\_context.xml file in the skin folder with your favorite editor. This file is probably at:
    * **Windows:** C:\Program Files\Boxee\skin\boxee\720p\
    * **Mac OS X:** /Applications/Boxee.app/Contents/Resources/boxee/skin/boxee/720p/
    * **Linux:** /opt/boxee/skin/boxee/720p

Look for
```
<item>
<controlid>9008</controlid>
<visible>!IsEmpty(container(5000).ListItem.TVShowTitle) + !IsEmpty(container(5000).ListItem.FileNameAndPath) + !container(5000).ListItem.property(IsInternetStream)</visible>
<onclick>RunScript(special://xbmc/scripts/OpenSubtitles/default.py, [TV]$INFO[container(5000).ListItem.Season] $INFO[container(5000).ListItem.Episode] $INFO[container(5000).ListItem.TVshowtitle][/TV][PATH]$INFO[container(5000).ListItem.filenameandpath][/PATH])</onclick>
<onclick>Dialog.Close(354)</onclick>
<thumb>icons/icon_osd_subtitles.png</thumb>
<label>287</label>
</item>
```

Replace OpenSubtitles occurrences with PeriscopeSubtitles like:
```
<item>
<controlid>9008</controlid>
<visible>!IsEmpty(container(5000).ListItem.TVShowTitle) + !IsEmpty(container(5000).ListItem.FileNameAndPath) + !container(5000).ListItem.property(IsInternetStream)</visible>
<onclick>RunScript(special://xbmc/scripts/PeriscopeSubtitles/default.py, [TV]$INFO[container(5000).ListItem.Season] $INFO[container(5000).ListItem.Episode] $INFO[container(5000).ListItem.TVshowtitle][/TV][PATH]$INFO[container(5000).ListItem.filenameandpath][/PATH])</onclick>
<onclick>Dialog.Close(354)</onclick>
<thumb>icons/icon_osd_subtitles.png</thumb>
<label>287</label>
</item>
```

> 3. Save the file

> 4. Start Boxee and watch a TV Show, bring up the OSD and press the subtitle button. If you did everything right you should see a popup from the PeriscopeSubtitles script.

Thanks to http://ikbenjaap.com/2010/04/12/tip-using-bierdopje-subtitles-in-boxee/