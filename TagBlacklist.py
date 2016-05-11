# Comment any you don't believe should be in here or create an ongoing issue for discussion
tagBlacklistAniDBHelpers=[
    "cast missing",
    "cast",
    "content indicators",
    "delayed 16-9 broadcast",
    "description missing",
    "dynamic",
    "earth",
    "elements",
    "ensemble cast",
    "fillers",
    "full hd version available",
    "incomplete story",
    "inconclusive",
    "inconclusive romantic plot",
    "jdrama adaptation",
    "meta tags",
    "multi-anime projects",
    "new",
    "noitamina",
    "open-ended",
    "past",
    "place",
    "present",
    "room for sequel",
    "season",
    "sentai",
    "setting",
    "some wierd shit goin` on",
    "sudden change of pace",
    "target audience",
    "television programme",
    "themes",
    "tone changes",
    "translation convention",
    "tropes",
    "unresolved",
    "unresolved romance"
]

tagBlackListSource=[
    "manga",
    "novel",
    "remake",
    "visual novel"
]

tagBlackListArtStyle=[
    "experimental animation",
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
    "long episodes",
    "op and ed sung by characters",
    "op variety",
    "recap in opening",
    "subtle op ed sequence change"
]

#Feed this a list of str types
def processTags(addon,string):

    toRemove=[]
    removeOriginal=0
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
        else:
            for remove in tagBlackListSource:
                if remove == str(a).lower():
                    removeOriginal=1
                    break
        if addon.getSetting("hideUsefulMiscTags") == "true":
            for remove in tagBlackListUsefulHelpers:
                if remove == str(a).lower():
                    toRemove.append(a)
                    break

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
            elif "old animetags" in str(a).lower():
                toRemove.append(a)
            elif "censor" in str(a).lower():
                toRemove.append(a)
            elif str(a).lower().startswith("plot"):
                toRemove.append(a)
            elif str(a).lower().startswith("predominantly"):
                toRemove.append(a)
            elif str(a).lower().startswith("preview"):
                toRemove.append(a)
            elif str(a).lower().startswith("weekly"):
                toRemove.append(a)
    # on a separate loop in case 'original work' came before the source
    for a in string:
        if str(a).lower() == "original work":
            toRemove.append("original work")
            break

    for a in toRemove:
        string.remove(a)

    return string
