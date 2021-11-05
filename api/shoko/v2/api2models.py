# -*- coding: utf-8 -*-
from json import JSONEncoder
from sys import int_info

from typing import List


class AuthUser:
    def __init__(self, 
                user: str = '',
                password: str = '',
                device: str = "nakamori"):
        self.user: str = user
        self.password: str = password
        self.device: str = device

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return AuthUser()
        authuser: AuthUser = AuthUser()
        
        authuser.user = json.get("user")
        authuser.password = json.get("pass")
        authuser.device = json.get("device")

        return authuser


class QueryOptions:
    def __init__(self,
                query: str = None,
                limit: int = None,
                limit_tag: int = None,
                filter: int = None,
                tags: int = None,
                tagfilter: int = None,
                fuzzy: int = None,
                nocast: int = None,
                notag: int = None,
                id: int = None,
                score: int = None,
                offset: int = None,
                level: int = None,
                all: int = None,
                progress: int = None,
                status: int = None,
                ismovie: int = None,
                filename: str = None,
                hash: str = None,
                allpics: int = None,
                pic: int = None,
                skip: int = None
                ):
        self.query: str = query
        self.limit: int = limit
        self.limit_tag: int = limit_tag
        self.filter: int = filter
        self.tags: int = tags
        self.tagfilter: int = tagfilter
        self.fuzzy: int = fuzzy
        self.nocast: int = nocast
        self.notag: int = notag
        self.id: int = id
        self.score: int = score
        self.offset: int = offset
        self.level: int = level
        self.all: int = all
        self.progress: int = progress
        self.status: int = status
        self.ismovie: int = ismovie
        self.filename: str = filename
        self.hash: str = hash
        self.allpics: int = allpics
        self.pic: int = pic
        self.skip: int = skip

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(obj):
        return QueryOptions(obj.get('query'),
                            obj.get('limit'),
                            obj.get('limit_tag'),
                            obj.get('filter'),
                            obj.get('tags'),
                            obj.get('tagfilter'),
                            obj.get('fuzzy'),
                            obj.get('nocast'),
                            obj.get('notag'),
                            obj.get('id'),
                            obj.get('score'),
                            obj.get('offset'),
                            obj.get('level'),
                            obj.get('all'),
                            obj.get('progress'),
                            obj.get('status'),
                            obj.get('ismovie'),
                            obj.get('filename'),
                            obj.get('hash'),
                            obj.get('allpics'),
                            obj.get('pic'),
                            obj.get('skip'))


class AnimeTitle:
    def __init__(self,
                Type: str = '',
                Language: str = '',
                Title: str = ''
                ):
        self.Type: str = Type
        self.Language: str = Language
        self.Title: str = Title

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return AnimeTitle()
        animetitle: AnimeTitle = AnimeTitle()

        animetitle.Type = json.get("Type")
        animetitle.Language = json.get("Language")
        animetitle.Title = json.get("Title")

        return animetitle


class Sizes:
    def __init__(self,
                Episodes: int = 0,
                Specials: int = 0,
                Credits: int = 0,
                Trailers: int = 0,
                Parodies: int = 0,
                Others: int = 0
                ):
        self.Episodes: int = Episodes
        self.Specials: int = Specials
        self.Credits: int = Credits
        self.Trailers: int = Trailers
        self.Parodies: int = Parodies
        self.Others: int = Others

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                # print(json)
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return Sizes()
                
        sizes: Sizes = Sizes()

        sizes.Episodes = json.get("Episodes")
        sizes.Specials = json.get("Specials")
        sizes.Credits = json.get("Credits")
        sizes.Trailers = json.get("Trailers")
        sizes.Parodies = json.get("Parodies")
        sizes.Others = json.get("Others")

        return sizes


class Role:
    def __init__(self,
                 character: str = '',
                 character_image: str = '',
                 character_description: str = '',
                 staff: str = '',
                 staff_image: str = '',
                 staff_description: str = '',
                 role: str = '',
                 type: str = ''
                 ):
        self.character: str = character
        self.character_image: str = character_image
        self.character_description: str = character_description
        self.staff: str = staff
        self.staff_image: str = staff_image
        self.staff_description: str = staff_description
        self.role: str = role
        self.type: str = type
    
    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return Role()
        role: Role = Role()

        role.character = json.get("character")
        role.character_image = json.get("character_image")
        role.character_description = json.get("character_description")
        role.staff = json.get("staff")
        role.staff_image = json.get("staff_image")
        role.staff_description = json.get("staff_description")
        role.role = json.get("role")
        role.type = json.get("type")

        return role


class Art:
    def __init__(self,
                 url: str = '',
                 index: int = 0
                 ):
        self.url: str = url
        self.index: int = index

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return Art()
        art: Art = Art()

        art.url = json.get("url")
        art.index = json.get("index")

        return art


class ArtCollection:
    def __init__(self,
                 banner: List[Art] = [],
                 fanart: List[Art] = [],
                 thumb: List[Art] = []
                 ):
        self.banner: List[Art] = banner
        self.fanart: List[Art] = fanart
        self.thumb: List[Art] = thumb

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return ArtCollection()

        artcollection: ArtCollection = ArtCollection()

        artcollection.banner = []
        tmp = json.get("banner", [])
        for art in tmp:
            art = Art.Decoder(art)
            artcollection.banner.append(art)
        artcollection.fanart = []
        tmp = json.get("fanart", [])
        for art in tmp:
            art = Art.Decoder(art)
            artcollection.fanart.append(art)
        artcollection.thumb = []
        tmp = json.get("thumb", [])
        for art in tmp:
            art = Art.Decoder(art)
            artcollection.thumb.append(art)

        return artcollection


class General:
    def __init__(self,
                 id = {},
                 format = {},
                 format_version = {},
                 size = {},
                 duration = {},
                 overallbitrate = {},
                 overallbitrate_mode = {},
                 encoded = {},
                 encoded_date = {},
                 encoded_lib = {},
                 attachments = {}
                 ):
        self.id = id
        self.format = format
        self.format_version = format_version
        self.size = size
        self.duration = duration
        self.overallbitrate = overallbitrate
        self.overallbitrate_mode = overallbitrate_mode
        self.encoded = encoded
        self.encoded_date = encoded_date
        self.encoded_lib = encoded_lib
        self.attachments = attachments

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return General()
        general: General = General()
        
        general.id = json.get("id")
        general.format = json.get("format")
        general.format_version = json.get("format_version")
        general.size = json.get("size")
        general.duration = json.get("duration")
        general.overallbitrate = json.get("overallbitrate")
        general.overallbitrate_mode = json.get("overallbitrate_mode")
        general.encoded = json.get("encoded")
        general.encoded_date = json.get("encoded_date")
        general.encoded_lib = json.get("encoded_lib")
        general.attachments = json.get("attachments")

        return general


class Stream:
    def __init__(self,
                 Title: str = '',
                 Language: str = '',
                 Key: str = '',
                 Duration: int = 0,
                 Height: int = 0,
                 Width: int = 0,
                 Bitrate: int = 0,
                 SubIndex: int = 0,
                 Id: int = 0,
                 ScanType: str = '',
                 RefFrames: int = 0,
                 Profile: str = '',
                 Level: int = 0,
                 HeaderStripping: int = 0,
                 HasScalingMatrix: int = 0,
                 FrameRateMode: str = '',
                 File: str = '',
                 FrameRate: float = 0.0,
                 ColorSpace: str = '',
                 CodecID: str = '',
                 ChromaSubsampling: str = '',
                 Cabac: int = 0,
                 BitDepth: int = 0,
                 Index: int = 0,
                 Codec: str = '',
                 StreamType: int = 0,
                 Orientation: int = 0,
                 QPel: int = 0,
                 GMC: str = '',
                 BVOP: int = 0,
                 SamplingRate: int = 0,
                 LanguageCode: str = '',
                 Channels: int = 0,
                 Selected: int = 0,
                 DialogNorm: str = '',
                 BitrateMode: str = '',
                 Format: str = '',
                 Default: int = 0,
                 Forced: int = 0,
                 PixelAspectRatio: str = '',
                 ):
        self.Title: str = Title
        self.Language: str = Language
        self.Key: str = Key
        self.Duration: int = Duration
        self.Height: int = Height
        self.Width: int = Width
        self.Bitrate: int = Bitrate
        self.SubIndex: int = SubIndex
        self.Id: int = Id
        self.ScanType: str = ScanType
        self.RefFrames: int = RefFrames
        self.Profile: str = Profile
        self.Level: int = Level
        self.HeaderStripping: int = HeaderStripping
        self.HasScalingMatrix: int = HasScalingMatrix
        self.FrameRateMode: str = FrameRateMode
        self.File: str = File
        self.FrameRate: float = FrameRate
        self.ColorSpace: str = ColorSpace
        self.CodecID: str = CodecID
        self.ChromaSubsampling: str = ChromaSubsampling
        self.Cabac: int = Cabac
        self.BitDepth: int = BitDepth
        self.Index: int = Index
        self.Codec: str = Codec
        self.StreamType: int = StreamType
        self.Orientation: int = Orientation
        self.QPel: int = QPel
        self.GMC: str = GMC
        self.BVOP: int = BVOP
        self.SamplingRate: int = SamplingRate
        self.LanguageCode: str = LanguageCode
        self.Channels: int = Channels
        self.Selected: int = Selected
        self.DialogNorm: str = DialogNorm
        self.BitrateMode: str = BitrateMode
        self.Format: str = Format
        self.Default: int = Default
        self.Forced: int = Forced
        self.PixelAspectRatio: str = PixelAspectRatio
    
    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return Stream()
        stream: Stream = Stream()

        stream.Title = json.get("Title")
        stream.Language = json.get("Language")
        stream.Key = json.get("Key")
        stream.Duration = json.get("Duration")
        stream.Height = json.get("Height")
        stream.Width = json.get("Width")
        stream.Bitrate = json.get("Bitrate")
        stream.SubIndex = json.get("SubIndex")
        stream.Id = json.get("Id")
        stream.ScanType = json.get("ScanType")
        stream.RefFrames = json.get("RefFrames")
        stream.Profile = json.get("Profile")
        stream.Level = json.get("Level")
        stream.HeaderStripping = json.get("HeaderStripping")
        stream.HasScalingMatrix = json.get("HasScalingMatrix")
        stream.FrameRateMode = json.get("FrameRateMode")
        stream.File = json.get("File")
        stream.FrameRate = json.get("FrameRate")
        stream.ColorSpace = json.get("ColorSpace")
        stream.CodecID = json.get("CodecID")
        stream.ChromaSubsampling = json.get("ChromaSubsampling")
        stream.Cabac = json.get("Cabac")
        stream.BitDepth = json.get("BitDepth")
        stream.Index = json.get("Index")
        stream.Codec = json.get("Codec")
        stream.StreamType = json.get("StreamType")
        stream.Orientation = json.get("Orientation")
        stream.QPel = json.get("QPel")
        stream.GMC = json.get("GMC")
        stream.BVOP = json.get("BVOP")
        stream.SamplingRate = json.get("SamplingRate")
        stream.LanguageCode = json.get("LanguageCode")
        stream.Channels = json.get("Channels")
        stream.Selected = json.get("Selected")
        stream.DialogNorm = json.get("DialogNorm")
        stream.BitrateMode = json.get("BitrateMode")
        stream.Format = json.get("Format")
        stream.Default = json.get("Default")
        stream.Forced = json.get("Forced")
        stream.PixelAspectRatio = json.get("PixelAspectRatio")

        return stream
        

class MediaInfo:
    def __init__(self,
                 general: General = {},
                 audios: List[Stream] = [],
                 videos: List[Stream] = [],
                 subtitles: List[Stream] = [],
                 menus: List[Stream] = []
                 ):
        self.general: General = general
        self.audios: List[Stream] = audios
        self.videos: List[Stream] = videos
        self.subtitles: List[Stream] = subtitles
        self.menus: List[Stream] = menus

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return MediaInfo()
        mediainfo: MediaInfo = MediaInfo()

        mediainfo.general = General.Decoder(json.get("general"))
        for a in json.get("audios", []):
            mediainfo.audios.append(Stream.Decoder(a))
        for a in json.get("videos", []):
            mediainfo.videos.append(Stream.Decoder(a))
        for a in json.get("subtitles", []):
            mediainfo.subtitles.append(Stream.Decoder(a))
        for a in json.get("menus", []):
            mediainfo.menus.append(Stream.Decoder(a))

        return mediainfo


