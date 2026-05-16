# Schema-Dokumentation: vocabularies-kroatic-data

Verbindliche Spezifikation des Datenformats für Contributor und für die
App-Implementierung. Aktuelle Version: `schemaVersion: 1.0.0`.

---

## 1. Repo-Struktur

```
v1/
├── manifest.json
└── lessons/
    ├── <lessonId>.json
    └── ...
licenses/
└── attribution.json
```

Der Top-Level-Pfad `v1/` ist Teil der Schema-Version: ein Breaking-Change
würde unter `v2/` parallel verfügbar gemacht, damit Alt-Clients
weiterarbeiten können.

---

## 2. `manifest.json`

### 2.1 Felder

| Feld | Typ | Pflicht | Beschreibung |
|---|---|:-:|---|
| `schemaVersion` | string (semver) | ✓ | Aktuell `"1.0.0"` |
| `dataVersion` | string (ISO-Datum) | ✓ | Datum der letzten Inhalts-Änderung |
| `generatedAt` | string (ISO-Datetime) | ✓ | Zeitstempel der Manifest-Generierung |
| `baseUrl` | string (URL) | ✓ | Absoluter Basis-Pfad für Lektions-Files |
| `languages.source` | string (BCP-47) | ✓ | `"de-DE"` |
| `languages.target` | string (BCP-47) | ✓ | `"hr-HR"` |
| `lessons` | array | ✓ | Lektions-Einträge (siehe 2.2) |
| `globalLicenses` | array | ✓ | Referenzen für `license.sourceId` (siehe 2.3) |

### 2.2 Lektions-Eintrag

| Feld | Typ | Pflicht | Beschreibung |
|---|---|:-:|---|
| `id` | string | ✓ | Eindeutige Lektions-ID (kebab-case) |
| `version` | string (semver) | ✓ | Lektions-Inhalts-Version |
| `title.de` | string | ✓ | Lektionstitel auf Deutsch |
| `title.hr` | string | ✓ | Lektionstitel auf Kroatisch |
| `description.de` | string | – | Lektions-Beschreibung |
| `order` | integer | ✓ | Reihenfolge im Lesson Browser |
| `difficulty` | 1–5 | ✓ | Aggregierte Lektions-Schwierigkeit |
| `wordCount` | integer | ✓ | Anzahl Items mit `type: word` |
| `phraseCount` | integer | ✓ | Anzahl Items mit `type: phrase` |
| `sentenceCount` | integer | ✓ | Anzahl Items mit `type: sentence` |
| `prerequisites` | string[] | ✓ | IDs vorher abzuschließender Lektionen |
| `tags` | string[] | ✓ | Filter-Tags |
| `file` | string | ✓ | Pfad relativ zu `baseUrl` |
| `sha256` | string | ✓ | SHA-256-Hash der Lektionsdatei (Integritätsprüfung) |
| `sizeBytes` | integer | ✓ | Dateigröße in Bytes |

### 2.3 `globalLicenses`-Eintrag

| Feld | Typ | Pflicht | Beschreibung |
|---|---|:-:|---|
| `id` | string | ✓ | Referenz-ID (z.B. `tatoeba-cc-by-2.0`) |
| `name` | string | ✓ | Anzeigename der Quelle |
| `url` | string | ✓ | URL der Quelle |
| `license` | string | ✓ | Lizenz-Kurzname (z.B. `CC-BY 2.0`) |
| `licenseUrl` | string | ✓ | URL des Lizenztextes |

---

## 3. Lektionsdatei `lessons/<lessonId>.json`

### 3.1 Top-Level-Felder

| Feld | Typ | Pflicht | Beschreibung |
|---|---|:-:|---|
| `schemaVersion` | string | ✓ | Muss zum Manifest passen |
| `lessonId` | string | ✓ | Muss dem Manifest-Eintrag entsprechen |
| `version` | string (semver) | ✓ | Muss zum Manifest-Eintrag passen |
| `title.de` / `title.hr` | string | ✓ | Wie im Manifest |
| `description.de` | string | – | Optionale Lang-Beschreibung |
| `stages` | array | ✓ | Definition der Lern-Stufen (siehe 3.2) |
| `items` | array | ✓ | Lerneinheiten (siehe 3.3) |

### 3.2 `stages`-Eintrag

| Feld | Typ | Pflicht | Beschreibung |
|---|---|:-:|---|
| `id` | string | ✓ | `"words"` \| `"phrases"` \| `"sentences"` |
| `type` | string | ✓ | `"vocabulary"` \| `"phrase"` \| `"sentence"` |
| `label.de` | string | ✓ | UI-Label auf Deutsch |

