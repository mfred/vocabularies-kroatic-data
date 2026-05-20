#!/usr/bin/env python3
"""Vocabulary expansion 2026-05: adds ~534 A1/A2 items across 9 existing
and 3 new lessons, then refreshes manifest hashes/counts. Idempotent: re-running
with the same data file leaves identical output (it skips items whose hr.text
already exists in the target lesson)."""

import hashlib
import json
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
V1_DIR = REPO_ROOT / "v1"
LESSONS_DIR = V1_DIR / "lessons"
MANIFEST_PATH = V1_DIR / "manifest.json"

TODAY = "2026-05-20"
GENERATED_AT = "2026-05-20T12:00:00Z"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def W(de, hr, *, ipa=None, pos="noun", tags=None, alt_hr=None, diff=2):
    return _item("word", "words", de, hr, ipa=ipa, pos=pos, tags=tags or [],
                 alt_hr=alt_hr, diff=diff)


def P(de, hr, *, ipa=None, tags=None, diff=2):
    return _item("phrase", "phrases", de, hr, ipa=ipa, pos="phrase",
                 tags=tags or [], diff=diff)


def S(de, hr, *, ipa=None, tags=None, diff=2):
    return _item("sentence", "sentences", de, hr, ipa=ipa, pos="phrase",
                 tags=tags or [], diff=diff)


def _item(typ, stage, de, hr, *, ipa, pos, tags, diff, alt_hr=None):
    out = {
        "type": typ,
        "stage": stage,
        "difficulty": diff,
        "de": {"text": de, "pos": pos},
        "hr": {"text": hr, "pos": pos},
    }
    if ipa:
        out["hr"]["ipa"] = ipa
    if alt_hr:
        out["alternatives"] = {"hr": alt_hr}
    if tags:
        out["tags"] = tags
    out["license"] = None
    return out


# ---------------------------------------------------------------------------
# Items per lesson
# ---------------------------------------------------------------------------

GREETINGS_NEW = [
    P("Gruß!/Hallo!", "Pozdrav!", tags=["greeting", "neutral"], diff=1),
    P("Herzlich willkommen! (Pl.)", "Dobro došli!", tags=["welcome", "formal"], diff=2),
    S("Wie geht es Ihnen?", "Kako ste?", tags=["smalltalk", "formal", "question"], diff=1),
    P("Was gibt's?", "Što ima?", tags=["smalltalk", "informal"], diff=2),
    S("Alles in Ordnung, danke.", "Sve u redu, hvala.", tags=["smalltalk", "response"], diff=2),
    S("Mir geht es schlecht.", "Loše mi je.", tags=["mood", "negative"], diff=2),
    P("Nicht schlecht.", "Nije loše.", tags=["mood"], diff=2),
    P("So lala.", "Tako-tako.", tags=["mood"], diff=2),
    S("Freut mich, dich kennenzulernen.", "Drago mi je upoznati te.", tags=["greeting", "polite"], diff=2),
    P("Bis später.", "Vidimo se kasnije.", tags=["farewell"], diff=2),
    P("Schönes Wochenende!", "Ugodan vikend!", tags=["wish", "farewell"], diff=2),
    W("Hallo/Tschüss (Zagreb)", "Bog", ipa="boːk", pos="interjection", tags=["greeting", "regional"], diff=2),
    W("Hey!", "Ej", pos="interjection", tags=["greeting", "informal"], diff=1),
    P("Danke (Sie/Plural)", "Hvala vam", tags=["politeness", "formal"], diff=2),
    P("Bitte (Sie/Plural)", "Molim vas", tags=["politeness", "formal"], diff=1),
    W("Entschuldige (du)", "Oprosti", pos="interjection", tags=["politeness", "informal"], diff=2),
    P("Ich entschuldige mich", "Ispričavam se", tags=["politeness", "formal"], diff=3),
    P("Es tut mir leid", "Žao mi je", tags=["politeness", "feeling"], diff=2),
    P("Kein Problem", "Nema problema", tags=["response"], diff=2),
    P("Schon gut/passt", "U redu je", tags=["response", "affirmative"], diff=2),
    P("Hat mich gefreut", "Bilo mi je drago", tags=["farewell", "polite"], diff=3),
    P("Grüß alle!", "Pozdravi sve!", tags=["greeting", "wish"], diff=2),
    W("Viel Glück!", "Sretno", pos="interjection", tags=["wish"], diff=2),
    W("Bravo!", "Bravo", pos="interjection", tags=["positive"], diff=1),
    W("Prost! (zum Anstoßen)", "Živjeli", ipa="ʒîʋjeli", pos="interjection", tags=["wish", "social"], diff=2),
    W("Gesundheit! (beim Niesen)", "Nazdravlje", pos="interjection", tags=["wish"], diff=2),
    P("Guten Appetit!", "Dobar tek!", tags=["wish", "polite"], diff=2),
    P("Willkommen (Sg. m.)", "Dobro došao", tags=["welcome", "formal"], diff=3),
    P("Willkommen (Sg. f.)", "Dobro došla", tags=["welcome", "formal"], diff=3),
    W("wütend (m.)", "ljut", pos="adjective", tags=["mood", "negative"], diff=2),
    W("wütend (f.)", "ljuta", pos="adjective", tags=["mood", "negative"], diff=2),
    W("nervös (m.)", "nervozan", pos="adjective", tags=["mood"], diff=3),
    W("ruhig", "miran", pos="adjective", tags=["mood"], diff=2),
    W("enttäuscht (m.)", "razočaran", pos="adjective", tags=["mood", "negative"], diff=3),
    W("überrascht (m.)", "iznenađen", pos="adjective", tags=["mood"], diff=3),
    S("Wie geht es der Familie?", "Kako je obitelj?", tags=["smalltalk", "question"], diff=3),
    S("Geht es dir gut?", "Jesi li dobro?", tags=["smalltalk", "question", "informal"], diff=2),
    S("Mir geht's nicht gut.", "Nisam dobro.", tags=["mood", "negative"], diff=2),
]

