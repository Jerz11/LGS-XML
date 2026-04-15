# Changelog

Všechny významné změny v projektu LGS XML jsou zdokumentovány v tomto souboru.

Formát vychází z [Keep a Changelog](https://keepachangelog.com/cs/1.1.0/) a verze dodržuje [Semantic Versioning](https://semver.org/lang/cs/).

---

## [2.0.2] — 2026-04-15

### Fixed
- **Bar & Grill (B&G)** — opraveno zaúčtování pokladních dokladů. Dříve šly na pokladnu Molo Restaurant (`cashAccount_ids: "MOLO"`) místo správné pokladny Bar & Grill.
  - `outlets["B&G"].cashAccount_ids`: `"MOLO"` → `"BaG"`
  - `number_series.voucher_prefix_by_outlet["B&G"]`: `"R{YY}P"` → `"{YY}GP"` (pro 2026 → `26GP`)
  - Účetní potvrdila end-to-end importem do Pohody.

### Changed
- `config_version`: `2.2` → `2.3` (kvůli změně DEFAULT_CONFIG se uživatelům automaticky přepíše cached config při prvním spuštění).

### Documentation
- Nový lesson learned 9.9 (DEVELOPER.md) — pozor na copy-paste mezi outlety v configu.
- Aktualizovaný checklist pro přidání nového outletu (10.1) — 5 povinných identifikátorů.
- Aktualizovaný popis B&G v sekci "Podporované provozy".

---

## [2.0.1] — 2026-02

### Fixed
- `<typ:numberRequested>` → `<typ:ids>` ve všech XML výstupech. Dřívější chování způsobovalo duplikáty v Pohodě při importu více souborů ("Doklad se zadaným číslem již existuje"). Nyní apka posílá jen prefix řady a Pohoda sama přiděluje sekvenční čísla.

### Added
- Automatická migrace cached configu pomocí `config_version` — při změně DEFAULT_CONFIG v novém buildu se klientův config v AppData automaticky přepíše na novou verzi.

### Changed
- Opravený voucher prefix pro Bistro (`BisP0070` → `BisP`).

---

## [2.0.0] — 2026-01

### Changed
- Migrace na rok 2026:
  - Nové symbolické předkontace (`Beverage` / `FOOD` / `SCH` místo numerických účtů v items).
  - Středisko změněno na symbolické `MOLO GASTR`.
  - Přidán element `<activity>` a `<calculateVAT>`.
  - Nový formát poznámky v `<dat:dataPack note="…">`.
  - Šablony `{YY}` v prefixech číselných řad (místo hard-kódovaných let).
  - Přidán rok selector v UI (ošetření přelomu roku — leden zpracovává data z prosince).

### Added
- Podpora platební metody **Cashless** (vedle Card a Voucher).

---

## [1.0.1] — 2025

### Added
- Původní release předaný účtárně Lipno Gastro Services (LGS).
- Číselné řady per-outlet: `BisP`, `MOLP`, `CdLP`, `BaGP`.
- Numerické účty v items, numerické centre.
- `<typ:ids>` pro číslování dokladů.

---

## Versioning policy

- **MAJOR** (`1.x → 2.x`): Změna konceptu/formátu configu, nekompatibilní s předchozí strukturou.
- **MINOR** (`2.0.x → 2.1.x`): Nové funkce zpětně kompatibilní (např. nová platební metoda, nový outlet).
- **PATCH** (`2.0.1 → 2.0.2`): Oprava chyby bez funkční změny z pohledu uživatele.

Při každé změně `DEFAULT_CONFIG` se musí bumpnout `config_version` v `main.py` a v `config.json` / `config_distribution.json`, jinak migrace v AppData neproběhne.
