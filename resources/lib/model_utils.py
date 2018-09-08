# -*- coding: utf-8 -*-
from collections import defaultdict

import nakamoritools as nt


def populate_tag_setting_flags():
    """
    Get user settings from local Kodi, and use them with Nakamori
    :rtype: object
    :return: setting_flags
    """
    tag_setting_flags = 0
    tag_setting_flags |= 0b000001 if nt.addon.getSetting('hideMiscTags') == 'true' else 0
    tag_setting_flags |= 0b000010 if nt.addon.getSetting('hideArtTags') == 'true' else 0
    tag_setting_flags |= 0b000100 if nt.addon.getSetting('hideSourceTags') == 'true' else 0
    tag_setting_flags |= 0b001000 if nt.addon.getSetting('hideUsefulMiscTags') == 'true' else 0
    tag_setting_flags |= 0b010000 if nt.addon.getSetting('hideSpoilerTags') == 'true' else 0
    tag_setting_flags |= 0b100000 if nt.addon.getSetting('hideSettingTags') == 'true' else 0
    return tag_setting_flags


def get_tags(tag_node):
    """
    Get the tags from the new style
    Args:
        tag_node: node containing group

    Returns: a string of all of the tags formatted

    """
    try:
        if tag_node is None:
            return ''
        if len(tag_node) > 0:
            temp_genres = []
            for tag in tag_node:
                if isinstance(tag, str) or isinstance(tag, unicode):
                    temp_genres.append(tag)
                else:
                    temp_genre = nt.decode(tag["tag"]).strip()
                    temp_genres.append(temp_genre)
            temp_genre = " | ".join(temp_genres)
            return temp_genre
        else:
            return ''
    except Exception as exc:
        nt.error('util.error generating tags', str(exc))
        return ''


def get_cast_and_role_new(data):
    """
    Get cast from the json and arrange in the new setCast format
    Args:
        data: json node containing 'roles'

    Returns: a list of dictionaries for the cast
    """
    result_list = []
    if data is not None and len(data) > 0:
        for char in data:
            char_charname = char.get("character", "")
            char_seiyuuname = char.get("staff", "")
            char_seiyuupic = nt.server + char.get("character_image", "")

            # only add it if it has data
            # reorder these to match the convention (Actor is cast, character is role, in that order)
            if len(char_charname) != 0:
                actor = {
                    'name':         char_seiyuuname,
                    'role':         char_charname,
                    'thumbnail':    char_seiyuupic
                }
                result_list.append(actor)
        if len(result_list) == 0:
            return None
        return result_list
    return None


def get_cast_and_role(data):
    """
    Get cast from the json and arrange in the new setCast format
    Args:
        data: json node containing 'roles'

    Returns: a list of dictionaries for the cast
    """
    result_list = []
    if data is not None and len(data) > 0:
        for char in data:
            char_charname = char["role"]
            char_seiyuuname = char['name']
            char_seiyuupic = char["rolepic"]

            # only add it if it has data
            # reorder these to match the convention (Actor is cast, character is role, in that order)
            if len(char_charname) != 0:
                actor = {
                    'name':         char_seiyuuname,
                    'role':         char_charname,
                    'thumbnail':    char_seiyuupic
                }
                result_list.append(actor)
        if len(result_list) == 0:
            return None
        return result_list
    return None


def convert_cast_and_role_to_legacy(list_of_dicts):
    """
    Convert standard cast_and_role to version supported by Kodi16 and lower
    :param list_of_dicts:
    :return: list
    """

    result_list = []
    list_cast = []
    list_cast_and_role = []
    if list_of_dicts is not None and len(list_of_dicts) > 0:
        for actor in list_of_dicts:
            seiyuu = actor.get('name', '')
            role = actor.get('role', '')
            if len(role) != 0:
                list_cast.append(role)
                if len(seiyuu) != 0:
                    list_cast_and_role.append((seiyuu, role))
        result_list.append(list_cast)
        result_list.append(list_cast_and_role)
    return result_list


