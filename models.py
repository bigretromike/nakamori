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


class Image:
    def __init__(self, source, type, id, relativefilepath):
        self.source = source
        self.type = type
        self.id = id
        self.relativefilepath = relativefilepath

    def __repr__(self):
        return '<Image(id: {}, source: {}, type: {}, path: {})>'.format(self.id, self.source, self.type, self.relativefilepath)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__


class Images:
    def __init__(self, posters):
        # b'{"Posters":[{"Source":"AniDB","Type":"Poster","ID":"14725","RelativeFilepath":"/AniDB/14/230929.jpg"}]}'
        self.posters = [Image(img.get('Source', None), img.get('Type', None), img.get('ID', None), img.get('RelativeFilepath', None)) for img in posters.get('Posters', [])]

    def __repr__(self):
        return '<Images({})>'.format(self.posters)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'IDs' in obj.keys():
            return Series(obj.get('IDs', None), obj.get('Images', None), obj.get('Created', None),
                          obj.get('Updated', None), obj.get('Name', None), obj.get('Size', None),
                          obj.get('Sizes', None), obj.get('SeriesType', None), obj.get('Title', None),
                          obj.get('Restricted', None), obj.get('AirDate', None), obj.get('EndDate', None),
                          obj.get('Titles', None), obj.get('Description', None), obj.get('Poster', None),
                          obj.get('Rating', None))
        return obj


class Series:
    def __init__(self, ids, images, created, updated, name, size, sizes, series_type=None, title=None, restricted=None, airdate=None, enddate=None, titles=None, description=None, poster=None, rating=None):
    # b'[{"IDs":{"AniDB":16539,"ID":3981},
    # "Images":{"Posters":[{"Source":"AniDB","Type":"Poster","ID":"16539","RelativeFilepath":"/AniDB/16/263387.jpg"}]},
    # "Created":"2021-08-27T23:25:31.6502042+02:00",
    # "Updated":"2021-08-27T23:28:02.0002872+02:00",
    # "Name":"AWOL Compression Re-Mix",
    # "Size":4,
    # "Sizes":{"Local":{"Episodes":4},"Watched":{},"Total":{"Episodes":4}}}]'
        self.ids = ids
        self.images = Images(images)  #{"Posters":[{"Source":"AniDB","Type":"Poster","ID":"16539","RelativeFilepath":"/AniDB/16/263387.jpg"}]}
        self.created = created
        self.updated = updated
        self.name = name
        self.size = size
        self.sizes = sizes  # {"Local":{"Episodes":4},"Watched":{},"Total":{"Episodes":4}}
        self.series_type = series_type
        self.title = title
        self.restricted = restricted
        self.airdate = airdate
        self.enddate = enddate
        self.titles = titles
        self.description = description
        self.poster = poster
        self.rating = rating

    def __repr__(self):
        return '<Series(ids: {}, name: {}, size: {})>'.format(self.ids, self.name, self.size)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'IDs' in obj.keys():
            return Series(obj.get('IDs', None), obj.get('Images', None), obj.get('Created', None),
                          obj.get('Updated', None), obj.get('Name', None), obj.get('Size', None),
                          obj.get('Sizes', None), obj.get('SeriesType', None), obj.get('Title', None),
                          obj.get('Restricted', None), obj.get('AirDate', None), obj.get('EndDate', None),
                          obj.get('Titles', None), obj.get('Description', None), obj.get('Poster', None),
                          obj.get('Rating', None))
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


class Tag:
    def __init__(self, name, description, weight):
        self.name = name
        self.description = description
        self.weight = weight

    def __repr__(self):
        return '<Tag({})>'.format(self.name)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        return Tag(obj)


