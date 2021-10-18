# -*- coding: utf-8 -*-

from enum import IntEnum


class ThisType(IntEnum):
    filters = 0
    filter = 1
    group = 2
    series = 3
    # episodes type
    credits = 4
    episode = 5
    parody = 6
    special = 7
    trailer = 8
    other = 9
    # end of eps type
    file = 10
    raw = 11


def map_episodetype_to_thistype(input_type: str) -> ThisType:
    this = input_type.lower()
    if this == "episode":
        return ThisType.episode
    elif this == "special":
        return ThisType.special
    else:
        return ThisType.other


def map_filter_group_to_thistype(input_type: str) -> ThisType:
    this = input_type.lower()
    if this == 'filter':
        return ThisType.filter
    elif this == 'filters':
        return ThisType.filters