INTRODUCTION_NEW = [
    S("Wie heißen Sie?", "Kako se zovete?", tags=["intro", "question", "formal"], diff=1),
    P("Mein Name ist ...", "Moje ime je ...", tags=["intro"], diff=1),
    P("Mein Nachname ist ...", "Moje prezime je ...", tags=["intro"], diff=2),
    P("Ich bin ...", "Ja sam ...", tags=["intro"], diff=1),
    S("Wir sind aus Österreich.", "Mi smo iz Austrije.", tags=["intro", "origin"], diff=2),
    S("Wo wohnen Sie?", "Gdje živite?", tags=["intro", "question", "formal"], diff=1),
    S("Ich wohne in Graz.", "Živim u Grazu.", tags=["intro", "origin"], diff=2),
    P("Ich bin geboren in ... (m.)", "Rođen sam u ...", tags=["intro", "origin"], diff=2),
    P("Ich bin geboren in ... (f.)", "Rođena sam u ...", tags=["intro", "origin"], diff=2),
    W("Alter", "dob", pos="noun", tags=["personal"], diff=2),
    W("Nationalität", "nacionalnost", pos="noun", tags=["nationality", "personal"], diff=2),
    W("Herkunft", "podrijetlo", pos="noun", tags=["origin", "personal"], diff=3),
    P("Muttersprache", "materinski jezik", tags=["language"], diff=2),
    P("Fremdsprache", "strani jezik", tags=["language"], diff=2),
    S("Ich spreche ein bisschen Kroatisch.", "Govorim malo hrvatski.", tags=["language", "communication"], diff=2),
    S("Ich spreche fließend Englisch.", "Govorim tečno engleski.", tags=["language", "communication"], diff=3),
    S("Können Sie bitte langsamer sprechen?", "Govorite li polako, molim?", tags=["communication", "polite", "question"], diff=2),
    S("Können Sie wiederholen?", "Možete li ponoviti?", tags=["communication", "question"], diff=2),
    S("Was bedeutet das?", "Što znači to?", tags=["communication", "question"], diff=2),
    S("Wie sagt man ... auf Kroatisch?", "Kako se kaže ... na hrvatskom?", tags=["communication", "language", "question"], diff=2),
    S("Wie schreibt man das?", "Kako se piše?", tags=["communication", "question"], diff=2),
    P("Bitte schreiben Sie es auf", "Pišite, molim", tags=["communication", "polite"], diff=2),
    W("Beamter/Angestellter", "službenik", pos="noun", tags=["work"], diff=3),
    W("Beamtin/Angestellte", "službenica", pos="noun", tags=["work"], diff=3),
    W("Unternehmer", "poduzetnik", pos="noun", tags=["work"], diff=3),
    W("Unternehmerin", "poduzetnica", pos="noun", tags=["work"], diff=3),
    W("Anwalt", "odvjetnik", pos="noun", tags=["work"], diff=3),
    W("Anwältin", "odvjetnica", pos="noun", tags=["work"], diff=3),
    W("Journalist", "novinar", pos="noun", tags=["work"], diff=3),
    W("Journalistin", "novinarka", pos="noun", tags=["work"], diff=3),
    P("Krankenpfleger", "medicinski tehničar", tags=["work"], diff=3),
    W("Friseur", "frizer", pos="noun", tags=["work"], alt_hr=["frizerka"], diff=3),
    W("Elektriker", "električar", pos="noun", tags=["work"], diff=3),
    W("Landwirt", "poljoprivrednik", pos="noun", tags=["work"], diff=3),
    W("Rentnerin", "umirovljena", pos="noun", tags=["work", "status"], diff=3),
    W("Hausfrau", "domaćica", pos="noun", tags=["work"], diff=2),
    P("Straße und Hausnummer", "ulica i kućni broj", tags=["contact", "personal"], diff=2),
    P("Postleitzahl", "poštanski broj", tags=["contact", "personal"], diff=2),
    S("Ich habe zwei Kinder.", "Imam dvoje djece.", tags=["family", "intro"], diff=2),
    S("Ich bin nicht verheiratet (m.).", "Nisam oženjen.", tags=["status"], diff=2),
    S("Ich bin in einer Beziehung.", "U vezi sam.", tags=["status"], diff=3),
]

NUMBERS_TIME_NEW = [
    W("erster", "prvi", pos="adjective", tags=["number", "ordinal"], diff=2),
    W("zweiter", "drugi", pos="adjective", tags=["number", "ordinal"], diff=2),
    W("dritter", "treći", pos="adjective", tags=["number", "ordinal"], diff=2),
    W("vierter", "četvrti", pos="adjective", tags=["number", "ordinal"], diff=2),
    W("fünfter", "peti", pos="adjective", tags=["number", "ordinal"], diff=2),
    W("sechster", "šesti", pos="adjective", tags=["number", "ordinal"], diff=2),
    W("siebter", "sedmi", pos="adjective", tags=["number", "ordinal"], diff=2),
    W("achter", "osmi", pos="adjective", tags=["number", "ordinal"], diff=2),
    W("neunter", "deveti", pos="adjective", tags=["number", "ordinal"], diff=2),
    W("zehnter", "deseti", pos="adjective", tags=["number", "ordinal"], diff=2),
    W("elfter", "jedanaesti", pos="adjective", tags=["number", "ordinal"], diff=3),
    W("zwölfter", "dvanaesti", pos="adjective", tags=["number", "ordinal"], diff=3),
    W("halb", "pola", pos="adverb", tags=["time", "clock"], diff=1),
    W("Viertel", "četvrt", pos="noun", tags=["time", "clock"], diff=2),
    P("Viertel nach fünf", "pet i petnaest", tags=["time", "clock"], diff=3),
    P("halb sechs (5:30)", "pet i pol", tags=["time", "clock"], diff=2),
    P("Viertel vor sechs", "četvrt do šest", tags=["time", "clock"], diff=3),
    P("Punkt neun", "točno u devet", tags=["time", "clock"], diff=2),
    P("gegen zehn", "oko deset", tags=["time"], diff=2),
    P("etwa zehn Minuten", "desetak minuta", tags=["time"], diff=3),
    P("jeden Tag", "svaki dan", tags=["time", "frequency"], diff=1),
    P("jede Woche", "svaki tjedan", tags=["time", "frequency"], diff=2),
    P("jedes Jahr", "svake godine", tags=["time", "frequency"], diff=2),
    W("manchmal", "ponekad", pos="adverb", tags=["time", "frequency"], diff=2),
    W("oft", "često", pos="adverb", tags=["time", "frequency"], diff=1),
    W("selten", "rijetko", pos="adverb", tags=["time", "frequency"], diff=2),
    W("sofort", "odmah", pos="adverb", tags=["time"], diff=2),
    W("bald", "uskoro", pos="adverb", tags=["time"], diff=2),
    W("schon", "već", pos="adverb", tags=["time"], diff=2),
    W("noch", "još", pos="adverb", tags=["time"], diff=2),
    P("nie wieder", "nikada više", tags=["time", "frequency"], diff=3),
    W("Hälfte", "polovica", pos="noun", tags=["quantity"], diff=3),
    W("Drittel", "trećina", pos="noun", tags=["quantity"], diff=4),
    P("ein paar Stunden", "par sati", tags=["time", "quantity"], diff=2),
    W("fünfundzwanzig (25)", "dvadeset i pet", pos="adjective", tags=["number"], diff=1),
    W("einunddreißig (31)", "trideset i jedan", pos="adjective", tags=["number"], diff=2),
    W("etwa hundert", "stotinjak", pos="adjective", tags=["number", "quantity"], diff=4),
    P("null Prozent", "nula posto", tags=["number", "quantity"], diff=3),
    P("fünfzig Prozent", "pedeset posto", tags=["number", "quantity"], diff=2),
    S("Welcher Wochentag ist?", "Koji je dan u tjednu?", tags=["time", "weekday", "question"], diff=2),
    S("Ich bin am 3. Mai geboren.", "Rođen sam treći svibnja.", tags=["time", "date", "personal"], diff=3),
]

FAMILY_NEW = [
    W("Cousine (Mutterseite)", "sestrična", pos="noun", tags=["extended", "family"], diff=3),
    W("Cousin (Bruder-Sohn)", "bratić", pos="noun", tags=["extended", "family"], diff=3),
    W("Stiefsohn", "pastorak", pos="noun", tags=["family", "in-laws"], diff=4),
    W("Stieftochter", "pastorka", pos="noun", tags=["family", "in-laws"], diff=4),
    W("Stiefvater", "očuh", pos="noun", tags=["family", "in-laws"], diff=3),
    W("Stiefmutter", "maćeha", pos="noun", tags=["family", "in-laws"], diff=3),
    W("Halbbruder", "polubrat", pos="noun", tags=["family", "siblings"], diff=3),
    W("Halbschwester", "polusestra", pos="noun", tags=["family", "siblings"], diff=3),
    W("Einzelkind (m.)", "jedinac", pos="noun", tags=["family", "child"], diff=3),
    W("Einzelkind (f.)", "jedinica", pos="noun", tags=["family", "child"], diff=3),
    W("Zwillinge", "blizanci", pos="noun", tags=["family", "siblings"], diff=3),
    W("Dreijähriger", "trogodišnjak", pos="noun", tags=["age", "child"], diff=4),
    W("Junge", "dječak", pos="noun", tags=["age", "child"], diff=1),
    W("Mädchen", "djevojčica", pos="noun", tags=["age", "child"], diff=1),
    W("junger Mann/Freund", "momak", pos="noun", tags=["age", "relationship"], diff=2),
    W("junge Frau/Freundin", "djevojka", pos="noun", tags=["age", "relationship"], diff=2),
    W("Paar", "par", pos="noun", tags=["relationship"], diff=2),
    W("Verlobter", "zaručnik", pos="noun", tags=["relationship", "status"], diff=3),
    W("Verlobte", "zaručnica", pos="noun", tags=["relationship", "status"], diff=3),
    W("Verlobung", "zaruke", pos="noun", tags=["event", "status"], diff=3),
    W("Schwangerschaft", "trudnoća", pos="noun", tags=["event"], diff=4),
    W("schwanger", "trudna", pos="adjective", tags=["status"], diff=3),
    W("Neugeborenes", "novorođenče", pos="noun", tags=["age", "child"], diff=4),
    P("glückliche Familie", "sretna obitelj", tags=["family", "positive"], diff=2),
    P("strenge Mutter", "stroga majka", tags=["family", "parents"], diff=3),
    P("guter Vater", "dobar otac", tags=["family", "parents"], diff=2),
    P("gute Freundin", "dobra prijateljica", tags=["friend"], diff=2),
    P("bester Freund", "najbolji prijatelj", tags=["friend", "superlative"], diff=2),
    P("gemeinsame Erinnerungen", "zajedničke uspomene", tags=["family", "social"], diff=4),
    S("Wie heißt deine Mutter?", "Kako se zove tvoja majka?", tags=["family", "question"], diff=2),
    S("Hast du Kinder?", "Imaš li djecu?", tags=["family", "question", "informal"], diff=2),
    S("Wie viele Kinder haben Sie?", "Koliko djece imate?", tags=["family", "question", "formal"], diff=2),
    S("Mein Opa ist 80 Jahre alt.", "Moj djed ima 80 godina.", tags=["family", "grandparents", "age"], diff=2),
    S("Ich verstehe mich mit meinem Bruder.", "Slažem se s bratom.", tags=["family", "siblings"], diff=3),
    S("Ich verbringe gern Zeit mit der Familie.", "Volim provoditi vrijeme s obitelji.", tags=["family"], diff=3),
    S("Unsere Verwandten sind in Split.", "Naši su rođaci u Splitu.", tags=["family", "extended", "location"], diff=3),
]