class RawFile:
    def __init__(self,
                type: str = '',
                crc32: str = '',
                ed2khash: str = '',
                md5: str = '',
                sha1: str = '',
                created: str = '',
                updated: str = '',
                duration: int = 0,
                filename: str = '',
                server_path: str = '',
                size: int = 0,
                hash: str = '',
                hash_source: int = 0,
                is_ignored: int = 0,
                media: MediaInfo = {},
                group_full: str = '',
                group_short: str = '',
                group_id: int = 0,
                recognized: bool = False,
                offset: int = 0,
                videolocal_place_id: int = 0,
                import_folder_id: int = 0,
                is_preferred: int = 0,
                id: int = 0,
                name: str = '',
                titles: List[AnimeTitle] = [],
                summary: str = '',
                url: str = '',
                added: str = '',
                edited: str = '',
                year: str = '',
                air: str = '',
                localsize: int = 0,
                total_sizes: Sizes = {},
                local_sizes: Sizes = {},
                watched_sizes: Sizes = {},
                viewed: int = 0,
                rating: str = '',
                votes: str = '',
                userrating: str = '',
                roles: List[Role] = [],
                tags: List[str] = [],
                art: ArtCollection = {}
    ):
        self.type: str = type
        self.crc32: str = crc32
        self.ed2khash: str = ed2khash
        self.md5: str = md5
        self.sha1: str = sha1
        self.created: str = created
        self.updated: str = updated
        self.duration: int = duration
        self.filename: str = filename
        self.server_path: str = server_path
        self.hash: str = hash
        self.hash_source: int = hash_source
        self.is_ignored: int = is_ignored
        self.media: MediaInfo = media
        self.group_full: str = group_full
        self.group_short: str = group_short
        self.group_id: int = group_id
        self.recognized: bool = recognized
        self.offset: int = offset
        self.videolocal_place_id: int = videolocal_place_id
        self.import_folder_id: int = import_folder_id
        self.is_preferred: int = is_preferred
        self.id: int = id
        self.name: str = name
        self.titles: List[AnimeTitle] = titles
        self.summary: str = summary
        self.url: str = url
        self.added: str = added
        self.edited: str = edited
        self.year: str = year
        self.air: str = air
        self.size: int = size
        self.localsize: int = localsize
        self.total_sizes: Sizes = total_sizes
        self.local_sizes: Sizes = local_sizes
        self.watched_sizes: Sizes = watched_sizes
        self.viewed: int = viewed
        self.rating: str = rating
        self.votes: str = votes
        self.userrating: str = userrating
        self.roles: List[Role] = roles
        self.tags: List[str] = tags
        self.art: ArtCollection = art

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return RawFile()
        rawfile: RawFile = RawFile()

        rawfile.type = json.get("type")
        rawfile.crc32 = json.get("crc32")
        rawfile.ed2khash = json.get("ed2khash")
        rawfile.md5 = json.get("md5")
        rawfile.sha1 = json.get("sha1")
        rawfile.created = json.get("created")
        rawfile.updated = json.get("updated")
        rawfile.duration = json.get("duration")
        rawfile.filename = json.get("filename")
        rawfile.server_path = json.get("server_path")
        rawfile.hash = json.get("hash")
        rawfile.hash_source = json.get("hash_source")
        rawfile.is_ignored = json.get("is_ignored")
        rawfile.media = MediaInfo.Decoder(json.get("media"))
        rawfile.group_full = json.get("group_full")
        rawfile.group_short = json.get("group_short")
        rawfile.group_id = json.get("group_id")
        rawfile.recognized = json.get("recognized")
        rawfile.offset = json.get("offset")
        rawfile.videolocal_place_id = json.get("videolocal_place_id")
        rawfile.import_folder_id = json.get("import_folder_id")
        rawfile.is_preferred = json.get("is_preferred")
        rawfile.id = json.get("id")
        rawfile.name = json.get("name")
        rawfile.titles = []
        tmp = json.get("titles", [])
        for title in tmp:
            title = AnimeTitle.Decoder(title)
            rawfile.titles.append(title)
        rawfile.summary = json.get("summary")
        rawfile.url = json.get("url")
        rawfile.added = json.get("added")
        rawfile.edited = json.get("edited")
        rawfile.year = json.get("year")
        rawfile.air = json.get("air")
        rawfile.size = json.get("size")
        rawfile.localsize = json.get("localsize")
        rawfile.total_sizes = Sizes.Decoder(json.get('total_sizes'))
        rawfile.local_sizes = Sizes.Decoder(json.get('local_sizes'))
        rawfile.watched_sizes = Sizes.Decoder(json.get('watched_sizes'))
        rawfile.viewed = json.get("viewed")
        rawfile.rating = json.get("rating")
        rawfile.votes = json.get("votes")
        rawfile.userrating = json.get("userrating")
        rawfile.roles = []
        tmp = json.get("roles", [])
        for role in tmp:
            role = Role.Decoder(role)
            rawfile.roles.append(role)        
            rawfile.tags = []
        tmp = json.get("tags", [])
        for tag in tmp:
            rawfile.tags.append(tag)        
        rawfile.art = ArtCollection.Decoder(json.get("art"))

        return rawfile


class RecentFile:
    def __init__(self,
                 series_id: int = 0,
                 ep_id: int = 0,
                 type: str = '',
                 crc32: str = '',
                 ed2khash: str = '',
                 md5: str = '',
                 sha1: str = '',
                 created: str = '',
                 updated: str = '',
                 duration: int = 0,
                 filename: str = '',
                 server_path: str = '',
                 size: int = 0,
                 hash: str = '',
                 hash_source: int = 0,
                 is_ignored: int = 0,
                 media: MediaInfo = {},
                 group_full: str = '',
                 group_short: str = '',
                 group_id: int = 0,
                 recognized: bool = False,
                 offset: int = 0,
                 videolocal_place_id: int = 0,
                 import_folder_id: int = 0,
                 is_preferred: int = 0,
                 id: int = 0,
                 name: str = '',
                 titles: List[AnimeTitle] = [],
                 summary: str = '',
                 url: str = '',
                 added: str = '',
                 edited: str = '',
                 year: str = '',
                 air: str = '',
                 localsize: int = 0,
                 total_sizes: Sizes = {},
                 local_sizes: Sizes = {},
                 watched_sizes: Sizes = {},
                 viewed: int = 0,
                 rating: str = '',
                 votes: str = '',
                 userrating: str = '',
                 roles: List[Role] = [],
                 tags: List[str] = [],
                 art: ArtCollection = {}
                 ):
        self.series_id: int = series_id
        self.ep_id: int = ep_id
        self.type: str = type
        self.crc32: str = crc32
        self.ed2khash: str = ed2khash
        self.md5: str = md5
        self.sha1: str = sha1
        self.created: str = created
        self.updated: str = updated
        self.duration: int = duration
        self.filename: str = filename
        self.server_path: str = server_path
        self.hash: str = hash
        self.hash_source: int = hash_source
        self.is_ignored: int = is_ignored
        self.media: MediaInfo = media
        self.group_full: str = group_full
        self.group_short: str = group_short
        self.group_id: int = group_id
        self.recognized: bool = recognized
        self.offset: int = offset
        self.videolocal_place_id: int = videolocal_place_id
        self.import_folder_id: int = import_folder_id
        self.is_preferred: int = is_preferred
        self.id: int = id
        self.name: str = name
        self.titles: List[AnimeTitle] = titles
        self.summary: str = summary
        self.url: str = url
        self.added: str = added
        self.edited: str = edited
        self.year: str = year
        self.air: str = air
        self.size: int = size
        self.localsize: int = localsize
        self.total_sizes: Sizes = total_sizes
        self.local_sizes: Sizes = local_sizes
        self.watched_sizes: Sizes = watched_sizes
        self.viewed: int = viewed
        self.rating: str = rating
        self.votes: str = votes
        self.userrating: str = userrating
        self.roles: List[Role] = roles
        self.tags: List[str] = tags
        self.art: ArtCollection = art

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return RecentFile()
        recentfile: RecentFile = RecentFile()

        recentfile.series_id = json.get("series_id")
        recentfile.ep_id = json.get("ep_id")
        recentfile.type = json.get("type")
        recentfile.crc32 = json.get("crc32")
        recentfile.ed2khash = json.get("ed2khash")
        recentfile.md5 = json.get("md5")
        recentfile.sha1 = json.get("sha1")
        recentfile.created = json.get("created")
        recentfile.updated = json.get("updated")
        recentfile.duration = json.get("duration")
        recentfile.filename = json.get("filename")
        recentfile.server_path = json.get("server_path")
        recentfile.hash = json.get("hash")
        recentfile.hash_source = json.get("hash_source")
        recentfile.is_ignored = json.get("is_ignored")
        recentfile.media = MediaInfo.Decoder(json.get("media"))
        recentfile.group_full = json.get("group_full")
        recentfile.group_short = json.get("group_short")
        recentfile.group_id = json.get("group_id")
        recentfile.recognized = json.get("recognized")
        recentfile.offset = json.get("offset")
        recentfile.videolocal_place_id = json.get("videolocal_place_id")
        recentfile.import_folder_id = json.get("import_folder_id")
        recentfile.is_preferred = json.get("is_preferred")
        recentfile.id = json.get("id")
        recentfile.name = json.get("name")
        recentfile.titles = []
        tmp = json.get("titles", [])
        for title in tmp:
            title = AnimeTitle.Decoder(title)
            recentfile.titles.append(title)
        recentfile.summary = json.get("summary")
        recentfile.url = json.get("url")
        recentfile.added = json.get("added")
        recentfile.edited = json.get("edited")
        recentfile.year = json.get("year")
        recentfile.air = json.get("air")
        recentfile.size = json.get("size")
        recentfile.localsize = json.get("localsize")
        recentfile.total_sizes = Sizes.Decoder(json.get('total_sizes'))
        recentfile.local_sizes = Sizes.Decoder(json.get('local_sizes'))
        recentfile.watched_sizes = Sizes.Decoder(json.get('watched_sizes'))
        recentfile.viewed = json.get("viewed")
        recentfile.rating = json.get("rating")
        recentfile.votes = json.get("votes")
        recentfile.userrating = json.get("userrating")
        recentfile.roles = []
        tmp = json.get("roles", [])
        for role in tmp:
            role = Role.Decoder(role)
            recentfile.roles.append(role)        
            recentfile.tags = []
        tmp = json.get("tags", [])
        for tag in tmp:
            recentfile.tags.append(tag)        
        recentfile.art = ArtCollection.Decoder(json.get("art"))

        return recentfile


