# LGS XML — Vývojářská dokumentace

> Kompletní průvodce aplikací pro budoucí vývojáře. Tato dokumentace popisuje, jak aplikace funguje, jak je strukturovaná, jak ji upravovat a jakých chyb se vyvarovat.

---

## 1. Co aplikace dělá

**LGS XML** je desktopová Windows aplikace, která transformuje Excel exporty tržeb ze systému **Storyous** (POS) na XML soubory kompatibilní s účetním systémem **Pohoda** (Stormware).

### Vstup
- Excel soubor (`.xlsx`) z měsíčního exportu Storyous obsahující denní tržby po dnech, rozdělené podle platebních metod (hotově, kartou, voucherem, cashless) a sazeb DPH (21%, 12%, 0%).

### Výstup
Pro každý vybraný den apka generuje až 4 XML soubory:

| Typ dokladu | Pohoda agenda | Filename prefix | Podmínka |
|---|---|---|---|
| Pokladna (voucher) | Pokladna (příjem) | `Pokladna` | Hotovostní tržby > 0 |
| Ostatní pohledávky (invoice) — kartou | Ostatní pohledávky | `OstatniPohledavky ... kartou` | Kartové tržby > 0 |
| Ostatní pohledávky (invoice) — voucherem | Ostatní pohledávky | `OstatniPohledavky ... voucherem` | Voucher tržby > 0 |
| Ostatní pohledávky (invoice) — cashless | Ostatní pohledávky | `OstatniPohledavky ... cashless` | Cashless tržby > 0 |

Výstupní soubory se ukládají do `~/Documents/Pohoda XML/` (lze změnit v UI).

### Podporované provozy
- **Bistro** — středisko `MOLO GASTR`, activity `10207`, pokladna `Bistro`, řada `B{YY}P`
- **Restaurant** — středisko `MOLO GASTR`, activity `10205`, pokladna `MOLO`, řada `R{YY}P`
- **CDL** (Café du Lac) — středisko `MOLO GASTR`, activity `10208`, pokladna `CdL`, řada `C{YY}P`
- **B&G** (Bar & Grill) — středisko `MOLO GASTR`, activity `10206`, pokladna `BaG` (vlastní), řada `{YY}GP` (vlastní)
- **Molo2** (Molo 2 Stánek) — středisko `MOLO GASTR`, activity `10205`, pokladna `MOLO`, řada `R{YY}P` (sdílí s Restaurant)

Invoice (Ostatní pohledávky) — všechny provozy sdílí číselnou řadu `{YY}OP`.

---

## 2. Tech stack

- **Jazyk**: Python 3.11
- **GUI**: PySide6 (Qt 6)
- **Excel**: pandas + openpyxl
- **XML**: lxml
- **Packaging**: PyInstaller (`--onedir --windowed`)
- **Target OS**: Windows 10/11 (offline)

### Závislosti
Viz `requirements.txt`:
```
PySide6
pandas
openpyxl
lxml
```

Pro vývoj navíc: `pyinstaller`

---

## 3. Struktura repozitáře

```
LGS-XML/
├── main.py                      # Veškerá logika aplikace (~1650 řádků, single-file)
├── config.json                  # Výchozí konfigurace (distribuovaná s .exe)
├── config_distribution.json     # Kopie config.json pro distribuci (mirror)
├── requirements.txt             # Python závislosti
├── build.py                     # Wrapper pro PyInstaller build
├── build_installer.py           # (volitelné) Inno Setup installer build
├── installer_script.iss         # Inno Setup script
├── PRD.md                       # Původní product requirements document
├── pohoda_xml_ordered_schema.md # Dokumentace Pohoda XML schématu
├── README.md                    # Uživatelská dokumentace
├── README_distribution.md       # Pokyny pro distribuci
└── DEVELOPER.md                 # Tento soubor
```

Single-file architektura (`main.py`) je záměrná — zjednodušuje deployment a údržbu. Aplikace je malá (~1650 řádků), takže rozdělení do modulů nepřináší benefit.

