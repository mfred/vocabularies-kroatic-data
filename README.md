# vocabularies-kroatic-data

Daten-Repository für den **Vokabeltrainer Deutsch ↔ Kroatisch**
([App-Repo: vocabularies-kroatic](https://github.com/<owner>/vocabularies-kroatic)).

Enthält die thematischen Lektionen als versionierte JSON-Dateien.
Die App lädt diese Inhalte zur Laufzeit, sodass neue Vokabeln **ohne
App-Update** ausgerollt werden können.

## Struktur

```
v1/
├── manifest.json              ← Index aller Lektionen mit Versionen & SHA256
└── lessons/
    ├── greetings.json         ← Begrüßung (difficulty 1–2)
    ├── introduction.json      ← Sich vorstellen (difficulty 1–3)
    ├── numbers-time.json      ← Zahlen & Uhrzeit (difficulty 1–3)
    ├── family.json            ← Familie (difficulty 2–3)
    ├── shopping.json          ← Einkaufen (difficulty 2–4)
    ├── restaurant.json        ← Restaurant (difficulty 2–4)
    ├── traffic.json           ← Verkehr & Wegbeschreibung (difficulty 3–4)
    └── tourism.json           ← Tourismus (difficulty 3–5)
licenses/
└── attribution.json           ← Aggregierte CC-BY-Attributionen (Tatoeba)
SCHEMA.md                      ← Vollständige Feld-Dokumentation
LICENSE                        ← CC-BY 4.0 für eigenkurierte Inhalte
CHANGELOG.md                   ← Datenänderungen pro Version
```

## Einbindung in die App

Die App ruft beim Start ab:

```
https://raw.githubusercontent.com/<owner>/vocabularies-kroatic-data/main/v1/manifest.json
```

und folgt von dort auf die einzelnen Lektionsdateien. Versionierung
funktioniert pro Lektion — nur geänderte Lektionen werden neu geladen.

Details: siehe `SCHEMA.md` und die App-Dokumentation
[PROJECT.md §4 (Externes Datenschema)](https://github.com/<owner>/vocabularies-kroatic/blob/main/PROJECT.md).

## Datenmodell

Jedes Item trägt:

- **`type`** — `word` | `phrase` | `sentence`
- **`stage`** — `words` | `phrases` | `sentences` (Progressions-Stufe)
- **`difficulty`** — 1 (sehr leicht) bis 5 (fortgeschritten)

Damit kann die App:
- Wörter und Sätze visuell trennen
- Schwierigkeit beim Spaced-Repetition-Algorithmus berücksichtigen
- Sätze erst freischalten, wenn die zugehörigen Wörter gelernt sind
  (`requires`-Feld)

## Beitragen

Schritte zum Hinzufügen einer neuen Vokabel:

1. Datei `v1/lessons/<lesson>.json` öffnen
2. Neues Item mit nächster freier ID anhängen (siehe ID-Bereich in `SCHEMA.md`)
3. `version` der Lektion bumpen (PATCH bei Hinzufügen)
4. `wordCount` / `phraseCount` / `sentenceCount` im `manifest.json` updaten
5. `dataVersion` im `manifest.json` auf heutiges Datum setzen
6. PR öffnen — Validierungs-Workflow prüft Schema-Konformität

**Regel:** IDs sind unveränderlich. Gelöschte IDs werden nicht recycled.

## Lizenzen

| Quelle | Lizenz | Wirkung |
|---|---|---|
| Eigenkuriete Items (`license: null`) | **CC-BY 4.0** | Repo-Lizenz aus `LICENSE` |
| Tatoeba-Items (`license.sourceId: "tatoeba-cc-by-2.0"`) | **CC-BY 2.0** | Attribution-Block im Item |

Vollständige Attribution-Liste: `licenses/attribution.json`.

## Status

Version `1.1.0` — alle 8 Lektionen voll ausgebaut auf ca. 100 Items je
Lektion (insgesamt **805 Items**: 538 Wörter, 144 Phrasen, 123 Sätze).
Schwierigkeitsspanne pro Lektion deckt 4–5 Stufen ab (1–5).