class Episode:
    def __init__(self,
                 type: str = '',
                 season: str = '',
                 view: int = 0,
                 view_date: str = '',
                 eptype: str = '',
                 epnumber: int = 0,
                 aid: int = 0,
                 eid: int = 0,
                 files: List[RawFile] = [],
                 id: int = 0,
                 name: str = '',
                 titles: List[AnimeTitle] = [],
                 summary: str = '',
                 url: str = '',
                 added: str = '',
                 edited: str = '',
                 year: str = '',
                 air: str = '',
                 size: int = 0,
                 localsize: int = 0,
                 total_sizes: Sizes = {},
                 local_sizes: Sizes = {},
                 watched_sizes: Sizes = {},
                 viewed: int = 0,
                 rating: str = '',
                 votes: str = '',
                 userrating: int = 0,
                 roles: List[Role] = [],
                 tags: List[str] = [],
                 art: ArtCollection = {}
                 ):
        self.type: str = type
        self.season: str = season
        self.view: int = view
        self.view_date: str = view_date
        self.eptype: str = eptype
        self.epnumber: int = epnumber
        self.aid: int = aid
        self.eid: int = eid
        self.files: List[RawFile] = files
        self.id: int = id
        self.name: str = name
        self.titles: List[AnimeTitle] = titles
        self.summary: str = summary
        self.url: str = url
        self.added: str = added
        self.edited: str = edited
        self.year: str = year
        self.air: str = air
        self.size: int = size
        self.localsize: int = localsize
        self.total_sizes: Sizes = total_sizes
        self.local_sizes: Sizes = local_sizes
        self.watched_sizes: Sizes = watched_sizes
        self.viewed: int = viewed
        self.rating: str = rating
        self.votes: str = votes
        self.userrating: int = userrating
        self.roles: List[Role] = roles
        self.tags: List[str] = tags
        self.art: ArtCollection = art

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return Episode()
        episode: Episode = Episode()

        episode.type = json.get("type")
        episode.season = json.get("season")
        episode.view = json.get("view")
        episode.view_date = json.get("view_date")
        episode.eptype = json.get("eptype")
        episode.epnumber = json.get("epnumber")
        episode.aid = json.get("aid")
        episode.eid = json.get("eid")
        episode.files = []
        tmp = json.get("files", [])
        for file in tmp:
            file = RawFile.Decoder(file)
            episode.files.append(file)
        episode.id = json.get("id")
        episode.name = json.get("name")
        episode.titles = []
        tmp = json.get("titles", [])
        for title in tmp:
            title = AnimeTitle.Decoder(title)
            episode.titles.append(title)
        episode.summary = json.get("summary")
        episode.url = json.get("url")
        episode.added = json.get("added")
        episode.edited = json.get("edited")
        episode.year = json.get("year")
        episode.air = json.get("air")
        episode.size = json.get("size")
        episode.localsize = json.get("localsize")
        episode.total_sizes = Sizes.Decoder(json.get('total_sizes'))
        episode.local_sizes = Sizes.Decoder(json.get('local_sizes'))
        episode.watched_sizes = Sizes.Decoder(json.get('watched_sizes'))
        episode.viewed = json.get("viewed")
        episode.rating = json.get("rating")
        episode.votes = json.get("votes")
        episode.userrating = json.get("userrating", 0)
        episode.roles = []
        tmp = json.get("roles", [])
        for role in tmp:
            role = Role.Decoder(role)
            episode.roles.append(role)        
            episode.tags = []
        tmp = json.get("tags", [])
        for tag in tmp:
            episode.tags.append(tag)        
        episode.art = ArtCollection.Decoder(json.get("art"))

        return episode


class Serie:
    def __init__(self,
                 type: str = '',
                 aid: int = 0,
                 season: str = '',
                 eps: List[Episode] = [],
                 ismovie: int = 0,
                 filesize: int = 0,
                 id: int = 0,
                 name: str = '',
                 titles: List[AnimeTitle] = [],
                 summary: str = '',
                 match: str = '',
                 url: str = '',
                 added: str = '',
                 edited: str = '',
                 year: str = '',
                 air: str = '',
                 size: int = 0,
                 localsize: int = 0,
                 total_sizes: Sizes = {},
                 local_sizes: Sizes = {},
                 watched_sizes: Sizes = {},
                 viewed: int = 0,
                 rating: str = '',
                 votes: str = '',
                 userrating: int = 0,
                 roles: List[Role] = [],
                 tags: List[str] = [],
                 art: ArtCollection = {}
                 ):
        self.type: str = type
        self.aid: int = aid
        self.season: str = season
        self.eps: List[Episode] = eps
        self.ismovie: int = ismovie
        self.filesize: int = filesize
        self.id: int = id
        self.name: str = name
        self.titles: List[AnimeTitle] = titles
        self.summary: str = summary
        self.match: str = match
        self.url: str = url
        self.added: str = added
        self.edited: str = edited
        self.year: str = year
        self.air: str = air
        self.size: int = size
        self.localsize: int = localsize
        self.total_sizes: Sizes = total_sizes
        self.local_sizes: Sizes = local_sizes
        self.watched_sizes: Sizes = watched_sizes
        self.viewed: int = viewed
        self.rating: str = rating
        self.votes: str = votes
        self.userrating: int = userrating
        self.roles: List[Role] = roles
        self.tags: List[str] = tags
        self.art: ArtCollection = art

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return Serie()
        serie: Serie = Serie()

        serie.type = json.get("type")
        serie.aid = json.get("aid")
        serie.season = json.get("season")
        serie.eps = []
        tmp = json.get("eps", [])
        for ep in tmp:
            ep = Episode.Decoder(ep)
            serie.eps.append(ep)
        serie.ismovie = json.get("ismovie")
        serie.filesize = json.get("filesize")
        serie.id = json.get("id")
        serie.name = json.get("name")
        serie.titles = []
        tmp = json.get("titles", [])
        for title in tmp:
            title = AnimeTitle.Decoder(title)
            serie.titles.append(title)
        serie.summary = json.get("summary")
        serie.match = json.get("match")
        serie.url = json.get("url")
        serie.added = json.get("added")
        serie.edited = json.get("edited")
        serie.year = json.get("year")
        serie.air = json.get("air")
        serie.size = json.get("size")
        serie.localsize = json.get("localsize")
        serie.total_sizes = Sizes.Decoder(json.get('total_sizes'))
        serie.local_sizes = Sizes.Decoder(json.get('local_sizes'))
        serie.watched_sizes = Sizes.Decoder(json.get('watched_sizes'))
        serie.viewed = json.get("viewed")
        serie.rating = json.get("rating")
        serie.votes = json.get("votes")
        serie.userrating = json.get("userrating", 0)
        serie.roles = []
        tmp = json.get("roles", [])
        for role in tmp:
            role = Role.Decoder(role)
            serie.roles.append(role)        
        serie.tags = []
        tmp = json.get("tags", [])
        for tag in tmp:
            serie.tags.append(tag)        
        serie.art = ArtCollection.Decoder(json.get("art"))

        return serie


class Group:
    def __init__(self,
                 series: List[Serie] = [],
                 type: str = '',
                 id: int = 0,
                 name: str = '',
                 titles: List[AnimeTitle] = [],
                 summary: str = '',
                 url: str = '',
                 added: str = '',
                 edited: str = '',
                 year: str = '',
                 air: str = '',
                 size: int = 0,
                 localsize: int = 0,
                 total_sizes: Sizes = {},
                 local_sizes: Sizes = {},
                 watched_sizes: Sizes = {},
                 viewed: int = 0,
                 rating: str = '',
                 votes: str = '',
                 userrating: str = '',
                 roles: List[Role] = [],
                 tags: List[str] = [],
                 art: ArtCollection = {}
                 ):
        self.series: List[Serie] = series
        self.type: str = type
        self.id: int = id
        self.name: str = name
        self.titles: List[AnimeTitle] = titles
        self.summary: str = summary
        self.url: str = url
        self.added: str = added
        self.edited: str = edited
        self.year: str = year
        self.air: str = air
        self.size: int = size
        self.localsize: int = localsize
        self.total_sizes: Sizes = total_sizes
        self.local_sizes: Sizes = local_sizes
        self.watched_sizes: Sizes = watched_sizes
        self.viewed: int = viewed
        self.rating: str = rating
        self.votes: str = votes
        self.userrating: str = userrating
        self.roles: List[Role] = roles
        self.tags: List[str] = tags
        self.art: ArtCollection = art
    
    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return Group()
        group: Group = Group()

        group.series = []
        tmp = json.get("series", [])
        for serie in tmp:
            serie = Serie.Decoder(serie)
            group.series.append(serie)
        group.type = json.get("type")
        group.id = json.get("id")
        group.name = json.get("name")
        group.titles = []
        tmp = json.get("titles", [])
        for title in tmp:
            title = AnimeTitle.Decoder(title)
            group.titles.append(title)
        group.summary = json.get("summary")
        group.url = json.get("url")
        group.added = json.get("added")
        group.edited = json.get("edited")
        group.year = json.get("year")
        group.air = json.get("air")
        group.size = json.get("size")
        group.localsize = json.get("localsize")
        group.total_sizes = Sizes.Decoder(json.get("total_sizes"))
        group.local_sizes = Sizes.Decoder(json.get("local_sizes"))
        group.watched_sizes = Sizes.Decoder(json.get("watched_sizes"))
        group.viewed = json.get("viewed")
        group.rating = json.get("rating")
        group.votes = json.get("votes")
        group.userrating = json.get("userrating")
        group.roles = []
        tmp = json.get("roles", [])
        for role in tmp:
            role = Role.Decoder(role)
            group.roles.append(role)
        group.tags = []
        tmp = json.get("tags", [])
        for tag in tmp:
            group.tags.append(tag)
        group.art = ArtCollection.Decoder(json.get("art"))
        
        return group


class Filter:
    def __init__(self,
                 type: str = '',
                 groups: List[Group] = [],
                 filters: list = [],
                 id: int = 0,
                 name: str = '',
                 titles: List[AnimeTitle] = [],
                 summary: str = '',
                 url: str = '',
                 added: str = '',
                 edited: str = '',
                 year: str = '',
                 air: str = '',
                 size: int = 0,
                 localsize: int = 0,
                 total_sizes: Sizes = [],
                 local_sizes: Sizes = [],
                 watched_sizes: Sizes = [],
                 viewed: int = 0,
                 rating: str = '',
                 votes: str = '',
                 userrating: str = '',
                 roles: List[Role] = [],
                 tags: List[str] = [],
                 art: ArtCollection = {}
                 ):
        self.type: str = type
        self.groups: List[Group] = groups
        self.filters: List[Filter] = filters
        self.id: int = id
        self.name: str = name
        self.titles: List[AnimeTitle] = titles
        self.summary: str = summary
        self.url: str = url
        self.added: str = added
        self.edited: str = edited
        self.year: str = year
        self.air: str = air
        self.size: int = size
        self.localsize: int = localsize
        self.total_sizes: Sizes = total_sizes
        self.local_sizes: Sizes = local_sizes
        self.watched_sizes: Sizes = watched_sizes
        self.viewed: int = viewed
        self.rating: str = rating
        self.votes: str = votes
        self.userrating: str = userrating
        self.roles: List[Role] = roles
        self.tags: List[str] = tags
        self.art: ArtCollection = art

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return Filter()

        filter = Filter(id=json.get("id"), name=json.get("name"), type=json.get('type'))
        filter.groups = []  # <--- ain't this default value ?
        filter.titles = []  # <--- ain't this default value ?

        for _group in json.get("groups", []):
            group = Group.Decoder(_group)
            filter.groups.append(group)
        filter.filters = []

        for _filter in json.get("filters", []):
            __filter = Filter.Decoder(_filter)
            filter.filters.append(__filter)

        for _title in json.get("titles", []):
            title = AnimeTitle.Decoder(_title)
            filter.titles.append(title)
        filter.summary = json.get("summary")
        filter.url = json.get("url")
        filter.added = json.get("added")
        filter.edited = json.get("edited")
        filter.year = json.get("year")
        filter.air = json.get("air")
        filter.size = json.get("size")
        filter.localsize = json.get("localsize")
        filter.total_sizes = Sizes.Decoder(json.get('total_sizes'))
        filter.local_sizes = Sizes.Decoder(json.get('local_sizes'))
        filter.watched_sizes = Sizes.Decoder(json.get('watched_sizes'))
        filter.viewed = json.get("viewed")
        filter.rating = json.get("rating")
        filter.votes = json.get("votes")
        filter.userrating = json.get("userrating")
        filter.roles = []

        for role in json.get("roles", []):
            role = Role.Decoder(role)
            filter.roles.append(role)        
        filter.tags = []

        for tag in json.get("tags", []):
            filter.tags.append(tag)        

        filter.art = ArtCollection.Decoder(json.get("art"))

        return filter


class ImportFolder:
    def __init__(self,
                 ImportFolderID: int = 0,
                 ImportFolderType: int = 0,
                 ImportFolderName: str = '',
                 ImportFolderLocation: str = '',
                 CloudID: int = 0,
                 IsWatched: int = 0,
                 IsDropSource: int = 0,
                 IsDropDestination: int = 0
                 ):
        self.ImportFolderID: int = ImportFolderID
        self.ImportFolderType: int = ImportFolderType
        self.ImportFolderName: str = ImportFolderName
        self.ImportFolderLocation: str = ImportFolderLocation
        self.CloudID: int = CloudID
        self.IsWatched: int = IsWatched
        self.IsDropSource: int = IsDropSource
        self.IsDropDestination: int = IsDropDestination
        
    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return ImportFolder()
        importfolder: ImportFolder = ImportFolder()

        importfolder.ImportFolderID = json.get("ImportFolderID")
        importfolder.ImportFolderType = json.get("ImportFolderType")
        importfolder.ImportFolderName = json.get("ImportFolderName")
        importfolder.ImportFolderLocation = json.get("ImportFolderLocation")
        importfolder.CloudID = json.get("CloudID")
        importfolder.IsWatched = json.get("IsWatched")
        importfolder.IsDropSource = json.get("IsDropSource")
        importfolder.IsDropDestination = json.get("IsDropDestination")

        return importfolder