SHOPPING_NEW = [
    W("Apotheke", "ljekarna", pos="noun", tags=["place", "shop"], diff=2),
    W("Drogerie", "drogerija", pos="noun", tags=["place", "shop"], diff=2),
    W("Kiosk", "kiosk", pos="noun", tags=["place", "shop"], diff=2),
    W("Buchhandlung", "knjižara", pos="noun", tags=["place", "shop"], diff=2),
    W("Blumenladen", "cvjećarnica", pos="noun", tags=["place", "shop"], diff=3),
    P("Kaufhaus", "robna kuća", tags=["place", "shop"], diff=2),
    P("Einkaufszentrum", "trgovački centar", tags=["place", "shop"], diff=2),
    W("Schaufenster", "izlog", pos="noun", tags=["shop"], diff=3),
    W("Regal", "polica", pos="noun", tags=["shop", "object"], diff=3),
    W("Einkaufskorb", "košarica", pos="noun", tags=["shop", "object"], diff=2),
    W("Einkaufswagen", "kolica", pos="noun", tags=["shop", "object"], diff=2),
    W("Größe", "veličina", pos="noun", tags=["clothing", "size"], diff=2),
    P("Schuhgröße", "broj cipela", tags=["clothing", "size"], diff=2),
    W("zu klein (m.)", "premali", pos="adjective", tags=["size"], diff=2),
    W("zu groß (m.)", "prevelik", pos="adjective", tags=["size"], diff=2),
    W("passt", "pristaje", pos="verb", tags=["clothing", "verb"], diff=2),
    W("anprobieren", "isprobati", pos="verb", tags=["clothing", "verb"], diff=2),
    S("Kann ich das anprobieren?", "Mogu li ovo isprobati?", tags=["clothing", "question", "request"], diff=2),
    W("Umkleidekabine", "garderoba", pos="noun", tags=["shop"], diff=3),
    W("Reklamation", "reklamacija", pos="noun", tags=["service"], diff=3),
    W("Garantie", "jamstvo", pos="noun", tags=["service"], diff=3),
    W("Umtausch", "zamjena", pos="noun", tags=["service"], diff=3),
    P("Rückerstattung", "povrat novca", tags=["service", "payment"], diff=3),
    P("Kleingeld", "sitan novac", tags=["money", "payment"], diff=2),
    W("Geldschein", "novčanica", pos="noun", tags=["money", "payment"], diff=3),
    W("Münze", "kovanica", pos="noun", tags=["money", "payment"], diff=3),
    W("Geldautomat", "bankomat", pos="noun", tags=["money", "service"], diff=2),
    W("geöffnet", "otvoreno", pos="adjective", tags=["shop", "status"], diff=1),
    W("geschlossen", "zatvoreno", pos="adjective", tags=["shop", "status"], diff=1),
    P("Öffnungszeiten", "radno vrijeme", tags=["shop", "time"], diff=2),
    W("Ausverkauf", "sniženje", pos="noun", tags=["price", "bargain"], diff=2),
    P("im Ausverkauf", "na rasprodaji", tags=["price", "bargain"], diff=3),
    W("billiger", "jeftinije", pos="adverb", tags=["price"], diff=2),
    W("teurer", "skuplje", pos="adverb", tags=["price"], diff=2),
    P("bester Preis", "najbolja cijena", tags=["price"], diff=2),
    P("inkl. MwSt.", "s PDV-om", ipa="pe-de-ʋe-om", tags=["price", "payment"], diff=4),
    S("Kann ich bar bezahlen?", "Mogu li platiti gotovinom?", tags=["payment", "question"], diff=2),
    S("Ich brauche eine Tüte, bitte.", "Trebam vrećicu, molim.", tags=["shop", "request", "polite"], diff=2),
    S("Ich suche ein Geschenk.", "Tražim poklon.", tags=["shop", "request"], diff=2),
    S("Ich schaue nur, danke.", "Samo gledam, hvala.", tags=["shop", "polite"], diff=2),
]

RESTAURANT_NEW = [
    S("Haben Sie einen freien Tisch?", "Imate li slobodan stol?", tags=["reservation", "question"], diff=2),
    S("Ich habe eine Reservierung.", "Imam rezervaciju.", tags=["reservation"], diff=2),
    S("Wir möchten einen Tisch reservieren.", "Htjeli bismo rezervirati stol.", tags=["reservation", "request"], diff=3),
    P("für zwei Personen", "za dvije osobe", tags=["reservation"], diff=2),
    P("um sieben Uhr", "u sedam sati", tags=["reservation", "time"], diff=2),
    P("auf der Terrasse", "na terasi", tags=["place"], diff=2),
    W("drinnen", "unutra", pos="adverb", tags=["place"], diff=2),
    W("draußen", "vani", pos="adverb", tags=["place"], diff=2),
    S("Können wir draußen sitzen?", "Možemo li sjesti vani?", tags=["request", "question"], diff=2),
    S("Wie heißt dieses Gericht?", "Kako se zove ovo jelo?", tags=["menu", "question"], diff=2),
    S("Was ist da drin?", "Što je u tome?", tags=["menu", "question", "diet"], diff=2),
    P("Ich habe eine Allergie gegen ...", "Imam alergiju na ...", tags=["diet", "allergy"], diff=3),
    S("Enthält es Milch?", "Sadrži li mlijeko?", tags=["diet", "question"], diff=3),
    P("ohne Nüsse", "bez orašastih plodova", tags=["diet", "allergy"], diff=4),
    W("scharf", "ljuto", pos="adjective", tags=["taste"], diff=2),
    W("süß", "slatko", pos="adjective", tags=["taste"], diff=1),
    W("salzig", "slano", pos="adjective", tags=["taste"], diff=2),
    W("sauer", "kiselo", pos="adjective", tags=["taste"], diff=2),
    W("bitter", "gorko", pos="adjective", tags=["taste"], diff=3),
    W("lecker", "ukusno", pos="adjective", tags=["taste", "positive"], diff=1),
    W("Trinkgeld", "napojnica", pos="noun", tags=["payment"], diff=3),
    S("Stimmt so. (Behalten Sie den Rest.)", "Zadržite ostatak.", tags=["payment", "polite"], diff=3),
    S("Komplimente an den Koch!", "Pošaljite kuhara!", tags=["compliment", "service"], diff=4),
    S("Es schmeckt mir nicht.", "Ne sviđa mi se.", tags=["complaint"], diff=3),
    S("Es ist kalt. (Speise)", "Hladno je.", tags=["complaint", "temperature"], diff=2),
    W("Pašticada (Rinderschmorbraten)", "pašticada", pos="noun", tags=["balkan", "specialty"], diff=4),
    P("schwarzes Risotto (Tinte)", "crni rižot", tags=["balkan", "specialty"], diff=4),
    W("Seehecht", "oslić", pos="noun", tags=["fish", "specialty"], diff=4),
    W("Fischeintopf", "brudet", pos="noun", tags=["balkan", "specialty"], diff=4),
    W("Štrukli (Käseteigtaschen)", "štrukli", pos="noun", tags=["balkan", "specialty"], diff=4),
    W("Rožata (Karamellpudding)", "rožata", pos="noun", tags=["balkan", "dessert"], diff=4),
    P("Brot mit Olivenöl", "kruh s maslinovim uljem", tags=["food"], diff=3),
    P("Bier vom Fass", "točeno pivo", tags=["alcohol"], diff=3),
    P("Flaschenbier", "flaširano pivo", tags=["alcohol"], diff=3),
    P("Glas Rotwein", "čaša crnog vina", tags=["alcohol"], diff=2),
    P("Glas Weißwein", "čaša bijelog vina", tags=["alcohol"], diff=2),
    P("hausgemachter Schnaps", "domaća rakija", tags=["alcohol", "specialty"], diff=3),
    S("Es war ausgezeichnet, danke.", "Bilo je odlično, hvala.", tags=["feedback", "compliment"], diff=2),
]

