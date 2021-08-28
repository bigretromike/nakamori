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


class Group:
    def __init__(self, ids, name, size, sizes):
    # b'[{"IDs":{"ID":3981},"Name":"AWOL Compression Re-Mix","Size":1,"Sizes":{}]'
        self.ids = ids
        self.name = name
        self.size = size
        self.sizes = sizes  # {"Local":{"Episodes":4},"Watched":{},"Total":{"Episodes":4}}

    def __repr__(self):
        return '<Group(ids: {}, name: {}, size: {})>'.format(self.ids, self.name, self.size)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'IDs' in obj.keys():
            return Group(obj.get('IDs', None), obj.get('Name', None), obj.get('Size', None), obj.get('Sizes', None))
        return obj


class Series:
    def __init__(self, ids, images, created, updated, name, size, sizes):
    # b'[{"IDs":{"AniDB":16539,"ID":3981},
    # "Images":{"Posters":[{"Source":"AniDB","Type":"Poster","ID":"16539","RelativeFilepath":"/AniDB/16/263387.jpg"}]},
    # "Created":"2021-08-27T23:25:31.6502042+02:00",
    # "Updated":"2021-08-27T23:28:02.0002872+02:00",
    # "Name":"AWOL Compression Re-Mix",
    # "Size":4,
    # "Sizes":{"Local":{"Episodes":4},"Watched":{},"Total":{"Episodes":4}}}]'
        self.ids = ids
        self.images = images  #{"Posters":[{"Source":"AniDB","Type":"Poster","ID":"16539","RelativeFilepath":"/AniDB/16/263387.jpg"}]}
        self.created = created
        self.updated = updated
        self.name = name
        self.size = size
        self.sizes = sizes  # {"Local":{"Episodes":4},"Watched":{},"Total":{"Episodes":4}}

    def __repr__(self):
        return '<Series(ids: {}, name: {}, size: {})>'.format(self.ids, self.name, self.size)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'IDs' in obj.keys():
            return Series(obj.get('IDs', None), obj.get('Images', None), obj.get('Created', None), obj.get('Updated', None), obj.get('Name', None), obj.get('Size', None), obj.get('Sizes', None))
        return obj


class Episode:
    def __init__(self, ids, duration, name):
    # b'[{"IDs":{"AniDB":213179,"ID":473},
    # "Duration":"00:20:00",
    # "Name":"Target: Yuki - Sexual Guidance! Punish That Cheeky Girl"},
    # {"IDs":{"AniDB":214732,"ID":474},
    # "Duration":"00:20:00",
    # "Name":"Target: Yuki - Bitch Training! Milk That Beautiful-Breasted Tsundere Dry","Size":1},
    # {"IDs":{"AniDB":216620,"ID":475},
    # "Duration":"00:20:00",
    # "Name":"Target: Sayaka - Revelation of One\'s True Nature! Strip the Busty Honor Student\'s Disguise off Her","Size":1}]'
        self.ids = ids
        self.name = name
        self.duration = duration

    def __repr__(self):
        return '<Episode(ids: {}, name: {}, duration: {})>'.format(self.ids, self.name, self.duration)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'IDs' in obj.keys():
            return Episode(obj.get('IDs', None), obj.get('Duration', None), obj.get('Name', None))
        return obj

# endregion



# region Series

# endregion