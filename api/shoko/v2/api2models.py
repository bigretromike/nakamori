# -*- coding: utf-8 -*-
from json import JSONEncoder
from json import JSONDecoder


class AuthUser:
    def __init__(self, 
                user: str,
                password: str,
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
                print("Exception: at AuthUser.Decoder --- json is not dictionary")
                return AuthUser()
        authuser: AuthUser = AuthUser()
        
        authuser.user = json.get("user")
        authuser.password = json.get("pass")
        authuser.device = json.get("device")

        return authuser

class QueryOptions:
    def __init__(self,
                query: str = '',
                limit: int = 0,
                limit_tag: int = 0,
                filter: int = 0,
                tags: int = 0,
                tagfilter: int = 0,
                fuzzy: int = 0,
                nocast: int = 0,
                notag: int = 0,
                id: int = 0,
                score: int = 0,
                offset: int = 0,
                level: int = 0,
                all: int = 0,
                progress: int = 0,
                status: int = 0,
                ismovie: int = 0,
                filename: str = '',
                hash: str = '',
                allpics: int = 0,
                pic: int = 0,
                skip: int = 0
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
        return QueryOptions(obj.get('query', None),
                            obj.get('limit', None),
                            obj.get('limit_tag', None),
                            obj.get('filter', None),
                            obj.get('tags', None),
                            obj.get('tagfilter', None),
                            obj.get('fuzzy', None),
                            obj.get('nocast', None),
                            obj.get('notag', None),
                            obj.get('id', None),
                            obj.get('score', None),
                            obj.get('offset', None),
                            obj.get('level', None),
                            obj.get('all', None),
                            obj.get('progress', None),
                            obj.get('status', None),
                            obj.get('ismovie', None),
                            obj.get('filename', None),
                            obj.get('hash', None),
                            obj.get('allpics', None),
                            obj.get('pic', None),
                            obj.get('skip', None))


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
                print("Exception: at AnimeTitle.Decoder --- json is not dictionary")
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
                # print("Exception: at Sizes.Decoder --- json is not dictionary")
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
                print("Exception: at Role.Decoder --- json is not dictionary")
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
                print("Exception: at Art.Decoder --- json is not dictionary")
                return Art()
        art: Art = Art()

        art.url = json.get("url")
        art.index = json.get("index")

        return art


class ArtCollection:
    def __init__(self,
                banner: Art = [],
                fanart: Art = [],
                thumb: Art = []
                ):
        self.banner: list[Art] = banner
        self.fanart: list[Art] = fanart
        self.thumb: list[Art] = thumb

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
                print("Exception: at ArtCollection.Decoder --- json is not dictionary")
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
                print("Exception: at General.Decoder --- json is not dictionary")
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
                print("Exception: at Stream.Decoder --- json is not dictionary")
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
                audios: Stream = {},
                videos: Stream = {},
                subtitles: Stream = {},
                menus = {}
                ):
        self.general: General = general
        self.audios: Stream = audios
        self.videos: Stream = videos
        self.subtitles: Stream = subtitles
        self.menus = menus

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
                print("Exception: at MediaInfo.Decoder --- json is not dictionary")
                return MediaInfo()
        mediainfo: MediaInfo = MediaInfo()

        mediainfo.general = General.Decoder(json.get("general"))
        mediainfo.audios = Stream.Decoder(json.get("audios"))
        mediainfo.videos = Stream.Decoder(json.get("videos"))
        mediainfo.subtitles = Stream.Decoder(json.get("subtitles"))
        mediainfo.menus = json.get("menus")

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
                titles: AnimeTitle = [],
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
                roles: Role = [],
                tags: str = [],
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
        self.titles: list[AnimeTitle] = titles
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
        self.roles: list[Role] = roles
        self.tags: list[str] = tags
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
                print("Exception: at RawFile.Decoder --- json is not dictionary")
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
                titles: AnimeTitle = [],
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
                roles: Role = [],
                tags: str = [],
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
        self.titles: list[AnimeTitle] = titles
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
        self.roles: list[Role] = roles
        self.tags: list[str] = tags
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
                print("Exception: at RecentFile.Decoder --- json is not dictionary")
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
                files: RawFile = [],
                id: int = 0,
                name: str = '',
                titles: AnimeTitle = [],
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
                roles: Role = [],
                tags: str = [],
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
        self.files: list[RawFile] = files
        self.id: int = id
        self.name: str = name
        self.titles: list[AnimeTitle] = titles
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
        self.roles: list[Role] = roles
        self.tags: list[str] = tags
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
                print("Exception: at Episode.Decoder --- json is not dictionary")
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
        episode.userrating = json.get("userrating")
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
                eps: Episode = [],
                ismovie: int = 0,
                filesize: int = 0,
                id: int = 0,
                name: str = '',
                titles: AnimeTitle = [],
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
                roles: Role = [],
                tags: str = [],
                art: ArtCollection = {}
                ):
        self.type: str = type
        self.aid: int = aid
        self.season: str = season
        self.eps: list[Episode] = eps
        self.ismovie: int = ismovie
        self.filesize: int = filesize
        self.id: int = id
        self.name: str = name
        self.titles: list[AnimeTitle] = titles
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
        self.roles: list[Role] = roles
        self.tags: list[str] = tags
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
                print("Exception: at Serie.Decoder --- json is not dictionary")
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
        serie.userrating = json.get("userrating")
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
                series: list = [],
                type: str = '',
                id: int = 0,
                name: str = '',
                titles: list = [],
                summary: str = '',
                url: str = '',
                added: str = '',
                edited: str = '',
                year: str = '',
                air: str = '',
                size: int = 0,
                localsize: int = 0,
                total_sizes: object = {},
                local_sizes: object = {},
                watched_sizes: object = {},
                viewed: int = 0,
                rating: str = '',
                votes: str = '',
                userrating: str = '',
                roles: list = [],
                tags: list = [],
                art: object = {}
                ):
        self.series: list[Serie] = series
        self.type: str = type
        self.id: int = id
        self.name: str = name
        self.titles: list[AnimeTitle] = titles
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
        self.roles: list[Role] = roles
        self.tags: list[str] = tags
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
                print("Exception: at Group.Decoder --- json is not dictionary")
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