class Tags:
    def __init__(self, tag):
        # b'[{"Name":"content indicators","Description":"The content indicators branch is intended to be a less geographically specific tool than the \'age rating\' used by convention, for warning about things that might cause offence. Obviously there is still a degree of subjectivity involved, but hopefully it will prove useful for parents with delicate children, or children with delicate parents.\\nNote: Refer to further guidance on http://wiki.anidb.net/w/Categories:Content_Indicators [the Wiki page] for how to apply tag weights for content indicators."},
        # {"Name":"dynamic","Description":"Some of the central structural elements in anime are: \\nPlot Continuity \\nHow does the plot or several plots unfold. Are they a strictly linear retelling of one big continuing story, a serial, possibly with several side stories, or is the content chopped into a set of unconnected episodes, only sharing the same setting and characters?\\nStereotype Characters\\nThen there is the question of the character set presentation. Is it completely original, or is it your usual stereotypical character cast. Both choices have their merit, for example it would not really make much sense to reinvent the wheel for a harem anime. Fans of that genre come to expect their favourite stereotype protagonists.\\nPlot Twists\\nFinally there is the question of how complex the plot / the story unfolds. Are there side-plots that merge into the main plot leading to unexpected plot twists, or is the anime quite predictable? The latter would not be appropriate for detective stories. In harem anime on the other hand a foreseeable outcome is actually something the fans will come to expect."},{"Name":"target audience","Description":"Anime, like everything else in the modern world, is targeted towards specific audiences, both implicitly by the creators and overtly by the marketing. While categories are associated with specific sex and age groups, this is not a bar on the anime being enjoyed by people who don\'t fit into that band; not only do crossover titles exist, but the categories also have a considerable following outside their main demographic, and a person might as well enjoy anime from all categories. Still, does not invalidate the usefulness of marking a title as one of the categories; the same themes will likely be treated differently in anime geared for different audiences. Only one should not jump the gun and assume that a title will be more or less serious or present content in this or that way due to its target audience, or conversely assume the target audience on the content and its presentation alone. As such, the audience categories help form a broad impression of how a title might work with the announced themes, but offer little to no in-depth information about specific content or its treatment.\\nThe audience categories originate from manga magazines, which group titles of a same intended audience into a magazine that is advertised as belonging to that category, and so manga-based anime will have the category from their parent work. As for anime based on other works, the audience is often debatable, but comparing information such as time slot to the manga-based anime generally helps figure out the most likely possibility.\\nIf the parent material was classified under multiple audiences over time (for example, it was originally shounen, but then as the plot changed and became more mature, it was reclassified as seinen), and the anime adapts parent material time periods covering multiple audiences, we tag all audiences covered by the anime adaptation."},{"Name":"elements","Description":"Next to Themes setting the backdrop for the protagonists in anime, there are the more detailed plot Elements that centre on character interactions: \\"What do characters do to each other or what is done to them?\\". Is it violent Action, an awe-inspiring Adventure in a foreign place, the gripping life of a Detective, a slapstick Comedy, an Ecchi Harem anime, a SciFi epic, or some Fantasy travelling adventure?"},{"Name":"18 restricted","Description":"This isn\'t really an \\"audience\\".\\nWhile some anime might feature sexual content they still might not be considered pornography. This category is meant only for when the content is clearly *not* intended for minors. The distinction is made by whether the content is sold only to adults."},{"Name":"creampie","Description":"The act of a man ejaculating inside a girl\'s vagina, leaving the semen oozing out of her.","Weight":600},{"Name":"urination","Description":"Urination, also known as micturition, voiding, peeing, weeing, pissing, and more rarely, emiction, is the ejection of urine from the urinary bladder through the urethra to the outside of the body. In healthy humans the process of urination is under voluntary control. In infants, some elderly individuals, and those with neurological injury or extreme psychological problems, urination may occur as an involuntary reflex. In other animals, in addition to expelling waste material, urination can mark territory or express submissiveness.","Weight":100},{"Name":"sex toys","Description":"A sex toy is an object or device that is primarily used to facilitate human sexual pleasure, such as a dildo or vibrator.","Weight":100},{"Name":"sex","Description":"Sexual intercourse, the ultimate bond of love and the \\"Origin of the World\\" (just think of Gustave Courbet\'s painting: http://en.wikipedia.org/wiki/L%27Origine_du_monde).\\nNote: Refer to further guidance on http://wiki.anidb.net/w/Categories:Content_Indicators [the Wiki page] for how to apply tag weights for content indicators.","Weight":600},{"Name":"nudity","Description":"Nudity is the state of wearing no clothing. The wearing of clothing is exclusively a human characteristic. The amount of clothing worn depends on functional considerations (such as a need for warmth or protection from the elements) and social considerations. In some situations the minimum amount of clothing (i.e. covering of a person\'s genitals) may be socially acceptable, while in others much more clothing is expected.\\nNote: Refer to further guidance on http://wiki.anidb.net/w/Categories:Content_Indicators [the Wiki page] for how to apply tag weights for content indicators. No frontal (visible genitals) = 1.5 stars or less.\\nPeople, as individuals and in groups, have varying attitudes towards their own nudity. Some people are relaxed about appearing less than fully clothed in front of others, while others are uncomfortable or inhibited in that regard. People are nude in a variety of situations, and whether they are prepared to disrobe in front of others depends on the social context in which the issue arises. For example, people need to bathe without clothing, some people also sleep in the nude, some prefer to sunbathe in the nude or at least topless, while others are nude in other situations. Some people adopt naturism as a lifestyle.\\nThough the wearing of clothes is the social norm in most cultures, some cultures, groups and individuals are more relaxed about nudity, though attitudes often depend on context. On the other hand, some people feel uncomfortable in the presence of any nudity, and the presence of a nude person in a public place can give rise to controversy, irrespective of the attitude of the person who is nude. Besides meeting social disapproval, in some places public nudity may constitute a crime of indecent exposure. Many people have strong views on nudity, which to them can involve issues and standards of modesty, decency and morality. Some people have an psychological aversion to nudity, called gymnophobia. Many people regard nudity to be inherently sexual and erotic.\\nNudity is to be found in a multitude of media, including art, photography, film and on the Internet. It is a factor in adult entertainment of various types.\\nEspecially gratuitous fanservice anime shows tend to show their (usually female) characters frequently without any clothes, though often hiding genitals through the means of additions like steam.\\nSource: wiki","Weight":100},{"Name":"game","Description":"Based on an interactive (even if minimally so) form of entertainment software, generally available for PCs, consoles or arcade machines."},{"Name":"erotic game","Description":"An erotic game (eroge) is a Japanese video or computer game that features erotic content, usually in the form of anime-style artwork. In English, eroge are often called hentai games in keeping with the English slang definition of hentai. This is sometimes shortened to H games. In Japan, eroge are also referred to as 18+ games. Most erotic games are visual novels or dating sims but are not limited to them.\\nAny anime adaptation of a game that contains (or had a version that contains) adult content (generally sex scenes), regardless of how some fanboys blabber on how \\"the story in that visual novel was too good to be labelled as porn!\\", should definitely get this category added under them. This should make it pretty clear as to what is an erotic game and what is not."},{"Name":"pornography","Description":"Anime clearly marked as \\"Restricted 18\\" material centring on all variations of adult sex, some of which can be considered as quite perverted. To certain extent, some of the elements can be seen on late night TV animations."},{"Name":"male protagonist","Description":"This anime has a male protagonist."},{"Name":"impregnation","Description":"At least one of the character is impregnated during the anime. This is confirmed by the characters, or the character is later shown as pregnant. Merely shouting \\"I\'ll become pregnant!\\" or something similar during sex is not impregnation.\\nA porn anime can be tagged with impregnation only when all of the following conditions are met:\\n* She must be shown having sex in such a way that she can become pregnant\\n* She must be known as http://anidb.net/t775 [pregnant] after the fact, be it the pregnant stomach, pregnancy test, verbal confirmation, doctor\'s report, etc\\n* Having an abortion after the event, does not change the fact that an impregnation still occurred\\n* http://anidb.net/t2705 [Creampies] are not a necessary criteria to have an impregnation, and impregnations do not automatically result from a creampie.\\nIf she is impregnated by a non-human, the http://anidb.net/t7148 [impregnation with larvae] tag may also apply."},{"Name":"predominantly female cast","Description":"A show with a predominantly female cast has mostly females as main and secondary cast members while few if any male characters have major roles. This also applies when a male lead is surrounded by females of lesser individual plot relevance, such as in a harem setting."},{"Name":"branching story","Description":"The whole series consists of alternative stories, starting at the same point, branching off to different endings. It is like a normal http://anidb.net/t2804 [visual novel / dating sim], where you have different choices to meet different girls."},{"Name":"technical aspects","Description":"It may sometimes be useful to know about technical aspects of a show, such as information about its broadcasting or censorship. Such information can be found here."},{"Name":"cast","Description":""},{"Name":"pregnant sex","Description":"Pregnant sex involves having sex with a pregnant individual.\\nEngaging in at least 1 pregnant sex scene is not sufficient in and of itself for tagging http://anidb.net/t775 [pregnant] on the character; only tag pregnant sex at the anime level in such a case. A character only shown pregnant for a small segment of their total appearance(s) should not be tagged as pregnant. Pregnancy and/or pregnant sex typically follows after an http://anidb.net/t3976 [impregnation] or http://anidb.net/t7148 [impregnation with larvae] scene.","Weight":300},{"Name":"lactation","Description":"Capable of secreting breast milk, sometimes referred to as Mother\'s milk.","Weight":500},{"Name":"fetishes","Description":"For non-porn anime, the fetish must be a major element of the show; incidental appearances of the fetish is not sufficient for a fetish tag. Please do not add fetish tags to anime that do not pander to the fetish in question in any meaningful way. For example, there\'s some ecchi in http://anidb.net/a22 [Shinseiki Evangelion], but the fact you get to see http://anidb.net/ch39 [Asuka]\'s pantsu is not sufficient to warrant applying the http://anidb.net/t2894 [school girl] fetish tag. See also the http://wiki.anidb.net/Tags#Minimum_Relevance_Rule [minimum relevancy rule].\\nFor porn anime, the application of fetish tags are fairly straightforward, as porn will fully play out most fetishes."},{"Name":"sixty-nine","Description":"At least one sex position from a group generically called sixty-nine or 69 is featured, characterised by a mutually inverted alignment of two people of any sex in which both perform oral sex simultaneously. Putting it another way, the top of the head of one person points more or less towards the feet of the other, and the head of each is at the height of the other\'s genitals, and both perform cunnilingus or fellatio, whichever is appropriate in each case. The name stems from this mutual inversion, which resembles the numbers 6 and 9."},{"Name":"mammary intercourse","Description":"Mammary intercourse is a sex act, performed as foreplay or as non-penetrative sex, that involves the stimulation of the male penis by the female breasts. Commonly, this sex act involves the man placing his penis in the woman\'s cleavage and thrusting between her breasts, while the breasts are squeezed around the penis for additional stimulation, and fellatio may also be performed in combination. Mammary intercourse is also commonly known as titty-fucking or titfuck in the United States, as well as tit wank or French fuck in the United Kingdom. The Japanese term, paizuri (from oppai, breasts, and the verb suru, used in this context to describe the sexual act), is commonly used in the anime fandom. A variant term is \\"naizuri\\" (a pun on nai, the negative of the verb aru, indicating existence/presence), which describes an attempt to do a paizuri, but with insufficient cleavage.","Weight":100},{"Name":"masturbation","Description":"Manual erotic stimulation of the genitals or other erogenous regions, often to orgasm, either by oneself or a partner.","Weight":100},{"Name":"oral","Description":"Oral sex is sexual activity involving the stimulation of the genitalia of a sex partner by the use of the mouth, tongue, teeth or throat."},{"Name":"ahegao","Description":"A term for the weird face occasionally seen in adult games/anime/manga. Canonically, ahegao has eyes rolled up, mouth open and tongue sticking out. Sometimes also referred to as \\"fucked silly\\".","Weight":300},{"Name":"BDSM","Description":"A form of \\"kinky sex\\". The acronym BDSM derives from BD (bondage and discipline), DS (dominance and submission) and SM (sadism and masochism). BDSM usually characterizes with one side being superior (active) over the other (passive), with each side being one or more participants. Whips, chains, handcuffs, ropes, blindfolds are common elements of BDSM."},{"Name":"foot fetish","Description":"Anime contains scenes which revolve around foot-fetishism.","Weight":100},{"Name":"deflowering","Description":"Deflowering is the act of breaking the hymen of a female who hadn\'t yet had vaginal intercourse. This tag can be applied only to pornographic anime in which a female is seen being deflowered; most often, one knows she had been a virgin because blood is seen coming out of her vagina during sex or after it, but her word on the matter is also considered valid.","Weight":200},{"Name":"dildos - vibrators","Description":"These are toys that are used for sexual pleasure.","Weight":100},{"Name":"bondage","Description":"Bondage is the use of restraints for the sexual pleasure of the parties involved. It may be used in its own right, as in the case of rope bondage and breast bondage, or as part of sexual activity or BDSM activity. When a person is sexually aroused by bondage, it may be considered a paraphilia, known as vincilagnia (from Latin vincio, to bind or fetter with chains, and lagneia, lust).\\n[Source: wiki]","Weight":300},
        # {"Name":"footjob","Description":"A foot is used to invoke sexual pleasure.","Weight":100}]'

        self.tags = []
        self.tags.append(Tag(tag.get('Name', None), tag.get('Description', None), tag.get('Weight', None)))

    def __repr__(self):
        return '<Tags({})>'.format(self.tags)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        return Tag(obj.get('Name', None), obj.get('Description', None), obj.get('Weight', None))