TRAFFIC_NEW = [
    P("Busbahnhof", "autobusni kolodvor", tags=["place", "transport"], diff=2),
    P("Hauptbahnhof", "željeznički kolodvor", tags=["place", "transport"], diff=2),
    W("Haltestelle", "stajalište", pos="noun", tags=["transport", "place"], diff=2),
    P("Fernbus", "međugradski autobus", tags=["transport"], diff=3),
    W("Fahrgast", "putnik", pos="noun", tags=["transport", "people"], diff=2),
    P("Busfahrer", "vozač autobusa", tags=["transport", "work"], diff=2),
    W("Schaffner", "kondukter", pos="noun", tags=["transport", "work"], diff=3),
    W("Eingang", "ulaz", pos="noun", tags=["place", "infrastructure"], diff=1),
    W("Ausgang", "izlaz", pos="noun", tags=["place", "infrastructure"], diff=1),
    W("Abbiegung", "skretanje", pos="noun", tags=["direction"], diff=3),
    P("Kreisverkehr", "kružni tok", tags=["road", "infrastructure"], diff=3),
    P("Zebrastreifen", "pješački prijelaz", tags=["road", "infrastructure"], diff=3),
    P("Fußgängerzone", "zona pješaka", tags=["road", "place"], diff=3),
    P("Einbahnstraße", "jednosmjerna ulica", tags=["road", "sign"], diff=3),
    P("Gegenverkehr", "dvosmjerni promet", tags=["road", "traffic"], diff=4),
    W("warten", "čekati", pos="verb", tags=["verb"], diff=1),
    W("einsteigen", "ući", pos="verb", tags=["verb", "transport"], diff=2),
    W("aussteigen", "izaći", pos="verb", tags=["verb", "transport"], diff=2),
    W("umsteigen", "presjedati", pos="verb", tags=["verb", "transport"], diff=3),
    W("sich verspäten", "zakasniti", pos="verb", tags=["verb", "time"], diff=3),
    W("ankommen", "stići", pos="verb", tags=["verb", "movement"], diff=2),
    W("losfahren", "krenuti", pos="verb", tags=["verb", "movement"], diff=3),
    P("links abbiegen", "skrenuti lijevo", tags=["direction", "instruction"], diff=2),
    P("rechts abbiegen", "skrenuti desno", tags=["direction", "instruction"], diff=2),
    P("die nächste links", "sljedeća lijevo", tags=["direction", "instruction"], diff=2),
    P("die zweite rechts", "druga desno", tags=["direction", "instruction"], diff=2),
    P("neben der Kirche", "pored crkve", tags=["direction", "location"], diff=2),
    P("um die Ecke", "iza ugla", tags=["direction", "location"], diff=2),
    P("an der Ecke", "na uglu", tags=["direction", "location"], diff=2),
    W("gegenüber", "nasuprot", pos="adverb", tags=["direction"], diff=3),
    W("zwischen", "između", pos="adverb", tags=["direction", "preposition"], diff=2),
    W("vor", "ispred", pos="adverb", tags=["direction", "preposition"], diff=2),
    W("hinter", "iza", pos="adverb", tags=["direction", "preposition"], diff=2),
    W("unter", "ispod", pos="adverb", tags=["direction", "preposition"], diff=2),
    W("über", "iznad", pos="adverb", tags=["direction", "preposition"], diff=2),
    P("einfache Fahrt", "karta u jednom smjeru", tags=["ticket", "transport"], diff=3),
    P("Rückfahrkarte", "povratna karta", tags=["ticket", "transport"], diff=2),
    P("Tageskarte", "dnevna karta", tags=["ticket", "transport"], diff=3),
    P("Monatskarte", "mjesečna karta", tags=["ticket", "transport"], diff=3),
    P("Auto mieten", "iznajmiti auto", tags=["car", "rental"], diff=2),
    P("Tankstelle", "benzinska postaja", tags=["place", "car"], diff=2),
    P("tanken", "napuniti gorivo", tags=["car", "verb"], diff=3),
    W("Reifen", "guma", pos="noun", tags=["car", "vehicle-part"], diff=3),
    W("Panne", "kvar", pos="noun", tags=["car"], diff=4),
    P("Fußgängerzone", "pješačka zona", tags=["road", "place"], diff=3),
]

