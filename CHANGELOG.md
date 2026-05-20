# Changelog – vocabularies-kroatic-data

Inhalts- und Schema-Änderungen am Vokabel-Datensatz. Format basiert auf
[Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [1.3.0] – 2026-05-20

### Added — Wortschatzerweiterung über alle Themen (+531 Items)

Recherche typischer Kroatisch-für-Anfänger-Quellen (Croaticum FFZG
„Hrvatski za početnike", Bilic „Ja govorim hrvatski 1", Pinhok
100/1000 Croatian, Loecsen Reisewortschatz, Talkpal A1) — Lücken
gegen den Bestand gefüllt.

**Bestehende Lektionen erweitert** (Versionen → 1.2.0; `advanced` → 1.1.0):

| Lektion | + Items | neue Gesamtzahl |
|---|---:|---:|
| greetings    | +38 | 138 |
| introduction | +41 | 146 |
| numbers-time | +41 | 141 |
| family       | +36 | 136 |
| shopping     | +39 | 139 |
| restaurant   | +37 | 137 |
| traffic      | +45 | 145 |
| tourism      | +46 | 146 |
| advanced     | +43 | 329 |

Schwerpunkte: Smalltalk-/Emotionsvokabular (Greetings), Berufe und
Selbstvorstellung (Introduction), Ordinalzahlen + Uhrzeit-Idiome
(Numbers), Stieffamilie + Beziehungsstatus (Family), Nicht-Lebensmittel-
Läden + Größen (Shopping), Reservierung + Allergien + Croatian-Specialties
(Restaurant), Präpositionen + Transit-Verben (Traffic), Notfall +
Strandausrüstung + Ortsnamen (Tourism), Konnektoren + Modal-`bih`-Formen
(Advanced).

**Drei neue Lektionen angelegt** (typische A1-Themen):

| Lektion | Order | Items |
|---|---:|---:|
| `colors` — Farben & Beschreibung | 10 | 50 |
| `body-health` — Körper & Gesundheit | 11 | 56 |
| `daily-life` — Alltag, Wetter & Hobbys | 12 | 59 |

**Σ neue Items**: 531; App-Wortschatz wächst von ~1091 auf ~1622.

## [1.2.0] – 2026-05-17

### Added — neue Lektion `advanced` (286 Items)

Eigene Vokabel-Sammlung des Maintainers (Google Sheet) gegen die
bestehenden 8 Lektionen abgeglichen, **286 noch nicht enthaltene
Einträge** in einer neuen 9. Lektion `advanced` (Titel:
„Fortgeschritten / Napredno") zusammengefasst.

| Stage | Items |
|---|---:|
| words     | 196 |
| phrases   | 31  |
| sentences | 59  |
| **Σ**     | **286** |

**Schwierigkeits-Mapping** der Sheet-Skala 1–3 auf die Repo-Skala 1–5
nach `f(x) = 2x − 1` (sheet 1 → 1, 2 → 3, 3 → 5). Verteilung in der
neuen Lektion: diff 1: 63, diff 3: 84, diff 5: 139.

**Inhaltsspanne**: Farben, Adjektive und Alltagsobjekte (`Crveno`,
`Veliko`, `Auto`, `Knjiga`) auf diff 1; Kleidung, Möbel, Gesundheit
(`Cipele`, `Bolnica`, `Lijek`) auf diff 3; abstrakte Begriffe
(`Znanost`, `Pravda`, `Odgovornost`) und komplexe Sätze
(`Gospodarska situacija se značajno poboljšala`) auf diff 5.

Aggregierte `difficulty` der Lektion: 4. Lektion enthält keine
IPA-/POS-/Notiz-Felder — diese werden bei einem späteren
Inhaltspflege-Lauf nachgepflegt.

**Gesamtstand**: 9 Lektionen, 1 091 Items (805 → 1 091, +35,5 %).

## [1.1.0] – 2026-05-16

### Changed — Lektionsumfang massiv erweitert
Jede Lektion auf ~100 Items hochgezogen — **805 Items insgesamt**
(zuvor 339), also etwa **+137 % Wachstum**. Verteilung pro Lektion
weiterhin nach `type` (`word` / `phrase` / `sentence`) und
`difficulty` (1–5) sortiert.

| Lektion | Version | Items vorher | Items nachher | Diff-Spanne |
|---|---|---:|---:|---|
| greetings    | 1.0.0 → 1.1.0 | 24  | 100 (65W/18P/17S) | 1–4 |
| introduction | 1.0.0 → 1.1.0 | 35  | 105 (70W/18P/17S) | 1–4 |
| numbers-time | 1.0.0 → 1.1.0 | 60  | 100 (73W/15P/12S) | 1–4 |
| family       | 1.0.0 → 1.1.0 | 30  | 100 (70W/16P/14S) | 1–5 |
| shopping     | 1.0.0 → 1.1.0 | 45  | 100 (70W/17P/13S) | 2–4 |
| restaurant   | 1.0.0 → 1.1.0 | 50  | 100 (65W/20P/15S) | 2–5 |
| traffic      | 1.0.0 → 1.1.0 | 40  | 100 (65W/20P/15S) | 2–5 |
| tourism      | 1.0.0 → 1.1.0 | 55  | 100 (60W/20P/20S) | 2–5 |
| **Σ**        |               | **339** | **805** | |

### Added — neue thematische Schwerpunkte
- **greetings**: Befindlichkeiten (sretan/tužan/umoran/bolestan/zdrav),
  Wetter (sunčano, oblačno, kišno, kiša, snijeg, vjetar), Jahreszeiten,
  Adverbien (naravno, sigurno, možda, stvarno), Anreden (gospodin,
  gospođa, gospođica, kolega, susjed, gost, domaćin), Wunschformeln.
- **introduction**: Berufe (medicinska sestra, inženjer, arhitekt,
  programer, kuhar, pekar, vozač, prodavač), 10 Länder (Njemačka,
  Austrija, Švicarska, Hrvatska, Italija, Francuska, Engleska,
  Slovenija, Mađarska, Bosna), 5 Nationalitäten, 5 Sprachen,
  Verben (razumijem, govorim, znam, učim, radim), Kontaktdaten
  (adresa, telefon, e-pošta, putovnica), Familienstand.
- **numbers-time**: Wochentage komplett (Mo–So), alle 12 Monate
  (siječanj…prosinac), Zahlen bis 1000 (200, 300, 1000, milijun),
  Wochen-/Monats-/Jahres-Adverbien (prošli, sljedeći, prošle godine,
  ove godine).
- **family**: Erweiterte Verwandtschaft (unuk/unuka, prabaka/pradjed,
  stric, nećak/nećakinja, svekar/svekrva, zet/snaha, šurjak/šurjakinja),
  Beziehungs-Verben (voljeti, živjeti, posjetiti, telefonirati),
  Beziehungs-Status (brak, vjenčanje, razvod, udovac/udovica),
  Alter-Stufen (beba, tinejdžer, odrastao), Haustiere (pas, mačka),
  Heim-Vokabular (dom, kuća, stan).
- **shopping**: Vollständiges Gemüse (rajčica, krastavac, paprika,
  luk, češnjak, mrkva, kupus), Obst (kruška, grožđe, jagoda, limun,
  lubenica), Backwaren (žemlja, brašno), Gewürze (šećer, sol, papar,
  ulje, ocat), Süßwaren (čokolada, keks, bombon, med), Mengeneinheiten
  (kilogram, gram, litra, komad, boca, konzerva), Bezahlvokabular
  (popust, akcija, blagajna, blagajnik, kupac).
- **restaurant**: Balkan-Spezialitäten (burek, ćevapi, pljeskavica,
  rakija), internationale Klassiker (pizza, lazanja, sendvič, tost,
  palačinka), Geschirr & Besteck (tanjur, čaša, šalica, žlica,
  vilica, nož, ubrus), Kaffeesorten (kapučino, espreso, latte),
  Speisefolge (predjelo, glavno jelo, desert, garnitura),
  Diät-Optionen (vegetarijansko, bez glutena).
- **traffic**: Verkehrsmittel komplett (tramvaj, metro, avion,
  brod, motor, kamion), Himmelsrichtungen (sjever, jug, istok,
  zapad), Infrastruktur (most, tunel, autocesta, cesta, pločnik),
  Verben der Bewegung (voziti, stati, parkirati, ići, doći,
  putovati), Fahrzeug-Teile (kotač, kočnica, gas, prtljažnik).
- **tourism**: Kulturdenkmäler (spomenik, dvorac, tvrđava, galerija,
  kazalište, katedrala, utvrda, ruševine), Naturvokabular (rijeka,
  jezero, planina, brdo, šuma, livada, vodopad, spilja),
  Aktivitäten (planinariti, trčati, jedriti, skijati, pjevati,
  plesati, fotografirati, razgledati), Reise-Praktisches (viza,
  granica, carina, turist), Hotelkategorien (jednokrevetna,
  dvokrevetna, polupansion, puni pansion, privatni smještaj).

### Changed — Manifest
- Aggregierte `difficulty` pro Lektion neu kalibriert (z.B.
  greetings 1 → 2, family 2 → 3, tourism 4 bleibt).
- `wordCount`/`phraseCount`/`sentenceCount` jeder Lektion
  aktualisiert.
- `sha256` + `sizeBytes` jeder Lektion neu berechnet.
- `version` jeder Lektion auf `1.1.0` gebumpt (MINOR — additive
  Erweiterung, keine Breaking Changes am Schema).

### Migration für Client-Implementierungen
- Bestehende `progress`-Einträge zu IDs aus 1.0.0 bleiben gültig
  (alle alten IDs sind erhalten).
- Beim Update läuft der normale Cache-Invalidierungs-Flow:
  Versions-Mismatch → Lektion neu laden, IDs werden upgesertet.

## [1.0.0] – 2026-05-16

### Added — Schema
- `schemaVersion: 1.0.0` mit Manifest- und Lektions-Format.
- Drei Item-Typen: `word`, `phrase`, `sentence` mit zugehörigen Stages.
- Schwierigkeitsstufen 1–5 als Pflichtfeld pro Item.
- Optionales `requires`-Feld für Voraussetzungs-IDs (z.B. Sätze auf
  vorher gelernten Wörtern).
- Optionales `license`-Feld für Drittquellen-Attribution.

### Added — Manifest
- Initiales `v1/manifest.json` mit Index von 8 Lektionen:
  greetings, introduction, numbers-time, family, shopping, restaurant,
  traffic, tourism.
- `globalLicenses` mit Tatoeba (CC-BY 2.0) und eigenkurierten
  Inhalten (CC-BY 4.0).

### Added — Lektionen
- `greetings.json` (v1.0.0): 12 Wörter, 6 Phrasen, 6 Sätze.
- `introduction.json` (v1.0.0): 20 Wörter, 8 Phrasen, 7 Sätze.
- `numbers-time.json` (v1.0.0): 45 Wörter, 8 Phrasen, 7 Sätze.
- `family.json` (v1.0.0): 20 Wörter, 4 Phrasen, 6 Sätze.
- `shopping.json` (v1.0.0): 25 Wörter, 10 Phrasen, 10 Sätze.
- `restaurant.json` (v1.0.0): 28 Wörter, 12 Phrasen, 10 Sätze.
- `traffic.json` (v1.0.0): 22 Wörter, 8 Phrasen, 10 Sätze.
- `tourism.json` (v1.0.0): 30 Wörter, 12 Phrasen, 13 Sätze.

### Added — Dokumentation
- `README.md` mit Einbindungs-Anleitung für App-Entwickler.
- `SCHEMA.md` mit vollständiger Feld-Dokumentation und Validierungs-Checkliste.
- `LICENSE` (CC-BY 4.0) für eigenkurierte Inhalte.
- `licenses/attribution.json` (initial leer, gefüllt bei Tatoeba-Imports).
