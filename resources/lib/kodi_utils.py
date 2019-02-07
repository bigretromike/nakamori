# -*- coding: utf-8 -*-
import sys
import os
import traceback

import xbmc
import xbmcaddon
import xbmcgui

from resources.lib import model_utils

import nakamoritools as nt
import nakamoriplayer as nplayer

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

if sys.version_info < (3, 0):
    from urllib import unquote
else:
    # For Python 3.0 and later
    # noinspection PyCompatibility,PyUnresolvedReferences
    from urllib.parse import unquote


busy = xbmcgui.DialogProgress()


def set_window_heading(window_name):
    """
    Sets the window titles
    Args:
        window_name: name to put in titles
    """
    if window_name == 'Continue Watching (SYSTEM)':
        window_name = 'Continue Watching'
    elif window_name == 'Unsort':
        window_name = 'Unsorted'

    window_obj = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    try:
        window_obj.setProperty("heading", str(window_name))
    except Exception as e:
        error('set_window_heading Exception', str(e))
        window_obj.clearProperty("heading")
    try:
        window_obj.setProperty("heading2", str(window_name))
    except Exception as e:
        error('set_window_heading2 Exception', str(e))
        window_obj.clearProperty("heading2")


def error(msg, error_type='Error', silent=False):
    """
    Log and notify the user of an error
    Args:
        msg: the message to print to log and user notification
        error_type: Type of Error
        silent: disable visual notification
    """
    xbmc.log("Nakamori " + str(nt.addonversion) + " id: " + str(nt.addonid), xbmc.LOGERROR)
    xbmc.log('---' + msg + '---', xbmc.LOGERROR)
    key = sys.argv[0]
    if len(sys.argv) > 2 and sys.argv[2] != '':
        key += sys.argv[2]
    xbmc.log('On url: ' + unquote(key), xbmc.LOGERROR)
    try:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        if exc_type is not None and exc_obj is not None and exc_tb is not None:
            xbmc.log(str(exc_type) + " at line " + str(exc_tb.tb_lineno) + " in file " + str(
                os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]), xbmc.LOGERROR)
            traceback.print_exc()
    except Exception as e:
        xbmc.log("There was an error catching the error. WTF.", xbmc.LOGERROR)
        xbmc.log("The error message: " + str(e), xbmc.LOGERROR)
        traceback.print_exc()
    if not silent:
        xbmc.executebuiltin('XBMC.Notification(%s, %s %s, 2000, %s)' % (error_type, ' ', msg,
                                                                        nt.addon.getAddonInfo('icon')))


def play_continue_item():
    """
    Move to next item that was not marked as watched
    Essential information are query from Parameters via util lib
    """
    params = nt.parse_parameters(sys.argv[2])
    if 'offset' in params:
        offset = params['offset']
        pos = int(offset)
        if pos == 1:
            xbmcgui.Dialog().ok(nt.addon.getLocalizedString(30182), nt.addon.getLocalizedString(30183))
        else:
            wind = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            control_id = wind.getFocusId()
            control_list = wind.getControl(control_id)
            nt.move_position_on_list(control_list, pos)
            xbmc.sleep(1000)
    else:
        pass


def file_list_gui(ep_body):
    """
    Create DialogBox with file list to pick if there is more than 1 file for episode
    :param ep_body:
    :return: int (id of picked file or 0 if none)
    """
    pick_filename = []
    get_fileid = []
    if len(ep_body['files']) > 1:
        for body in ep_body['files']:
            filename = os.path.basename(body['filename'])
            pick_filename.append(filename)
            get_fileid.append(str(body['id']))
        my_file = xbmcgui.Dialog().select(nt.addon.getLocalizedString(30196), pick_filename)
        if my_file > -1:
            return get_fileid[my_file]
        else:
            # cancel -1,0
            return 0
    elif len(ep_body['files']) == 1:
        return ep_body['files'][0]['id']
    else:
        return 0


def import_folder_list():
    """
    Create DialogBox with folder list to pick if there
    :return: int (vl of selected folder)
    """
    pick_folder = []
    get_id = []
    import_list = nt.json.loads(nt.get_json(nt.server + "/api/folder/list"))
    if len(import_list) > 1:
        for body in import_list:
            location = str(body['ImportFolderLocation'])
            pick_folder.append(location)
            get_id.append(str(body['ImportFolderID']))
        my_folder = xbmcgui.Dialog().select(nt.addon.getLocalizedString(30119), pick_folder)
        if my_folder > -1:
            return get_id[my_folder]
        else:
            # cancel -1,0
            return 0
    elif len(import_list) == 1:
        return import_list[0]['ImportFolderID']
    else:
        return 0