TOURISM_NEW = [
    P("Reisebüro", "putna agencija", tags=["travel", "shop"], diff=2),
    P("Reiseversicherung", "putna polica", tags=["travel", "document"], diff=3),
    P("Reiserücktrittsversicherung", "osiguranje od otkaza", tags=["travel", "document"], diff=4),
    P("ein Zimmer mieten", "iznajmiti sobu", tags=["accommodation"], diff=2),
    P("privater Vermieter", "privatni iznajmljivač", tags=["accommodation", "people"], diff=3),
    W("Appartement", "apartman", pos="noun", tags=["accommodation"], diff=2),
    W("Zimmermädchen", "sobarica", pos="noun", tags=["accommodation", "work"], diff=3),
    W("Gepäck", "prtljaga", pos="noun", tags=["travel", "object"], diff=1),
    W("Koffer", "kofer", pos="noun", tags=["travel", "object"], diff=1),
    W("Rucksack", "ruksak", pos="noun", tags=["travel", "object"], diff=2),
    P("Handgepäck", "ručna prtljaga", tags=["travel", "object"], diff=3),
    P("Kurtaxe", "boravišna pristojba", tags=["travel", "payment"], diff=4),
    P("Stadtrundgang", "razgled grada", tags=["tour", "activity"], diff=3),
    P("Touristenkarte/Stadtplan", "turistička karta", tags=["tour", "object"], diff=2),
    W("Postkarte", "razglednica", pos="noun", tags=["souvenir", "object"], diff=2),
    W("Souvenir", "suvenir", pos="noun", tags=["souvenir", "object"], diff=1),
    P("Strandtuch", "ručnik za plažu", tags=["beach", "object"], diff=2),
    W("Sonnenschirm", "suncobran", pos="noun", tags=["beach", "object"], diff=2),
    W("Liegestuhl", "ležaljka", pos="noun", tags=["beach", "object"], diff=2),
    P("Sonnencreme", "krema za sunčanje", tags=["beach", "object"], diff=2),
    P("Sonnenbrille", "sunčane naočale", tags=["beach", "object"], diff=2),
    P("Badeanzug", "kupaći kostim", tags=["beach", "clothing"], diff=2),
    P("Badehose", "kupaće gaće", tags=["beach", "clothing"], diff=2),
    W("Flip-Flops", "japanke", pos="noun", tags=["beach", "clothing"], diff=2),
    P("das Meer ist ruhig", "more je mirno", tags=["sea", "weather"], diff=3),
    P("das Meer ist aufgewühlt", "more je uzburkano", tags=["sea", "weather"], diff=4),
    W("Wellen", "valovi", pos="noun", tags=["sea", "nature"], diff=2),
    W("Sand", "pijesak", pos="noun", tags=["beach", "nature"], diff=1),
    W("Kies", "šljunak", pos="noun", tags=["beach", "nature"], diff=3),
    W("Felsen", "stijene", pos="noun", tags=["nature"], diff=3),
    W("Leuchtturm", "svjetionik", pos="noun", tags=["sea", "historic"], diff=3),
    P("Nationalpark", "nacionalni park", tags=["nature", "place"], diff=2),
    W("Plitvicer Seen", "Plitvička jezera", pos="noun", tags=["place", "geography"], diff=2),
    W("Dubrovnik", "Dubrovnik", pos="noun", tags=["place", "city"], diff=1),
    W("Hvar", "Hvar", pos="noun", tags=["place", "city"], diff=1),
    W("Split", "Split", pos="noun", tags=["place", "city"], diff=1),
    W("Zagreb", "Zagreb", pos="noun", tags=["place", "city"], diff=1),
    W("Istrien", "Istra", pos="noun", tags=["place", "geography"], diff=2),
    W("Dalmatien", "Dalmacija", pos="noun", tags=["place", "geography"], diff=2),
    W("Kvarner", "Kvarner", pos="noun", tags=["place", "geography"], diff=2),
    W("Wechselstube", "mjenjačnica", pos="noun", tags=["money", "place"], diff=3),
    P("Euro-Kurs", "tečaj eura", tags=["money"], diff=3),
    S("Wo kann ich Geld wechseln?", "Gdje mogu zamijeniti novac?", tags=["money", "question"], diff=3),
    S("Ich brauche Hilfe!", "Trebam pomoć!", tags=["emergency"], diff=1),
    S("Rufen Sie die Polizei!", "Zovite policiju!", tags=["emergency"], diff=2),
    S("Rufen Sie den Notarzt!", "Zovite hitnu!", tags=["emergency"], diff=2),
    S("Ich habe meinen Pass verloren. (m.)", "Izgubio sam putovnicu.", tags=["emergency", "document"], diff=3),
]

ADVANCED_NEW = [
    W("dennoch", "ipak", pos="adverb", tags=["connector"], diff=4),
    W("jedoch", "međutim", pos="adverb", tags=["connector"], diff=4),
    W("daher", "stoga", pos="adverb", tags=["connector"], diff=4),
    W("also (folglich)", "dakle", pos="adverb", tags=["connector"], diff=3),
    P("da (kausal)", "budući da", tags=["connector"], diff=4),
    P("weil", "zato što", tags=["connector"], diff=3),
    W("obwohl", "premda", pos="adverb", tags=["connector"], diff=4),
    W("obwohl/auch wenn", "iako", pos="adverb", tags=["connector"], diff=3),
    W("sobald", "čim", pos="adverb", tags=["connector", "time"], diff=4),
    W("während", "dok", pos="adverb", tags=["connector", "time"], diff=3),
    P("bevor", "prije nego što", tags=["connector", "time"], diff=4),
    P("nachdem", "nakon što", tags=["connector", "time"], diff=4),
    P("stattdessen", "umjesto toga", tags=["connector"], diff=4),
    P("außerdem", "osim toga", tags=["connector"], diff=4),
    P("andererseits", "s druge strane", tags=["connector"], diff=4),
    P("zum Beispiel", "na primjer", tags=["connector"], diff=3),
    P("eigentlich", "u stvari", tags=["adverb"], diff=3),
    W("tatsächlich", "zapravo", pos="adverb", tags=["adverb"], diff=4),
    W("angeblich", "navodno", pos="adverb", tags=["adverb"], diff=5),
    W("gewohnt (m.)", "navikao", pos="adjective", tags=["state"], diff=4),
    W("bewusst (m.)", "svjestan", pos="adjective", tags=["state"], diff=4),
    W("unabhängig", "nezavisno", pos="adverb", tags=["state"], diff=4),
    P("abhängig von", "ovisno o", tags=["preposition"], diff=4),
    P("Ich könnte ...", "Mogao bih ...", tags=["modal", "polite"], diff=4),
    P("Ich sollte ...", "Trebao bih ...", tags=["modal", "polite"], diff=4),
    P("Ich müsste ...", "Morao bih ...", tags=["modal", "polite"], diff=4),
    S("Ich würde gern reden.", "Htio bih razgovarati.", tags=["modal", "request"], diff=3),
    P("Es wäre besser, wenn ...", "Bilo bi bolje da ...", tags=["modal"], diff=4),
    S("Was halten Sie davon?", "Što mislite o tome?", tags=["opinion", "question"], diff=3),
    S("Ich stimme zu.", "Slažem se.", tags=["opinion"], diff=3),
    S("Ich stimme nicht zu.", "Ne slažem se.", tags=["opinion"], diff=3),
    S("Es kommt auf die Situation an.", "Ovisi o situaciji.", tags=["opinion"], diff=4),
    S("Das ist verständlich.", "To je razumljivo.", tags=["opinion"], diff=4),
    S("Haben Sie einen Beweis?", "Imate li dokaz?", tags=["question", "formal"], diff=4),
    S("Kann ich einen Termin bekommen?", "Mogu li dobiti termin?", tags=["request", "appointment"], diff=3),
    P("ein Treffen vereinbaren", "dogovoriti sastanak", tags=["appointment", "verb"], diff=3),
    W("verschieben", "odgoditi", pos="verb", tags=["appointment", "verb"], diff=4),
    W("absagen", "otkazati", pos="verb", tags=["appointment", "verb"], diff=3),
    W("bestätigen", "potvrditi", pos="verb", tags=["appointment", "verb"], diff=3),
    W("erinnern", "podsjetiti", pos="verb", tags=["verb"], diff=3),
    W("veröffentlichen", "objaviti", pos="verb", tags=["verb"], diff=4),
    P("bezweifeln", "sumnjati u", tags=["verb"], diff=4),
    P("glauben an", "vjerovati u", tags=["verb"], diff=3),
]

# ---------------------------------------------------------------------------
# New lessons
# ---------------------------------------------------------------------------