---

## 4. Architektura `main.py`

Aplikace je rozdělená do logických sekcí v jednom souboru. Hlavní komponenty:

### 4.1 Konstanty a stylesheet (~ř. 40–360)
- `APP_NAME`, `APP_VERSION` — zobrazované v titulbaru a .exe názvu
- `COLORS` — paleta barev pro Qt stylesheet
- `get_professional_stylesheet()` — Qt CSS-like stylesheet (pozor: při dark mode musí všechny widgety mít explicitní `color` atribut, jinak budou neviditelné)

### 4.2 DEFAULT_CONFIG (~ř. 385–620)
Fallback konfigurace v kódu. Používá se, když neexistuje žádný cached config v AppData. **Musí být zrcadlem `config.json`.**

### 4.3 Cesty a pomocné funkce (~ř. 620–730)
- `APP_DATA_DIR` = `~/AppData/Local/MoloXML/` — **cache config a logy**
- `CONFIG_PATH` = `APP_DATA_DIR/Config/config.json` — runtime config
- `OUTPUT_DIR` = `~/Documents/Pohoda XML/` — výstupní XML
- `ensure_dirs()`, `load_config()`, `save_config()`, `write_log()`, `log_path_today()`

### 4.4 `ExcelAdapter` (~ř. 750–870)
Čte Excel, mapuje sloupce přes regex patterns v `header_map`, vrací částky pro každý den a platební metodu.

Klíčové metody:
- `_pick_sheet()` — najde sheet "Přehled tržeb" v Excelu
- `_section_values()` — namapuje sloupce Excelu přes regex na base/vat/gross pro každou sazbu DPH
- `read_day(path, target_day)` — vrátí `{"cash": {...}, "card": {...}, "voucher": {...}, "cashless": {...}}` pro daný den
- `detect_month_year_from_excel()` — detekuje měsíc/rok z dat
- `available_days()` — seznam dnů dostupných v Excelu

### 4.5 XML generátory (~ř. 880–1170)
- `E(tag, text, ns, attrib, nsmap)` — helper pro tvorbu XML elementů s namespace
- `_fmt(n)` — formátování čísel (celé vs. 2 desetinná místa)
- `add_sum_home_currency()` — společný helper pro summary element
- `build_invoice(method, amounts, day, outlet_cfg)` — faktura (Ostatní pohledávky) pro card/voucher/cashless
- `build_voucher(amounts, day, outlet_cfg, outlet_name)` — pokladní doklad pro hotovost

### 4.6 Datapack wrapper (~ř. 1170–1220)
- `datapack_with(child, day, outlet, doc_type, note_override)` — obalí invoice/voucher do `<dat:dataPack>` s correct metadata
- `_compute_datapack_key()` — deterministický UUID v5 jako idempotent key

### 4.7 UI (~ř. 1300–1700)
- `DropFrame` — drag & drop zone pro Excel
- `DayPicker` — checkboxy pro výběr dnů
- `MainWindow` — hlavní okno s:
  - Výběr provozu (ComboBox)
  - Rok selector (QSpinBox, range `current_year ± 1`)
  - Drop zone / Vybrat soubor
  - Day picker
  - Output directory
  - Generate + Open folder
  - Status log

### 4.8 `main()` entry point (~ř. 1710+)
Vytvoří QApplication, MainWindow, spustí event loop.

---

## 5. Konfigurační systém

### 5.1 Dva konfigurační soubory, tři vrstvy

Apka používá **dvouvrstvou** konfiguraci:

1. **`DEFAULT_CONFIG`** (v `main.py`)
   - Fallback v kódu, distribuovaný uvnitř .exe
   - Používá se, když žádný external config neexistuje

2. **`config.json`** vedle .exe
   - Šablona distribuovaná se .exe
   - Referenční config
   - Nikdy se runtime nepoužívá přímo — jen jako fallback content pro první spuštění