def play_video(ep_id, raw_id, movie):
    """
    Plays a file or episode
    Args:
        ep_id: episode id, if applicable for watched status and stream details
        raw_id: file id, that is only used when ep_id = 0
        movie: determinate if played object is movie or episode (ex.Trakt)
    Returns:

    """
    details = {
        'plot':          xbmc.getInfoLabel('ListItem.Plot'),
        'title':         xbmc.getInfoLabel('ListItem.Title'),
        'sorttitle':     xbmc.getInfoLabel('ListItem.Title'),
        'rating':        xbmc.getInfoLabel('ListItem.Rating'),
        'duration':      xbmc.getInfoLabel('ListItem.Duration'),
        'mpaa':          xbmc.getInfoLabel('ListItem.Mpaa'),
        'year':          xbmc.getInfoLabel('ListItem.Year'),
        'tagline':       xbmc.getInfoLabel('ListItem.Tagline'),
        'episode':       xbmc.getInfoLabel('ListItem.Episode'),
        'aired':         xbmc.getInfoLabel('ListItem.Premiered'),
        'tvshowtitle':   xbmc.getInfoLabel('ListItem.TVShowTitle'),
        'votes':         xbmc.getInfoLabel('ListItem.Votes'),
        'originaltitle': xbmc.getInfoLabel('ListItem.OriginalTitle'),
        'size':          xbmc.getInfoLabel('ListItem.Size'),
        'season':        xbmc.getInfoLabel('ListItem.Season'),
        'epid':          ep_id,  # player
        'movie':         movie,  # player
        'fileid':        0,      # player, coded below
        'rawid':         raw_id  # player
    }

    file_id = ''
    file_url = ''
    file_body = None
    offset = 0
    item = ''

    resume = nt.addon.getSetting('resume') == '1'
    nt.addon.setSetting('resume', '0')

    try:
        if ep_id != "0":
            episode_url = nt.server + "/api/ep?id=" + str(ep_id)
            episode_url = nt.set_parameter(episode_url, "level", "1")
            html = nt.get_json(nt.encode(episode_url))
            if nt.addon.getSetting("spamLog") == "true":
                xbmc.log(html, xbmc.LOGWARNING)
            episode_body = nt.json.loads(html)
            if nt.addon.getSetting("pick_file") == "true":
                file_id = file_list_gui(episode_body)
            else:
                file_id = episode_body["files"][0]["id"]
        else:
            file_id = raw_id

        if file_id is not None and file_id != 0:
            details['fileid'] = file_id
            file_url = nt.server + "/api/file?id=" + str(file_id)
            file_body = nt.json.loads(nt.get_json(file_url))

            file_url = file_body['url']
            server_path = file_body.get('server_path', '')
            if server_path is not None and server_path != '':
                try:
                    if os.path.isfile(server_path):
                        if nt.python_two:
                            # noinspection PyCompatibility
                            if unicode(server_path).startswith('\\\\'):
                                server_path = "smb:"+server_path
                        else:
                            if server_path.startswith('\\\\'):
                                server_path = "smb:"+server_path
                        file_url = server_path
                except:
                    pass

            # Information about streams inside video file
            # Video
            codecs = dict()
            model_utils.video_file_information(file_body["media"], codecs)
            details['path'] = file_url
            details['duration'] = file_body.get('duration', 0)
            details['size'] = file_body['size']

            item = xbmcgui.ListItem(details.get('title', 'Unknown'),
                                    thumbnailImage=xbmc.getInfoLabel('ListItem.Thumb'),
                                    path=file_url)
            item.setInfo(type='Video', infoLabels=details)

            if 'offset' in file_body:
                offset = file_body.get('offset', 0)
                if offset != 0:
                    offset = int(offset) / 1000
                    if nt.addon.getSetting("file_resume") == "true" and resume:
                        item.setProperty('ResumeTime', str(offset))
                        item.setProperty('StartOffset', str(offset))

            for stream_index in codecs["VideoStreams"]:
                if not isinstance(codecs["VideoStreams"][stream_index], dict):
                    continue
                item.addStreamInfo('video', codecs["VideoStreams"][stream_index])
            for stream_index in codecs["AudioStreams"]:
                if not isinstance(codecs["AudioStreams"][stream_index], dict):
                    continue
                item.addStreamInfo('audio', codecs["AudioStreams"][stream_index])
            for stream_index in codecs["SubStreams"]:
                if not isinstance(codecs["SubStreams"][stream_index], dict):
                    continue
                item.addStreamInfo('subtitle', codecs["SubStreams"][stream_index])
        else:
            if nt.addon.getSetting("pick_file") == "false":
                nt.error("file_id not retrieved")
            return 0
    except Exception as exc:
        nt.error('util.error getting episode info', str(exc))

    m3u8_url = ''
    is_transcoded = False

    # region Eigakan
    try:
        if nt.addon.getSetting("enableEigakan") == "true":
            eigakan_url = nt.addon.getSetting("ipEigakan")
            eigakan_port = nt.addon.getSetting("portEigakan")
            eigakan_host = 'http://' + eigakan_url + ':' + eigakan_port
            video_url = eigakan_host + '/api/transcode/' + str(file_id)
            post_data = '"file":"' + file_url + '"'
            try_count = 0
            m3u8_url = eigakan_host + '/api/video/' + str(file_id) + '/play.m3u8'
            ts_url = eigakan_host + '/api/video/' + str(file_id) + '/play0.ts'

            try:
                eigakan_data = nt.get_json(eigakan_host + '/api/version')
                if 'eigakan' in eigakan_data:
                    audio_stream_id = -1
                    stream_index = -1
                    for audio_code in nt.addon.getSetting("audiolangEigakan").split(","):
                        for audio_stream in file_body['media']['audios']:
                            stream_index += 1
                            if 'Language' in file_body['media']['audios'][audio_stream]:
                                if audio_code in file_body['media']['audios'][audio_stream].get('Language').lower():
                                    audio_stream_id = stream_index
                                    break
                            if 'LanguageCode' in file_body['media']['audios'][audio_stream]:
                                if audio_code in file_body['media']['audios'][audio_stream].get('LanguageCode').lower():
                                    audio_stream_id = stream_index
                                    break
                            if 'Title' in file_body['media']['audios'][audio_stream]:
                                if audio_code in file_body['media']['audios'][audio_stream].get('Language').lower():
                                    audio_stream_id = stream_index
                                    break
                        if audio_stream_id != -1:
                            break

                    sub_stream_id = -1
                    stream_index = -1
                    for sub_code in nt.addon.getSetting("subEigakan").split(","):
                        for sub_stream in file_body['media']['subtitles']:
                            stream_index += 1
                            if 'Language' in file_body['media']['subtitles'][sub_stream]:
                                if sub_code in file_body['media']['subtitles'][sub_stream].get('Language').lower():
                                    sub_stream_id = stream_index
                                    break
                            if 'LanguageCode' in file_body['media']['subtitles'][sub_stream]:
                                if sub_code in file_body['media']['subtitles'][sub_stream].get('LanguageCode').lower():
                                    sub_stream_id = stream_index
                                    break
                            if 'Title' in file_body['media']['subtitles'][sub_stream]:
                                if sub_code in file_body['media']['subtitles'][sub_stream].get('Language').lower():
                                    sub_stream_id = stream_index
                                    break
                        if sub_stream_id != -1:
                            break

                    busy.create(nt.addon.getLocalizedString(30160), nt.addon.getLocalizedString(30165))

                    if audio_stream_id != -1:
                        post_data += ',"audio_stream":"' + str(audio_stream_id) + '"'
                    if sub_stream_id != -1:
                        post_data += ',"subtitles_stream":"' + str(sub_stream_id) + '"'

                    if nt.addon.getSetting("advEigakan") == "true":
                        post_data += ',"resolution":"' + nt.addon.getSetting("resolutionEigakan") + '"'
                        post_data += ',"audio_codec":"' + nt.addon.getSetting("audioEigakan") + '"'
                        post_data += ',"video_bitrate":"' + nt.addon.getSetting("vbitrateEigakan") + '"'
                        post_data += ',"x264_profile":"' + nt.addon.getSetting("profileEigakan") + '"'
                    nt.post_json(video_url, post_data)
                    xbmc.sleep(1000)
                    busy.close()

                    busy.create(nt.addon.getLocalizedString(30160), nt.addon.getLocalizedString(30164))
                    while True:
                        if nt.head(url_in=ts_url) is False:
                            x_try = int(nt.addon.getSetting("tryEigakan"))
                            if try_count > x_try:
                                break
                            if busy.iscanceled():
                                break
                            try_count += 1
                            busy.update(try_count)
                            xbmc.sleep(1000)
                        else:
                            break
                    busy.close()

                    postpone_seconds = int(nt.addon.getSetting("postponeEigakan"))
                    if postpone_seconds > 0:
                        busy.create(nt.addon.getLocalizedString(30160), nt.addon.getLocalizedString(30166))
                        while postpone_seconds > 0:
                            xbmc.sleep(1000)
                            postpone_seconds -= 1
                            busy.update(postpone_seconds)
                            if busy.iscanceled():
                                break
                        busy.close()

                    if nt.head(url_in=ts_url):
                        is_transcoded = True

                else:
                    nt.error("Eigakan server is unavailable")
            except Exception as exc:
                nt.error('eigakan.post_json error', str(exc))
                busy.close()
    except Exception as eigakan_ex:
        xbmc.log('---> enableEigakan: ' + str(eigakan_ex), xbmc.LOGWARNING)
        pass
    # endregion

    player = nplayer.Service()
    player.feed(details)

    try:
        if is_transcoded:
            details['path'] = m3u8_url
            player.feed(details)
            player.play(item=m3u8_url)
        else:
            player.play(item=file_url, listitem=item)

    except Exception as player_ex:
        xbmc.log('---> player_ex: ' + str(player_ex), xbmc.LOGWARNING)
        pass

    # leave player alive so we can handle onPlayBackStopped/onPlayBackEnded
    xbmc.sleep(int(nt.addon.getSetting("player_sleep")))

    # while player.isPlaying():
    #     xbmc.sleep(500)
    while player.PlaybackStatus != 'Stopped' and player.PlaybackStatus != 'Ended':
        xbmc.sleep(500)

    if player.PlaybackStatus == 'Ended':
        xbmc.log(' Ended -------~ ~~ ~ ----> ' + str(xbmc.abortRequested), xbmc.LOGWARNING)
        return -1
    else:
        xbmc.log('player.PlaybackStatus=============' + str(player.PlaybackStatus))

    xbmc.log('-------~ ~~ ~ ----> ' + str(xbmc.abortRequested), xbmc.LOGWARNING)
    return 0