COLORS_ITEMS = [
    W("Farbe", "boja", pos="noun", tags=["colors"], diff=1),
    W("rot (f.)", "crvena", pos="adjective", tags=["colors"], diff=1),
    W("rot (m.)", "crven", pos="adjective", tags=["colors"], diff=1),
    W("blau (f.)", "plava", pos="adjective", tags=["colors"], diff=1),
    W("blau (m.)", "plav", pos="adjective", tags=["colors"], diff=1),
    W("grün (f.)", "zelena", pos="adjective", tags=["colors"], diff=1),
    W("grün (m.)", "zelen", pos="adjective", tags=["colors"], diff=1),
    W("gelb (f.)", "žuta", pos="adjective", tags=["colors"], diff=1),
    W("gelb (m.)", "žut", pos="adjective", tags=["colors"], diff=1),
    W("schwarz (f.)", "crna", pos="adjective", tags=["colors"], diff=1),
    W("schwarz (m.)", "crn", pos="adjective", tags=["colors"], diff=1),
    W("weiß (f.)", "bijela", pos="adjective", tags=["colors"], diff=1),
    W("weiß (m.)", "bijel", pos="adjective", tags=["colors"], diff=1),
    W("grau (f.)", "siva", pos="adjective", tags=["colors"], diff=2),
    W("braun (f.)", "smeđa", pos="adjective", tags=["colors"], diff=2),
    W("orange", "narančasta", pos="adjective", tags=["colors"], diff=2),
    W("lila/violett", "ljubičasta", pos="adjective", tags=["colors"], diff=2),
    W("rosa", "ružičasta", pos="adjective", tags=["colors"], diff=2),
    W("golden", "zlatna", pos="adjective", tags=["colors"], diff=3),
    W("silbern", "srebrna", pos="adjective", tags=["colors"], diff=3),
    P("hellblau", "svijetlo plava", tags=["colors", "description"], diff=2),
    P("dunkelblau", "tamno plava", tags=["colors", "description"], diff=2),
    P("hellgrün", "svijetlo zelena", tags=["colors", "description"], diff=2),
    P("dunkelgrün", "tamno zelena", tags=["colors", "description"], diff=2),
    P("Hautfarbe", "boja kože", tags=["colors", "body"], diff=3),
    P("in Farbe (Druck)", "u boji", tags=["colors", "description"], diff=3),
    P("schwarz-weiß", "crno-bijelo", tags=["colors", "description"], diff=2),
    W("bunt", "šaren", pos="adjective", tags=["colors", "description"], diff=2),
    W("einfarbig", "jednobojan", pos="adjective", tags=["colors", "description"], diff=3),
    W("gestreift", "prugast", pos="adjective", tags=["description", "pattern"], diff=3),
    W("gepunktet", "točkasto", pos="adjective", tags=["description", "pattern"], diff=4),
    W("groß", "velik", pos="adjective", tags=["description", "size"], alt_hr=["velika"], diff=1),
    W("klein", "mali", pos="adjective", tags=["description", "size"], alt_hr=["mala"], diff=1),
    W("lang", "dug", pos="adjective", tags=["description", "size"], alt_hr=["duga"], diff=1),
    W("kurz", "kratak", pos="adjective", tags=["description", "size"], alt_hr=["kratka"], diff=1),
    W("breit", "širok", pos="adjective", tags=["description", "size"], diff=2),
    W("schmal", "uzak", pos="adjective", tags=["description", "size"], diff=2),
    W("hoch / groß (Person)", "visok", pos="adjective", tags=["description", "size"], diff=2),
    W("niedrig / klein (Person)", "nizak", pos="adjective", tags=["description", "size"], diff=2),
    W("dick", "debeo", pos="adjective", tags=["description"], diff=2),
    W("dünn", "tanak", pos="adjective", tags=["description"], diff=2),
    W("schwer", "težak", pos="adjective", tags=["description"], diff=2),
    W("leicht", "lagan", pos="adjective", tags=["description"], diff=2),
    W("rund", "okrugao", pos="adjective", tags=["description", "shape"], diff=3),
    W("viereckig", "četvrtast", pos="adjective", tags=["description", "shape"], diff=3),
    W("Kreis", "krug", pos="noun", tags=["shape"], diff=3),
    W("Quadrat", "kvadrat", pos="noun", tags=["shape"], diff=3),
    W("Dreieck", "trokut", pos="noun", tags=["shape"], diff=3),
    S("Welche Farbe hat ...?", "Koje je boje ...?", tags=["colors", "question"], diff=2),
    S("Mein Auto ist rot.", "Moj auto je crven.", tags=["colors"], diff=1),
]

BODY_HEALTH_ITEMS = [
    W("Körper", "tijelo", pos="noun", tags=["body"], diff=1),
    W("Kopf", "glava", pos="noun", tags=["body"], diff=1),
    W("Haar", "kosa", pos="noun", tags=["body"], diff=1),
    W("Gesicht", "lice", pos="noun", tags=["body"], diff=1),
    W("Auge", "oko", pos="noun", tags=["body"], diff=1),
    W("Augen", "oči", pos="noun", tags=["body"], diff=1),
    W("Nase", "nos", pos="noun", tags=["body"], diff=1),
    W("Ohr", "uho", pos="noun", tags=["body"], diff=1),
    W("Ohren", "uši", pos="noun", tags=["body"], diff=2),
    W("Mund", "usta", pos="noun", tags=["body"], diff=1),
    W("Zunge / Sprache", "jezik", pos="noun", tags=["body", "language"], diff=2),
    W("Zahn", "zub", pos="noun", tags=["body"], diff=1),
    W("Zähne", "zubi", pos="noun", tags=["body"], diff=2),
    W("Hals", "vrat", pos="noun", tags=["body"], diff=1),
    W("Schulter", "rame", pos="noun", tags=["body"], diff=2),
    W("Schultern", "ramena", pos="noun", tags=["body"], diff=2),
    W("Arm / Hand", "ruka", pos="noun", tags=["body"], diff=1),
    W("Arme / Hände", "ruke", pos="noun", tags=["body"], diff=1),
    W("Finger", "prst", pos="noun", tags=["body"], diff=2),
    W("Finger (Pl.)", "prsti", pos="noun", tags=["body"], diff=2),
    W("Bein / Fuß", "noga", pos="noun", tags=["body"], diff=1),
    W("Beine", "noge", pos="noun", tags=["body"], diff=1),
    W("Knie", "koljeno", pos="noun", tags=["body"], diff=2),
    W("Fuß", "stopalo", pos="noun", tags=["body"], diff=2),
    W("Rücken", "leđa", pos="noun", tags=["body"], diff=2),
    W("Bauch", "trbuh", pos="noun", tags=["body"], diff=2),
    W("Magen", "želudac", pos="noun", tags=["body"], diff=3),
    W("Herz", "srce", pos="noun", tags=["body"], diff=2),
    W("Lunge", "pluća", pos="noun", tags=["body"], diff=3),
    W("Haut", "koža", pos="noun", tags=["body"], diff=2),
    W("Blut", "krv", pos="noun", tags=["body"], diff=3),
    W("gesund", "zdrav", pos="adjective", tags=["health"], diff=2),
    W("krank (m.)", "bolestan", pos="adjective", tags=["health"], diff=2),
    W("krank (f.)", "bolesna", pos="adjective", tags=["health"], diff=2),
    W("Schmerz", "bol", pos="noun", tags=["health", "pain"], diff=2),
    W("Kopfschmerzen", "glavobolja", pos="noun", tags=["health", "pain"], diff=2),
    W("Fieber/Temperatur", "temperatura", pos="noun", tags=["health"], diff=2),
    W("Erkältung", "prehlada", pos="noun", tags=["health"], diff=2),
    W("Grippe", "gripa", pos="noun", tags=["health"], diff=2),
    W("Husten", "kašalj", pos="noun", tags=["health"], diff=3),
    W("Niesen", "kihanje", pos="noun", tags=["health"], diff=4),
    W("Müdigkeit", "umor", pos="noun", tags=["health"], diff=3),
    W("Arzt", "liječnik", pos="noun", tags=["health", "work"], diff=1),
    W("Zahnarzt", "zubar", pos="noun", tags=["health", "work"], diff=2),
    W("Krankenhaus", "bolnica", pos="noun", tags=["health", "place"], diff=2),
    W("Apotheke", "ljekarna", pos="noun", tags=["health", "place"], diff=2),
    W("Rezept", "recept", pos="noun", tags=["health", "medical"], diff=3),
    W("Medikament", "lijek", pos="noun", tags=["health", "medical"], diff=2),
    W("Tablette", "tableta", pos="noun", tags=["health", "medical"], diff=2),
    S("Mein Kopf tut weh.", "Boli me glava.", tags=["health", "pain"], diff=2),
    S("Mein Bauch tut weh.", "Boli me trbuh.", tags=["health", "pain"], diff=2),
    S("Mein Hals tut weh.", "Boli me grlo.", tags=["health", "pain"], diff=2),
    S("Ich habe Fieber.", "Imam temperaturu.", tags=["health"], diff=2),
    S("Ich brauche einen Arzt.", "Trebam liječnika.", tags=["health", "emergency"], diff=2),
    S("Wo ist das nächste Krankenhaus?", "Gdje je najbliža bolnica?", tags=["health", "question", "emergency"], diff=2),
    S("Ich bin allergisch gegen ... (m.)", "Alergičan sam na ...", tags=["health", "allergy"], diff=3),
]