3. **`~/AppData/Local/MoloXML/Config/config.json`** (runtime cache)
   - **Toto je jediný config, který apka za běhu čte.**
   - Při prvním spuštění se vytvoří kopií `DEFAULT_CONFIG`.
   - Uživatel ho může upravit (např. přidat nový outlet, změnit texty) a apka změny uvidí.

### 5.2 Proč dvě vrstvy?

Důvod: Aplikace běží v režimu, kde uživatel může mít vlastní konfigurační úpravy (texty faktur, účty), které chceme zachovat. Jenže když my (vývojáři) vydáme novou verzi, potřebujeme ty změny distribuovat — a uživatelův starý cache by je jinak přepsal.

### 5.3 Config migrace — jak to funguje

V `DEFAULT_CONFIG` máme klíč `"config_version"` (string jako `"2.2"`). Při každém `load_config()`:

```python
if cached_config.get("config_version") != DEFAULT_CONFIG.get("config_version"):
    # přepíše cached config novým DEFAULT_CONFIG
    CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, ...))
    return DEFAULT_CONFIG
```

**DŮLEŽITÉ PRAVIDLO pro vývojáře:**
> Kdykoliv měníte `DEFAULT_CONFIG` (nebo `config.json`), **MUSÍTE bumpnout `config_version`** (např. z `"2.2"` na `"2.3"`). Jinak uživatelé budou stále vidět starý cached config a vaše změny se neprojeví.

### 5.4 Struktura configu

```json
{
  "version": "1.0",
  "config_version": "2.2",
  "ico": "17126240",
  "programVersion": "14203.8 SQL (28.1.2026)",
  "application": "Transformace",
  "timezone": "Europe/Prague",
  "datapack_key": "...",                   // fixed UUID (volitelné)

  "note_text_by_outlet": {                 // Texty pro <dat:note>
    "Bistro": "bistro", "Restaurant": "res", ...
  },

  "number_series": {                       // Šablony pro číselné řady
    "voucher_prefix_by_outlet": {
      "Bistro": "B{YY}P", ...              // {YY} nahrazeno dvouciferným rokem
    },
    "invoice_prefix": "{YY}OP"
  },

  "header_map": {                          // Regexy pro čtení Excelu
    "date_col_candidates": [...],
    "sections": {
      "cash": { "base_high": "^Základ 21% \\(Hotově\\)$", ... },
      ...
    }
  },

  "company_identity": { ... },             // Údaje firmy pro <myIdentity>
  "naming": { ... },                       // Šablony filename
  "global_rules": { ... },                 // Encoding, rounding
  "payment_ids": { ... },                  // card/voucher/cashless identifikátory
  "liquidation_rules": { ... },            // same_day / next_business_day

  "outlets": {
    "Bistro": {
      "centre": "MOLO GASTR",              // Středisko v Pohodě
      "activity_id": "10207",              // Činnost v Pohodě
      "cashAccount_ids": "Bistro",         // Pokladna v Pohodě
      "voucher_header_text": "...",        // Text na pokladním dokladu
      "invoice_header_texts": {
        "card": "Tržby card Bistro",       // Text na faktuře dle platby
        "voucher": "...",
        "cashless": "..."
      },
      "accounts": {
        "inv_header": "315000/602116",     // MD/DAL v hlavičce faktury
        "inv": { "high": "Beverage", ... },// Předkontace položek
        "vch_header": "211000/602116",     // MD/DAL v hlavičce pokladny
        "vch": { "high": "Beverage", ... }
      },
      "item_texts": {                      // Texty řádků (hotove/kartou/...)
        "cash": { "high": "21% Beverage - hotově", ... },
        ...
      }
    },
    ...
  }
}
```

---

## 6. Pohoda XML — klíčové koncepty

### 6.1 Struktura dokladu

Pohoda XML má tři agendy, které apka používá:

- `<vch:voucher>` → **Pokladní doklad** (hotovost)
- `<inv:invoice>` (typ `receivable`) → **Ostatní pohledávky** (karta, voucher, cashless)

Každý doklad je obalen v `<dat:dataPack>` → `<dat:dataPackItem>`.

### 6.2 Namespace prefixy

```
dat: http://www.stormware.cz/schema/version_2/data.xsd
inv: http://www.stormware.cz/schema/version_2/invoice.xsd
vch: http://www.stormware.cz/schema/version_2/voucher.xsd
typ: http://www.stormware.cz/schema/version_2/type.xsd
```

### 6.3 Pořadí elementů — POZOR!

Pohoda je **striktní na pořadí elementů** v XML. Pokud pořadí nesedí s XSD schématem, import selže s obecnou chybou. Referenční pořadí je v souborech `.tmp/New/*.xml` (poslané účetní) a v `pohoda_xml_ordered_schema.md`.

Pokud přidáváte nový element (např. `<inv:activity>`), **musíte ho umístit na správné místo** podle schématu. V současné implementaci:
- `<inv:activity>` jde **mezi `centre` a `liquidation`**
- `<vch:activity>` jde **mezi `centre` a `lock2`**
- `<vch:calculateVAT>` jde **mezi `roundingVAT` a `typeCalculateVATInclusivePrice`**

### 6.4 Číslování dokladů — `<typ:ids>` vs `<typ:numberRequested>`

**KRITICKÝ ROZDÍL:**

- `<vch:number><typ:ids>R26P</typ:ids></vch:number>` → Pohoda **automaticky přidělí** další sekvenční číslo z řady `R26P` (např. `R26P0091`).
- `<vch:number><typ:numberRequested>R26P</typ:numberRequested></vch:number>` → Pohoda použije **přesně "R26P"** jako číslo dokladu. Druhý import stejného → duplikát.

**Aplikace používá `<typ:ids>` s prefixem řady.** Nikdy neposíláme `numberRequested`. Pohoda si sama přidělí sekvenční čísla. Tím je vyřešena synchronizace sekvencí mezi apkou a Pohodou — my je nedržíme.

### 6.5 Předkontace — symbolické jméno vs. účet

V item accounting apka posílá **symbolický název**, ne číslo účtu:

```xml
<inv:accounting>
  <typ:ids>Beverage</typ:ids>    <!-- ne 315000/602823 -->
</inv:accounting>
```

Pohoda má interní mapování `Beverage` → `315000/602823`, `FOOD` → `.../602822`, `SCH`/`SCh` → `.../602821`. Toto mapování udržuje účetní v Pohodě, apka o něm neví.

Poznámka: V item accounting vouchers se používá `SCh` (lowercase h), v invoice `SCH` (uppercase). Takto je to v referenčních XML od účetní — nevíme proč, ale je to schválně.

### 6.6 Header accounting

V **hlavičce** dokladu apka posílá **numerický účet** (např. `315000/602116` pro Bistro), ne symbolický název. Tohle je jiné oproti items. Je to proto, že header účet je per-outlet specifický (odlišuje provoz), zatímco item účty sdílí všechny provozy (přes symbolické názvy).

### 6.7 Centre a activity

- `<inv:centre><typ:ids>MOLO GASTR</typ:ids></inv:centre>` — všechny provozy LGS mají stejné středisko
- `<inv:activity><typ:ids>10207</typ:ids></inv:activity>` — **činnost** rozlišuje provozy místo čísel účtů (nová koncepce 2026)

### 6.8 Note format (v `<dat:dataPack note="...">`)

- **Faktura**: `"Uživatelský export, Zd.plnění = DD/MM/YYYY, Text = {outlet_note}"`
- **Pokladna**: `"Uživatelský export, Datum = {měsíc_cz}, Datum = DD/MM/YYYY, Text = {outlet_note}"`

Kde `měsíc_cz` je český název měsíce (leden, únor, …, prosinec) — viz `CZ_MONTHS` v main.py.

---