class Counter:
    def __init__(self, 
                count: int = 0
                ):
        self.count: int = count

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return Counter()
        counter: Counter = Counter()

        counter.count = json.get("count")

        return counter


class WebNews:
    def __init__(self,
                date: str = '',
                link: str = '',
                title: str = '',
                description: str = '',
                author: str = ''
                ):
        self.date: str = date
        self.link: str = link
        self.title: str = title
        self.description: str = description
        self.author: str = author
        
    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return WebNews()
        webnews: WebNews = WebNews()
        
        webnews.date = json.get("date")
        webnews.link = json.get("link")
        webnews.title = json.get("title")
        webnews.description = json.get("description")
        webnews.author = json.get("author")
        
        return webnews


class QueueInfo:
    def __init__(self,
                 count: int = 0,
                 state: str = '',
                 isrunning: str = '',
                 ispause: str = ''
                 ):
        self.count: int = count
        self.state: str = state
        self.isrunning: str = isrunning
        self.ispause: str = ispause

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return QueueInfo()
        queueinfo: QueueInfo = QueueInfo()

        queueinfo.count = json.get("count")
        queueinfo.state = json.get("state")
        queueinfo.isrunning = json.get("isrunning")
        queueinfo.ispause = json.get("ispause")

        return queueinfo


class SeriesInFolderInfo:
    def __init__(self,
                 name: str = '',
                 id: int = 0,
                 filesize: int = 0,
                 size: int = 0,
                 paths: List[str] = []
                 ):
        self.name: str = name
        self.id: int = id
        self.filesize: int = filesize
        self.size: int = size
        self.paths: List[str] = paths

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return SeriesInFolderInfo()
        seriesinfolderinfo: SeriesInFolderInfo = SeriesInFolderInfo()

        seriesinfolderinfo.name = json.get("name")
        seriesinfolderinfo.id = json.get("id")
        seriesinfolderinfo.filesize = json.get("filesize")
        seriesinfolderinfo.size = json.get("size")
        seriesinfolderinfo.paths = []
        tmp = json.get("paths", [])
        for path in tmp:
            seriesinfolderinfo.paths.append(path)

        return seriesinfolderinfo


class FolderInfo:
    def __init__(self,
               id: int = 0,
               filesize: int = 0,
               size: int = 0,
               series: List[SeriesInFolderInfo] = {}
                ):
        self.id: int = id
        self.filesize: int = filesize
        self.size: int = size
        self.series: List[SeriesInFolderInfo] = series

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return FolderInfo()
        folderinfo: FolderInfo = FolderInfo()

        folderinfo.id = json.get("id")
        folderinfo.filesize = json.get("filesize")
        folderinfo.size = json.get("size")
        folderinfo.series = []
        tmp = json.get("series", [])
        for serie in tmp:
            serie = SeriesInFolderInfo.Decoder(serie)
            folderinfo.series.append(serie)

        return folderinfo


class ImagePath:
    def __init__(self, 
                path: str = '',
                isdefault: bool = False
                ):
        self.path: str = path
        self.isdefault: bool = isdefault

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return ImagePath()
        imagepath: ImagePath = ImagePath()

        imagepath.path = json.get("path")
        imagepath.isdefault = json.get("isdefault")

        return imagepath


class LogRotatorSettings:
    def __init__(self,
                Enabled: bool = True,
                Zip: bool = True,
                Delete: bool = True,
                Delete_Days: str = ''
                ):
        self.Enabled: bool = Enabled
        self.Zip: bool = Zip
        self.Delete: bool = Delete
        self.Delete_Days: str = Delete_Days

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return LogRotatorSettings()
        logrotatorsettings: LogRotatorSettings = LogRotatorSettings()

        logrotatorsettings.Enabled = json.get("Enabled")
        logrotatorsettings.Zip = json.get("Zip")
        logrotatorsettings.Delete = json.get("Delete")
        logrotatorsettings.Delete_Days = json.get("Delete_Days")

        return logrotatorsettings


class DatabaseSettings:
    def __init__(self,
                MySqliteDirectory: str = '',
                DatabaseBackupDirectory: str = '',
                Type: str = '',
                Username: str = '',
                Password: str = '',
                Schema: str = '',
                Hostname: str = '',
                SQLite_DatabaseFile: str = ''
                ):
        self.MySqliteDirectory: str = MySqliteDirectory
        self.DatabaseBackupDirectory: str = DatabaseBackupDirectory
        self.Type: str = Type
        self.Username: str = Username
        self.Password: str = Password
        self.Schema: str = Schema
        self.Hostname: str = Hostname
        self.SQLite_DatabaseFile: str = SQLite_DatabaseFile

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return DatabaseSettings()
        databasesettings: DatabaseSettings = DatabaseSettings()

        databasesettings.MySqliteDirectory = json.get("MySqliteDirectory")
        databasesettings.DatabaseBackupDirectory = json.get("DatabaseBackupDirectory")
        databasesettings.Type = json.get("Type")
        databasesettings.Username = json.get("Username")
        databasesettings.Password = json.get("Password")
        databasesettings.Schema = json.get("Schema")
        databasesettings.Hostname = json.get("Hostname")
        databasesettings.SQLite_DatabaseFile = json.get("SQLite_DatabaseFile")

        return databasesettings


class AniDBSettings:
    def __init__(self,
                Username: str = '',
                Password: str = '',
                ServerAddress: str = '',
                ServerPort: int = 0,
                ClientPort: int = 0,
                AVDumpKey: str = '',
                AVDumpClientPort: int = 0,
                DownloadRelatedAnime: bool = True,
                DownloadSimilarAnime: bool = True,
                DownloadReviews: bool = True,
                DownloadReleaseGroups: bool = True,
                MyList_AddFiles: bool = True,
                MyList_StorageState: int = 0,
                MyList_DeleteType: int = 0,
                MyList_ReadUnwatched: bool = True,
                MyList_ReadWatched: bool = True,
                MyList_SetWatched: bool = True,
                MyList_SetUnwatched: bool = True,
                MyList_UpdateFrequency: int = 1,
                Calendar_UpdateFrequency: int = 1,
                Anime_UpdateFrequency: int = 1,
                MyListStats_UpdateFrequency: int = 1,
                File_UpdateFrequency: int = 1,
                DownloadCharacters: bool = True,
                DownloadCreators: bool = True,
                MaxRelationDepth: int = 0
                ):
        self.Username: str = Username
        self.Password: str = Password
        self.ServerAddress: str = ServerAddress
        self.ServerPort: int = ServerPort
        self.ClientPort: int = ClientPort
        self.AVDumpKey: str = AVDumpKey
        self.AVDumpClientPort: int = AVDumpClientPort
        self.DownloadRelatedAnime: bool = DownloadRelatedAnime
        self.DownloadSimilarAnime: bool = DownloadSimilarAnime
        self.DownloadReviews: bool = DownloadReviews
        self.DownloadReleaseGroups: bool = DownloadReleaseGroups
        self.MyList_AddFiles: bool = MyList_AddFiles
        self.MyList_StorageState: int = MyList_StorageState
        self.MyList_DeleteType: int = MyList_DeleteType
        self.MyList_ReadUnwatched: bool = MyList_ReadUnwatched
        self.MyList_ReadWatched: bool = MyList_ReadWatched
        self.MyList_SetWatched: bool = MyList_SetWatched
        self.MyList_SetUnwatched: bool = MyList_SetUnwatched
        self.MyList_UpdateFrequency: int = MyList_UpdateFrequency
        self.Calendar_UpdateFrequency: int = Calendar_UpdateFrequency
        self.Anime_UpdateFrequency: int = Anime_UpdateFrequency
        self.MyListStats_UpdateFrequency: int = MyListStats_UpdateFrequency
        self.File_UpdateFrequency: int = File_UpdateFrequency
        self.DownloadCharacters: bool = DownloadCharacters
        self.DownloadCreators: bool = DownloadCreators
        self.MaxRelationDepth: int = MaxRelationDepth

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return AniDBSettings()
        anidbsettings: AniDBSettings = AniDBSettings()

        anidbsettings.Username = json.get("Username")
        anidbsettings.Password = json.get("Password")
        anidbsettings.ServerAddress = json.get("ServerAddress")
        anidbsettings.ServerPort = json.get("ServerPort")
        anidbsettings.ClientPort = json.get("ClientPort")
        anidbsettings.AVDumpKey = json.get("AVDumpKey")
        anidbsettings.AVDumpClientPort = json.get("AVDumpClientPort")
        anidbsettings.DownloadRelatedAnime = json.get("DownloadRelatedAnime")
        anidbsettings.DownloadSimilarAnime = json.get("DownloadSimilarAnime")
        anidbsettings.DownloadReviews = json.get("DownloadReviews")
        anidbsettings.DownloadReleaseGroups = json.get("DownloadReleaseGroups")
        anidbsettings.MyList_AddFiles = json.get("MyList_AddFiles")
        anidbsettings.MyList_StorageState = json.get("MyList_StorageState")
        anidbsettings.MyList_DeleteType = json.get("MyList_DeleteType")
        anidbsettings.MyList_ReadUnwatched = json.get("MyList_ReadUnwatched")
        anidbsettings.MyList_ReadWatched = json.get("MyList_ReadWatched")
        anidbsettings.MyList_SetWatched = json.get("MyList_SetWatched")
        anidbsettings.MyList_SetUnwatched = json.get("MyList_SetUnwatched")
        anidbsettings.MyList_UpdateFrequency = json.get("MyList_UpdateFrequency")
        anidbsettings.Calendar_UpdateFrequency = json.get("Calendar_UpdateFrequency")
        anidbsettings.Anime_UpdateFrequency = json.get("Anime_UpdateFrequency")
        anidbsettings.MyListStats_UpdateFrequency = json.get("MyListStats_UpdateFrequency")
        anidbsettings.File_UpdateFrequency = json.get("File_UpdateFrequency")
        anidbsettings.DownloadCharacters = json.get("DownloadCharacters")
        anidbsettings.DownloadCreators = json.get("DownloadCreators")
        anidbsettings.MaxRelationDepth = json.get("MaxRelationDepth")

        return anidbsettings


class WebCacheSettings:
    def __init__(self,
                Enabled: bool = True,
                Address: str = '',
                BannedReason: str = '',
                BannedExpiration: str = '',
                XRefFileEpisode_Get: bool = True,
                XRefFileEpisode_Send: bool = True,
                TvDB_Get: bool = True,
                TvDB_Send: bool = True,
                Trakt_Get: bool = True,
                Trakt_Send: bool = True
                ):
        self.Enabled: bool = Enabled
        self.Address: str = Address
        self.BannedReason: str = BannedReason
        self.BannedExpiration: str = BannedExpiration
        self.XRefFileEpisode_Get: bool = XRefFileEpisode_Get
        self.XRefFileEpisode_Send: bool = XRefFileEpisode_Send
        self.TvDB_Get: bool = TvDB_Get
        self.TvDB_Send: bool = TvDB_Send
        self.Trakt_Get: bool = Trakt_Get
        self.Trakt_Send: bool = Trakt_Send

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return WebCacheSettings()
        webcachesettings: WebCacheSettings = WebCacheSettings()

        webcachesettings.Enabled = json.get("Enabled")
        webcachesettings.Address = json.get("Address")
        webcachesettings.BannedReason = json.get("BannedReason")
        webcachesettings.BannedExpiration = json.get("BannedExpiration")
        webcachesettings.XRefFileEpisode_Get = json.get("XRefFileEpisode_Get")
        webcachesettings.XRefFileEpisode_Send = json.get("XRefFileEpisode_Send")
        webcachesettings.TvDB_Get = json.get("TvDB_Get")
        webcachesettings.TvDB_Send = json.get("TvDB_Send")
        webcachesettings.Trakt_Get = json.get("Trakt_Get")
        webcachesettings.Trakt_Send = json.get("Trakt_Send")

        return webcachesettings


