"""The language Blocky writes in: the current one, the Dutch and Hungarian texts, and Windows' display language.

Texts are written in English where they are used, as `_("Add a site")`; the English text is the key into the tables
below. Named placeholders (`_("{domain} is already in the list", domain=domain)`) let a language order the words its
own way. A context tells apart the same English used in two places that other languages word differently: the
table key is then "context|text". tests/test_translations.py checks that every text in the code has an entry in both
tables.
"""

LANGUAGES = ("en", "nl", "hu")
NAMES = {"en": "English", "nl": "Nederlands", "hu": "Magyar"}  # each language named in itself
# The primary language of a Windows LANGID (its low 10 bits) for the languages Blocky has.
WINDOWS_PRIMARY = {0x09: "en", 0x13: "nl", 0x0E: "hu"}
OTHER = "other"  # Windows' display language when it is one Blocky does not have

_current = "en"


def apply(code: str) -> None:
    """Make this language current for every text made from now on; English for an unknown code."""
    global _current
    _current = code if code in LANGUAGES else "en"


def current() -> str:
    return _current


def _fill(text: str, code: str, context: str, values: dict[str, object]) -> str:
    chosen = TABLES.get(code, {}).get(f"{context}|{text}" if context else text, text)
    return chosen.format(**values) if values else chosen


def translate(text: str, code: str, /, context: str = "", **values: object) -> str:
    """The text in the given language, with its placeholders filled; English when there is no translation."""
    return _fill(text, code, context, values)


def _(text: str, /, context: str = "", **values: object) -> str:
    """The text in the current language."""
    return _fill(text, _current, context, values)


class Shown(str):
    """A text in the current language that also keeps its English form, for errors.log."""

    english: str


def shown(text: str, /, **values: object) -> Shown:
    """Like _(), but the result also carries the English, built from the English of any value that has one."""
    result = Shown(_fill(text, _current, "", values))
    result.english = _fill(text, "en", "", {name: english(value) for name, value in values.items()})
    return result


def english(value: object) -> object:
    """The English form of a text made by shown(); any other value as it is."""
    return getattr(value, "english", value)


def marked(text: str, context: str = "") -> str:
    """Marks an English text that is translated later, where it is shown, so the table test still finds it."""
    return text


def from_langid(langid: int) -> str:
    return WINDOWS_PRIMARY.get(langid & 0x3FF, OTHER)


def windows_language() -> str:
    """Windows' display language when Blocky has it, whatever the region, or OTHER; English when unreadable."""
    try:
        import ctypes

        langid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
    except (AttributeError, OSError):
        return "en"
    return from_langid(int(langid))


