# -*- coding: utf-8 -*-
from json import JSONEncoder
from json import JSONDecoder

# region auth


class AuthUser:
    def __init__(self, apikey):
        self.apikey = apikey['apikey']

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        return AuthUser(obj)

# endregion


# region init


class Version:
    def __init__(self, name, version):
        self.name, self.version = name, version

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        return Version(obj['Name'], obj['Version'])


class Status:
    def __init__(self, state, uptime, databaseblocked):
        # b'{"State":2,"Uptime":"13:53:59","DatabaseBlocked":{}}'
        self.state, self.uptime, self.databaseblocked = state, uptime, databaseblocked

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'State' in obj.keys():
            return Status(obj['State'], obj['Uptime'], obj['DatabaseBlocked'])
        return ''


# TODO cos jest nie tak, zwraca wartosc a nie obiekt
class InUse:
    def __init__(self, status):
        self.status = status

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        return InUse(obj)


class DefaultUser:
    def __init__(self, status):
        self.status = status

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        return InUse(obj)

# endregion


# region filter

class Filter:
    def __init__(self, ids, locked, name, size, directory, applyateerieslevel):
    # b'[{"IDs":{"ID":2},"Locked":true,"Name":"All","Size":3981},
    # {"IDs":{"ID":1},"Locked":true,"Name":"Continue Watching (SYSTEM)","Size":28},
    # {"IDs":{"ID":7},"Name":"Missing Episodes","Size":506},
    # {"IDs":{"ID":8},"Name":"Newly Added Series","Size":1},
    # {"IDs":{"ID":5},"Locked":true,"Directory":true,"Name":"Seasons","Size":232},
    # {"IDs":{"ID":3},"Locked":true,"Directory":true,"Name":"Tags","Size":1554},
    # {"IDs":{"ID":12},"ApplyAtSeriesLevel":true,"Name":"TvDB/MovieDB Link Missing","Size":2778},
    # {"IDs":{"ID":10},"ApplyAtSeriesLevel":true,"Name":"Votes Needed","Size":62},
    # {"IDs":{"ID":4},"Locked":true,"Directory":true,"Name":"Years","Size":95}]'
        self.ids = ids
        self.locked = locked
        self.name = name
        self.size = size
        self.directory = directory
        self.applyateerieslevel = applyateerieslevel

    def __repr__(self):
        return '<Filter(ids: {}, name: {}, size: {})>'.format(self.ids, self.name, self.size)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'IDs' in obj.keys():
            return Filter(obj.get('IDs', None), obj.get('Locked', None), obj.get('Name', None), obj.get('Size', None), obj.get('Directory', None), obj.get('ApplyAtSeriesLevel', None))
        return obj



# endregion



# region Series

# endregion