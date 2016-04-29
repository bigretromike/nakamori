# Comment any you don't believe should be in here or create an ongoing issue for discussion
tagBlacklist=[
    "cast missing",
    "cast",
    "content indicators",
    "delayed 16-9 broadcast",
    "description missing",
    "dynamic",
    "earth",
    "ed variety",
    "elements",
    "ensemble cast",
    "experimental animation",
    "fillers",
    "full hd version available",
    "incomplete story",
    "inconclusive",
    "inconclusive romantic plot",
    "jdrama adaptation",
    "long episodes",
    "manga",
    "meta tags",
    "multi-anime projects",
    "new",
    "noitamina",
    "novel",
    "off-model animation",
    "op and ed sung by characters",
    "op variety",
    "open-ended",
    "past",
    "photographic backgrounds",
    "place",
    "present",
    "product placement",
    "recap in opening",
    "recycled animation",
    "remake",
    "room for sequel",
    "season",
    "sentai",
    "setting",
    "slide show animation",
    "some wierd shit goin` on",
    "subtle op ed sequence change",
    "sudden change of pace",
    "target audience",
    "television programme",
    "themes",
    "thick line animation",
    "tone changes",
    "translation convention",
    "tropes",
    "unresolved",
    "unresolved romance",
    "vignette scenes",
    "visual novel",
    "watercolour style",
    "widescreen transition"
]

#Feed this a list of str types
def processTags(string):
    for remove in tagBlacklist:
        if remove in string:
            string.remove(remove)
    toRemove=[]
    for a in string:
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


    for a in toRemove:
        string.remove(a)

    return string