class TvDBSettings:
    def __init__(self,
                AutoLink: bool = True,
                AutoFanart: bool = True,
                AutoFanartAmount: int = 0,
                AutoWideBanners: bool = True,
                AutoWideBannersAmount: int = 0,
                AutoPosters: bool = True,
                AutoPostersAmount: int = 0,
                UpdateFrequency: int = 1,
                Language: str = ''
                ):
        self.AutoLink: bool = AutoLink
        self.AutoFanart: bool = AutoFanart
        self.AutoFanartAmount: int = AutoFanartAmount
        self.AutoWideBanners: bool = AutoWideBanners
        self.AutoWideBannersAmount: int = AutoWideBannersAmount
        self.AutoPosters: bool = AutoPosters
        self.AutoPostersAmount: int = AutoPostersAmount
        self.UpdateFrequency: int = UpdateFrequency
        self.Language: str = Language

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return TvDBSettings()
        tvdbsettings: TvDBSettings = TvDBSettings()

        tvdbsettings.AutoLink = json.get("AutoLink")
        tvdbsettings.AutoFanart = json.get("AutoFanart")
        tvdbsettings.AutoFanartAmount = json.get("AutoFanartAmount")
        tvdbsettings.AutoWideBanners = json.get("AutoWideBanners")
        tvdbsettings.AutoWideBannersAmount = json.get("AutoWideBannersAmount")
        tvdbsettings.AutoPosters = json.get("AutoPosters")
        tvdbsettings.AutoPostersAmount = json.get("AutoPostersAmount")
        tvdbsettings.UpdateFrequency = json.get("UpdateFrequency")
        tvdbsettings.Language = json.get("Language")

        return tvdbsettings


class MovieDbSettings:
    def __init__(self,
                AutoFanart: bool = True,
                AutoFanartAmount: int = 0,
                AutoPosters: bool = True,
                AutoPostersAmount: int = 0
                ):
        self.AutoFanart: bool = AutoFanart
        self.AutoFanartAmount: int = AutoFanartAmount
        self.AutoPosters: bool = AutoPosters
        self.AutoPostersAmount: int = AutoPostersAmount

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return MovieDbSettings()
        moviedbsettings: MovieDbSettings = MovieDbSettings()

        moviedbsettings.AutoFanart = json.get("AutoFanart")
        moviedbsettings.AutoFanartAmount = json.get("AutoFanartAmount")
        moviedbsettings.AutoPosters = json.get("AutoPosters")
        moviedbsettings.AutoPostersAmount = json.get("AutoPostersAmount")

        return moviedbsettings


class ImportSettings:
    def __init__(self,
                VideoExtensions: List[str] = [],
                Exclude: List[str] = [],
                DefaultSeriesLanguage: int = 1,
                DefaultEpisodeLanguage: int = 1,
                RunOnStart: bool = True,
                ScanDropFoldersOnStart: bool = True,
                Hash_CRC32: bool = True,
                Hash_MD5: bool = True,
                Hash_SHA1: bool = True,
                UseExistingFileWatchedStatus: bool = True,
                AutomaticallyDeleteDuplicatesOnImport: bool = True,
                FileLockChecking: bool = True,
                AggressiveFileLockChecking: bool = True,
                FileLockWaitTimeMS: int = 0,
                AggressiveFileLockWaitTimeSeconds: int = 0,
                RenameThenMove: bool = True,
                RenameOnImport: bool = True,
                MoveOnImport: bool = True,
                MediaInfoPath: str = '',
                MediaInfoTimeoutMinutes: int = 0
                ):
        self.VideoExtensions: List[str] = VideoExtensions
        self.Exclude: List[str] = Exclude
        self.DefaultSeriesLanguage: int = DefaultSeriesLanguage
        self.DefaultEpisodeLanguage: int = DefaultEpisodeLanguage
        self.RunOnStart: bool = RunOnStart
        self.ScanDropFoldersOnStart: bool = ScanDropFoldersOnStart
        self.Hash_CRC32: bool = Hash_CRC32
        self.Hash_MD5: bool = Hash_MD5
        self.Hash_SHA1: bool = Hash_SHA1
        self.UseExistingFileWatchedStatus: bool = UseExistingFileWatchedStatus
        self.AutomaticallyDeleteDuplicatesOnImport: bool = AutomaticallyDeleteDuplicatesOnImport
        self.FileLockChecking: bool = FileLockChecking
        self.AggressiveFileLockChecking: bool = AggressiveFileLockChecking
        self.FileLockWaitTimeMS: int = FileLockWaitTimeMS
        self.AggressiveFileLockWaitTimeSeconds: int = AggressiveFileLockWaitTimeSeconds
        self.RenameThenMove: bool = RenameThenMove
        self.RenameOnImport: bool = RenameOnImport
        self.MoveOnImport: bool = MoveOnImport
        self.MediaInfoPath: str = MediaInfoPath
        self.MediaInfoTimeoutMinutes: int = MediaInfoTimeoutMinutes

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return ImportSettings()
        importsettings: ImportSettings = ImportSettings()

        importsettings.VideoExtensions = []
        tmp = json.get("VideoExtensions", [])
        for VideoExtension in tmp:
            importsettings.VideoExtensions.append(VideoExtension)
        importsettings.Exclude = []
        tmp = json.get("Exclude", [])
        for Exclude in tmp:
            importsettings.Exclude.append(Exclude)
        importsettings.DefaultSeriesLanguage = json.get("DefaultSeriesLanguage")
        importsettings.DefaultEpisodeLanguage = json.get("DefaultEpisodeLanguage")
        importsettings.RunOnStart = json.get("RunOnStart")
        importsettings.ScanDropFoldersOnStart = json.get("ScanDropFoldersOnStart")
        importsettings.Hash_CRC32 = json.get("Hash_CRC32")
        importsettings.Hash_MD5 = json.get("Hash_MD5")
        importsettings.Hash_SHA1 = json.get("Hash_SHA1")
        importsettings.UseExistingFileWatchedStatus = json.get("UseExistingFileWatchedStatus")
        importsettings.AutomaticallyDeleteDuplicatesOnImport = json.get("AutomaticallyDeleteDuplicatesOnImport")
        importsettings.FileLockChecking = json.get("FileLockChecking")
        importsettings.AggressiveFileLockChecking = json.get("AggressiveFileLockChecking")
        importsettings.FileLockWaitTimeMS = json.get("FileLockWaitTimeMS")
        importsettings.AggressiveFileLockWaitTimeSeconds = json.get("AggressiveFileLockWaitTimeSeconds")
        importsettings.RenameThenMove = json.get("RenameThenMove")
        importsettings.RenameOnImport = json.get("RenameOnImport")
        importsettings.MoveOnImport = json.get("MoveOnImport")
        importsettings.MediaInfoPath = json.get("MediaInfoPath")
        importsettings.MediaInfoTimeoutMinutes = json.get("MediaInfoTimeoutMinutes")

        return importsettings


class PlexSettings:
    def __init__(self,
                ThumbnailAspects: str = '',
                Libraries: List[int] = [],
                Token: str = '',
                Server: str = ''
                ):
        self.ThumbnailAspects: str = ThumbnailAspects
        self.Libraries: List[int] = Libraries
        self.Token: str = Token
        self.Server: str = Server

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return PlexSettings()
        plexsettings: PlexSettings = PlexSettings()

        plexsettings.ThumbnailAspects = json.get("ThumbnailAspects")
        plexsettings.Libraries = []
        tmp = json.get("Libraries", [])
        for library in tmp:
            plexsettings.Libraries.append(library)
        plexsettings.Token = json.get("Token")
        plexsettings.Server = json.get("Server")

        return plexsettings


class PluginSettings:
    def __init__(self,
                EnabledPlugins: dict = {},
                Priority: List[str] = [],
                EnabledRenamers: dict = {},
                RenamerPriorities: dict = {}
                ):
        self.EnabledPlugins: dict = EnabledPlugins
        self.Priority: List[str] = Priority
        self.EnabledRenamers: dict = EnabledRenamers
        self.RenamerPriorities: dict = RenamerPriorities

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return PluginSettings()
        pluginsettings: PluginSettings = PluginSettings()

        pluginsettings.EnabledPlugins = json.get("EnabledPlugins")
        pluginsettings.Priority = []
        tmp = json.get("Priority", [])
        for prio in tmp:
            pluginsettings.Priority.append(prio)
        pluginsettings.EnabledRenamers = json.get("EnabledRenamers")
        pluginsettings.RenamerPriorities = json.get("RenamerPriorities")

        return pluginsettings


class FileQualityPreferences:
    def __init__(self,
                Require10BitVideo: bool = True,
                MaxNumberOfFilesToKeep: int = 0,
                PreferredTypes: List[int] = [],
                PreferredAudioCodecs: List[str] = [],
                PreferredResolutions: List[str] = [],
                PreferredSubGroups: List[str] = [],
                PreferredVideoCodecs: List[str] = [],
                Prefer8BitVideo: bool = True,
                AllowDeletionOfImportedFiles: bool = True,
                RequiredTypes: List[int] = [],
                RequiredAudioCodecs: dict = {},
                RequiredAudioStreamCount: dict = {},
                RequiredResolutions: dict = {},
                RequiredSources: dict = {},
                RequiredSubGroups: dict = {},
                RequiredSubStreamCount: dict = {},
                RequiredVideoCodecs: dict = {},
                PreferredSources: List[str] = []
                ):
        self.Require10BitVideo: bool = Require10BitVideo
        self.MaxNumberOfFilesToKeep: int = MaxNumberOfFilesToKeep
        self.PreferredTypes: List[int] = PreferredTypes
        self.PreferredAudioCodecs: List[str] = PreferredAudioCodecs
        self.PreferredResolutions: List[str] = PreferredResolutions
        self.PreferredSubGroups: List[str] = PreferredSubGroups
        self.PreferredVideoCodecs: List[str] = PreferredVideoCodecs
        self.Prefer8BitVideo: bool = Prefer8BitVideo
        self.AllowDeletionOfImportedFiles: bool = AllowDeletionOfImportedFiles
        self.RequiredTypes: List[int] = RequiredTypes
        self.RequiredAudioCodecs: dict = RequiredAudioCodecs
        self.RequiredAudioStreamCount: dict = RequiredAudioStreamCount
        self.RequiredResolutions: dict = RequiredResolutions
        self.RequiredSources: dict = RequiredSources
        self.RequiredSubGroups: dict = RequiredSubGroups
        self.RequiredSubStreamCount: dict = RequiredSubStreamCount
        self.RequiredVideoCodecs: dict = RequiredVideoCodecs
        self.PreferredSources: List[str] = PreferredSources

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return FileQualityPreferences()
        filequalitypreferences: FileQualityPreferences = FileQualityPreferences()

        filequalitypreferences.Require10BitVideo = json.get("Require10BitVideo")
        filequalitypreferences.MaxNumberOfFilesToKeep = json.get("MaxNumberOfFilesToKeep")
        filequalitypreferences.PreferredTypes = []
        tmp = json.get("PreferredTypes", [])
        for PreferredType in tmp:
            filequalitypreferences.PreferredTypes.append(PreferredType)
        filequalitypreferences.PreferredAudioCodecs = []
        tmp = json.get("PreferredAudioCodecs", [])
        for PreferredAudioCodec in tmp:
            filequalitypreferences.PreferredAudioCodecs.append(PreferredAudioCodec)
        filequalitypreferences.PreferredResolutions = []
        tmp = json.get("PreferredResolutions", [])
        for PreferredResolution in tmp:
            filequalitypreferences.PreferredResolutions.append(PreferredResolution)
        filequalitypreferences.PreferredSubGroups = []
        tmp = json.get("PreferredSubGroups", [])
        for PreferredSubGroup in tmp:
            filequalitypreferences.PreferredSubGroups.append(PreferredSubGroup)
        filequalitypreferences.PreferredVideoCodecs = []
        tmp = json.get("PreferredVideoCodecs", [])
        for PreferredVideoCodec in tmp:
            filequalitypreferences.PreferredVideoCodecs.append(PreferredVideoCodec)
        filequalitypreferences.Prefer8BitVideo = json.get("Prefer8BitVideo")
        filequalitypreferences.AllowDeletionOfImportedFiles = json.get("AllowDeletionOfImportedFiles")
        filequalitypreferences.RequiredTypes = []
        tmp = json.get("RequiredTypes", [])
        for RequiredType in tmp:
            filequalitypreferences.RequiredTypes.append(RequiredType)
        filequalitypreferences.RequiredAudioCodecs = json.get("RequiredAudioCodecs")
        filequalitypreferences.RequiredAudioStreamCount = json.get("RequiredAudioStreamCount")
        filequalitypreferences.RequiredResolutions = json.get("RequiredResolutions")
        filequalitypreferences.RequiredSources = json.get("RequiredSources")
        filequalitypreferences.RequiredSubGroups = json.get("RequiredSubGroups")
        filequalitypreferences.RequiredSubStreamCount = json.get("RequiredSubStreamCount")
        filequalitypreferences.RequiredVideoCodecs = json.get("RequiredVideoCodecs")
        filequalitypreferences.PreferredSources = []
        tmp = json.get("PreferredSources", [])
        for PreferredSource in tmp:
            filequalitypreferences.PreferredSources.append(PreferredSource)

        return filequalitypreferences