DAILY_LIFE_ITEMS = [
    W("aufstehen", "ustati", pos="verb", tags=["routine", "verb"], diff=2),
    P("ich stehe früh auf", "ustajem rano", tags=["routine"], diff=2),
    W("duschen", "tuširati se", pos="verb", tags=["routine", "reflexive"], diff=2),
    W("sich waschen (Gesicht)", "umiti se", pos="verb", tags=["routine", "reflexive"], diff=3),
    P("Zähne putzen", "oprati zube", tags=["routine"], diff=2),
    W("sich anziehen", "obući se", pos="verb", tags=["routine", "reflexive"], diff=2),
    W("sich ausziehen", "svući se", pos="verb", tags=["routine", "reflexive"], diff=3),
    W("frühstücken", "doručkovati", pos="verb", tags=["routine", "verb"], diff=2),
    W("zu Mittag essen", "ručati", pos="verb", tags=["routine", "verb"], diff=2),
    W("zu Abend essen", "večerati", pos="verb", tags=["routine", "verb"], diff=2),
    W("kochen", "kuhati", pos="verb", tags=["routine", "verb"], diff=2),
    P("abspülen", "oprati suđe", tags=["routine"], diff=3),
    W("aufräumen", "pospremiti", pos="verb", tags=["routine", "verb"], diff=3),
    P("zur Arbeit gehen", "ići na posao", tags=["routine"], diff=2),
    P("in die Schule gehen", "ići u školu", tags=["routine"], diff=1),
    P("nach Hause kommen", "vratiti se kući", tags=["routine"], diff=2),
    P("ins Bett gehen", "ići u krevet", tags=["routine"], diff=2),
    W("einschlafen", "zaspati", pos="verb", tags=["routine", "verb"], diff=3),
    W("aufwachen", "probuditi se", pos="verb", tags=["routine", "reflexive"], diff=3),
    W("sich ausruhen", "odmoriti se", pos="verb", tags=["routine", "reflexive"], diff=3),
    P("Freizeit", "slobodno vrijeme", tags=["hobby"], diff=2),
    W("Hobby", "hobi", pos="noun", tags=["hobby"], diff=1),
    P("Bücher lesen", "čitati knjige", tags=["hobby"], diff=1),
    P("einen Film anschauen", "gledati film", tags=["hobby"], diff=1),
    P("fernsehen", "gledati TV", tags=["hobby"], diff=1),
    P("Musik hören", "slušati glazbu", tags=["hobby"], diff=2),
    P("Gitarre spielen", "svirati gitaru", tags=["hobby"], diff=2),
    P("Klavier spielen", "svirati klavir", tags=["hobby"], diff=2),
    W("singen", "pjevati", pos="verb", tags=["hobby", "verb"], diff=2),
    W("tanzen", "plesati", pos="verb", tags=["hobby", "verb"], diff=2),
    W("zeichnen", "crtati", pos="verb", tags=["hobby", "verb"], diff=2),
    W("malen / fotografieren", "slikati", pos="verb", tags=["hobby", "verb"], diff=2),
    W("fotografieren", "fotografirati", pos="verb", tags=["hobby", "verb"], diff=2),
    W("joggen / laufen", "trčati", pos="verb", tags=["hobby", "sport"], diff=2),
    P("Fahrrad fahren", "voziti bicikl", tags=["hobby", "sport"], diff=2),
    W("schwimmen", "plivati", pos="verb", tags=["hobby", "sport"], diff=1),
    P("Fußball spielen", "igrati nogomet", tags=["hobby", "sport"], diff=1),
    P("Basketball spielen", "igrati košarku", tags=["hobby", "sport"], diff=2),
    P("Tennis spielen", "igrati tenis", tags=["hobby", "sport"], diff=2),
    P("ins Fitnessstudio gehen", "ići u teretanu", tags=["hobby", "sport"], diff=2),
    W("reisen", "putovati", pos="verb", tags=["hobby", "verb"], diff=2),
    P("zum Spaß kochen", "kuhati za zabavu", tags=["hobby"], diff=3),
    P("gärtnern", "baviti se vrtlarstvom", tags=["hobby"], diff=4),
    W("Wetter", "vrijeme", pos="noun", tags=["weather"], diff=1),
    S("Wie ist das Wetter?", "Kakvo je vrijeme?", tags=["weather", "question"], diff=1),
    S("Es ist sonnig.", "Sunčano je.", tags=["weather"], diff=1),
    S("Es ist bewölkt.", "Oblačno je.", tags=["weather"], diff=1),
    S("Es regnet.", "Pada kiša.", tags=["weather"], diff=1),
    S("Es schneit.", "Pada snijeg.", tags=["weather"], diff=2),
    S("Es ist windig.", "Vjetrovito je.", tags=["weather"], diff=2),
    S("Es ist heiß.", "Vruće je.", tags=["weather"], diff=1),
    S("Es ist kalt.", "Hladno je.", tags=["weather"], diff=1),
    S("Es ist klar/heiter.", "Vedro je.", tags=["weather"], diff=2),
    W("Nebel", "magla", pos="noun", tags=["weather"], diff=2),
    W("Donner", "grom", pos="noun", tags=["weather"], diff=3),
    W("Blitz", "munja", pos="noun", tags=["weather"], diff=3),
    W("Sturm", "oluja", pos="noun", tags=["weather"], diff=3),
    P("Lufttemperatur", "temperatura zraka", tags=["weather"], diff=3),
    P("zwanzig Grad", "dvadeset stupnjeva", tags=["weather"], diff=2),
]

# ---------------------------------------------------------------------------
# Lesson configuration: prefix, file name, new version, new items
# ---------------------------------------------------------------------------

EXISTING = [
    ("greet",   "greetings.json",     "1.2.0", GREETINGS_NEW),
    ("intro",   "introduction.json",  "1.2.0", INTRODUCTION_NEW),
    ("num",     "numbers-time.json",  "1.2.0", NUMBERS_TIME_NEW),
    ("fam",     "family.json",        "1.2.0", FAMILY_NEW),
    ("shop",    "shopping.json",      "1.2.0", SHOPPING_NEW),
    ("rest",    "restaurant.json",    "1.2.0", RESTAURANT_NEW),
    ("traf",    "traffic.json",       "1.2.0", TRAFFIC_NEW),
    ("tour",    "tourism.json",       "1.2.0", TOURISM_NEW),
    ("adv",     "advanced.json",      "1.1.0", ADVANCED_NEW),
]

NEW_LESSONS = [
    {
        "prefix": "col",
        "file": "colors.json",
        "id": "colors",
        "version": "1.0.0",
        "order": 10,
        "difficulty": 2,
        "title_de": "Farben & Beschreibung",
        "title_hr": "Boje i opis",
        "description_de": "Farben, Formen, Größen- und Beschreibungs-Adjektive für den A1-Wortschatz.",
        "prerequisites": ["greetings"],
        "tags": ["basics", "description"],
        "items": COLORS_ITEMS,
    },
    {
        "prefix": "body",
        "file": "body-health.json",
        "id": "body-health",
        "version": "1.0.0",
        "order": 11,
        "difficulty": 2,
        "title_de": "Körper & Gesundheit",
        "title_hr": "Tijelo i zdravlje",
        "description_de": "Körperteile, häufige Beschwerden, Arzt-/Apothekenphrasen für Reise und Alltag.",
        "prerequisites": ["introduction"],
        "tags": ["body", "health"],
        "items": BODY_HEALTH_ITEMS,
    },
    {
        "prefix": "daily",
        "file": "daily-life.json",
        "id": "daily-life",
        "version": "1.0.0",
        "order": 12,
        "difficulty": 2,
        "title_de": "Alltag, Wetter & Hobbys",
        "title_hr": "Svakodnevnica, vrijeme i hobiji",
        "description_de": "Tagesablauf-Verben, Freizeitaktivitäten, Sport, Wetterausdrücke.",
        "prerequisites": ["greetings"],
        "tags": ["routine", "hobby", "weather"],
        "items": DAILY_LIFE_ITEMS,
    },
]


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def _compact(obj):
    return json.dumps(obj, ensure_ascii=False)


