import attr

PageText = str
Url = str
Date = int
Year = int
Week = int
SafeMode = bool
TeamId = int
GameKey = str

@attr.s
class Period(object):
    year: int = attr.ib()
    week: int = attr.ib()