## 7. Detekce roku — KRITICKÝ EDGE CASE

### 7.1 Jak funguje detekce

Rok se určuje ve dvou krocích:

1. **Z názvu souboru** — regex `(\d{1,2})_(\d{4})` hledá pattern `M_YYYY` (např. `bistro_12_2026.xlsx`)
2. **Z dat v Excelu** — Excel obsahuje datumy ve formátu `D.M.` (bez roku). Kód použije `datetime.now().year` jako fallback.

### 7.2 Problém: přelom roku

Pokud uživatel v lednu 2027 zpracovává data z prosince 2026:

- Soubor `bistro_12_2026.xlsx` → OK (rok z názvu)
- Soubor `bistro.xlsx` (bez roku v názvu) → ŠPATNĚ: `datetime.now().year == 2027`, rok se detekuje jako 2027, číselné řady budou `27OP` místo `26OP`.

### 7.3 Řešení: Rok selector v UI

Apka má `QSpinBox` pro rok v pravém horním rohu (range `current_year ± 1`). Při načtení Excelu se auto-nastaví z detekovaného roku, ale uživatel ho může **ručně přepsat**.

Pravidlo: **Generate() čte rok ze spinneru, ne z `self.month_year`.** Spinner má přednost.

### 7.4 Doporučení pro dokumentaci účtárny

Do uživatelské dokumentace je **nutné uvést**:
- Preferované pojmenování souborů: `{nazev}_{M}_{YYYY}.xlsx`
- Kolem přelomu roku **vždy vizuálně zkontrolovat rok v UI** před generováním

---

## 8. Build a distribuce

### 8.1 Vývojové prostředí

```bash
pip install PySide6 pandas openpyxl lxml pyinstaller
python main.py  # spuštění v dev módu
```

### 8.2 Build .exe

```bash
pyinstaller --noconfirm --onedir --windowed --name "LGS XML vX.Y.Z" main.py
```

Výsledek v `dist/LGS XML vX.Y.Z/`:
```
LGS XML vX.Y.Z/
├── LGS XML vX.Y.Z.exe
└── _internal/         # Python runtime + knihovny
    ├── python311.dll
    └── ...
```

**POZOR:** .exe potřebuje složku `_internal/` vedle sebe. Pokud uživatel zkopíruje jen .exe, dostane chybu `Failed to load Python DLL`. Vždy distribuujte **celou složku**.

Po buildu **zkopírujte** `config.json` do `dist/LGS XML vX.Y.Z/` pro referenci (pro případ, že by ho uživatel chtěl zkontrolovat).

### 8.3 Verzování

Při každém buildu nové verze:
1. Bumpněte `APP_VERSION` v `main.py` (např. `"2.0.2"`)
2. Pokud jste změnili DEFAULT_CONFIG: bumpněte i `config_version`
3. Buildněte s novým jménem: `--name "LGS XML v2.0.2"`

Verzování v názvu .exe slouží k tomu, aby uživatel poznal, kterou verzi používá. Title bar okna taky zobrazuje verzi (`LGS XML v2.0.2`).

---

## 9. Lessons learned — čemu se vyhnout

Tato sekce dokumentuje chyby, které jsme udělali během migrace na rok 2026, aby se neopakovaly.

### 9.1 Neměňte `<typ:ids>` na `<typ:numberRequested>` bez pochopení rozdílu

**Co jsme udělali špatně:** Mysleli jsme, že `numberRequested` je novější nebo lepší způsob. Změnili jsme všechny `<typ:ids>` na `<typ:numberRequested>`.

**Co se stalo:** Pohoda začala brát naše prefixy (26OP, B26P) jako **kompletní čísla dokladů**. Při importu více souborů najednou to hlásilo duplikáty ("Doklad se zadaným číslem již existuje"). 5 z 8 souborů selhalo.

**Správné chování:** Posílat **jen prefix řady** v `<typ:ids>`, a **nechat Pohodu** přidělovat sekvenční čísla. Apka nemá co dělat se synchronizací čísel s Pohodou.