def fmt(obj):
    """Format JSON so the outer structure is pretty-printed (indent=2) but every
    item/stage/lesson-entry stays on one line — matches the repo's existing style
    and keeps PR diffs review-friendly."""
    if isinstance(obj, dict) and "items" in obj and "stages" in obj:
        return _fmt_lesson(obj)
    if isinstance(obj, dict) and "lessons" in obj and "schemaVersion" in obj:
        return _fmt_manifest(obj)
    return json.dumps(obj, ensure_ascii=False, indent=2) + "\n"


def _fmt_lesson(lesson):
    # Preserve key order from the dict, but render items/stages compactly.
    parts = ["{"]
    keys = list(lesson.keys())
    for i, k in enumerate(keys):
        v = lesson[k]
        comma = "," if i < len(keys) - 1 else ""
        if k == "stages":
            parts.append(f'  "stages": [')
            for j, s in enumerate(v):
                sc = "," if j < len(v) - 1 else ""
                parts.append(f'    {_compact(s)}{sc}')
            parts.append(f'  ]{comma}')
        elif k == "items":
            parts.append(f'  "items": [')
            for j, it in enumerate(v):
                ic = "," if j < len(v) - 1 else ""
                parts.append(f'    {_compact(it)}{ic}')
            parts.append(f'  ]{comma}')
        else:
            parts.append(f'  {json.dumps(k, ensure_ascii=False)}: {_compact(v)}{comma}')
    parts.append("}")
    return "\n".join(parts) + "\n"


def _fmt_manifest(manifest):
    parts = ["{"]
    keys = list(manifest.keys())
    for i, k in enumerate(keys):
        v = manifest[k]
        comma = "," if i < len(keys) - 1 else ""
        if k == "lessons":
            parts.append(f'  "lessons": [')
            for j, entry in enumerate(v):
                ec = "," if j < len(v) - 1 else ""
                parts.append(f'    {_compact(entry)}{ec}')
            parts.append(f'  ]{comma}')
        elif k == "globalLicenses":
            parts.append(f'  "globalLicenses": [')
            for j, entry in enumerate(v):
                ec = "," if j < len(v) - 1 else ""
                parts.append(f'    {_compact(entry)}{ec}')
            parts.append(f'  ]{comma}')
        else:
            parts.append(f'  {json.dumps(k, ensure_ascii=False)}: {_compact(v)}{comma}')
    parts.append("}")
    return "\n".join(parts) + "\n"


def assign_ids(items, prefix, start_num):
    out = []
    n = start_num
    for it in items:
        clone = {"id": f"{prefix}_{n:03d}"}
        clone.update(it)
        out.append(clone)
        n += 1
    return out


def next_id_num(items, prefix):
    max_n = 0
    for it in items:
        iid = it.get("id", "")
        if iid.startswith(prefix + "_"):
            try:
                n = int(iid.split("_", 1)[1])
                if n > max_n:
                    max_n = n
            except ValueError:
                pass
    return max_n + 1


def count_by_type(items):
    w = sum(1 for it in items if it.get("type") == "word")
    p = sum(1 for it in items if it.get("type") == "phrase")
    s = sum(1 for it in items if it.get("type") == "sentence")
    return w, p, s


def hr_text_set(items):
    return {it["hr"]["text"] for it in items if "hr" in it and "text" in it.get("hr", {})}


def update_existing_lesson(prefix, file_name, new_version, new_items):
    path = LESSONS_DIR / file_name
    data = json.loads(path.read_text(encoding="utf-8"))
    existing_items = data["items"]
    existing_hr = hr_text_set(existing_items)
    # Skip dupes by hr.text
    fresh = [it for it in new_items if it["hr"]["text"] not in existing_hr]
    start_n = next_id_num(existing_items, prefix)
    fresh_with_ids = assign_ids(fresh, prefix, start_n)
    data["items"] = existing_items + fresh_with_ids
    data["version"] = new_version
    path.write_text(fmt(data), encoding="utf-8")
    return count_by_type(data["items"]), len(fresh_with_ids)


def write_new_lesson(cfg):
    path = LESSONS_DIR / cfg["file"]
    items = assign_ids(cfg["items"], cfg["prefix"], 1)
    body = {
        "schemaVersion": "1.0.0",
        "lessonId": cfg["id"],
        "version": cfg["version"],
        "title": {"de": cfg["title_de"], "hr": cfg["title_hr"]},
        "description": {"de": cfg["description_de"]},
        "stages": [
            {"id": "words",     "type": "vocabulary", "label": {"de": "Einzelwörter"}},
            {"id": "phrases",   "type": "phrase",     "label": {"de": "Wortgruppen"}},
            {"id": "sentences", "type": "sentence",   "label": {"de": "Sätze"}},
        ],
        "items": items,
    }
    path.write_text(fmt(body), encoding="utf-8")
    return count_by_type(items)


def sha256_of(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def size_of(path):
    return path.stat().st_size


def update_manifest(manifest_lessons_summary):
    """manifest_lessons_summary: dict[lesson_id] -> dict(version, wc, pc, sc, prereqs?, tags?, order?, difficulty?, title?, description?, file)"""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    manifest["dataVersion"] = TODAY
    manifest["generatedAt"] = GENERATED_AT
    existing_by_id = {entry["id"]: entry for entry in manifest["lessons"]}

    # Update existing entries
    for lid, summary in manifest_lessons_summary.items():
        entry = existing_by_id.get(lid)
        path = LESSONS_DIR / summary["file"]
        if entry is None:
            # New lesson — build from scratch
            entry = {
                "id": lid,
                "version": summary["version"],
                "title": {"de": summary["title_de"], "hr": summary["title_hr"]},
                "description": {"de": summary["description_de"]},
                "order": summary["order"],
                "difficulty": summary["difficulty"],
                "wordCount": summary["wc"],
                "phraseCount": summary["pc"],
                "sentenceCount": summary["sc"],
                "prerequisites": summary["prerequisites"],
                "tags": summary["tags"],
                "file": f"lessons/{summary['file']}",
                "sha256": sha256_of(path),
                "sizeBytes": size_of(path),
            }
            manifest["lessons"].append(entry)
        else:
            entry["version"] = summary["version"]
            entry["wordCount"] = summary["wc"]
            entry["phraseCount"] = summary["pc"]
            entry["sentenceCount"] = summary["sc"]
            entry["sha256"] = sha256_of(path)
            entry["sizeBytes"] = size_of(path)

    # Sort lessons by order so the new ones land at the bottom in the right place
    manifest["lessons"].sort(key=lambda e: e.get("order", 0))
    MANIFEST_PATH.write_text(fmt(manifest), encoding="utf-8")


def main():
    summary = {}
    total_added = 0
    for prefix, file_name, new_version, new_items in EXISTING:
        (wc, pc, sc), added = update_existing_lesson(prefix, file_name, new_version, new_items)
        total_added += added
        lesson_id = file_name.replace(".json", "")
        summary[lesson_id] = {
            "version": new_version,
            "wc": wc, "pc": pc, "sc": sc,
            "file": file_name,
        }
        print(f"  {lesson_id:14s} v{new_version}  +{added:3d}  total={wc + pc + sc} (w={wc}, p={pc}, s={sc})")

    for cfg in NEW_LESSONS:
        wc, pc, sc = write_new_lesson(cfg)
        total_added += wc + pc + sc
        summary[cfg["id"]] = {
            "version": cfg["version"],
            "wc": wc, "pc": pc, "sc": sc,
            "file": cfg["file"],
            "title_de": cfg["title_de"], "title_hr": cfg["title_hr"],
            "description_de": cfg["description_de"],
            "order": cfg["order"], "difficulty": cfg["difficulty"],
            "prerequisites": cfg["prerequisites"], "tags": cfg["tags"],
        }
        print(f"  {cfg['id']:14s} v{cfg['version']}  NEW   total={wc + pc + sc} (w={wc}, p={pc}, s={sc})")

    update_manifest(summary)
    print(f"\nManifest updated: dataVersion={TODAY}, total added items: {total_added}")


if __name__ == "__main__":
    main()