class TraktSettings:
    def __init__(self,
                Enabled: bool = True,
                PIN: str = '',
                AuthToken: str = '',
                RefreshToken: str = '',
                TokenExpirationDate: str = '',
                UpdateFrequency: int = 1,
                SyncFrequency: int = 1
                ):
        self.Enabled: bool = Enabled
        self.PIN: str = PIN
        self.AuthToken: str = AuthToken
        self.RefreshToken: str = RefreshToken
        self.TokenExpirationDate: str = TokenExpirationDate
        self.UpdateFrequency: int = UpdateFrequency
        self.SyncFrequency: int = SyncFrequency


    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return TraktSettings()
        traktsettings: TraktSettings = TraktSettings()

        traktsettings.Enabled = json.get("Enabled")
        traktsettings.PIN = json.get("PIN")
        traktsettings.AuthToken = json.get("AuthToken")
        traktsettings.RefreshToken = json.get("RefreshToken")
        traktsettings.TokenExpirationDate = json.get("TokenExpirationDate")
        traktsettings.UpdateFrequency = json.get("UpdateFrequency")
        traktsettings.SyncFrequency = json.get("SyncFrequency")

        return traktsettings


class LinuxSettings:
    def __init__(self,
                UID: int = 0,
                GID: int = 0,
                Permission: int = 0
                ):
        self.UID: int = UID
        self.GID: int = GID
        self.Permission: int = Permission

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return LinuxSettings()
        linuxsettings: LinuxSettings = LinuxSettings()

        linuxsettings.UID = json.get("UID")
        linuxsettings.GID = json.get("GID")
        linuxsettings.Permission = json.get("Permission")

        return linuxsettings


class ServerSettingsExport:
    def __init__(self, 
                AnimeXmlDirectory: str = '',
                MyListDirectory: str = '',
                ServerPort: int = 0,
                PluginAutoWatchThreshold: int = 0,
                Culture: str = '',
                WebUI_Settings: str = '',
                FirstRun: bool = True,
                LegacyRenamerMaxEpisodeLength: int = 0,
                LogRotator: LogRotatorSettings = LogRotatorSettings(),
                Database: DatabaseSettings = DatabaseSettings(),
                AniDb: AniDBSettings = AniDBSettings(),
                WebCache: WebCacheSettings = WebCacheSettings(),
                TvDB: TvDBSettings = TvDBSettings(),
                MovieDb: MovieDbSettings = MovieDbSettings(),
                Import: ImportSettings = ImportSettings(),
                Plex: PlexSettings = PlexSettings(),
                Plugins: PluginSettings = PluginSettings(),
                AutoGroupSeries: bool = True,
                AutoGroupSeriesRelationExclusions: str = '',
                AutoGroupSeriesUseScoreAlgorithm: bool = True,
                FileQualityFilterEnabled: bool = True,
                FileQualityPreferences: FileQualityPreferences = FileQualityPreferences(),
                LanguagePreference: List[str] = [],
                EpisodeLanguagePreference: str = '',
                LanguageUseSynonyms: bool = True,
                CloudWatcherTime: int = 0,
                EpisodeTitleSource: int = 1,
                SeriesDescriptionSource: int = 1,
                SeriesNameSource: int = 1,
                ImagesPath: str = '',
                TraktTv: TraktSettings = TraktSettings(),
                UpdateChannel: str = '',
                Linux: LinuxSettings = LinuxSettings(),
                TraceLog: bool = True,
                GA_ClientId: str = '',
                GA_OptOutPlzDont: bool = True
                ):
        self.AnimeXmlDirectory: str = AnimeXmlDirectory
        self.MyListDirectory: str = MyListDirectory
        self.ServerPort: int = ServerPort
        self.PluginAutoWatchThreshold: int = PluginAutoWatchThreshold
        self.Culture: str = Culture
        self.WebUI_Settings: str = WebUI_Settings
        self.FirstRun: bool = FirstRun
        self.LegacyRenamerMaxEpisodeLength: int = LegacyRenamerMaxEpisodeLength
        self.LogRotator: LogRotatorSettings = LogRotator
        self.Database: DatabaseSettings = Database
        self.AniDb: AniDBSettings = AniDb
        self.WebCache: WebCacheSettings = WebCache
        self.TvDB: TvDBSettings = TvDB
        self.MovieDb: MovieDbSettings = MovieDb
        self.Import: ImportSettings = Import
        self.Plex: PlexSettings = Plex
        self.Plugins: PluginSettings = Plugins
        self.AutoGroupSeries: bool = AutoGroupSeries
        self.AutoGroupSeriesRelationExclusions: str = AutoGroupSeriesRelationExclusions
        self.AutoGroupSeriesUseScoreAlgorithm: bool = AutoGroupSeriesUseScoreAlgorithm
        self.FileQualityFilterEnabled: bool = FileQualityFilterEnabled
        self.FileQualityPreferences: FileQualityPreferences = FileQualityPreferences
        self.LanguagePreference: List[str] = LanguagePreference
        self.EpisodeLanguagePreference: str = EpisodeLanguagePreference
        self.LanguageUseSynonyms: bool = LanguageUseSynonyms
        self.CloudWatcherTime: int = CloudWatcherTime
        self.EpisodeTitleSource: int = EpisodeTitleSource
        self.SeriesDescriptionSource: int = SeriesDescriptionSource
        self.SeriesNameSource: int = SeriesNameSource
        self.ImagesPath: str = ImagesPath
        self.TraktTv: TraktSettings = TraktTv
        self.UpdateChannel: str = UpdateChannel
        self.Linux: LinuxSettings = Linux
        self.TraceLog: bool = TraceLog
        self.GA_ClientId: str = GA_ClientId
        self.GA_OptOutPlzDont: bool = GA_OptOutPlzDont

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return ServerSettingsExport()
        serversettingsexport: ServerSettingsExport = ServerSettingsExport()

        serversettingsexport.AnimeXmlDirectory = json.get("AnimeXmlDirectory")
        serversettingsexport.MyListDirectory = json.get("MyListDirectory")
        serversettingsexport.ServerPort = json.get("ServerPort")
        serversettingsexport.PluginAutoWatchThreshold = json.get("PluginAutoWatchThreshold")
        serversettingsexport.Culture = json.get("Culture")
        serversettingsexport.WebUI_Settings = json.get("WebUI_Settings")
        serversettingsexport.FirstRun = json.get("FirstRun")
        serversettingsexport.LegacyRenamerMaxEpisodeLength = json.get("LegacyRenamerMaxEpisodeLength")
        serversettingsexport.LogRotator = json.get("LogRotator")
        serversettingsexport.Database = json.get("Database")
        serversettingsexport.AniDb = json.get("AniDb")
        serversettingsexport.WebCache = json.get("WebCache")
        serversettingsexport.TvDB = json.get("TvDB")
        serversettingsexport.MovieDb = json.get("MovieDb")
        serversettingsexport.Import = json.get("Import")
        serversettingsexport.Plex = json.get("Plex")
        serversettingsexport.Plugins = json.get("Plugins")
        serversettingsexport.AutoGroupSeries = json.get("AutoGroupSeries")
        serversettingsexport.AutoGroupSeriesRelationExclusions = json.get("AutoGroupSeriesRelationExclusions")
        serversettingsexport.AutoGroupSeriesUseScoreAlgorithm = json.get("AutoGroupSeriesUseScoreAlgorithm")
        serversettingsexport.FileQualityFilterEnabled = json.get("FileQualityFilterEnabled")
        serversettingsexport.FileQualityPreferences = json.get("FileQualityPreferences")
        serversettingsexport.LanguagePreference = []
        tmp = json.get("LanguagePreference", [])
        for LanguagePreference in tmp:
            serversettingsexport.LanguagePreference.append(LanguagePreference)
        serversettingsexport.EpisodeLanguagePreference = json.get("EpisodeLanguagePreference")
        serversettingsexport.LanguageUseSynonyms = json.get("LanguageUseSynonyms")
        serversettingsexport.CloudWatcherTime = json.get("CloudWatcherTime")
        serversettingsexport.EpisodeTitleSource = json.get("EpisodeTitleSource")
        serversettingsexport.SeriesDescriptionSource = json.get("SeriesDescriptionSource")
        serversettingsexport.SeriesNameSource = json.get("SeriesNameSource")
        serversettingsexport.ImagesPath = json.get("ImagesPath")
        serversettingsexport.TraktTv = json.get("TraktTv")
        serversettingsexport.UpdateChannel = json.get("UpdateChannel")
        serversettingsexport.Linux = json.get("Linux")
        serversettingsexport.TraceLog = json.get("TraceLog")
        serversettingsexport.GA_ClientId = json.get("GA_ClientId")
        serversettingsexport.GA_OptOutPlzDont = json.get("GA_OptOutPlzDont")

        return serversettingsexport