### 9.2 Při změně DEFAULT_CONFIG vždy bumpnout `config_version`

**Co jsme udělali špatně:** Upravili jsme číselné řady v `DEFAULT_CONFIG` a `config.json`, ale zapomněli bumpnout `config_version`. Rebuild .exe nebyl problém, ale u uživatele se změny **neprojevily**, protože cached config v AppData měl stejné `config_version` a migrace neproběhla.

**Důsledek:** Uživatel nám psal, že oprava nefunguje. Strávili jsme hodiny hledáním, proč apka generuje staré hodnoty, než jsme si všimli migrace.

**Pravidlo:** Každá změna v `DEFAULT_CONFIG` = bump `config_version`. **Bez výjimky.**

### 9.3 Pořadí elementů v Pohoda XML — nelze ignorovat

Pohoda striktně kontroluje pořadí XML elementů dle XSD. Pokud přidáte nový element na špatné místo, import selže s obecnou chybou bez detailu.

**Jak testovat:** Nejlepší je porovnávat s **golden XML** (referenční vzory od účetní). Apka má některé v `.tmp/New/`. Před release vždy ověřte, že vygenerované XML má identickou strukturu jako referenční.

### 9.4 Nevytvářejte číselné řady, které v Pohodě neexistují

**Co jsme udělali špatně:** Vymysleli jsme prefixy `M{YY}P` pro Molo2 a `{YY}GP` / `G{YY}P` pro B&G. Zdálo se to logické, ale v Pohodě tyto řady **nebyly vytvořené**.

**Co se stalo:** Pokladní doklady s těmito prefixy selhávaly na "v průběhu zpracování vašeho požadavku se objevila chyba" (Pohoda pro neexistující řady nevrací smysluplnou chybu).

**Správný postup:**
1. Vyžádat si od účetní **seznam existujících číselných řad** v Pohodě
2. Config dělat **přesně podle toho seznamu**, ne podle intuice
3. Pokud provoz nemá vlastní řadu, nechat ho sdílet s existující (Molo2 a B&G sdílí `R26P` s Restaurant)

### 9.5 Pohoda má uzamčená DPH období

Pohoda neumožňuje import dokladů do měsíce, pro který je už uzavřené DPH přiznání. Apka tento case nedetekuje, takže uživatel dostane z Pohody obecnou chybu.

**Doporučení do uživatelské dokumentace:** *"Pokud import selže s generickou chybou, zkontrolujte, zda datum dokladu není v uzamčeném DPH období."*

### 9.6 Qt dark mode a viditelnost textu

Windows 11 dark mode ovlivňuje Qt dialogy a komponenty. **QMessageBox**, **QSpinBox**, **QComboBox dropdown** potřebují v stylesheetu explicitně nastavenou `color` i `background-color`, jinak jsou při dark mode neviditelné (bílý text na bílém pozadí).

**Pravidlo:** Každá nová UI komponenta dostane explicitní `color: {COLORS['text_primary']}` a `background-color: white` v stylesheetu.

### 9.7 Single-file .exe vs. onedir

PyInstaller umí `--onefile` (jedna spustitelná EXE) i `--onedir` (složka s EXE + `_internal/`). Apka používá `--onedir`:

- **Výhoda onedir:** Rychlejší start (není třeba rozbalovat do tempu).
- **Nevýhoda onedir:** Uživatel musí kopírovat **celou složku**, ne jen .exe.

Kdybychom přešli na `--onefile`, uživatel by mohl nosit jen jeden .exe, ale start by byl pomalejší a některé antivirusy by mohly na rozbalování v tempu reagovat.

### 9.8 Config caching — `~/AppData/Local/MoloXML`

Apka si ukládá runtime config do `~/AppData/Local/MoloXML/Config/config.json`. Pokud debugujete a chcete "vynucené" načtení nového configu:

```bash
del %LOCALAPPDATA%\MoloXML\Config\config.json
```

