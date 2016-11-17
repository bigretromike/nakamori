---------------------------------------------------------
Nakamori
---------------------------------------------------------

Nakamori addon is design for Kodi (initial version was released for 15.2 Isengard, but works great on 16.1 Jarvis).
The main goal was to connect Japanese Media Manager (known as JMM) Server Database to be accessible within Kodi.
Kodi wasn't design with anime in mind. Thanks to alot of work from community there are many
options to improve Kodi compatibility with Anime, which sometimes break compatibility with non-anime content.

Thats why using a specialized application which is fully dedicated for managing anime as a back-end for Kodi give great results.

I would like to credit author of JAVStream (http://www.ptom.co.uk/home/) which I used as a base code for my project at the start.
A great help was plugin.video.plexbmc (https://github.com/hippojay/plugin.video.plexbmc/) which showed how some things can be done.
The overwrite of player methods and fix for 'Playback failed' was lookup on forum.kodi.tv (http://forum.kodi.tv/showthread.php?tid=205441&pid=1806212#pid1806212)

This is only hobby attempt to join both words of awesome and this is my first python project.

REMEMBER:
After adding add-on configure ip address and port in settings if needed (default: 127.0.0.1:8111)



---------------------------------------------------------
SETTINGS
---------------------------------------------------------

%AppData%\Roaming\Kodi\userdata\advancedsettings.xml 

If you dont want Kodi to mark watched videos as watched:
```
 <advancedsettings>
  <video>
    <playcountminimumpercent>101</playcountminimumpercent>
    <ignorepercentatend>101</ignorepercentatend>
  </video>
</advancedsettings>
```
