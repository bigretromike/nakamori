# -*- coding: utf-8 -*-
from json import JSONEncoder
from json import JSONDecoder


class AuthUser:
    def __init__(self, apikey):
        self.apikey = apikey['apikey']

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        return AuthUser(obj)

class QueryOptions:
    def __init__(self, query: str = '', limit: int = 0, limit_tag: int = 0, filter: int = 0, tags: int = 0, tagfilter: int = 0, fuzzy: int = 0, nocast: int = 0, notag: int = 0, id: int = 0, score: int = 0, offset: int = 0, level: int = 0, all: int = 0, progress: int = 0, status: int = 0, ismovie: int = 0, filename: str = '', hash: str = '', allpics: int = 0, pic: int = 0, skip: int = 0):
        self.query = query
        self.limit = limit
        self.limit_tag = limit_tag
        self.filter = filter
        self.tags = tags
        self.tagfilter = tagfilter
        self.fuzzy = fuzzy
        self.nocast = nocast
        self.notag = notag
        self.id = id
        self.score = score
        self.offset = offset
        self.level = level
        self.all = all
        self.progress = progress
        self.status = status
        self.ismovie = ismovie
        self.filename = filename
        self.hash = hash
        self.allpics = allpics
        self.pic = pic
        self.skip = skip

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        return QueryOptions(obj)