class Filters:
    def __init__(self,
                type: str = '',
                filters = [],
                id: int = 0,
                name: str = '',
                titles: AnimeTitle = [],
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
                roles: Role = [],
                tags: str = [],
                art: ArtCollection = {}
                ):
        self.type: str = type
        self.filters: list = filters
        self.id: int = id
        self.name: str = name
        self.titles: list[AnimeTitle] = titles
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
        self.roles: list[Role] = roles
        self.tags: list[str] = tags
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
                print("Exception: at Filters.Decoder --- json is not dictionary")
                return Filters()
        filters: Filters = Filters()

        filters.type = json.get("type")
        filters.filters = []
        tmp = json.get("filters", [])
        for filter in tmp:
            filters.filters.append(filter)
        filters.id = json.get("id")
        filters.name = json.get("name")
        filters.titles = []
        tmp = json.get("titles", [])
        for title in tmp:
            title = AnimeTitle.Decoder(title)
            filters.titles.append(title)
        filters.summary = json.get("summary")
        filters.url = json.get("url")
        filters.added = json.get("added")
        filters.edited = json.get("edited")
        filters.year = json.get("year")
        filters.air = json.get("air")
        filters.size = json.get("size")
        filters.localsize = json.get("localsize")
        filters.total_sizes = Sizes.Decoder(json.get('total_sizes'))
        filters.local_sizes = Sizes.Decoder(json.get('local_sizes'))
        filters.watched_sizes = Sizes.Decoder(json.get('watched_sizes'))
        filters.viewed = json.get("viewed")
        filters.rating = json.get("rating")
        filters.votes = json.get("votes")
        filters.userrating = json.get("userrating")
        filters.roles = []
        tmp = json.get("roles", [])
        for role in tmp:
            role = Role.Decoder(role)
            filters.roles.append(role)        
            filters.tags = []
        tmp = json.get("tags", [])
        for tag in tmp:
            filters.tags.append(tag)        
        filters.art = ArtCollection.Decoder(json.get("art"))

        return filters


class Filter:
    def __init__(self,
                type: str = '',
                groups: list = [],
                filters: list = [],
                id: int = 0,
                name: str = '',
                titles: list = [],
                summary: str = '',
                url: str = '',
                added: str = '',
                edited: str = '',
                year: str = '',
                air: str = '',
                size: int = 0,
                localsize: int = 0,
                total_sizes: list = [],
                local_sizes: list = [],
                watched_sizes: list = [],
                viewed: int = 0,
                rating: str = '',
                votes: str = '',
                userrating: str = '',
                roles: list = [],
                tags: list = [],
                art: object = {}
                ):
        self.type: str = type
        self.groups: list[Group] = groups
        self.filters: list[Filters] = filters
        self.id: int = id
        self.name: str = name
        self.titles: list[AnimeTitle] = titles
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
        self.roles: list[Role] = roles
        self.tags: list[str] = tags
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
                print("Exception: at Filter.Decoder --- json is not dictionary")
                return Filter()
        filter: Filter = Filter()

        filter.type = json.get('type')
        filter.groups = []
        tmp = json.get("groups", [])
        for group in tmp:
            group = Group.Decoder(group)
            filter.groups.append(group)
        filter.filters = []
        tmp = json.get("filters", [])
        for filter in tmp:
            filter = Filter.Decoder(filter)
            filter.filters.append(filter)
        filter.id = json.get("id")
        filter.name = json.get("name")
        filter.titles = []
        tmp = json.get("titles", [])
        for title in tmp:
            title = AnimeTitle.Decoder(title)
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
        tmp = json.get("roles", [])
        for role in tmp:
            role = Role.Decoder(role)
            filter.roles.append(role)        
        filter.tags = []
        tmp = json.get("tags", [])
        for tag in tmp:
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
                print("Exception: at ImportFolder.Decoder --- json is not dictionary")
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
                print("Exception: at Counter.Decoder --- json is not dictionary")
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
                print("Exception: at WebNews.Decoder --- json is not dictionary")
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
                print("Exception: at QueueInfo.Decoder --- json is not dictionary")
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
                paths: list = []
                ):
        self.name: str = name
        self.id: int = id
        self.filesize: int = filesize
        self.size: int = size
        self.paths: list[str] = paths

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
                print("Exception: at SeriesInFolderInfo.Decoder --- json is not dictionary")
                return SeriesInFolderInfo()
        seriesinfolderinfo: SeriesInFolderInfo = SeriesInFolderInfo()

        seriesinfolderinfo.name = json.get("name")
        seriesinfolderinfo.id = json.get("id")
        seriesinfolderinfo.filesize = json.get("filesize")
        seriesinfolderinfo.size = json.get("size")
        seriesinfolderinfo.paths = []
        tmp = json.get("paths")
        for path in tmp:
            seriesinfolderinfo.paths.append(path)

        return seriesinfolderinfo

class FolderInfo:
    def __init__(self,
               id: int = 0,
               filesize: int = 0,
               size: int = 0,
               series: SeriesInFolderInfo = {}
                ):
        self.id: int = id
        self.filesize: int = filesize
        self.size: int = size
        self.series: list[SeriesInFolderInfo] = series

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
                print("Exception: at FolderInfo.Decoder --- json is not dictionary")
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


