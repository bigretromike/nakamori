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
        self.size = size if size is not None else 0
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


class Title:
    def __init__(self, name, language, source):
        self.name = name
        self.language = language
        self.source = source

    def __repr__(self):
        return '<Title({}, {}, {})>'.format(self.name, self.language, self.source)


class Rating:
    def __init__(self, value, maxvalue, source, votes):
        # {"Value":3.94,"MaxValue":10,"Source":"AniDB","Votes":2}
        self.value = value
        self.maxvalue = maxvalue
        self.source = source
        self.votes = votes

    def __repr__(self):
        return '<Rating({}, {})>'.format(self.value, self.votes)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__


class EpisodeAniDB:
    def __init__(self, id, type, episodenumber, airdate, titles, description, rating):
        # b'{
        # "ID":225445,
        # "Type":1,
        # "EpisodeNumber":1,"
        # AirDate":"2020-01-04",
        # "Titles":[{"Name":"\xe5\x88\x9d\xe9\x99\xa3[\xe3\x83\x95\xe3\x82\xa1\xe3\x83\xbc\xe3\x82\xb9\xe3\x83\x88\xe3\x82\xb2\xe3\x83\xbc\xe3\x83\xa0]","Language":"JA","Source":"AniDB"},
        #           {"Name":"First Game","Language":"EN","Source":"AniDB"},
        #           {"Name":"First Game - Premier combat","Language":"FR","Source":"AniDB"},
        #           {"Name":"\xd8\xa7\xd9\x84\xd9\x84\xd8\xb9\xd8\xa8\xd8\xa9 \xd8\xa7\xd9\x84\xd8\xa3\xd9\x88\xd9\x84\xd9\x89","Language":"AR","Source":"AniDB"},
        #           {"Name":"First Game","Language":"X-JAT","Source":"AniDB"}],
        # "Description":"One day, high school student Kaname Sudo\xe2\x80\x99s average life is interrupted by the arrival of an emailed invitation to join \xe2\x80\x9cDarwin\xe2\x80\x99s Game.\xe2\x80\x9d Without even thinking, he opens the app, thereby becoming a player in the game. Just as Kaname begins to suspect there\xe2\x80\x99s more to the shady app than meets the eye, his first battle suddenly begins, with a mysterious man in a panda suit lunging at him with a butcher knife. \\nWill Kaname survive his first, desperate battle against a bloodthirsty killer?\\nSource: crunchyroll",
        # "Rating":{"Value":3.94,"MaxValue":10,"Source":"AniDB","Votes":2}}'
        self.id = id
        self.type = type
        self.episodenumber = episodenumber
        self.airdate = airdate
        self.titles = [Title(title.get('Name', None), title.get('Language', None), title.get('Source', None)) for title in titles]
        self.description = description
        self.rating = Rating(rating.get('Value', None), rating.get('MaxValue', None), rating.get('Source', None), rating.get('Votes', None))

    def __repr__(self):
        return '<EpisodeAniDB({}, {}, {})>'.format(self.id, self.type, self.episodenumber)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'ID' in obj.keys():
            return EpisodeAniDB(obj.get('ID', None), obj.get('Type', None), obj.get('EpisodeNumber', None),
                                obj.get('AirDate', None), obj.get('Titles', None), obj.get('Description', None),
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


class Conditions:
    def __init__(self, conditions):
        # b'{"Conditions":[{"Type":14,"Operator":1,"Parameter":""}]}'
        self.conditions = [Condition(condition.get('Type', None),condition.get('Operator', None),condition.get('Parameter', None)) for condition in conditions.get('Conditions', [])]

    def __repr__(self):
        return '<Conditions({})>'.format(self.conditions)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'Conditions' in obj:
            return Conditions(obj)  # Cast(obj.get('Staff', None), obj.get('Character', None), obj.get('RoleName', None), obj.get('RoleDetails', None))
        return obj


class Condition:
    def __init__(self, type, operator, parameter):
        # b'{"Conditions":[{"Type":14,"Operator":1,"Parameter":""}]}'
        self.type = type
        self.operator = operator
        self.parameter = parameter

    def __repr__(self):
        return '<Condition({}, {}, {})>'.format(self.type, self.operator, self.parameter)


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


class Hashes:
    def __init__(self, hashes):
        # {"ED2K":"F0D28BF0603E78DED467003C3C1B9EE4","SHA1":"4B25AE178DC9D87EE55AF83D0432ECB202F1A1DF","CRC32":"D7A0BEE4","MD5":"B34A4D71ABB885C4DE1CA9AF7B47FC35"}
        if hashes is not None:
            self.ed2k = hashes.get('ED2k', None)
            self.sha1 = hashes.get('SHA1', None)
            self.crc32 = hashes.get('CRC32', None)
            self.md5 = hashes.get('MD5', None)

    def __repr__(self):
        return '<Hashes({}, {})>'.format(self.ed2k if self.ed2k is not None else '', self.crc32)


class Location:
    def __init__(self, importfolderid, relativepath):
        self.importfolderid = importfolderid
        self.relativepath = relativepath

    def __repr__(self):
        return '<Location({}, {})>'.format(self.importfolderid, self.relativepath)


class IDsList:
    def __init__(self, seriesid, episodeid):
        # {"SeriesID":{"AniDB":12661,"ID":4},"EpisodeIDs":[{"AniDB":209780,"ID":140}]}
        self.seriesid = seriesid
        self.episodeid = episodeid

    def __repr__(self):
        return '<IDs({}, {})>'.format(self.seriesid, self.episodeid)


class File:
    def __init__(self, id, size, hashes, locations, resumeposition, created, seriesids=[]):
        # b'{
        # "ID":3,
        # "Size":1441021183,
        # "Hashes":{"ED2K":"F0D28BF0603E78DED467003C3C1B9EE4","SHA1":"4B25AE178DC9D87EE55AF83D0432ECB202F1A1DF","CRC32":"D7A0BEE4","MD5":"B34A4D71ABB885C4DE1CA9AF7B47FC35"},
        # "Locations":[{"ImportFolderID":2,"RelativePath":"Boku no Tonari ni Ankoku Hakaishin ga Imasu\xe2\x80\xa4\\\\[HorribleSubs] Boku no Tonari ni Ankoku Hakaishin ga Imasu - 05 [1080p].mkv"}],
        # "ResumePosition":0,
        # "Created":"2020-03-03T16:55:42"}'
        # ----- DETAILED VERSION ----
        # b'{"SeriesIDs":[{"SeriesID":{"AniDB":12661,"ID":4},"EpisodeIDs":[{"AniDB":209780,"ID":140}]}'
        self.id = id
        self.size = size
        self.hashes = Hashes(hashes)
        if locations is not None:
            self.locations = [Location(location.get('ImportFolderID', None), location.get('RelativePath', None)) for location in locations]
        self.resumeposition = resumeposition
        self.created = created
        # TODO fix __repr__ for IDs
        self.seriesids = [IDsList(seriesid.get('SeriesID', None), seriesid.get('EpisodeIDs', None)) for seriesid in seriesids]

    def __repr__(self):
        return '<File({}, {}, {})>'.format(self.id, self.size, self.created)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'ID' in obj:
            return File(obj.get('ID', None), obj.get('Size', None), obj.get('Hashes', None), obj.get('Locations', None),
                        obj.get('ResumePosition', None), obj.get('Created', None), obj.get('SeriesIDs', []))
        return obj


class FileMediaInfo:
    def __init__(self):
        pass


class ReleaseGroup:
    def __init__(self, name, shortname, id):
        # {"Name": "HorribleSubs", "ShortName": "HorribleSubs", "ID": 7172}
        self.name = name
        self.shortname = shortname
        self.id = id

    def __repr__(self):
        return '<ReleaseGroup({}, {}, {})>'.format(self.id, self.name, self.shortname)


class FileAniDB:
    def __init__(self, id, source, releasegroup, releasedate, version, originalfilename, filesize, duration, resolution,
                 descirption, audiocodes, audiolanguages, sublanguage, videocodec, updated):
        # b'{"ID":2450313,
        # "Source":"www",
        # "ReleaseGroup":{"Name":"HorribleSubs","ShortName":"HorribleSubs","ID":7172},
        # "ReleaseDate":"2020-02-08",
        # "Version":1,
        # "OriginalFileName":"[HorribleSubs] Boku no Tonari ni Ankoku Hakaishin ga Imasu - 05 [1080p].mkv",
        # "FileSize":1441021183,
        # "Duration":"00:23:40",
        # "Resolution":"1920x1080",
        # "Description":"",
        # "AudioCodecs":["(HE-)AAC"],
        # "AudioLanguages":["japanese"],
        # "SubLanguages":["english"],
        # "VideoCodec":"H264/AVC",
        # "Updated":"2020-03-03T16:58:34"}'
        self.id = id
        self.source = source
        self.releasegroup = ReleaseGroup(releasegroup.get('Name', None), releasegroup.get('ShortName', None), releasegroup.get('ID', None))
        self.releasedate = releasedate
        self.version = version
        self.originalfilename = originalfilename
        self.filesize = filesize
        self.duration = duration
        self.resolution = resolution
        self.descirption = descirption
        self.audiocodes = audiocodes
        self.audiolanguages = audiolanguages
        self.sublanguage = sublanguage
        self.videocodec = videocodec
        self.updated = updated

    def __repr__(self):
        return '<FileAniDB({}, {}, {})>'.format(self.id, self.source, self.version)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'ID' in obj and 'ShortName' not in obj:
            return FileAniDB(obj.get('ID', None), obj.get('Source', None), obj.get('ReleaseGroup', None),
                        obj.get('ReleaseDate', None), obj.get('Version', None), obj.get('OriginalFileName', None),
                        obj.get('FileSize', None), obj.get('Duration', None), obj.get('Resolution', None),
                        obj.get('Description', None), obj.get('AudioCodecs', None), obj.get('AudioLanguages', None),
                        obj.get('SubLanguages', None), obj.get('VideoCodec', None), obj.get('Updated', None))
        return obj


class FolderDrives:
    def __init__(self, drivetype, path, canaccess, sizes):
        # b'[{"DriveType":"Fixed","Path":"C:\\\\","CanAccess":true,"Sizes":{"Folders":20,"Files":3}},]'
        self.drivetype = drivetype
        self.path = path
        self.canaccess = canaccess
        self.sizes = sizes

    def __repr__(self):
        return '<FolderDriver({})>'.format(self.path)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'DriveType' in obj:
            return FolderDrives(obj.get('DriveType', None), obj.get('Path', None), obj.get('CanAccess', None),
                             obj.get('Sizes', None))
        return obj


class Folder:
    def __init__(self, path, canaccess, sizes):
        # b'[{"Path":"C:\\\\Program Files (x86)\\\\Shoko\\\\Shoko Server\\\\cs","CanAccess":true,"Sizes":{"Files":19}}]'
        self.path = path
        self.canaccess = canaccess
        self.sizes = sizes

    def __repr__(self):
        return '<Folder({})>'.format(self.path)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'Path' in obj:
            return Folder(obj.get('Path', None), obj.get('CanAccess', None),
                             obj.get('Sizes', None))
        return obj


class ImportFolder:
    def __init__(self, id, dropfoldertype, path, filesszie, name, size):
        # b'[{"ID":2,"DropFolderType":2,"Path":"\\\\\\\\AKIRA\\\\anime\\\\","FileSize":18158552044584,"Name":"NA","Size":3976},{"ID":4,"DropFolderType":1,"Path":"\\\\\\\\AKIRA\\\\photo\\\\NewNew\\\\","FileSize":20485918470,"Name":"NA","Size":2}]'
        self.id = id
        self.dropfoldertype = dropfoldertype
        self.path = path
        self.filessize = filesszie
        self.name = name
        self.size = size

    def __repr__(self):
        return '<ImportFolder({}, {})>'.format(self.id, self.path)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'Path' in obj:
            return ImportFolder(obj.get('ID', None), obj.get('DropFolderType', None), obj.get('Path', None),
                                obj.get('FileSize', None), obj.get('Name', None), obj.get('Size', None))
        return obj


class Settings:
    def __init__(self, settings):
        # TODO change this to better model, as we need it to Post later
        # b'{"AnimeXmlDirectory":"C:\\\\ProgramData\\\\ShokoServer\\\\Anime_HTTP",
        # "MyListDirectory":"C:\\\\ProgramData\\\\ShokoServer\\\\MyList",
        # "ServerPort":8111,"PluginAutoWatchThreshold":0.89,
        # "Culture":"en",
        # "WebUI_Settings":"{\\"v3\\":{\\"actions\\":[\\"remove-missing-files-mylist\\",\\"update-series-stats\\",\\"update-all-anidb-info\\",\\"update-all-tvdb-info\\",\\"plex-sync-all\\",\\"run-import\\"],\\"layout\\":{\\"dashboard\\":{\\"lg\\":[{\\"i\\":\\"collectionBreakdown\\",\\"x\\":0,\\"y\\":0,\\"w\\":6,\\"h\\":6,\\"minW\\":5,\\"minH\\":6,\\"maxH\\":8,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"seriesBreakdown\\",\\"x\\":6,\\"y\\":0,\\"w\\":6,\\"h\\":6,\\"minW\\":5,\\"minH\\":6,\\"maxH\\":8,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"commandQueue\\",\\"x\\":0,\\"y\\":6,\\"w\\":5,\\"h\\":10,\\"minW\\":5,\\"minH\\":5,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"importFolders\\",\\"x\\":5,\\"y\\":6,\\"w\\":4,\\"h\\":10,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"importBreakdown\\",\\"x\\":0,\\"y\\":16,\\"w\\":9,\\"h\\":11,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"actionItems\\",\\"x\\":9,\\"y\\":6,\\"w\\":3,\\"h\\":10,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"filesBreakdown\\",\\"x\\":9,\\"y\\":16,\\"w\\":3,\\"h\\":11,\\"moved\\":false,\\"static\\":false}],\\"sm\\":[{\\"w\\":6,\\"h\\":6,\\"x\\":0,\\"y\\":0,\\"i\\":\\"collectionBreakdown\\",\\"minW\\":5,\\"minH\\":6,\\"maxH\\":8,\\"moved\\":false,\\"static\\":false},{\\"w\\":6,\\"h\\":6,\\"x\\":0,\\"y\\":6,\\"i\\":\\"seriesBreakdown\\",\\"minW\\":5,\\"minH\\":6,\\"maxH\\":8,\\"moved\\":false,\\"static\\":false},{\\"w\\":5,\\"h\\":10,\\"x\\":0,\\"y\\":12,\\"i\\":\\"commandQueue\\",\\"minW\\":5,\\"minH\\":5,\\"moved\\":false,\\"static\\":false},{\\"w\\":4,\\"h\\":10,\\"x\\":2,\\"y\\":22,\\"i\\":\\"importFolders\\",\\"moved\\":false,\\"static\\":false},{\\"w\\":6,\\"h\\":11,\\"x\\":0,\\"y\\":42,\\"i\\":\\"importBreakdown\\",\\"moved\\":false,\\"static\\":false},{\\"w\\":3,\\"h\\":10,\\"x\\":3,\\"y\\":32,\\"i\\":\\"actionItems\\",\\"moved\\":false,\\"static\\":false},{\\"w\\":3,\\"h\\":11,\\"x\\":3,\\"y\\":53,\\"i\\":\\"filesBreakdown\\",\\"moved\\":false,\\"static\\":false}]},\\"importFolders\\":{\\"lg\\":[{\\"i\\":\\"importBreakdown\\",\\"x\\":0,\\"y\\":0,\\"w\\":8,\\"h\\":11,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"importFolders\\",\\"x\\":8,\\"y\\":0,\\"w\\":4,\\"h\\":11,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"seriesInImportFolder\\",\\"x\\":0,\\"y\\":11,\\"w\\":12,\\"h\\":11,\\"moved\\":false,\\"static\\":false}]},\\"actions\\":{\\"lg\\":[{\\"i\\":\\"anidb\\",\\"x\\":0,\\"y\\":0,\\"w\\":4,\\"h\\":9,\\"minW\\":3,\\"minH\\":5,\\"maxH\\":10,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"shoko\\",\\"x\\":4,\\"y\\":0,\\"w\\":4,\\"h\\":9,\\"minW\\":3,\\"minH\\":5,\\"maxH\\":10,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"import\\",\\"x\\":8,\\"y\\":0,\\"w\\":4,\\"h\\":9,\\"minW\\":3,\\"minH\\":5,\\"maxH\\":10,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"moviedb\\",\\"x\\":0,\\"y\\":14,\\"w\\":4,\\"h\\":4,\\"minW\\":3,\\"minH\\":4,\\"maxH\\":10,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"images\\",\\"x\\":4,\\"y\\":9,\\"w\\":4,\\"h\\":9,\\"minW\\":3,\\"minH\\":5,\\"maxH\\":10,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"plex\\",\\"x\\":8,\\"y\\":9,\\"w\\":4,\\"h\\":4,\\"minW\\":3,\\"minH\\":4,\\"maxH\\":10,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"trakt\\",\\"x\\":8,\\"y\\":14,\\"w\\":4,\\"h\\":5,\\"minW\\":3,\\"minH\\":5,\\"maxH\\":10,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"tvdb\\",\\"x\\":0,\\"y\\":9,\\"w\\":4,\\"h\\":5,\\"minW\\":3,\\"minH\\":5,\\"maxH\\":10,\\"moved\\":false,\\"static\\":false}]},\\"settings\\":{\\"lg\\":[{\\"i\\":\\"general\\",\\"x\\":0,\\"y\\":0,\\"w\\":4,\\"h\\":15,\\"minW\\":3,\\"minH\\":5,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"anidb-login\\",\\"x\\":0,\\"y\\":15,\\"w\\":4,\\"h\\":8,\\"minW\\":3,\\"minH\\":5,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"relation\\",\\"x\\":0,\\"y\\":23,\\"w\\":4,\\"h\\":10,\\"minW\\":3,\\"minH\\":3,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"anidb\\",\\"x\\":4,\\"y\\":0,\\"w\\":4,\\"h\\":21,\\"minW\\":3,\\"minH\\":5,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"import\\",\\"x\\":4,\\"y\\":21,\\"w\\":4,\\"h\\":7,\\"minW\\":3,\\"minH\\":3,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"plex\\",\\"x\\":4,\\"y\\":28,\\"w\\":4,\\"h\\":5,\\"minW\\":3,\\"minH\\":3,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"tvdb\\",\\"x\\":8,\\"y\\":0,\\"w\\":4,\\"h\\":12,\\"minW\\":3,\\"minH\\":5,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"moviedb\\",\\"x\\":8,\\"y\\":12,\\"w\\":4,\\"h\\":7,\\"minW\\":3,\\"minH\\":5,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"language\\",\\"x\\":8,\\"y\\":19,\\"w\\":4,\\"h\\":9,\\"minW\\":3,\\"minH\\":3,\\"moved\\":false,\\"static\\":false},{\\"i\\":\\"trakt\\",\\"x\\":8,\\"y\\":28,\\"w\\":4,\\"h\\":5,\\"minW\\":3,\\"minH\\":3,\\"moved\\":false,\\"static\\":false}]}},\\"notifications\\":true,\\"theme\\":\\"\\",\\"toastPosition\\":\\"bottom-right\\",\\"updateChannel\\":\\"stable\\"}}","LegacyRenamerMaxEpisodeLength":33,"LogRotator":{"Enabled":true,"Zip":true,"Delete":true,"Delete_Days":""},"Database":{"MySqliteDirectory":"C:\\\\ProgramData\\\\ShokoServer\\\\SQLite","DatabaseBackupDirectory":"C:\\\\ProgramData\\\\ShokoServer\\\\DatabaseBackup","Type":"SQLite","Username":"","Password":"","Schema":"","Hostname":"","SQLite_DatabaseFile":"C:\\\\ProgramData\\\\ShokoServer\\\\SQLite\\\\JMMServer.db3"},"AniDb":{"Username":"bigretromike","Password":"qwerty123456","ServerAddress":"api.anidb.net","ServerPort":9000,"ClientPort":4556,"AVDumpKey":"","AVDumpClientPort":4557,"DownloadRelatedAnime":true,"DownloadSimilarAnime":true,"MyList_AddFiles":true,"MyList_StorageState":2,"MyList_DeleteType":2,"MyList_ReadUnwatched":true,"MyList_ReadWatched":true,"MyList_SetWatched":true,"MyList_SetUnwatched":true,"MyList_UpdateFrequency":1,"Calendar_UpdateFrequency":3,"Anime_UpdateFrequency":4,"MyListStats_UpdateFrequency":4,"File_UpdateFrequency":4,"DownloadCharacters":true,"DownloadCreators":true,"MaxRelationDepth":3},"WebCache":{"Address":"https://localhost:44307","XRefFileEpisode_Get":true,"XRefFileEpisode_Send":true,"TvDB_Get":true,"TvDB_Send":true,"Trakt_Get":true,"Trakt_Send":true},"TvDB":{"AutoFanart":true,"AutoFanartAmount":3,"AutoWideBanners":true,"AutoWideBannersAmount":3,"AutoPosters":true,"AutoPostersAmount":3,"UpdateFrequency":3,"Language":"en"},"MovieDb":{"AutoFanart":true,"AutoFanartAmount":3,"AutoPosters":true,"AutoPostersAmount":3},"Import":{"VideoExtensions":["MKV","AVI","MP4","MOV","OGM","WMV","MPG","MPEG","MK3D","M4V","FLAC","ASS","SRT","MKA","SSA","AC3","MP3","RM","RMVB","FLV"],"Exclude":["[\\\\\\\\\\\\/]\\\\$RECYCLE\\\\.BIN[\\\\\\\\\\\\/]","[\\\\\\\\\\\\/]\\\\.Recycle\\\\.Bin[\\\\\\\\\\\\/]","[\\\\\\\\\\\\/]\\\\.Trash-\\\\d+[\\\\\\\\\\\\/]"],"DefaultSeriesLanguage":1,"DefaultEpisodeLanguage":1,"UseExistingFileWatchedStatus":true,"FileLockChecking":true,"AggressiveFileLockChecking":true,"FileLockWaitTimeMS":4000,"AggressiveFileLockWaitTimeSeconds":8,"RenameOnImport":true,"MoveOnImport":true,"MediaInfoTimeoutMinutes":5},"Plex":{"ThumbnailAspects":"Default, 0.6667, IOS, 1.0, Android, 1.3333","Token":"","Server":""},"Plugins":{},"AutoGroupSeriesRelationExclusions":"same setting|character","FileQualityPreferences":{"Require10BitVideo":true,"MaxNumberOfFilesToKeep":1,"PreferredTypes":[1,0,3,8,7,6,4,5,2],"PreferredAudioCodecs":["flac","dca","aac","ac3","wmav2","wmapro","adpcm_ms","mp3","mp2","vp6f"],"PreferredResolutions":["2160p","1440p","1080p","720p","480p"],"PreferredSubGroups":["fffpeeps","doki","commie","horriblesubs"],"PreferredVideoCodecs":["hevc","h264","mpeg4","vc1","flv","mpeg2","mpeg1","vp6f"],"RequiredTypes":[1,6,2],"RequiredAudioCodecs":{"Operator":3,"Value":["flac","dca","aac"]},"RequiredAudioStreamCount":{"Operator":2,"Value":1},"RequiredResolutions":{"Operator":2,"Value":["1080p"]},"RequiredSources":{"Operator":3,"Value":["bd","dvd"]},"RequiredSubGroups":{"Operator":4,"Value":["horriblesubs"]},"RequiredSubStreamCount":{"Operator":2,"Value":1},"RequiredVideoCodecs":{"Operator":3,"Value":["hevc","h264"]},"PreferredSources":["bd","dvd","tv","www","unknown"]},"LanguagePreference":["x-jat","en"],
        # "EpisodeLanguagePreference":"",
        # "LanguageUseSynonyms":true,
        # "CloudWatcherTime":3,
        # "EpisodeTitleSource":1,
        # "SeriesDescriptionSource":1,
        # "SeriesNameSource":1,
        # "TraktTv":{"PIN":"","AuthToken":"","RefreshToken":"","TokenExpirationDate":"","UpdateFrequency":4,"SyncFrequency":4},
        # "UpdateChannel":"Stable",
        # "Linux":{"UID":-1,"GID":-1},
        # "GA_ClientId":"ca962955-2d36-4068-a858-6b1f792603c8"}'
        self.settings = settings

    def __repr__(self):
        return '<Settings()>'

    @staticmethod
    def Decoder(obj):
        return Settings(obj)


class User:
    def __init__(self, id, username, isadmin, communitysites, tagblacklist=[]):
        #b'[{"ID":1,"Username":"Default","IsAdmin":true,"CommunitySites":[1,2]},
        # {"ID":2,"Username":"Family Friendly","IsAdmin":true,"CommunitySites":[1,2],"TagBlacklist":["ecchi","nudity","sex","sexual abuse","horror","erotic game","incest","18 restricted"]}]'
        self.id = id
        self.username = username
        self.isadmin = isadmin
        self.communitysites = communitysites
        self.tagblacklist = tagblacklist

    def __repr__(self):
        return '<User({}, {}, {})>'.format(self.id, self.username, self.isadmin)

    class Encoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

    @staticmethod
    def Decoder(obj):
        if 'ID' in obj and 'Username' in obj:
            return User(obj.get('ID', None), obj.get('Username', None), obj.get('IsAdmin', None),
                        obj.get('CommunitySites', None), obj.get('TagBlacklist', None))
        return obj

# endregion



# region Series

# endregion