class ServerSettingsImport:
    def __init__(self,
                AniDB_Username: str = '',
                AniDB_Password: str = '',
                AniDB_ServerAddress: str = '',
                AniDB_ServerPort: str = '',
                AniDB_ClientPort: str = '',
                AniDB_AVDumpClientPort: str = '',
                AniDB_AVDumpKey: str = '',
                AniDB_DownloadRelatedAnime: bool = True,
                AniDB_DownloadSimilarAnime: bool = True,
                AniDB_DownloadReviews: bool = True,
                AniDB_DownloadReleaseGroups: bool = True,
                AniDB_MyList_AddFiles: bool = True,
                AniDB_MyList_StorageState: int = 0,
                AniDB_MyList_DeleteType: int = 0,
                AniDB_MyList_ReadWatched: bool = True,
                AniDB_MyList_ReadUnwatched: bool = True,
                AniDB_MyList_SetWatched: bool = True,
                AniDB_MyList_SetUnwatched: bool = True,
                AniDB_MyList_UpdateFrequency: int = 0,
                AniDB_Calendar_UpdateFrequency: int = 0,
                AniDB_Anime_UpdateFrequency: int = 0,
                AniDB_MyListStats_UpdateFrequency: int = 0,
                AniDB_File_UpdateFrequency: int = 0,
                AniDB_DownloadCharacters: bool = True,
                AniDB_DownloadCreators: bool = True,
                AniDB_MaxRelationDepth: int = 0,
                WebCache_Address: str = '',
                WebCache_Anonymous: bool = True,
                WebCache_XRefFileEpisode_Get: bool = True,
                WebCache_XRefFileEpisode_Send: bool = True,
                WebCache_TvDB_Get: bool = True,
                WebCache_TvDB_Send: bool = True,
                WebCache_Trakt_Get: bool = True,
                WebCache_Trakt_Send: bool = True,
                WebCache_UserInfo: bool = True,
                TvDB_AutoLink: bool = True,
                TvDB_AutoFanart: bool = True,
                TvDB_AutoFanartAmount: int = 0,
                TvDB_AutoWideBanners: bool = True,
                TvDB_AutoWideBannersAmount: int = 0,
                TvDB_AutoPosters: bool = True,
                TvDB_AutoPostersAmount: int = 0,
                TvDB_UpdateFrequency: int = 0,
                TvDB_Language: str = '',
                MovieDB_AutoFanart: bool = True,
                MovieDB_AutoFanartAmount: int = 0,
                MovieDB_AutoPosters: bool = True,
                MovieDB_AutoPostersAmount: int = 0,
                VideoExtensions: str = '',
                AutoGroupSeries: bool = True,
                AutoGroupSeriesUseScoreAlgorithm: bool = True,
                AutoGroupSeriesRelationExclusions: str = '',
                FileQualityFilterEnabled: bool = True,
                FileQualityFilterPreferences: str = '',
                RunImportOnStart: bool = True,
                ScanDropFoldersOnStart: bool = True,
                Hash_CRC32: bool = True,
                Hash_MD5: bool = True,
                Hash_SHA1: bool = True,
                Import_UseExistingFileWatchedStatus: bool = True,
                LanguagePreference: str = '',
                LanguageUseSynonyms: bool = True,
                EpisodeTitleSource: int = 0,
                SeriesDescriptionSource: int = 0,
                SeriesNameSource: int = 0,
                Trakt_IsEnabled: bool = True,
                Trakt_AuthToken: str = '',
                Trakt_RefreshToken: str = '',
                Trakt_TokenExpirationDate: str = '',
                Trakt_UpdateFrequency: int = 0,
                Trakt_SyncFrequency: int = 0,
                RotateLogs: bool = True,
                RotateLogs_Zip: bool = True,
                RotateLogs_Delete: bool = True,
                RotateLogs_Delete_Days: str = '',
                WebUI_Settings: str = '',
                Plex_ServerHost: str = '',
                Plex_Sections: str = '',
                Import_MoveOnImport: bool = True,
                Import_RenameOnImport: bool = True
                ):
        self.AniDB_Username: str = AniDB_Username
        self.AniDB_Password: str = AniDB_Password
        self.AniDB_ServerAddress: str = AniDB_ServerAddress
        self.AniDB_ServerPort: str = AniDB_ServerPort
        self.AniDB_ClientPort: str = AniDB_ClientPort
        self.AniDB_AVDumpClientPort: str = AniDB_AVDumpClientPort
        self.AniDB_AVDumpKey: str = AniDB_AVDumpKey
        self.AniDB_DownloadRelatedAnime: bool = AniDB_DownloadRelatedAnime
        self.AniDB_DownloadSimilarAnime: bool = AniDB_DownloadSimilarAnime
        self.AniDB_DownloadReviews: bool = AniDB_DownloadReviews
        self.AniDB_DownloadReleaseGroups: bool = AniDB_DownloadReleaseGroups
        self.AniDB_MyList_AddFiles: bool = AniDB_MyList_AddFiles
        self.AniDB_MyList_StorageState: int = AniDB_MyList_StorageState
        self.AniDB_MyList_DeleteType: int = AniDB_MyList_DeleteType
        self.AniDB_MyList_ReadWatched: bool = AniDB_MyList_ReadWatched
        self.AniDB_MyList_ReadUnwatched: bool = AniDB_MyList_ReadUnwatched
        self.AniDB_MyList_SetWatched: bool = AniDB_MyList_SetWatched
        self.AniDB_MyList_SetUnwatched: bool = AniDB_MyList_SetUnwatched
        self.AniDB_MyList_UpdateFrequency: int = AniDB_MyList_UpdateFrequency
        self.AniDB_Calendar_UpdateFrequency: int = AniDB_Calendar_UpdateFrequency
        self.AniDB_Anime_UpdateFrequency: int = AniDB_Anime_UpdateFrequency
        self.AniDB_MyListStats_UpdateFrequency: int = AniDB_MyListStats_UpdateFrequency
        self.AniDB_File_UpdateFrequency: int = AniDB_File_UpdateFrequency
        self.AniDB_DownloadCharacters: bool = AniDB_DownloadCharacters
        self.AniDB_DownloadCreators: bool = AniDB_DownloadCreators
        self.AniDB_MaxRelationDepth: int = AniDB_MaxRelationDepth
        self.WebCache_Address: str = WebCache_Address
        self.WebCache_Anonymous: bool = WebCache_Anonymous
        self.WebCache_XRefFileEpisode_Get: bool = WebCache_XRefFileEpisode_Get
        self.WebCache_XRefFileEpisode_Send: bool = WebCache_XRefFileEpisode_Send
        self.WebCache_TvDB_Get: bool = WebCache_TvDB_Get
        self.WebCache_TvDB_Send: bool = WebCache_TvDB_Send
        self.WebCache_Trakt_Get: bool = WebCache_Trakt_Get
        self.WebCache_Trakt_Send: bool = WebCache_Trakt_Send
        self.WebCache_UserInfo: bool = WebCache_UserInfo
        self.TvDB_AutoLink: bool = TvDB_AutoLink
        self.TvDB_AutoFanart: bool = TvDB_AutoFanart
        self.TvDB_AutoFanartAmount: int = TvDB_AutoFanartAmount
        self.TvDB_AutoWideBanners: bool = TvDB_AutoWideBanners
        self.TvDB_AutoWideBannersAmount: int = TvDB_AutoWideBannersAmount
        self.TvDB_AutoPosters: bool = TvDB_AutoPosters
        self.TvDB_AutoPostersAmount: int = TvDB_AutoPostersAmount
        self.TvDB_UpdateFrequency: int = TvDB_UpdateFrequency
        self.TvDB_Language: str = TvDB_Language
        self.MovieDB_AutoFanart: bool = MovieDB_AutoFanart
        self.MovieDB_AutoFanartAmount: int = MovieDB_AutoFanartAmount
        self.MovieDB_AutoPosters: bool = MovieDB_AutoPosters
        self.MovieDB_AutoPostersAmount: int = MovieDB_AutoPostersAmount
        self.VideoExtensions: str = VideoExtensions
        self.AutoGroupSeries: bool = AutoGroupSeries
        self.AutoGroupSeriesUseScoreAlgorithm: bool = AutoGroupSeriesUseScoreAlgorithm
        self.AutoGroupSeriesRelationExclusions: str = AutoGroupSeriesRelationExclusions
        self.FileQualityFilterEnabled: bool = FileQualityFilterEnabled
        self.FileQualityFilterPreferences: str = FileQualityFilterPreferences
        self.RunImportOnStart: bool = RunImportOnStart
        self.ScanDropFoldersOnStart: bool = ScanDropFoldersOnStart
        self.Hash_CRC32: bool = Hash_CRC32
        self.Hash_MD5: bool = Hash_MD5
        self.Hash_SHA1: bool = Hash_SHA1
        self.Import_UseExistingFileWatchedStatus: bool = Import_UseExistingFileWatchedStatus
        self.LanguagePreference: str = LanguagePreference
        self.LanguageUseSynonyms: bool = LanguageUseSynonyms
        self.EpisodeTitleSource: int = EpisodeTitleSource
        self.SeriesDescriptionSource: int = SeriesDescriptionSource
        self.SeriesNameSource: int = SeriesNameSource
        self.Trakt_IsEnabled: bool = Trakt_IsEnabled
        self.Trakt_AuthToken: str = Trakt_AuthToken
        self.Trakt_RefreshToken: str = Trakt_RefreshToken
        self.Trakt_TokenExpirationDate: str = Trakt_TokenExpirationDate
        self.Trakt_UpdateFrequency: int = Trakt_UpdateFrequency
        self.Trakt_SyncFrequency: int = Trakt_SyncFrequency
        self.RotateLogs: bool = RotateLogs
        self.RotateLogs_Zip: bool = RotateLogs_Zip
        self.RotateLogs_Delete: bool = RotateLogs_Delete
        self.RotateLogs_Delete_Days: str = RotateLogs_Delete_Days
        self.WebUI_Settings: str = WebUI_Settings
        self.Plex_ServerHost: str = Plex_ServerHost
        self.Plex_Sections: str = Plex_Sections
        self.Import_MoveOnImport: bool = Import_MoveOnImport
        self.Import_RenameOnImport: bool = Import_RenameOnImport


    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return ServerSettingsImport()
        serversettingsimport: ServerSettingsImport = ServerSettingsImport()

        serversettingsimport.AniDB_Username = json.get("AniDB_Username")
        serversettingsimport.AniDB_Password = json.get("AniDB_Password")
        serversettingsimport.AniDB_ServerAddress = json.get("AniDB_ServerAddress")
        serversettingsimport.AniDB_ServerPort = json.get("AniDB_ServerPort")
        serversettingsimport.AniDB_ClientPort = json.get("AniDB_ClientPort")
        serversettingsimport.AniDB_AVDumpClientPort = json.get("AniDB_AVDumpClientPort")
        serversettingsimport.AniDB_AVDumpKey = json.get("AniDB_AVDumpKey")
        serversettingsimport.AniDB_DownloadRelatedAnime = json.get("AniDB_DownloadRelatedAnime")
        serversettingsimport.AniDB_DownloadSimilarAnime = json.get("AniDB_DownloadSimilarAnime")
        serversettingsimport.AniDB_DownloadReviews = json.get("AniDB_DownloadReviews")
        serversettingsimport.AniDB_DownloadReleaseGroups = json.get("AniDB_DownloadReleaseGroups")
        serversettingsimport.AniDB_MyList_AddFiles = json.get("AniDB_MyList_AddFiles")
        serversettingsimport.AniDB_MyList_StorageState = json.get("AniDB_MyList_StorageState")
        serversettingsimport.AniDB_MyList_DeleteType = json.get("AniDB_MyList_DeleteType")
        serversettingsimport.AniDB_MyList_ReadWatched = json.get("AniDB_MyList_ReadWatched")
        serversettingsimport.AniDB_MyList_ReadUnwatched = json.get("AniDB_MyList_ReadUnwatched")
        serversettingsimport.AniDB_MyList_SetWatched = json.get("AniDB_MyList_SetWatched")
        serversettingsimport.AniDB_MyList_SetUnwatched = json.get("AniDB_MyList_SetUnwatched")
        serversettingsimport.AniDB_MyList_UpdateFrequency = json.get("AniDB_MyList_UpdateFrequency")
        serversettingsimport.AniDB_Calendar_UpdateFrequency = json.get("AniDB_Calendar_UpdateFrequency")
        serversettingsimport.AniDB_Anime_UpdateFrequency = json.get("AniDB_Anime_UpdateFrequency")
        serversettingsimport.AniDB_MyListStats_UpdateFrequency = json.get("AniDB_MyListStats_UpdateFrequency")
        serversettingsimport.AniDB_File_UpdateFrequency = json.get("AniDB_File_UpdateFrequency")
        serversettingsimport.AniDB_DownloadCharacters = json.get("AniDB_DownloadCharacters")
        serversettingsimport.AniDB_DownloadCreators = json.get("AniDB_DownloadCreators")
        serversettingsimport.AniDB_MaxRelationDepth = json.get("AniDB_MaxRelationDepth")
        serversettingsimport.WebCache_Address = json.get("WebCache_Address")
        serversettingsimport.WebCache_Anonymous = json.get("WebCache_Anonymous")
        serversettingsimport.WebCache_XRefFileEpisode_Get = json.get("WebCache_XRefFileEpisode_Get")
        serversettingsimport.WebCache_XRefFileEpisode_Send = json.get("WebCache_XRefFileEpisode_Send")
        serversettingsimport.WebCache_TvDB_Get = json.get("WebCache_TvDB_Get")
        serversettingsimport.WebCache_TvDB_Send = json.get("WebCache_TvDB_Send")
        serversettingsimport.WebCache_Trakt_Get = json.get("WebCache_Trakt_Get")
        serversettingsimport.WebCache_Trakt_Send = json.get("WebCache_Trakt_Send")
        serversettingsimport.WebCache_UserInfo = json.get("WebCache_UserInfo")
        serversettingsimport.TvDB_AutoLink = json.get("TvDB_AutoLink")
        serversettingsimport.TvDB_AutoFanart = json.get("TvDB_AutoFanart")
        serversettingsimport.TvDB_AutoFanartAmount = json.get("TvDB_AutoFanartAmount")
        serversettingsimport.TvDB_AutoWideBanners = json.get("TvDB_AutoWideBanners")
        serversettingsimport.TvDB_AutoWideBannersAmount = json.get("TvDB_AutoWideBannersAmount")
        serversettingsimport.TvDB_AutoPosters = json.get("TvDB_AutoPosters")
        serversettingsimport.TvDB_AutoPostersAmount = json.get("TvDB_AutoPostersAmount")
        serversettingsimport.TvDB_UpdateFrequency = json.get("TvDB_UpdateFrequency")
        serversettingsimport.TvDB_Language = json.get("TvDB_Language")
        serversettingsimport.MovieDB_AutoFanart = json.get("MovieDB_AutoFanart")
        serversettingsimport.MovieDB_AutoFanartAmount = json.get("MovieDB_AutoFanartAmount")
        serversettingsimport.MovieDB_AutoPosters = json.get("MovieDB_AutoPosters")
        serversettingsimport.MovieDB_AutoPostersAmount = json.get("MovieDB_AutoPostersAmount")
        serversettingsimport.VideoExtensions = json.get("VideoExtensions")
        serversettingsimport.AutoGroupSeries = json.get("AutoGroupSeries")
        serversettingsimport.AutoGroupSeriesUseScoreAlgorithm = json.get("AutoGroupSeriesUseScoreAlgorithm")
        serversettingsimport.AutoGroupSeriesRelationExclusions = json.get("AutoGroupSeriesRelationExclusions")
        serversettingsimport.FileQualityFilterEnabled = json.get("FileQualityFilterEnabled")
        serversettingsimport.FileQualityFilterPreferences = json.get("FileQualityFilterPreferences")
        serversettingsimport.RunImportOnStart = json.get("RunImportOnStart")
        serversettingsimport.ScanDropFoldersOnStart = json.get("ScanDropFoldersOnStart")
        serversettingsimport.Hash_CRC32 = json.get("Hash_CRC32")
        serversettingsimport.Hash_MD5 = json.get("Hash_MD5")
        serversettingsimport.Hash_SHA1 = json.get("Hash_SHA1")
        serversettingsimport.Import_UseExistingFileWatchedStatus = json.get("Import_UseExistingFileWatchedStatus")
        serversettingsimport.LanguagePreference = json.get("LanguagePreference")
        serversettingsimport.LanguageUseSynonyms = json.get("LanguageUseSynonyms")
        serversettingsimport.EpisodeTitleSource = json.get("EpisodeTitleSource")
        serversettingsimport.SeriesDescriptionSource = json.get("SeriesDescriptionSource")
        serversettingsimport.SeriesNameSource = json.get("SeriesNameSource")
        serversettingsimport.Trakt_IsEnabled = json.get("Trakt_IsEnabled")
        serversettingsimport.Trakt_AuthToken = json.get("Trakt_AuthToken")
        serversettingsimport.Trakt_RefreshToken = json.get("Trakt_RefreshToken")
        serversettingsimport.Trakt_TokenExpirationDate = json.get("Trakt_TokenExpirationDate")
        serversettingsimport.Trakt_UpdateFrequency = json.get("Trakt_UpdateFrequency")
        serversettingsimport.Trakt_SyncFrequency = json.get("Trakt_SyncFrequency")
        serversettingsimport.RotateLogs = json.get("RotateLogs")
        serversettingsimport.RotateLogs_Zip = json.get("RotateLogs_Zip")
        serversettingsimport.RotateLogs_Delete = json.get("RotateLogs_Delete")
        serversettingsimport.RotateLogs_Delete_Days = json.get("RotateLogs_Delete_Days")
        serversettingsimport.WebUI_Settings = json.get("WebUI_Settings")
        serversettingsimport.Plex_ServerHost = json.get("Plex_ServerHost")
        serversettingsimport.Plex_Sections = json.get("Plex_Sections")
        serversettingsimport.Import_MoveOnImport = json.get("Import_MoveOnImport")
        serversettingsimport.Import_RenameOnImport = json.get("Import_RenameOnImport")

        return serversettingsimport


