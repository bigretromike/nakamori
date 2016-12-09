---------------------------------------------------------
Nakamori
---------------------------------------------------------

Nakamori is designed for Kodi (initial version was released for 15.2 Isengard, but works great on 16.1 Jarvis).
The main goal was to connect Shoko (formerly known as JMM) Server to Kodi as a library.
Kodi wasn't designed with anime in mind. Thanks to a lot of work from community, there are many
options to improve Kodi compatibility with Anime, which will sometimes break compatibility with non-anime content.

That's why using a specialized application, which is fully dedicated for managing anime, as a back-end for Kodi gives great results.

I would like to credit author of JAVStream (http://www.ptom.co.uk/home/) which was used as a base code for the project originally.
A great help was plugin.video.plexbmc (https://github.com/hippojay/plugin.video.plexbmc/) which showed how some things can be done.
The overwrite of player methods and fix for 'Playback failed' was looked up on forum.kodi.tv (http://forum.kodi.tv/showthread.php?tid=205441&pid=1806212#pid1806212)

REMEMBER:
After adding add-on, configure the ip address and port in settings if necessary (default: 127.0.0.1:8111)



---------------------------------------------------------
SETTINGS
---------------------------------------------------------

Windows Default: %AppData%\Roaming\Kodi\userdata\advancedsettings.xml 

If you dont want Kodi to mark watched videos as watched:
```
 <advancedsettings>
  <video>
    <playcountminimumpercent>101</playcountminimumpercent>
    <ignorepercentatend>101</ignorepercentatend>
  </video>
</advancedsettings>
```
