# -*- coding: utf-8 -*-

from enum import IntEnum


class ThisType(IntEnum):
    filters = 0
    filter = 1
    group = 2
    series = 3
    # episodes type
    credits = 4
    episodes = 5
    parodies = 6
    specials = 7
    trailers = 8
    other = 9
    misc = 10
    movie = 11
    ova = 12
    tvepisodes = 13
    webclips = 14
    # end of eps type
    file = 15
    raw = 16
    # naka types
    menu = 98
    none = 99


class WatchedStatus(IntEnum):
    UNWATCHED = 0
    PARTIAL = 1
    WATCHED = 2


def map_episodetype_to_thistype(input_type: str) -> ThisType:
    this = input_type.lower()
    if this == "episode":
        return ThisType.episodes
    elif this == "special":
        return ThisType.specials
    else:
        return ThisType.other


def map_filter_group_to_thistype(input_type: str) -> ThisType:
    this = input_type.lower()
    if this == 'filter':
        return ThisType.filter
    elif this == 'filters':
        return ThisType.filters


def map_thitype_to_eptype(input_type: ThisType) -> str:
    if input_type == ThisType.episodes:
        return 'episodes'
    elif input_type == ThisType.credits:
        return 'credits'
    elif input_type == ThisType.misc:
        return 'misc'
    elif input_type == ThisType.movie:
        return 'movie'
    elif input_type == ThisType.other:
        return 'other'
    elif input_type == ThisType.ova:
        return 'ova'
    elif input_type == ThisType.parodies:
        return 'parodies'
    elif input_type == ThisType.specials:
        return 'specials'
    elif input_type == ThisType.trailers:
        return 'trailes'
    elif input_type == ThisType.tvepisodes:
        return 'tvepisodes'
    elif input_type == ThisType.webclips:
        return 'webclips'