Potom apka při dalším spuštění vytvoří nový z `DEFAULT_CONFIG`.

Alternativně (preferovaná cesta): bumpněte `config_version` v kódu a přebuildujte.

### 9.9 Pozor na copy-paste mezi provozy v configu

**Co se stalo (v2.0.1):** Při refaktoru `DEFAULT_CONFIG` do nového formátu (plochý `outlets` dict s novými klíči `centre`, `activity_id`, `cashAccount_ids`) vznikl B&G outlet **kopií z Molo2**. Původní `cashAccount_ids: "BaG"` se v procesu ztratilo a nahradilo hodnotou `"MOLO"` (stejně jako Restaurant/Molo2). Také `voucher_prefix_by_outlet["B&G"]` zůstal na `"R{YY}P"` (řada Restaurantu).

**Důsledek:** Aplikace generovala technicky validní XML, které Pohoda přijala — ale pokladní doklady se **zaúčtovaly na pokladnu Molo Restaurant**, ne na Bar & Grill. Chyba byla viditelná až po importu do Pohody; unit-test / schema-validator by ji nechytil.

**Pravidlo:** Když zakládáte nebo refaktorujete outlet v configu, **explicitně ověřte u účetní všech 5 klíčů**:
1. `centre` — středisko
2. `activity_id` — činnost
3. `cashAccount_ids` — pokladna (ID, ne jméno!)
4. `voucher_prefix_by_outlet[<outlet>]` — číselná řada pokladních dokladů
5. `accounts.inv_header` + `accounts.vch_header` — hlavičkové účty

Nikdy nepředpokládejte, že "provozy ve stejném středisku sdílí i pokladnu/řadu". Někdy ano (Restaurant + Molo2 sdílí `MOLO`), někdy ne (B&G má vlastní `BaG`).

**Diagnostický tip:** Nejrychlejší kontrola je `grep "cashAccount_ids" config.json` — pokud vidíte dva různé outlety se stejnou hodnotou, je to podezřelé a patří to ověřit.

---

## 10. Časté úpravy

### 10.1 Přidání nového provozu

1. V `DEFAULT_CONFIG.outlets` a `config.json` přidejte novou položku. **Nekopírujte slepě existující outlet** — získejte od účetní **všech 5 identifikátorů** (viz lesson learned 9.9):
   - `centre` — středisko
   - `activity_id` — činnost
   - `cashAccount_ids` — ID pokladny v Pohodě
   - `accounts.inv_header` a `accounts.vch_header` — hlavičkové účty
   - Předkontace pro items (`accounts.inv.high/low/none`, `accounts.vch.high/low/none`)
2. V `number_series.voucher_prefix_by_outlet` přidejte vlastní řadu (výchozí šablona `{YY}XP`, kde `X` je zkratka provozu) — ověřte u účetní, že řada v Pohodě skutečně existuje.
3. V `MainWindow.__init__()` přidejte outlet do `self.outlet.addItems([...])`
4. V `suggest_outlet_from_filename()` přidejte pattern pro auto-detekci z názvu souboru
5. Bumpněte `config_version`
6. Rebuild
7. **Ověření**: po první generaci otevřete jeden XML soubor a ručně zkontrolujte `<vch:cashAccount><typ:ids>…</typ:ids>` a `<vch:number><typ:ids>…</typ:ids>` — musí odpovídat tomu, co účetní založila v Pohodě.

### 10.2 Změna číselné řady pro existující provoz

1. Ověřte u účetní, že nová řada v Pohodě **skutečně existuje**
2. Upravte prefix v `DEFAULT_CONFIG.number_series.voucher_prefix_by_outlet` a `config.json`
3. Bumpněte `config_version`
4. Rebuild

### 10.3 Změna roku (nic nedělat)

Rok se řeší automaticky přes šablonu `{YY}` v prefixu. Takže při přechodu na 2027 nemusíte nic upravovat — apka automaticky generuje `27OP`, `B27P` atd.