class Credentials:
    def __init__(self,
                login: str = '',
                password: str = '',
                port: int = 0,
                token: str = '',
                refresh_token: str = '',
                apikey: str = '',
                apiport: int = 0
                ):
        self.login: str = login
        self.password: str = password
        self.port: int = port
        self.token: str = token
        self.refresh_token: str = refresh_token
        self.apikey: str = apikey
        self.apiport: int = apiport

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return Credentials()
        credentials: Credentials = Credentials()

        credentials.login = json.get("login")
        credentials.password = json.get("password")
        credentials.port = json.get("port")
        credentials.token = json.get("token")
        credentials.refresh_token = json.get("refresh_token")
        credentials.apikey = json.get("apikey")
        credentials.apiport = json.get("apiport")

        return credentials
 

class JMMUser:
    def __init__(self,
                JMMUserID: int,
                Username: str,
                Password: str,
                IsAdmin: int,
                IsAniDBUser: int,
                IsTraktUser: int,
                HideCategories: str,
                CanEditServerSettings: int,
                PlexUsers: str,
                PlexToken: str
                ):
        self.JMMUserID: int = JMMUserID
        self.Username: str = Username
        self.Password: str = Password
        self.IsAdmin: int = IsAdmin
        self.IsAniDBUser: int = IsAniDBUser
        self.IsTraktUser: int = IsTraktUser
        self.HideCategories: str = HideCategories
        self.CanEditServerSettings: int = CanEditServerSettings
        self.PlexUsers: str = PlexUsers
        self.PlexToken: str = PlexToken

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return JMMUser()
        jmmuser: JMMUser = JMMUser()

        jmmuser.JMMUserID = json.get("JMMUserID")
        jmmuser.Username = json.get("Username")
        jmmuser.Password = json.get("Password")
        jmmuser.IsAdmin = json.get("IsAdmin")
        jmmuser.IsAniDBUser = json.get("IsAniDBUser")
        jmmuser.IsTraktUser = json.get("IsTraktUser")
        jmmuser.HideCategories = json.get("HideCategories")
        jmmuser.CanEditServerSettings = json.get("CanEditServerSettings")
        jmmuser.PlexUsers = json.get("PlexUsers")
        jmmuser.PlexToken = json.get("PlexToken")

        return jmmuser


class OSFolder:
    def __init__(self,
                dir: str = '',
                full_path: str = '',
                subdir: List[object] = []
                ):
        self.dir: str = dir
        self.full_path: str = full_path
        self.subdir: List[object] = subdir


    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return OSFolder()
        osfolder: OSFolder = OSFolder()

        osfolder.dir = json.get("dir")
        osfolder.full_path = json.get("full_path")
        osfolder.subdir = []
        for dir in json.get("subdir"):
            osfolder.subdir.append(dir)

        return osfolder


class Logs:
    def __init__(self,
                rotate: bool = True,
                zip: bool = True,
                delete: bool = True,
                days: int = 0
                ):
        self.rotate: bool = rotate
        self.zip: bool = zip
        self.delete: bool = delete
        self.days: int = days

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return Logs()
        logs: Logs = Logs()

        logs.rotate = json.get("rotate")
        logs.zip = json.get("zip")
        logs.delete = json.get("delete")
        logs.days = json.get("days")

        return logs


class Part:
    def __init__(self,
                Accessible: int = 0,
                Exists: int = 0,
                Streams: List[Stream] = [],
                Size: int = 0,
                Duration: int = 0,
                Key: str = '',
                LocalKey: str = '',
                Container: str = '',
                Id: int = 0,
                File: str = '',
                OptimizedForStreaming: int = 0,
                Has64bitOffsets: int = 0
                ):
        self.Accessible: int = Accessible
        self.Exists: int = Exists
        self.Streams: List[Stream] = Streams
        self.Size: int = Size
        self.Duration: int = Duration
        self.Key: str = Key
        self.LocalKey: str = LocalKey
        self.Container: str = Container
        self.Id: int = Id
        self.File: str = File
        self.OptimizedForStreaming: int = OptimizedForStreaming
        self.Has64bitOffsets: int = Has64bitOffsets


    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return Part()
        part: Part = Part()

        part.Accessible = json.get("Accessible")
        part.Exists = json.get("Exists")
        part.Streams = []
        tmp = json.get("Streams", [])
        for stream in tmp:
            stream = Stream.Decoder(stream)
            part.Streams.append(stream)
        part.Size = json.get("Size")
        part.Duration = json.get("Duration")
        part.Key = json.get("Key")
        part.LocalKey = json.get("LocalKey")
        part.Container = json.get("Container")
        part.Id = json.get("Id")
        part.File = json.get("File")
        part.OptimizedForStreaming = json.get("OptimizedForStreaming")
        part.Has64bitOffsets = json.get("Has64bitOffsets")

        return part


class Media:
    def __init__(self,
                Parts: List[Part] = [],
                Duration: int = 0,
                VideoFrameRate: str = '',
                Container: str = '',
                VideoCodec: str = '',
                AudioCodec: str = '',
                AudioChannels: int = 0,
                AspectRatio: int = 0,
                Height: int = 0,
                Width: int = 0,
                Bitrate: int = 0,
                Id: int = 0,
                VideoResolution: str = '',
                OptimizedForStreaming: int = 0,
                Chaptered: bool = True
                ):
        self.Parts: List[Part] = Parts
        self.Duration: int = Duration
        self.VideoFrameRate: str = VideoFrameRate
        self.Container: str = Container
        self.VideoCodec: str = VideoCodec
        self.AudioCodec: str = AudioCodec
        self.AudioChannels: int = AudioChannels
        self.AspectRatio: int = AspectRatio
        self.Height: int = Height
        self.Width: int = Width
        self.Bitrate: int = Bitrate
        self.Id: int = Id
        self.VideoResolution: str = VideoResolution
        self.OptimizedForStreaming: int = OptimizedForStreaming
        self.Chaptered: bool = Chaptered


    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return Media()
        media: Media = Media()

        media.Parts = []
        tmp = json.get("Parts", [])
        for part in tmp:
            part = Part.Decoder(part)
            media.Parts.append(part)
        media.Duration = json.get("Duration")
        media.VideoFrameRate = json.get("VideoFrameRate")
        media.Container = json.get("Container")
        media.VideoCodec = json.get("VideoCodec")
        media.AudioCodec = json.get("AudioCodec")
        media.AudioChannels = json.get("AudioChannels")
        media.AspectRatio = json.get("AspectRatio")
        media.Height = json.get("Height")
        media.Width = json.get("Width")
        media.Bitrate = json.get("Bitrate")
        media.Id = json.get("Id")
        media.VideoResolution = json.get("VideoResolution")
        media.OptimizedForStreaming = json.get("OptimizedForStreaming")
        media.Chaptered = json.get("Chaptered")

        return media


class ComponentVersion:
    def __init__(self,
                name: str = '',
                version: str = '',
                ):
        self.name: str = name
        self.version: str = version

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return ComponentVersion()
        componentversion: ComponentVersion = ComponentVersion()

        componentversion.name = json.get("name")
        componentversion.version = json.get("version")

        return componentversion


class ServerStatus:
    def __init__(self,
                startup_state: str = '',
                server_started: bool = True,
                server_uptime: str = '',
                first_run: bool = True,
                startup_failed: bool = True,
                startup_failed_error_message: str = ''
                ):
        self.startup_state: str = startup_state
        self.server_started: bool = server_started
        self.server_uptime: str = server_uptime
        self.first_run: bool = first_run
        self.startup_failed: bool = startup_failed
        self.startup_failed_error_message: str = startup_failed_error_message

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return ServerStatus()
        serverstatus: ServerStatus = ServerStatus()

        serverstatus.startup_state = json.get("startup_state")
        serverstatus.server_started = json.get("server_started")
        serverstatus.server_uptime = json.get("server_uptime")
        serverstatus.first_run = json.get("first_run")
        serverstatus.startup_failed = json.get("startup_failed")
        serverstatus.startup_failed_error_message = json.get("startup_failed_error_message")

        return serverstatus


class WebUI_Settings:
    def __init__(self,
                actions: List[str] = [],
                uiTheme: str = '',
                uiNotifications: bool = True,
                otherUpdateChannel: str = '',
                logDelta: int = 0
                ):
        self.actions: List[str] = actions
        self.uiTheme: str = uiTheme
        self.uiNotifications: bool = uiNotifications
        self.otherUpdateChannel: str = otherUpdateChannel
        self.logDelta: int = logDelta

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    def __repr__(self) -> str:
        return f"<{self.__class__.__qualname__} {self.__dict__}>"

    @staticmethod
    def Decoder(json: dict):
        if not isinstance(json, dict):
            try:
                json = json.__dict__
            except:
                print(f"Exception at: {__class__.__name__}.{__class__.Decoder.__name__} --- json is not dictionary")
                return WebUI_Settings()
        webui_settings: WebUI_Settings = WebUI_Settings()

        webui_settings.actions = []
        tmp = json.get("actions", [])
        for action in tmp:
            webui_settings.actions.append(action)
        webui_settings.uiTheme = json.get("uiTheme")
        webui_settings.uiNotifications = json.get("uiNotifications")
        webui_settings.otherUpdateChannel = json.get("otherUpdateChannel")
        webui_settings.logDelta = json.get("logDelta")

        return webui_settings