def wizard():
    """
    Run wizard if there weren't any before
    :return: nothing, set ip/port user/password in settings
    """
    if nt.addon.getSetting('wizard') == '0':
        xbmc.executebuiltin('RunScript(script.module.nakamori,?info=wizard)', True)


def detect_kodi18():
    """
    Detect if Kodi user run is not-yet-released 18.x
    check if '3' (unknown), set 1 if kodi18, set 0 if anything else
    :return: this function dont return anything, only set 'kodi18' in settings
    """
    if nt.addon.getSetting('kodi18') == '3':
        python = xbmcaddon.Addon('xbmc.addon')
        if python is not None:
            # kodi18 return 17.9.xxx as for now later it will be 18.x
            if str(python.getAddonInfo('version')).startswith('17.9.') or str(python.getAddonInfo('version')).startswith('18.0'):
                nt.addon.setSetting(id='kodi18', value='1')
            else:
                nt.addon.setSetting(id='kodi18', value='0')


def fix_mark_watch_in_kodi_db():
    """
    Clear mark for nakamori files in kodi db
    :return:
    """
    ret = xbmcgui.Dialog().yesno(nt.addon.getLocalizedString(30104),
                                 nt.addon.getLocalizedString(30081), nt.addon.getLocalizedString(30112))
    if ret:
        db_files = []
        db_path = os.path.join(nt.decode(xbmc.translatePath('special://home')), 'userdata')
        db_path = os.path.join(db_path, 'Database')
        for r, d, f in os.walk(db_path):
            for files in f:
                if "MyVideos" in files:
                    db_files.append(files)
        for db_file in db_files:
            db_connection = database.connect(os.path.join(db_path, db_file))
            db_cursor = db_connection.cursor()
            db_cursor.execute('DELETE FROM files WHERE strFilename like "%plugin.video.nakamori%"')
            db_connection.commit()
            db_connection.close()
        if len(db_files) > 0:
            xbmcgui.Dialog().ok('', nt.addon.getLocalizedString(30138))


def clear_image_cache_in_kodi_db():
    """
    Clear image cache in kodi db
    :return:
    """
    ret = xbmcgui.Dialog().yesno(nt.addon.getLocalizedString(30104),
                                 nt.addon.getLocalizedString(30081), nt.addon.getLocalizedString(30112))
    if ret:
        db_files = []
        db_path = os.path.join(nt.decode(xbmc.translatePath('special://home')), 'userdata')
        db_path = os.path.join(db_path, 'Database')
        for r, d, f in os.walk(db_path):
            for files in f:
                if "Textures" in files:
                    db_files.append(files)
        for db_file in db_files:
            db_connection = database.connect(os.path.join(db_path, db_file))
            db_cursor = db_connection.cursor()
            db_cursor.execute('DELETE FROM texture WHERE url LIKE "%' + nt.addon.getSetting('port') + '/api/%"')
            db_connection.commit()
            db_cursor.execute('DELETE FROM texture WHERE url LIKE "%nakamori%"')
            db_connection.commit()
            db_connection.close()
        if len(db_files) > 0:
            xbmcgui.Dialog().ok('', nt.addon.getLocalizedString(30138))
