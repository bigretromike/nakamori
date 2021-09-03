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
                return "Exception: at AuthUser.Decoder --- json is not dictionary"
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
                return "Exception: at AnimeTitle.Decoder --- json is not dictionary"
        animetitle: AnimeTitle = AnimeTitle()
        if "Type" in json:
            animetitle.Type = json["Type"]
        if "Language" in json:
            animetitle.Language = json["Language"]
        if "Title" in json:
            animetitle.Title = json["Title"]

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
                print(json)
                print("Exception: at Sizes.Decoder --- json is not dictionary")
                return "Exception: at Sizes.Decoder --- json is not dictionary"
        sizes: Sizes = Sizes()
        if "Episodes" in json:
            sizes.Episodes = json["Episodes"]
        if "Specials" in json:
            sizes.Specials = json["Specials"]
        if "Credits" in json:
            sizes.Credits = json["Credits"]
        if "Trailers" in json:
            sizes.Trailers = json["Trailers"]
        if "Parodies" in json:
            sizes.Parodies = json["Parodies"]
        if "Others" in json:
            sizes.Others = json["Others"]

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
                return "Exception: at Role.Decoder --- json is not dictionary"
        role: Role = Role()
        if "character" in json:
            role.character = json["character"]
        if "character_image" in json:
            role.character_image = json["character_image"]
        if "character_description" in json:
            role.character_description = json["character_description"]
        if "staff" in json:
            role.staff = json["staff"]
        if "staff_image" in json:
            role.staff_image = json["staff_image"]
        if "staff_description" in json:
            role.staff_description = json["staff_description"]
        if "role" in json:
            role.role = json["role"]
        if "type" in json:
            role.type = json["type"]

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
                return "Exception: at Art.Decoder --- json is not dictionary"
        art: Art = Art()
        if "url" in json:
            art.url = json["url"]
        if "index" in json:
            art.index = json["index"]

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
                return "Exception: at ArtCollection.Decoder --- json is not dictionary"
        artcollection: ArtCollection = ArtCollection()
        if "banner" in json:
            tmp = json["banner"]
            for art in tmp:
                art = Art.Decoder(art)
                artcollection.banner.append(art)
        if "fanart" in json:
            tmp = json["fanart"]
            for art in tmp:
                art = Art.Decoder(art)
                artcollection.fanart.append(art)
        if "thumb" in json:
            tmp = json["thumb"]
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
                return "Exception: at General.Decoder --- json is not dictionary"
        general: General = General()
        if "id" in json:
            general.id = json["id"]
        if "format" in json:
            general.format = json["format"]
        if "format_version" in json:
            general.format_version = json["format_version"]
        if "size" in json:
            general.size = json["size"]
        if "duration" in json:
            general.duration = json["duration"]
        if "overallbitrate" in json:
            general.overallbitrate = json["overallbitrate"]
        if "overallbitrate_mode" in json:
            general.overallbitrate_mode = json["overallbitrate_mode"]
        if "encoded" in json:
            general.encoded = json["encoded"]
        if "encoded_date" in json:
            general.encoded_date = json["encoded_date"]
        if "encoded_lib" in json:
            general.encoded_lib = json["encoded_lib"]
        if "attachments" in json:
            general.attachments = json["attachments"]

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
                return "Exception: at Stream.Decoder --- json is not dictionary"
        stream: Stream = Stream()
        if "Title" in json:
            stream.Title = json["Title"]
        if "Language" in json:
            stream.Language = json["Language"]
        if "Key" in json:
            stream.Key = json["Key"]
        if "Duration" in json:
            stream.Duration = json["Duration"]
        if "Height" in json:
            stream.Height = json["Height"]
        if "Width" in json:
            stream.Width = json["Width"]
        if "Bitrate" in json:
            stream.Bitrate = json["Bitrate"]
        if "SubIndex" in json:
            stream.SubIndex = json["SubIndex"]
        if "Id" in json:
            stream.Id = json["Id"]
        if "ScanType" in json:
            stream.ScanType = json["ScanType"]
        if "RefFrames" in json:
            stream.RefFrames = json["RefFrames"]
        if "Profile" in json:
            stream.Profile = json["Profile"]
        if "Level" in json:
            stream.Level = json["Level"]
        if "HeaderStripping" in json:
            stream.HeaderStripping = json["HeaderStripping"]
        if "HasScalingMatrix" in json:
            stream.HasScalingMatrix = json["HasScalingMatrix"]
        if "FrameRateMode" in json:
            stream.FrameRateMode = json["FrameRateMode"]
        if "File" in json:
            stream.File = json["File"]
        if "FrameRate" in json:
            stream.FrameRate = json["FrameRate"]
        if "ColorSpace" in json:
            stream.ColorSpace = json["ColorSpace"]
        if "CodecID" in json:
            stream.CodecID = json["CodecID"]
        if "ChromaSubsampling" in json:
            stream.ChromaSubsampling = json["ChromaSubsampling"]
        if "Cabac" in json:
            stream.Cabac = json["Cabac"]
        if "BitDepth" in json:
            stream.BitDepth = json["BitDepth"]
        if "Index" in json:
            stream.Index = json["Index"]
        if "Codec" in json:
            stream.Codec = json["Codec"]
        if "StreamType" in json:
            stream.StreamType = json["StreamType"]
        if "Orientation" in json:
            stream.Orientation = json["Orientation"]
        if "QPel" in json:
            stream.QPel = json["QPel"]
        if "GMC" in json:
            stream.GMC = json["GMC"]
        if "BVOP" in json:
            stream.BVOP = json["BVOP"]
        if "SamplingRate" in json:
            stream.SamplingRate = json["SamplingRate"]
        if "LanguageCode" in json:
            stream.LanguageCode = json["LanguageCode"]
        if "Channels" in json:
            stream.Channels = json["Channels"]
        if "Selected" in json:
            stream.Selected = json["Selected"]
        if "DialogNorm" in json:
            stream.DialogNorm = json["DialogNorm"]
        if "BitrateMode" in json:
            stream.BitrateMode = json["BitrateMode"]
        if "Format" in json:
            stream.Format = json["Format"]
        if "Default" in json:
            stream.Default = json["Default"]
        if "Forced" in json:
            stream.Forced = json["Forced"]
        if "PixelAspectRatio" in json:
            stream.PixelAspectRatio = json["PixelAspectRatio"]

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
                return "Exception: at MediaInfo.Decoder --- json is not dictionary"
        mediainfo: MediaInfo = MediaInfo()
        if "general" in json:
            mediainfo.general = General.Decoder(json["general"])
        if "audios" in json:
            mediainfo.audios = Stream.Decoder(json["audios"])
        if "videos" in json:
            mediainfo.videos = Stream.Decoder(json["videos"])
        if "subtitles" in json:
            mediainfo.subtitles = Stream.Decoder(json["subtitles"])
        if "menus" in json:
            mediainfo.menus = json["menus"]

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
                return "Exception: at RawFile.Decoder --- json is not dictionary"
        rawfile: RawFile = RawFile()
        if "type" in json:
            rawfile.type = json["type"]
        if "crc32" in json:
            rawfile.crc32 = json["crc32"]
        if "ed2khash" in json:
            rawfile.ed2khash = json["ed2khash"]
        if "md5" in json:
            rawfile.md5 = json["md5"]
        if "sha1" in json:
            rawfile.sha1 = json["sha1"]
        if "created" in json:
            rawfile.created = json["created"]
        if "updated" in json:
            rawfile.updated = json["updated"]
        if "duration" in json:
            rawfile.duration = json["duration"]
        if "filename" in json:
            rawfile.filename = json["filename"]
        if "server_path" in json:
            rawfile.server_path = json["server_path"]
        if "hash" in json:
            rawfile.hash = json["hash"]
        if "hash_source" in json:
            rawfile.hash_source = json["hash_source"]
        if "is_ignored" in json:
            rawfile.is_ignored = json["is_ignored"]
        if "media" in json:
            rawfile.media = MediaInfo.Decoder(json["media"])
        if "group_full" in json:
            rawfile.group_full = json["group_full"]
        if "group_short" in json:
            rawfile.group_short = json["group_short"]
        if "group_id" in json:
            rawfile.group_id = json["group_id"]
        if "recognized" in json:
            rawfile.recognized = json["recognized"]
        if "offset" in json:
            rawfile.offset = json["offset"]
        if "videolocal_place_id" in json:
            rawfile.videolocal_place_id = json["videolocal_place_id"]
        if "import_folder_id" in json:
            rawfile.import_folder_id = json["import_folder_id"]
        if "is_preferred" in json:
            rawfile.is_preferred = json["is_preferred"]
        if "id" in json:
            rawfile.id = json["id"]
        if "name" in json:
            rawfile.name = json["name"]
        if "titles" in json:
            tmp = json["titles"]
            for title in tmp:
                title = AnimeTitle.Decoder(title)
                rawfile.titles.append(title)
        if "summary" in json:
            rawfile.summary = json["summary"]
        if "url" in json:
            rawfile.url = json["url"]
        if "added" in json:
            rawfile.added = json["added"]
        if "edited" in json:
            rawfile.edited = json["edited"]
        if "year" in json:
            rawfile.year = json["year"]
        if "air" in json:
            rawfile.air = json["air"]
        if "size" in json:
            rawfile.size = json["size"]
        if "localsize" in json:
            rawfile.localsize = json["localsize"]
        if "total_sizes" in json:
            rawfile.total_sizes = Sizes.Decoder(json['total_sizes'])
        if "local_sizes" in json:
            rawfile.local_sizes = Sizes.Decoder(json['local_sizes'])
        if "watched_sizes" in json:
            rawfile.watched_sizes = Sizes.Decoder(json['watched_sizes'])
        if "viewed" in json:
            rawfile.viewed = json["viewed"]
        if "rating" in json:
            rawfile.rating = json["rating"]
        if "votes" in json:
            rawfile.votes = json["votes"]
        if "userrating" in json:
            rawfile.userrating = json["userrating"]
        if "roles" in json:
            tmp = json["roles"]
            for role in tmp:
                role = Role.Decoder(role)
                rawfile.roles.append(role)        
        if "tags" in json:
            tmp = json["tags"]
            for tag in tmp:
                rawfile.tags.append(tag)        
        if "art" in json:
            rawfile.art = ArtCollection.Decoder(json["art"])

        return rawfile
        

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
                return "Exception: at Episode.Decoder --- json is not dictionary"
        episode: Episode = Episode()
        if "type" in json:
            episode.type = json["type"]
        if "season" in json:
            episode.season = json["season"]
        if "view" in json:
             episode.view = json["view"]
        if "view_date" in json:
             episode.view_date = json["view_date"]
        if "eptype" in json:
             episode.eptype = json["eptype"]
        if "epnumber" in json:
             episode.epnumber = json["epnumber"]
        if "aid" in json:
             episode.aid = json["aid"]
        if "eid" in json:
             episode.eid = json["eid"]
        if "files" in json:
            tmp = json["files"]
            for file in tmp:
                file = RawFile.Decoder(file)
                episode.files.append(file)
        if "id" in json:
            episode.id = json["id"]
        if "name" in json:
            episode.name = json["name"]
        if "titles" in json:
            tmp = json["titles"]
            for title in tmp:
                title = AnimeTitle.Decoder(title)
                episode.titles.append(title)
        if "summary" in json:
            episode.summary = json["summary"]
        if "url" in json:
            episode.url = json["url"]
        if "added" in json:
            episode.added = json["added"]
        if "edited" in json:
            episode.edited = json["edited"]
        if "year" in json:
            episode.year = json["year"]
        if "air" in json:
            episode.air = json["air"]
        if "size" in json:
            episode.size = json["size"]
        if "localsize" in json:
            episode.localsize = json["localsize"]
        if "total_sizes" in json:
            episode.total_sizes = Sizes.Decoder(json['total_sizes'])
        if "local_sizes" in json:
            episode.local_sizes = Sizes.Decoder(json['local_sizes'])
        if "watched_sizes" in json:
            episode.watched_sizes = Sizes.Decoder(json['watched_sizes'])
        if "viewed" in json:
            episode.viewed = json["viewed"]
        if "rating" in json:
            episode.rating = json["rating"]
        if "votes" in json:
            episode.votes = json["votes"]
        if "userrating" in json:
            episode.userrating = json["userrating"]
        if "roles" in json:
            tmp = json["roles"]
            for role in tmp:
                role = Role.Decoder(role)
                episode.roles.append(role)        
        if "tags" in json:
            tmp = json["tags"]
            for tag in tmp:
                episode.tags.append(tag)        
        if "art" in json:
            episode.art = ArtCollection.Decoder(json["art"])

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
                return "Exception: at Serie.Decoder --- json is not dictionary"
        serie: Serie = Serie()
        if "type" in json:
            serie.type = json["type"]
        if "aid" in json:
            serie.aid = json["aid"]
        if "season" in json:
            serie.season = json["season"]
        if "eps" in json:
            tmp = json["eps"]
            for ep in tmp:
                ep = Episode.Decoder(ep)
                serie.eps.append(ep)
        if "ismovie" in json:
            serie.ismovie = json["ismovie"]
        if "filesize" in json:
            serie.filesize = json["filesize"]
        if "id" in json:
            serie.id = json["id"]
        if "name" in json:
            serie.name = json["name"]
        if "titles" in json:
            tmp = json["titles"]
            for title in tmp:
                title = AnimeTitle.Decoder(title)
                serie.titles.append(title)
        if "summary" in json:
            serie.summary = json["summary"]
        if "url" in json:
            serie.url = json["url"]
        if "added" in json:
            serie.added = json["added"]
        if "edited" in json:
            serie.edited = json["edited"]
        if "year" in json:
            serie.year = json["year"]
        if "air" in json:
            serie.air = json["air"]
        if "size" in json:
            serie.size = json["size"]
        if "localsize" in json:
            serie.localsize = json["localsize"]
        if "total_sizes" in json:
            serie.total_sizes = Sizes.Decoder(json['total_sizes'])
        if "local_sizes" in json:
            serie.local_sizes = Sizes.Decoder(json['local_sizes'])
        if "watched_sizes" in json:
            serie.watched_sizes = Sizes.Decoder(json['watched_sizes'])
        if "viewed" in json:
            serie.viewed = json["viewed"]
        if "rating" in json:
            serie.rating = json["rating"]
        if "votes" in json:
            serie.votes = json["votes"]
        if "userrating" in json:
            serie.userrating = json["userrating"]
        if "roles" in json:
            tmp = json["roles"]
            for role in tmp:
                role = Role.Decoder(role)
                serie.roles.append(role)        
        if "tags" in json:
            tmp = json["tags"]
            for tag in tmp:
                serie.tags.append(tag)        
        if "art" in json:
            serie.art = ArtCollection.Decoder(json["art"])

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
                return "Exception: at Group.Decoder --- json is not dictionary"
        group: Group = Group()
        # print(f"Group.Decoder === {json}")
        if "series" in json:
            # print(json["series"])
            tmp = json["series"]
            for serie in tmp:
                serie = Serie.Decoder(serie)
                group.series.append(serie)
        if "type" in json:
            group.type = json["type"]
        if "id" in json:
            group.id = json["id"]
        if "name" in json:
            group.name = json["name"]
        if "titles" in json:
            tmp = json["titles"]
            for title in tmp:
                title = AnimeTitle.Decoder(title)
                group.titles.append(title)
        if "summary" in json:
            group.summary = json["summary"]
        if "url" in json:
            group.url = json["url"]
        if "added" in json:
            group.added = json["added"]
        if "edited" in json:
            group.edited = json["edited"]
        if "year" in json:
            group.year = json["year"]
        if "air" in json:
            group.air = json["air"]
        if "size" in json:
            group.size = json["size"]
        if "localsize" in json:
            group.localsize = json["localsize"]
        if "total_sizes" in json:
            group.total_sizes = Sizes.Decoder(json["total_sizes"])
        if "local_sizes" in json:
            group.local_sizes = Sizes.Decoder(json["local_sizes"])
        if "watched_sizes" in json:
            group.watched_sizes = Sizes.Decoder(json["watched_sizes"])
        if "viewed" in json:
            group.viewed = json["viewed"]
        if "rating" in json:
            group.rating = json["rating"]
        if "votes" in json:
            group.votes = json["votes"]
        if "userrating" in json:
            group.userrating = json["userrating"]
        if "roles" in json:
            tmp = json["roles"]
            for role in tmp:
                role = Role.Decoder(role)
                group.roles.append(role)
        if "tags" in json:
            tmp = json["tags"]
            for tag in tmp:
                group.tags.append(tag)
        if "art" in json:
            group.art = ArtCollection.Decoder(json["art"])
        
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
                return "Exception: at Filters.Decoder --- json is not dictionary"
        filters: Filters = Filters()
        if "type" in json:
            filters.type = json["type"]
        if "filters" in json:
            tmp = json["filters"]
            for filter in tmp:
                filters.filters.append(filter)
        if "id" in json:
            filters.id = json["id"]
        if "name" in json:
            filters.name = json["name"]
        if "titles" in json:
            tmp = json["titles"]
            for title in tmp:
                title = AnimeTitle.Decoder(title)
                filters.titles.append(title)
        if "summary" in json:
            filters.summary = json["summary"]
        if "url" in json:
            filters.url = json["url"]
        if "added" in json:
            filters.added = json["added"]
        if "edited" in json:
            filters.edited = json["edited"]
        if "year" in json:
            filters.year = json["year"]
        if "air" in json:
            filters.air = json["air"]
        if "size" in json:
            filters.size = json["size"]
        if "localsize" in json:
            filters.localsize = json["localsize"]
        if "total_sizes" in json:
            filters.total_sizes = Sizes.Decoder(json['total_sizes'])
        if "local_sizes" in json:
            filters.local_sizes = Sizes.Decoder(json['local_sizes'])
        if "watched_sizes" in json:
            filters.watched_sizes = Sizes.Decoder(json['watched_sizes'])
        if "viewed" in json:
            filters.viewed = json["viewed"]
        if "rating" in json:
            filters.rating = json["rating"]
        if "votes" in json:
            filters.votes = json["votes"]
        if "userrating" in json:
            filters.userrating = json["userrating"]
        if "roles" in json:
            tmp = json["roles"]
            for role in tmp:
                role = Role.Decoder(role)
                filters.roles.append(role)        
        if "tags" in json:
            tmp = json["tags"]
            for tag in tmp:
                filters.tags.append(tag)        
        if "art" in json:
            filters.art = ArtCollection.Decoder(json["art"])

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
        # self._raw = f'Type={type} ID={id} Name={name} Summary={summary} Url={url}'
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
                return "Exception: at Filter.Decoder --- json is not dictionary"
        filter: Filter = Filter()
        if "type" in json:
            filter.type = json['type']
        if "groups" in json:
            # print(f"{json['groups']}")
            tmp = json["groups"]
            for group in tmp:
                # print(f"1 {group}")
                group = Group.Decoder(group)
                # print(f"2 {group.__dict__}")
                filter.groups.append(group)
        if "filters" in json:
            tmp = json["filters"]
            for filter in tmp:
                filter = Filter.Decoder(filter)
                filter.filters.append(filter)
        if "id" in json:
            filter.id = json["id"]
        if "name" in json:
            filter.name = json["name"]
        if "titles" in json:
            tmp = json["titles"]
            for title in tmp:
                title = AnimeTitle.Decoder(title)
                filter.titles.append(title)
        if "summary" in json:
            filter.summary = json["summary"]
        if "url" in json:
            filter.url = json["url"]
        if "added" in json:
            filter.added = json["added"]
        if "edited" in json:
            filter.edited = json["edited"]
        if "year" in json:
            filter.year = json["year"]
        if "air" in json:
            filter.air = json["air"]
        if "size" in json:
            filter.size = json["size"]
        if "localsize" in json:
            filter.localsize = json["localsize"]
        if "total_sizes" in json:
            filter.total_sizes = Sizes.Decoder(json['total_sizes'])
        if "local_sizes" in json:
            filter.local_sizes = Sizes.Decoder(json['local_sizes'])
        if "watched_sizes" in json:
            filter.watched_sizes = Sizes.Decoder(json['watched_sizes'])
        if "viewed" in json:
            filter.viewed = json["viewed"]
        if "rating" in json:
            filter.rating = json["rating"]
        if "votes" in json:
            filter.votes = json["votes"]
        if "userrating" in json:
            filter.userrating = json["userrating"]
        if "roles" in json:
            tmp = json["roles"]
            for role in tmp:
                role = Role.Decoder(role)
                filter.roles.append(role)        
        if "tags" in json:
            tmp = json["tags"]
            for tag in tmp:
                filter.tags.append(tag)        
        if "art" in json:
            filter.art = ArtCollection.Decoder(json["art"])

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
                return "Exception: at ImportFolder.Decoder --- json is not dictionary"
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
                return "Exception: at Counter.Decoder --- json is not dictionary"
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
                return "Exception: at WebNews.Decoder --- json is not dictionary"
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
                return "Exception: at QueueInfo.Decoder --- json is not dictionary"
        queueinfo: QueueInfo = QueueInfo()
        queueinfo.count = json.get("count")
        queueinfo.state = json.get("state")
        queueinfo.isrunning = json.get("isrunning")
        queueinfo.ispause = json.get("ispause")

        return queueinfo