### 3.3 `items`-Eintrag (Lerneinheit)

| Feld | Typ | Pflicht | Beschreibung |
|---|---|:-:|---|
| `id` | string | ✓ | `<prefix>_<3digit>` — eindeutig pro Lektion |
| `type` | string | ✓ | `"word"` \| `"phrase"` \| `"sentence"` |
| `stage` | string | ✓ | matcht `stages[].id` |
| `difficulty` | 1–5 | ✓ | Schwierigkeitsstufe (siehe §4) |
| `de.text` | string | ✓ | Deutsche Form |
| `de.ipa` | string | – | IPA-Transkription Deutsch (für Bewertung optional) |
| `de.pos` | string | – | Wortart (z.B. `noun`, `verb`, `interjection`) |
| `hr.text` | string | ✓ | Kroatische Form |
| `hr.ipa` | string | – | IPA-Transkription Kroatisch |
| `hr.pos` | string | – | Wortart |
| `hr.audioHint` | string | – | Pfad zu nativer Aufnahme unter `v1/audio/hr/` |
| `alternatives.hr` | string[] | – | Akzeptierte HR-Synonyme bei Eingabe-/STT-Prüfung |
| `alternatives.de` | string[] | – | Akzeptierte DE-Synonyme |
| `tags` | string[] | – | Frei wählbare Tags (z.B. `formal`, `informal`) |
| `notes.de` | string | – | Lern-Hinweise auf Deutsch |
| `requires` | string[] | – | IDs, die vorher gelernt sein müssen (transitive Auflösung) |
| `wordRefs` | string[] | – | Bei `type: sentence`: enthaltene Wort-IDs für Detail-Pages |
| `license` | object \| null | ✓ | Lizenz-Block bei Drittquellen; `null` = eigenkuriert |

### 3.4 `license`-Block

| Feld | Typ | Pflicht | Beschreibung |
|---|---|:-:|---|
| `sourceId` | string | ✓ | Muss in `manifest.globalLicenses[].id` existieren |
| `sentenceIdDe` | integer | – | Tatoeba-ID des deutschen Satzes |
| `sentenceIdHr` | integer | – | Tatoeba-ID des kroatischen Satzes |
| `contributors` | string[] | – | Tatoeba-User-Namen |

---

## 4. Schwierigkeitsstufen (`difficulty` 1–5)

| Stufe | Definition | Beispiel |
|:-:|---|---|
| **1** | Für einen Anfänger nach 5 Minuten Lernen reproduzierbar. Einsilbig oder sehr kurz. | „Bok", „Da", „Ne", „jedan" |
| **2** | Erweiterte Basis — mehrsilbig, aber lautlich klar. | „Dobrodošli", „Hvala lijepo" |
| **3** | Alltagstauglich. Kurze Verbformen im Präsens, einfache Aussagesätze. | „Koliko košta?", „Imam dva brata." |
| **4** | Aufbau. Längere Sätze, Konjugationen, Fragesätze mit Modalverb. | „Imate li slobodnu sobu?" |
| **5** | Fortgeschritten. Konjunktiv, idiomatische Wendungen, komplexe Syntax. | „Htio bih kartu za trajekt za Hvar." |

**Hinweis für Contributor:** Stufe wird vor allem aus *phonetischer*
und *grammatischer* Komplexität abgeleitet, nicht aus inhaltlicher
Geläufigkeit. Ein häufig gebrauchter Satz mit komplexer Konjugation ist
trotzdem Stufe 4.

---

## 5. Typ-Trennung (`type`)

| `type` | Wann verwenden? | Stage |
|---|---|---|
| `word` | Einzelne Vokabel, ein lexikalisches Item (Substantiv, Verb-Infinitiv, Interjektion, Partikel) | `words` |
| `phrase` | Feste Wortgruppe ohne vollständigen Satzbau („Guten Morgen", „Vielen Dank") | `phrases` |
| `sentence` | Vollständiger Satz mit Subjekt + Prädikat, terminiert mit `?` oder `.` | `sentences` |

**Faustregel:**
- Ein Satz hat ein konjugiertes Verb. → `sentence`
- Eine feste Floskel ohne konjugiertes Verb. → `phrase`
- Sonst → `word`

---

## 6. ID-Konventionen

```
<lessonPrefix>_<3-digit-block>
```

Pro Lektion gibt es **3 ID-Blöcke**:

