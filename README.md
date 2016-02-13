---------------------------------------------------------
Nakamori Plugin
---------------------------------------------------------

Nakamori Addon is design for Kodi (initial version was released for 15.2 Isengard).
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
REPORTING ISSUES and REQUESTS
---------------------------------------------------------
For requests please use "[request]"


---------------------------------------------------------
INSTALATION
---------------------------------------------------------
I) Installing from repository 
  1) Adding Repository to Kodi
  
  System > File manager 
  
  Add source:
  
  location: http://bigretromike.github.io/
  
  name: BigRetroMike Repo
  
  System > Settings > Add-ons
  
  Install from zip file
  
  Pick 'BigRetroMike Repo' and 'repository.bigretromike.zip'
  

  2) Installing plugin from repository
  
  System > Settings > Add-ons
  
  Install from repository
  
  Pick 'BigRetroMike Repo' > 'Video add-ons' > 'Nakamori Plugin'
  
  In new window pick 'Install'
  
  
  - OR - 
  

II) Installing from zip file

  1) Download plugin from https://github.com/bigretromike/nakamoriplugin/archive/master.zip 
  
  2) Rename it to plugin.video.nakamoriplugin.zip
  
  3) Install zip file
  
  System > Settings > Add-ons
  
  Install from zip file
  
  Browser to location where you saved and rename zip file
  
  Pick the zip file



---------------------------------------------------------
SETTINGS
---------------------------------------------------------

If you are changing timeout setting then set also %AppData%\Roaming\Kodi\userdata\advancedsettings.xml to same value
```
<advancedsettings>
<playlisttimeout>60</playlisttimeout>
</advancedsettings>
```

If you dont want Kodi to mark watched videos as watched:
```
 <advancedsettings>
  <video>
    <playcountminimumpercent>101</playcountminimumpercent>
    <ignorepercentatend>101</ignorepercentatend>
  </video>
</advancedsettings>
```