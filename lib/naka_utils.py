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


def map_episodetype_int_to_thistype(input_type: int) -> ThisType:
    if input_type == int(ThisType.episodes):
        return ThisType.episodes
    elif input_type == int(ThisType.credits):
        return ThisType.credits
    elif input_type == int(ThisType.misc):
        return ThisType.misc
    elif input_type == int(ThisType.movie):
        return ThisType.movie
    elif input_type == int(ThisType.other):
        return ThisType.other
    elif input_type == int(ThisType.ova):
        return ThisType.ova
    elif input_type == int(ThisType.parodies):
        return ThisType.parodies
    elif input_type == int(ThisType.specials):
        return ThisType.specials
    elif input_type == int(ThisType.trailers):
        return ThisType.trailers
    elif input_type == int(ThisType.tvepisodes):
        return ThisType.tvepisodes
    elif input_type == int(ThisType.webclips):
        return ThisType.webclips


def map_episodetype_to_thistype(input_type: str) -> ThisType:
    this = input_type.lower()
    if this == "episode":
        return ThisType.episodes
    elif this == "special":
        return ThisType.specials
    elif this == "credits":
        return ThisType.credits
    elif this == "trailer":
        return ThisType.trailers
    elif this == "parody":
        return ThisType.parodies
    elif this == "other":
        return ThisType.other
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
        return 'Episodes'
    elif input_type == ThisType.credits:
        return 'Credits'
    elif input_type == ThisType.misc:
        return 'Misc'
    elif input_type == ThisType.movie:
        return 'Movie'
    elif input_type == ThisType.other:
        return 'Other'
    elif input_type == ThisType.ova:
        return 'OVA'
    elif input_type == ThisType.parodies:
        return 'Parodies'
    elif input_type == ThisType.specials:
        return 'Specials'
    elif input_type == ThisType.trailers:
        return 'Trailes'
    elif input_type == ThisType.tvepisodes:
        return 'TVEpisodes'
    elif input_type == ThisType.webclips:
        return 'WebClips'