| Block | ID-Bereich | Für |
|---|---|---|
| Wörter | `001`–`099` | `type: word` |
| Phrasen | `100`–`199` | `type: phrase` |
| Sätze | `200`+ | `type: sentence` |

Lektion-Präfixe:

| Lektion | Präfix |
|---|---|
| greetings | `greet` |
| introduction | `intro` |
| numbers-time | `num` |
| family | `fam` |
| shopping | `shop` |
| restaurant | `rest` |
| traffic | `traf` |
| tourism | `tour` |

**Regel:** IDs sind unveränderlich. Wird ein Item gelöscht, bleibt die ID
„verbrannt" und wird nie neu vergeben. Der App-Client ignoriert Progress-Einträge
zu unbekannten IDs.

---

## 7. `requires`-Regeln

`requires` listet IDs, die vor diesem Item gelernt sein müssen. Beispiel:
Der Satz „Wie geht es dir?" (`greet_201`) hat `requires: ["greet_001"]`,
weil er „Bok" enthält.

- Auflösung ist **transitiv**: `requires: [A]` wenn A wiederum
  `requires: [B]` hat, wird B implizit vorausgesetzt.
- Zyklen sind verboten — Validierungs-Skript prüft das.
- IDs in `requires` müssen in **derselben Lektion** existieren oder einer
  Lektion aus `prerequisites` angehören.

---

## 8. IPA-Konvention

- Verwendet wird die **IPA-Notation des Kroatischen** nach der Wikipedia-Tabelle
  „Hilfe:IPA/Kroatisch".
- Diakritika **bleiben erhalten** (č, ć, š, ž, đ) — sie sind phonetisch
  unterscheidend und werden von der App-Aussprachebewertung berücksichtigt.
- IPA ist **optional**; fehlende Werte werden im UI ausgeblendet.

---

## 9. Validierungs-Checkliste vor Commit / PR

```bash
# 1. JSON-Syntax
jq empty v1/manifest.json
for f in v1/lessons/*.json; do jq empty "$f"; done

# 2. Alle im Manifest gelisteten Lektionen existieren
jq -r '.lessons[].file' v1/manifest.json | \
  while read f; do test -f "v1/$f" || echo "MISSING: $f"; done

# 3. Eindeutige IDs pro Lektion
for f in v1/lessons/*.json; do
  duplicates=$(jq -r '.items[].id' "$f" | sort | uniq -d)
  [ -z "$duplicates" ] || echo "DUPLICATE IDs in $f: $duplicates"
done

# 4. type/stage-Konsistenz
jq -r '.items[] | "\(.type)|\(.stage)"' v1/lessons/greetings.json | sort -u
# Erwartung: word|words, phrase|phrases, sentence|sentences

# 5. difficulty im Bereich 1–5
for f in v1/lessons/*.json; do
  jq -r '.items[].difficulty' "$f" | \
    awk '$0<1 || $0>5 || $0!~/^[1-5]$/ {print FILENAME": invalid difficulty "$0}'
done

# 6. license-Block: wenn nicht null, muss sourceId existieren
jq -r '.items[] | select(.license != null) | .license.sourceId' v1/lessons/*.json | sort -u
# Vergleiche manuell mit manifest.globalLicenses[].id

# 7. wordCount/phraseCount/sentenceCount im Manifest stimmt mit Items überein
for lesson in $(jq -r '.lessons[].id' v1/manifest.json); do
  f="v1/lessons/${lesson}.json"
  w=$(jq '[.items[]|select(.type=="word")]|length' "$f")
  p=$(jq '[.items[]|select(.type=="phrase")]|length' "$f")
  s=$(jq '[.items[]|select(.type=="sentence")]|length' "$f")
  manifest_w=$(jq -r ".lessons[]|select(.id==\"$lesson\")|.wordCount" v1/manifest.json)
  manifest_p=$(jq -r ".lessons[]|select(.id==\"$lesson\")|.phraseCount" v1/manifest.json)
  manifest_s=$(jq -r ".lessons[]|select(.id==\"$lesson\")|.sentenceCount" v1/manifest.json)
  [ "$w" = "$manifest_w" ] && [ "$p" = "$manifest_p" ] && [ "$s" = "$manifest_s" ] \
    || echo "COUNT MISMATCH in $lesson: items($w/$p/$s) vs manifest($manifest_w/$manifest_p/$manifest_s)"
done
```

Ein zukünftiger CI-Workflow `validate-data.yml` führt diese Checks
automatisch auf jedem PR aus.