# Keyed by the English text, or by "context|text"; grouped by where the text appears.
NL: dict[str, str] = {
    # Window: header and tabs
    "Fewer distractions, on your schedule": "Minder afleiding, volgens jouw schema",
    "Status": "Status",
    "Block list": "Blokkeerlijst",
    "Schedule": "Schema",
    "Shortlist": "Suggesties",
    "History": "Geschiedenis",
    "Settings": "Instellingen",
    # Status tab
    "RIGHT NOW": "NU",
    "No blocking right now": "Nu wordt er niets geblokkeerd",
    "Blocking active — {remaining} remaining": "Blokkeren actief — nog {remaining}",
    "Window active, nothing blocked — {remaining} remaining": "Blokkeertijd actief, niets geblokkeerd — nog {remaining}",
    "No sites are blocked.": "Er zijn geen sites geblokkeerd.",
    "Override a block": "Een blokkade opheffen",
    "Unblocks one site until this window ends. Your reason is kept in History.": (
        "Geeft één site vrij tot de blokkeertijd eindigt. Je reden komt in “Geschiedenis”."
    ),
    "No domain blocked": "Geen domein geblokkeerd",
    "Why do you need it?": "Waarom heb je het nodig?",
    "Override": "Opheffen",
    "Type a reason to override": "Typ een reden om op te heffen",
    "Unblocked right now": "Nu vrijgegeven",
    "Nothing is unblocked.": "Er is niets vrijgegeven.",
    "{domain} unblocked until {time} ({remaining} left)": "{domain} vrijgegeven tot {time} (nog {remaining})",
    "Undo": "Ongedaan maken",
    # Block list tab
    "Add a site": "Een site toevoegen",
    "Its www. version is blocked too. You can paste a full web address.": (
        "De www.-versie wordt ook geblokkeerd. Je kunt een volledig webadres plakken."
    ),
    "Add": "Toevoegen",
    "Blocked sites ({count})": "Geblokkeerde sites ({count})",
    "No sites yet. Add one above.": "Nog geen sites. Voeg er hierboven een toe.",
    "Save": "Opslaan",
    "Remove": "Verwijderen",
    "Not a full domain yet, e.g. reddit.com": "Nog geen volledig domein, bijv. reddit.com",
    "{domain} is already in the list": "{domain} staat al in de lijst",
    "Adds {domain}": "Voegt {domain} toe",
    "Adds {domain} and {other}": "Voegt {domain} en {other} toe",
    "'{entry}' is not a valid domain": "'{entry}' is geen geldig domein",
    # Schedule tab
    "Days": "Dagen",
    "Blocking only happens on the days you tick.": "Er wordt alleen geblokkeerd op de dagen die je aanvinkt.",
    "Time": "Tijd",
    "Sites are blocked between these times. Type, or use the arrow keys or mouse wheel.": (
        "Sites zijn tussen deze tijden geblokkeerd. Typ, of gebruik pijltjes of muiswiel."
    ),
    "From": "Van",
    "to": "tot",
    "Save schedule": "Schema opslaan",
    "Pick at least one day": "Kies minstens één dag",
    "Use a time like 09:00": "Gebruik een tijd als 09:00",
    "The start time must be before the end time": "De begintijd moet voor de eindtijd liggen",
    "Weekdays must be between 0 (Monday) and 6 (Sunday)": "Weekdagen moeten tussen 0 (maandag) en 6 (zondag) liggen",
    "no days": "geen dagen",
    # Shortlist tab
    "Add a suggestion": "Een suggestie toevoegen",
    "Something better to do, shown on the block page.": (
        "Iets beters om te doen, dit wordt getoond op de blokkeerpagina."
    ),
    "e.g. 10-minute walk": "bijv. 10 minuten wandelen",
    "Suggestions ({count})": "Suggesties ({count})",
    "No suggestions yet. Add one above.": "Nog geen suggesties. Voeg er hierboven een toe.",
    "Type a suggestion": "Typ een suggestie",
    "Keep it to {count} characters": "Maximaal {count} tekens",
    "“{text}” is already in the list": "‘{text}’ staat al in de lijst",
    # History tab
    "Every change you make in Blocky, newest first.": "Elke wijziging die je in Blocky maakt, nieuwste eerst.",
    "When": "Wanneer",
    "Event": "Gebeurtenis",
    "Item": "Item",
    "Details": "Details",
    "No changes yet.": "Nog geen wijzigingen.",
    "event|Site added": "Site toegevoegd",
    "event|Site edited": "Site gewijzigd",
    "event|Site removed": "Site verwijderd",
    "event|Suggestion added": "Suggestie toegevoegd",
    "event|Suggestion edited": "Suggestie gewijzigd",
    "event|Suggestion removed": "Suggestie verwijderd",
    "event|Schedule changed": "Schema gewijzigd",
    "event|Override": "Blokkade opgeheven",
    "event|Override undone": "Opheffing ongedaan gemaakt",
    # Settings tab
    "Appearance": "Weergave",
    "Changes show at once and are saved.": "Wijzigingen zijn meteen zichtbaar en worden opgeslagen.",
    "Theme": "Thema",
    "Forest": "Bos",
    "Navy": "Marine",
    "Sand": "Zand",
    "Aqua": "Aqua",
    "Blossom": "Bloesem",
    "Follow Windows": "Volg Windows",
    "Dark theme when Windows is dark": "Donker thema als Windows donker is",
    "Light theme when Windows is light": "Licht thema als Windows licht is",
    "Font": "Lettertype",
    "Text size": "Tekstgrootte",
    "Small": "Klein",
    "Normal": "Normaal",
    "Large": "Groot",
    "Extra large": "Extra groot",
    "Language and time": "Taal en tijd",
    "Language": "Taal",
    "Windows uses English.": "Windows gebruikt Engels.",
    "Windows uses Dutch.": "Windows gebruikt Nederlands.",
    "Windows uses Hungarian.": "Windows gebruikt Hongaars.",
    "Windows uses another language, so Follow Windows gives English.": (
        "Windows gebruikt een andere taal, dus Volg Windows geeft Engels."
    ),
    "Time format": "Tijdnotatie",
    "24-hour": "24-uurs",
    "12-hour": "12-uurs",
    "Windows uses 24-hour time.": "Windows gebruikt de 24-uursnotatie.",
    "Windows uses 12-hour time.": "Windows gebruikt de 12-uursnotatie.",
    "First day of the week": "Eerste dag van de week",
    "Windows starts the week on {day}.": "Windows begint de week op {day}.",
    "Reset to default": "Standaard herstellen",
    "Settings reset.": "Instellingen hersteld.",
    # Overrides
    "A reason is required to override a block": "Geef een reden om een blokkade op te heffen",
    "{domain} is not blocked right now": "{domain} is nu niet geblokkeerd",
    "{domain} is not unblocked right now": "{domain} is nu niet vrijgegeven",
    # Block page
    "{domain} is blocked until {time}": "{domain} is geblokkeerd tot {time}",
    "Try one of these instead:": "Probeer in plaats daarvan een van deze:",
    "No suggestions yet. Add some in Blocky.": "Nog geen suggesties. Voeg ze toe in Blocky.",
    # Starting and warnings
    "Blocky needs administrator rights to edit the hosts file. Start it again and choose Yes.": (
        "Blocky heeft beheerdersrechten nodig om het hosts-bestand aan te passen. Start Blocky opnieuw en kies Ja."
    ),
    "The block page could not start, so blocked sites show the browser's error page: {error}": (
        "De blokkeerpagina kon niet starten, dus geblokkeerde sites tonen de foutpagina van de browser: {error}"
    ),
    "Skipped invalid domains in the config: {domains}.": "Ongeldige domeinen in de configuratie overgeslagen: {domains}.",
    "{name} could not be read ({problem}), so Blocky started with an empty list. The old file was kept as {copy}.": (
        "{name} kon niet worden gelezen ({problem}), dus Blocky is gestart met een lege lijst. "
        "Het oude bestand is bewaard als {copy}."
    ),
    "it is not valid YAML": "het is geen geldige YAML",
    "it is empty or not a Blocky config": "het is leeg of geen Blocky-configuratie",
    "'schedule' is not a section": "'schedule' is geen sectie",
    "the schedule is not valid": "het schema is ongeldig",
    "'{key}' is not a list": "'{key}' is geen lijst",
    "an override entry has no domain": "een opheffing heeft geen domein",
    "an override entry has no valid end time": "een opheffing heeft geen geldige eindtijd",
    "a history entry has no type": "een regel in de geschiedenis heeft geen type",
    "a history entry has no valid time": "een regel in de geschiedenis heeft geen geldige tijd",
    "Nested Blocky section in the hosts file": "Geneste Blocky-sectie in het hosts-bestand",
    "Blocky section end without a start in the hosts file": "Einde van een Blocky-sectie zonder begin in het hosts-bestand",
    "Unterminated Blocky section in the hosts file": "Blocky-sectie zonder einde in het hosts-bestand",
}
HU: dict[str, str] = {
    # Window: header and tabs
    "Fewer distractions, on your schedule": "Kevesebb zavaró tényező, a saját időbeosztásod szerint",
    "Status": "Állapot",
    "Block list": "Tiltólista",
    "Schedule": "Ütemezés",
    "Shortlist": "Javaslatok",
    "History": "Előzmények",
    "Settings": "Beállítások",
    # Status tab
    "RIGHT NOW": "MOST",
    "No blocking right now": "Most nincs tiltás",
    "Blocking active — {remaining} remaining": "Tiltás aktív — még {remaining}",
    "Window active, nothing blocked — {remaining} remaining": "Tiltási időszak, de semmi sincs tiltva — még {remaining}",
    "No sites are blocked.": "Nincs tiltott webhely.",
    "Override a block": "Tiltás feloldása",
    "Unblocks one site until this window ends. Your reason is kept in History.": (
        "Egy webhelyet felold a tiltási időszak végéig. Az okot az Előzmények megőrzi."
    ),
    "No domain blocked": "Nincs tiltott domain",
    "Why do you need it?": "Miért van rá szükséged?",
    "Override": "Feloldás",
    "Type a reason to override": "A feloldáshoz írd be az okát",
    "Unblocked right now": "Most feloldva",
    "Nothing is unblocked.": "Semmi sincs feloldva.",
    "{domain} unblocked until {time} ({remaining} left)": "{domain} feloldva eddig: {time} (még {remaining})",
    "Undo": "Visszavonás",
    # Block list tab
    "Add a site": "Webhely hozzáadása",
    "Its www. version is blocked too. You can paste a full web address.": (
        "A www. változata is tiltva lesz. Teljes webcímet is beilleszthetsz."
    ),
    "Add": "Hozzáadás",
    "Blocked sites ({count})": "Tiltott webhelyek ({count})",
    "No sites yet. Add one above.": "Még nincs webhely. Adj hozzá egyet fent.",
    "Save": "Mentés",
    "Remove": "Eltávolítás",
    "Not a full domain yet, e.g. reddit.com": "Még nem teljes domain, pl. reddit.com",
    "{domain} is already in the list": "{domain} már szerepel a listán",
    "Adds {domain}": "Hozzáadja: {domain}",
    "Adds {domain} and {other}": "Hozzáadja: {domain} és {other}",
    "'{entry}' is not a valid domain": "'{entry}' nem érvényes domain",
    # Schedule tab
    "Days": "Napok",
    "Blocking only happens on the days you tick.": "Csak a bejelölt napokon van tiltás.",
    "Time": "Idő",
    "Sites are blocked between these times. Type, or use the arrow keys or mouse wheel.": (
        "Tiltás ezen időpontok között. Gépelj, vagy használd a nyilakat vagy a görgőt."
    ),
    "From": "Ettől",
    "to": "eddig",
    "Save schedule": "Ütemezés mentése",
    "Pick at least one day": "Válassz legalább egy napot",
    "Use a time like 09:00": "Adj meg egy időt, pl. 09:00",
    "The start time must be before the end time": "A kezdésnek a befejezés előtt kell lennie",
    "Weekdays must be between 0 (Monday) and 6 (Sunday)": "A napoknak 0 (hétfő) és 6 (vasárnap) között kell lenniük",
    "no days": "nincs nap",
    # Shortlist tab
    "Add a suggestion": "Javaslat hozzáadása",
    "Something better to do, shown on the block page.": "Valami jobb elfoglaltság, a tiltóoldalon jelenik meg.",
    "e.g. 10-minute walk": "pl. 10 perces séta",
    "Suggestions ({count})": "Javaslatok ({count})",
    "No suggestions yet. Add one above.": "Még nincs javaslat. Adj hozzá egyet fent.",
    "Type a suggestion": "Írj be egy javaslatot",
    "Keep it to {count} characters": "Legfeljebb {count} karakter",
    "“{text}” is already in the list": "„{text}” már szerepel a listán",
    # History tab
    "Every change you make in Blocky, newest first.": "Minden változtatásod a Blockyban, a legújabb elöl.",
    "When": "Mikor",
    "Event": "Esemény",
    "Item": "Elem",
    "Details": "Részletek",
    "No changes yet.": "Még nincs változtatás.",
    "event|Site added": "Webhely hozzáadva",
    "event|Site edited": "Webhely módosítva",
    "event|Site removed": "Webhely eltávolítva",
    "event|Suggestion added": "Javaslat hozzáadva",
    "event|Suggestion edited": "Javaslat módosítva",
    "event|Suggestion removed": "Javaslat eltávolítva",
    "event|Schedule changed": "Ütemezés módosítva",
    "event|Override": "Tiltás feloldva",
    "event|Override undone": "Feloldás visszavonva",
    # Settings tab
    "Appearance": "Megjelenés",
    "Changes show at once and are saved.": "A változások azonnal látszanak, és mentésre kerülnek.",
    "Theme": "Téma",
    "Forest": "Erdő",
    "Navy": "Sötétkék",
    "Sand": "Homok",
    "Aqua": "Akva",
    "Blossom": "Virág",
    "Follow Windows": "Windows szerint",
    "Dark theme when Windows is dark": "Sötét téma, ha a Windows sötét",
    "Light theme when Windows is light": "Világos téma, ha a Windows világos",
    "Font": "Betűtípus",
    "Text size": "Szövegméret",
    "Small": "Kicsi",
    "Normal": "Normál",
    "Large": "Nagy",
    "Extra large": "Extra nagy",
    "Language and time": "Nyelv és idő",
    "Language": "Nyelv",
    "Windows uses English.": "A Windows nyelve angol.",
    "Windows uses Dutch.": "A Windows nyelve holland.",
    "Windows uses Hungarian.": "A Windows nyelve magyar.",
    "Windows uses another language, so Follow Windows gives English.": (
        "A Windows más nyelvet használ, ezért a Windows szerint beállítás angolt ad."
    ),
    "Time format": "Időformátum",
    "24-hour": "24 órás",
    "12-hour": "12 órás",
    "Windows uses 24-hour time.": "A Windows 24 órás időt használ.",
    "Windows uses 12-hour time.": "A Windows 12 órás időt használ.",
    "First day of the week": "A hét első napja",
    "Windows starts the week on {day}.": "A Windowsban a hét első napja: {day}.",
    "Reset to default": "Alapértékek visszaállítása",
    "Settings reset.": "Beállítások visszaállítva.",
    # Overrides
    "A reason is required to override a block": "A tiltás feloldásához meg kell adnod az okát",
    "{domain} is not blocked right now": "{domain} most nincs tiltva",
    "{domain} is not unblocked right now": "{domain} most nincs feloldva",
    # Block page
    "{domain} is blocked until {time}": "{domain} tiltva eddig: {time}",
    "Try one of these instead:": "Próbáld inkább ezek egyikét:",
    "No suggestions yet. Add some in Blocky.": "Még nincs javaslat. Adj hozzá néhányat a Blockyban.",
    # Starting and warnings
    "Blocky needs administrator rights to edit the hosts file. Start it again and choose Yes.": (
        "A Blockynak rendszergazdai jogok kellenek a hosts fájl szerkesztéséhez. Indítsd újra, és válaszd az Igen gombot."
    ),
    "The block page could not start, so blocked sites show the browser's error page: {error}": (
        "A tiltóoldal nem tudott elindulni, ezért a tiltott webhelyeken a böngésző hibaoldala jelenik meg: {error}"
    ),
    "Skipped invalid domains in the config: {domains}.": "A beállítási fájl érvénytelen domainjei kimaradtak: {domains}.",
    "{name} could not be read ({problem}), so Blocky started with an empty list. The old file was kept as {copy}.": (
        "A(z) {name} nem olvasható ({problem}), ezért a Blocky üres listával indult. "
        "A régi fájl {copy} néven megmaradt."
    ),
    "it is not valid YAML": "nem érvényes YAML",
    "it is empty or not a Blocky config": "üres, vagy nem Blocky-beállítási fájl",
    "'schedule' is not a section": "a 'schedule' nem szakasz",
    "the schedule is not valid": "az ütemezés érvénytelen",
    "'{key}' is not a list": "a '{key}' nem lista",
    "an override entry has no domain": "egy feloldási bejegyzésnek nincs domainje",
    "an override entry has no valid end time": "egy feloldási bejegyzésnek nincs érvényes befejezési ideje",
    "a history entry has no type": "egy előzménybejegyzésnek nincs típusa",
    "a history entry has no valid time": "egy előzménybejegyzésnek nincs érvényes ideje",
    "Nested Blocky section in the hosts file": "Egymásba ágyazott Blocky-szakasz a hosts fájlban",
    "Blocky section end without a start in the hosts file": "Blocky-szakasz vége kezdet nélkül a hosts fájlban",
    "Unterminated Blocky section in the hosts file": "Lezáratlan Blocky-szakasz a hosts fájlban",
}
TABLES = {"nl": NL, "hu": HU}