### 10.4 Změna předkontace (symbolických názvů)

Pokud účetní přejmenuje předkontace v Pohodě (např. `Beverage` → `BeverageNew`):

1. Upravte `DEFAULT_CONFIG.outlets.<outlet>.accounts.inv` a `.vch` pro všechny provozy
2. Upravte stejnou strukturu v `config.json`
3. Bumpněte `config_version`
4. Rebuild

### 10.5 Změna textů faktur / pokladny

Upravte `voucher_header_text` a `invoice_header_texts.card/voucher/cashless` v configu. Bumpněte `config_version`.

---

## 11. Testování

Aplikace nemá automatizované testy. Manuální testy:

1. **Syntax check**: `python -c "import py_compile; py_compile.compile('main.py', doraise=True)"`
2. **UI smoke test**: Spustit `python main.py`, ověřit, že se okno otevře a výběr outlet + rok fungují
3. **XML generation test**: Načíst testovací Excel z `.tmp/Storyous Excel Files/`, vygenerovat XML, porovnat s `.tmp/New/*.xml` (referenční od účetní)
4. **Import test (end-to-end)**: Předat XMLka účetní k importu do Pohody. Toto je **jediný spolehlivý test**, protože Pohoda má striktní schéma a neumíme ho plně emulovat.

### 11.1 Testovací data

- `.tmp/Storyous Excel Files/` — Excel soubory z různých provozů
- `.tmp/New/` — golden XML od účetní (referenční vzor)
- `.tmp/Old/` — stará XML z verze 1.0 (pro srovnání, jak to vypadalo před migrací)
- `.tmp/2nd April/`, `.tmp/6th April/`, `.tmp/8th April/` — historické vygenerované XML z různých iterací

---

## 12. Historie klíčových změn

| Verze | Hlavní změny |
|---|---|
| 1.0 | Původní implementace (2025). Číselné řady `BisP`, `MOLP`, `CdLP`, `BaGP`. Numerické účty v items. Centre numerické. `<typ:ids>` pro čísla. |
| 2.0 | Migrace na 2026. Nové symbolické předkontace (Beverage/FOOD/SCH), centre `MOLO GASTR`, element `<activity>`, `<calculateVAT>`, note formát, šablony `{YY}` v prefixech, rok selector v UI. |
| 2.0.1 | **FIX:** `numberRequested` → `ids` (oprava duplikátů). Config migrace pomocí `config_version`. |
| 2.0.2 (aktuální) | **FIX:** B&G měl omylem nakopírované hodnoty z Molo2 (`cashAccount_ids: "MOLO"`, řada `R{YY}P`). Opraveno na `cashAccount_ids: "BaG"` a vlastní řada `{YY}GP` (pro 2026 → `26GP`). Potvrzeno účetní end-to-end importem do Pohody. Viz lessons learned 9.9. |

---

## 13. Kontakty a zdroje

- **GitHub repo**: https://github.com/Jerz11/LGS-XML
- **Pohoda XML schema**: http://www.stormware.cz/schema/version_2/
- **Firma**: Lipno Gastro Services s.r.o., IČO 17126240

---

## 14. Poslední rada pro budoucího vývojáře

1. **Nepředělávejte to, co funguje.** Apka je single-file Python + Qt + lxml. Je to jednoduché. Nedělejte z toho microservices.
2. **Čtěte golden XML.** Když měníte strukturu XML, vždy porovnávejte s `.tmp/New/*.xml`. Pohoda je striktní.
3. **Ptejte se účetní.** Hodně věcí (číselné řady, předkontace, činnosti) má logiku jen v Pohodě. Apka je jen prostředník. Bez znalosti Pohody budete tápat.
4. **Testujte na reálném Pohoda importu.** Žádný lokální test nenahradí skutečný import. Než vydáte novou verzi, nechte účetní otestovat.
5. **Bumpněte config_version.** Opravdu. Vždycky.