def get_title(data):
    """
    Get the new title
    Args:
        data: json node containing the title

    Returns: string of the desired title

    """
    try:
        if 'titles' not in data or nt.addon.getSetting('use_server_title') == 'true':
            return nt.decode(data.get('name', ''))
        # xbmc.log(data.get('title', 'Unknown'))
        title = nt.decode(data.get('name', '').lower())
        if title == 'ova' or title == 'ovas' \
                or title == 'episode' or title == 'episodes' \
                or title == 'special' or title == 'specials' \
                or title == 'parody' or title == 'parodies' \
                or title == 'credit' or title == 'credits' \
                or title == 'trailer' or title == 'trailers' \
                or title == 'other' or title == 'others':
            return nt.decode(data.get('name', ''))

        lang = nt.addon.getSetting("displaylang")
        title_type = nt.addon.getSetting("title_type")
        try:
            for titleTag in data.get("titles", []):
                if titleTag.get("Type", "").lower() == title_type.lower():
                    if titleTag.get("Language", "").lower() == lang.lower():
                        if nt.decode(titleTag.get("Title", "")) == "":
                            continue
                        return nt.decode(titleTag.get("Title", ""))
            # fallback on language any title
            for titleTag in data.get("titles", []):
                if titleTag.get("Type", "").lower() != 'short':
                    if titleTag.get("Language", "").lower() == lang.lower():
                        if nt.decode(titleTag.get("Title", "")) == "":
                            continue
                        return nt.decode(titleTag.get("Title", ""))
            # fallback on x-jat main title
            for titleTag in data.get("titles", []):
                if titleTag.get("Type", "").lower() == 'main':
                    if titleTag.get("Language", "").lower() == "x-jat":
                        if nt.decode(titleTag.get("Title", "")) == "":
                            continue
                        return nt.decode(titleTag.get("Title", ""))
            # fallback on directory title
            return nt.decode(data.get('name', ''))
        except Exception as expc:
            nt.error('util.error thrown on getting title', str(expc))
            return nt.decode(data.get('name', ''))
    except Exception as exw:
        nt.error("get_title Exception", str(exw))
        return 'util.error'


def set_watch_flag(extra_data, details):
    """
    Set the flag icon for the list item to the desired state based on watched episodes
    Args:
        extra_data: the extra_data dict
        details: the details dict
    """
    # Set up overlays for watched and unwatched episodes
    if extra_data['WatchedEpisodes'] == 0:
        details['playcount'] = 0
    elif extra_data['UnWatchedEpisodes'] == 0:
        details['playcount'] = 1
    else:
        extra_data['partialTV'] = 1


def video_file_information(node, detail_dict):
    """
    Process given 'node' and parse it to create proper file information dictionary 'detail_dict'
    :param node: node that contains file
    :param detail_dict: dictionary for output
    :return: dict
    """
    # Video
    if 'VideoStreams' not in detail_dict:
        detail_dict['VideoStreams'] = defaultdict(dict)
    if 'AudioStream' not in detail_dict:
        detail_dict['AudioStreams'] = defaultdict(dict)
    if 'SubStream' not in detail_dict:
        detail_dict['SubStreams'] = defaultdict(dict)

    if "videos" in node:
        for stream_node in node["videos"]:
            stream_info = node["videos"][stream_node]
            if not isinstance(stream_info, dict):
                continue
            streams = detail_dict.get('VideoStreams', defaultdict(dict))
            stream_id = int(stream_info["Index"])
            streams[stream_id]['VideoCodec'] = stream_info['Codec']
            streams['xVideoCodec'] = stream_info['Codec']
            streams[stream_id]['width'] = stream_info['Width']
            if 'width' not in streams:
                streams['width'] = stream_info['Width']
            streams['xVideoResolution'] = str(stream_info['Width'])
            streams[stream_id]['height'] = stream_info['Height']
            if 'height' not in streams:
                streams['height'] = stream_info['Height']
                streams[stream_id]['aspect'] = round(int(streams['width']) / int(streams['height']), 2)
            streams['xVideoResolution'] += "x" + str(stream_info['Height'])
            streams[stream_id]['duration'] = int(round(float(stream_info.get('Duration', 0)) / 1000, 0))
            detail_dict['VideoStreams'] = streams

    # Audio
    if "audios" in node:
        for stream_node in node["audios"]:
            stream_info = node["audios"][stream_node]
            if not isinstance(stream_info, dict):
                continue
            streams = detail_dict.get('AudioStreams', defaultdict(dict))
            stream_id = int(stream_info["Index"])
            streams[stream_id]['AudioCodec'] = stream_info["Codec"]
            streams['xAudioCodec'] = streams[stream_id]['AudioCodec']
            streams[stream_id]['AudioLanguage'] = stream_info["LanguageCode"] if "LanguageCode" in stream_info \
                else "unk"
            streams[stream_id]['AudioChannels'] = int(stream_info["Channels"]) if "Channels" in stream_info else 1
            streams['xAudioChannels'] = nt.safe_int(streams[stream_id]['AudioChannels'])
            detail_dict['AudioStreams'] = streams

    # Subtitle
    if "subtitles" in node:
        i = 0
        for stream_node in node["subtitles"]:
            stream_info = node["subtitles"][stream_node]
            if not isinstance(stream_info, dict):
                continue
            streams = detail_dict.get('SubStreams', defaultdict(dict))
            try:
                stream_id = int(stream_node)
            except:
                stream_id = i
            streams[stream_id]['SubtitleLanguage'] = stream_info["LanguageCode"] if "LanguageCode" in stream_info \
                else "unk"
            detail_dict['SubStreams'] = streams
            i += 1


global __tagSettingFlags__
__tagSettingFlags__ = populate_tag_setting_flags()
