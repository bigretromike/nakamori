# Comment any you don't believe should be in here or create an ongoing issue for discussion
tagBlacklistAniDBHelpers=[
    "broadcast cropped to 4-3",
    "cast missing",
    "cast",
    "content indicators",
    "delayed 16-9 broadcast",
    "description missing",
    "development hell",  # :( God Eater
    "dialogue driven",  # anidb and their british spellings
    "earth",
    "elements",
    "ensemble cast",
    "fast-paced",
    "full hd version available",
    "jdrama adaptation",
    "meta tags",
    "multi-anime projects",
    "new",
    "noitamina",
    "past",
    "place",
    "present",
    "season",
    "sentai",
    "setting",
    "some weird shit goin` on", # these are some grave accents in use...
    "target audience",
    "television programme",
    "themes",
    "translation convention",
    "tropes"
]

tagBlackListSource=[
    "4-koma",
    "game",
    "manga",
    "novel",
    "remake",
    "visual novel"
]

tagBlackListArtStyle=[
    "3d cg animation",
    "3d cg closing",
    "cel-shaded animation",
    "cgi",
    "chibi ed",
    "experimental animation",
    "flash animation",
    "live-action closing",
    "live-action imagery",
    "off-model animation",
    "photographic backgrounds",
    "product placement",
    "recycled animation",
    "slide show animation",
    "thick line animation",
    "vignette scenes",
    "watercolour style",
    "widescreen transition"
]

tagBlackListUsefulHelpers=[
    "ed variety",
    "half-length episodes",
    "long episodes",
    "multi-segment episodes",
    "op and ed sung by characters",
    "op variety",
    "post-credits scene",
    "recap in opening",
    "short episodes",
    "short movie",
    "stand-alone movie",
    "subtle op ed sequence change"
]

tagBlackListPlotSpoilers=[
    "branching story",
    "cliffhangers",
    "colour coded",
    "complex storyline",
    "drastic change in sequel",
    "dynamic",
    "fillers",
    "first girl wins",  # seriously a spoiler
    "incomplete story",
    "inconclusive",
    "inconclusive romantic plot",
    "non-linear",
    "open-ended",
    "room for sequel",
    "sudden change of pace",
    "tone changes",
    "unresolved",
    "unresolved romance"
]

# Feed this a list of str types
def processTags(addon,string):

    toRemove=[]
    removeOriginal=False

    for a in string:
        if addon.getSetting("hideArtTags") == "true":
            for remove in tagBlackListArtStyle:
                if remove == str(a).lower():
                    toRemove.append(a)
                    break
        if addon.getSetting("hideSourceTags") == "true":
            for remove in tagBlackListSource:
                if remove == str(a).lower():
                    toRemove.append(a)
                    break
            if "original work" == str(a).lower():
                toRemove.append(a)
        else:
            for remove in tagBlackListSource:
                if remove == str(a).lower():
                    removeOriginal=True
                    break

        if addon.getSetting("hideUsefulMiscTags") == "true":
            for remove in tagBlackListUsefulHelpers:
                if remove == str(a).lower():
                    toRemove.append(a)
                    break
            if str(a).lower().startswith("preview"):
                toRemove.append(a)

        if addon.getSetting("hideSpoilerTags") == "true":
            for remove in tagBlackListPlotSpoilers:
                if remove == str(a).lower():
                    toRemove.append(a)
                    break
            if str(a).lower().startswith("plot"):
                toRemove.append(a)
            if str(a).lower().endswith(" dies"):
                toRemove.append(a)
            if str(a).lower().endswith(" end"):
                toRemove.append(a)
            if str(a).lower().endswith(" ending"):
                toRemove.append(a)

        if addon.getSetting("hideMiscTags") == "true":
            for remove in tagBlacklistAniDBHelpers:
                if remove == str(a).lower():
                    toRemove.append(a)
                    break
            if "to be" in str(a).lower():
                if "merged" in str(a).lower():
                    toRemove.append(a)
                elif "deleted" in str(a).lower():
                    toRemove.append(a)
                elif "split" in str(a).lower():
                    toRemove.append(a)
                elif "moved" in str(a).lower():
                    toRemove.append(a)
            elif "need" in str(a).lower():
                if "merging" in str(a).lower():
                    toRemove.append(a)
                elif "deleting" in str(a).lower():
                    toRemove.append(a)
                elif "moving" in str(a).lower():
                    toRemove.append(a)
            elif "old animetags" in str(a).lower():
                toRemove.append(a)
            elif "censor" in str(a).lower():
                toRemove.append(a)
            elif str(a).lower().startswith("predominantly"):
                toRemove.append(a)
            elif str(a).lower().startswith("weekly"):
                toRemove.append(a)

    # on a separate loop in case 'original work' came before the source
    if removeOriginal == True:
        for a in string:
            if str(a).lower() == "original work":
                toRemove.append("original work")
                # both just in case
                toRemove.append("Original Work")
                break


    for a in toRemove:
        if a in string:
            string.remove(a)

    return string