class CastImage:
    def __init__(self, img):
        if img is not None:
            self.source = img.get('Source', None)
            self.type = img.get('Type', None)
            self.id = img.get('ID', None)
            self.relativefilepath = img.get('RelativeFilepath', None)

    def __repr__(self):
        return '<CastImage({}, {}, {})>'.format(self.source, self.type, self.id)


class Staff:
    def __init__(self, staff):
        self.name = staff.get('Name', None)
        self.image = CastImage(staff.get('Image', None))

    def __repr__(self):
        return '<Staff({})>'.format(self.name)


class Character:
    def __init__(self, char):
        self.name = char.get('Name', None)
        self.alternatename = char.get('AlternateName', None)
        self.description = char.get('Description', None)
        self.image = CastImage(char.get('Image', None))

    def __repr__(self):
        return '<Character({})>'.format(self.name)


class Cast:
    def __init__(self, staff, character, rolename, roledatails):
        if staff is not None:
            self.staff = Staff(staff)
        if character is not None:
            self.character = Character(character)
        self.rolename = rolename
        self.roledatails = roledatails

    def __repr__(self):
        return '<Cast({}, {}, {})>'.format(self.staff, self.character, self.rolename)


class FullCast:
    def __init__(self, cast):
        # b'[{"Staff":{"Name":"Aoi Miu","Image":{"Source":"Shoko","Type":"Staff","ID":"615","RelativeFilepath":"/AniDB_Creator/14/150923.jpg"}},
        # "Character":{"Name":"Katsuragi Sayaka","AlternateName":"","Description":"","Image":{"Source":"Shoko","Type":"Character","ID":"1193","RelativeFilepath":"/AniDB_Char/86/198011.jpg"}},
        # "RoleName":"Seiyuu",
        # "RoleDetails":"Minor Character"}]

        self.casts = []
        self.casts.append(Cast(cast.get('Staff', None), cast.get('Character', None), cast.get('RoleName', None), cast.get('RoleDetails', None)))

    def __repr__(self):
        return '<FullCast({})>'.format(self.casts)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'Staff' in obj:
            return FullCast(obj)  # Cast(obj.get('Staff', None), obj.get('Character', None), obj.get('RoleName', None), obj.get('RoleDetails', None))
        return obj

# endregion



# region Series

# endregion