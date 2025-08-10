# Molo XML – PRD (copy-ready)

## 0) Cíl

* Lokální desktop app pro **generaci POHODA XML** z **Excel exportů Storyous**.
* **1 den = 1 `dat:dataPack`** se 0–3 doklady (hotově/kartou/voucherem).
* Minimální tření: **drag\&drop**, **offline**, **per-user instalace**.

---

## 1) Scope / Out of scope

**Scope**

* Vstup: Excel „Přehled tržeb“ pro provozy **Bistro, Restaurant, CDL, B\&G, Molo2**.
* Výstup:

  * `vch:voucher` (Pokladna) – **hotově**
  * `inv:invoice` (Ostatní pohledávky – karta) – **kartou**
  * `inv:invoice` (Ostatní pohledávky – voucher) – **voucher**
* **Faktura/Bankovní převod = nikdy negenerovat.**
* **Naming** souborů předepsaný (níže).
* **Texty položek** předepsané (níže).
* **Účty/centre/paymentType/cashAccount** podle provozu (níže).
* **Validace součtů + tolerance ±0,01 Kč** (dorovnání).

**Out of scope**

* macOS build, auto-update, cloud, DB, import do POHODY.

---

## 2) Platforma & distribuce

* **Windows 10/11**, **offline**, **per-user MSI** (bez admin).
* Distribuce: **podepsané MSI** na **SharePointu klienta** (1 link + 1-page PDF).
* **Timezone:** Europe/Prague.

---

## 3) UI (Dropzone – single window)

```
+----------------------------------------------------------------------------------+
|  Molo XML • Jednoduchý režim                                                     |
+----------------------------------------------------------------------------------+
| Provoz: [ Bistro ▼ ]        Režim: [ Jednoduchý ▼ | Pokročilý ]                  |
|                                                                                  |
|  Přetáhni sem Excel z Storyous                                                   |
|  ┌────────────────────────────────────────────────────────────────────────────┐  |
|  │                                                                            │  |
|  │                 ⇩  Přetáhni soubor sem  ⇩                                  │  |
|  │                                                                            │  |
|  └────────────────────────────────────────────────────────────────────────────┘  |
|                                                                                  |
| Detekováno: Měsíc/Rok = 06/2025   Dny: [ Vše ] [ Víkendy ] [ Prac.dny ] [ Clear ]|
| [ Generovat XML ]     Výstup: C:\Users\...\Documents\Pohoda XML   [ Otevřít ]    |
|                                                                                  |
| Stav: —                                                                          |
+----------------------------------------------------------------------------------+
| ⚙ Nastavení   ⓘ Nápověda   [ Log ]                                              |
+----------------------------------------------------------------------------------+
```

**Flow:** drag\&drop → autodetekce měsíc/rok + dnů → volba dnů (presety) → **Generovat** → **Otevřít složku**.

---

## 4) Interní datový model

```ts
type Rate = 21 | 12 | 0;
type Method = "cash" | "card" | "voucher";

interface Item { rate: Rate; base: number; vat: number; gross: number; text: string; }
interface Doc   { method: Method; items: Item[]; }
interface DayBatch { date: string; outlet: string; docs: Doc[]; }
```

---

## 5) Parsing Excelu

* **Datum dne** v 1. sloupci jako `dd.mm.` → **rok/měsíc z názvu souboru**: `*_{M}_{YYYY}.xlsx`.
* Normalizace čísel: odstranit NBSP/mezery/`Kč`/`CZK`, čárku → tečka.
* **Sekce k použití (per provoz)**: Hotově / Kartou / Voucher (každá má `Základ`, `DPH`, `Tržby s DPH` pro **21/12/0**).
* **Ignorovat vždy**: **Faktura/Bankovní převod** + **Celkem** součty (jen kontrola).
* Detekce sloupců **regexem podle názvů headerů** (ne podle indexu).

### Generické regex mapování (adapter default)

```json
{
  "date_col_candidates": ["^Datum$","^Den$","^$"],
  "sections": {
    "cash": {
      "base_high": "^Základ 21% \\(Hotově\\)$",
      "vat_high": "^DPH 21% \\(Hotově\\)$",
      "gross_high": "^Tržby s DPH 21% \\(Hotově\\)$",
      "base_low": "^Základ 12% \\(Hotově\\)$",
      "vat_low": "^DPH 12% \\(Hotově\\)$",
      "gross_low": "^Tržby s DPH 12% \\(Hotově\\)$",
      "base_none": "^Základ 0% \\(Hotově\\)$",
      "vat_none": "^DPH 0% \\(Hotově\\)$",
      "gross_none": "^Tržby s DPH 0% \\(Hotově\\)$"
    },
    "card": {
      "base_high": "^Základ 21% \\(Kartou\\)$",
      "vat_high": "^DPH 21% \\(Kartou\\)$",
      "gross_high": "^Tržby s DPH 21% \\(Kartou\\)$",
      "base_low": "^Základ 12% \\(Kartou\\)$",
      "vat_low": "^DPH 12% \\(Kartou\\)$",
      "gross_low": "^Tržby s DPH 12% \\(Kartou\\)$",
      "base_none": "^Základ 0% \\(Kartou\\)$",
      "vat_none": "^DPH 0% \\(Kartou\\)$",
      "gross_none": "^Tržby s DPH 0% \\(Kartou\\)$"
    },
    "voucher": {
      "base_high": "^Základ 21% \\(Voucher\\)$",
      "vat_high": "^DPH 21% \\(Voucher\\)$",
      "gross_high": "^Tržby s DPH 21% \\(Voucher\\)$",
      "base_low": "^Základ 12% \\(Voucher\\)$",
      "vat_low": "^DPH 12% \\(Voucher\\)$",
      "gross_low": "^Tržby s DPH 12% \\(Voucher\\)$",
      "base_none": "^Základ 0% \\(Voucher\\)$",
      "vat_none": "^DPH 0% \\(Voucher\\)$",
      "gross_none": "^Tržby s DPH 0% \\(Voucher\\)$"
    },
    "invoice_ignore": { "any": ["\\(Faktura\\)","\\(Bankovní převod\\)"] },
    "totals_ignore":  { "any": ["^Základ Celkem$","^DPH Celkem$","^Tržby s DPH Celkem$"] }
  }
}
```

---

## 6) Generování XML (POHODA)

### Obecné

* Kořen: `dat:dataPack version="2.0"`; **encoding: Windows-1250**.
* **Pořadí elementů a namespaces** jako ve vzorových XML.
* **0 % řádky:** `classificationVAT UN` (line-level, `nonSubsume`).
* **Likvidace:** `card = D+1 pracovní den`, `voucher = D`, `cash = D`.
* Souhrny (`…Summary/homeCurrency`) = součty položek.

### Typy dokladů

* **Hotově** → `vch:voucher` (`voucherType=receipt`, `classificationVAT=UD`, `cashAccount:ids` dle provozu).
* **Kartou** → `inv:invoice` (`invoiceType=receivable`, `classificationVAT=UDA5`, `paymentType=creditcard`, `ids="Plat.kartou"`).
* **Voucher** → `inv:invoice` (`paymentType=cheque`, `ids="Šekem"`).

### Položky

* `quantity=1.0`; `unitPrice=price=Základ`; `priceVAT=DPH`; `priceSum=Základ+DPH`; `rateVAT=high|low|none`.

---

## 7) Texty položek (pevné)

| Metoda  | 21 %                       | 12 %                   | 0 %                             |
| ------- | -------------------------- | ---------------------- | ------------------------------- |
| Hotově  | `21% Beverage - hotově`    | `12% Food - hotově`    | `0% Service charge - hotově`    |
| Kartou  | `21% Beverage - kartou`    | `12% Food - kartou`    | `0% Service charge - kartou`    |
| Voucher | `21% Beverage - voucherem` | `12% Food - voucherem` | `0% Service charge - voucherem` |

*Hlavičkové texty dokladů beze změny. Diakritiku vždy normalizovat („hotově“).*

---

## 8) Účty, střediska, pokladny (per provoz)

| Provoz         | centre | cashAccount\:ids | inv 21%       | inv 12%       | inv 0%        | vch 21%       | vch 12%       | vch 0%        |
| -------------- | :----: | ---------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| **Bistro**     |    3   | Bistro           | 315000/602116 | 315000/602114 | 315000/602117 | 211000/602116 | 211000/602114 | 211000/602117 |
| **Restaurant** |    1   | MOLO             | 315000/602112 | 315000/602110 | 315000/602113 | 211000/602112 | 211000/602110 | 211000/602113 |
| **CDL**        |    4   | CdL              | 315000/602123 | 315000/602121 | 315000/602124 | 211000/602123 | 211000/602121 | 211000/602124 |
| **B\&G**       |    1   | BaG              | 315000/602112 | 315000/602110 | 315000/602113 | 211000/602112 | 211000/602110 | 211000/602113 |
| **Molo2**      |    2   | MOLO             | 315000/602112 | 315000/602110 | 315000/602113 | 211000/602112 | 211000/602110 | 211000/602113 |

---

## 9) Naming konvence výstupů

* **Pokladna:** `Pokladna {DD.M.YYYY} - {PROVOZ} - {ID}.xml`
* **OstatniPohledavky:** `OstatniPohledavky {DD.M.YYYY} - {METODA} - {PROVOZ} - {ID}.xml`

**Parametry**

* `{DD.M.YYYY}` např. `3.6.2025` (bez nul).
* `{METODA}`: `kartou` | `voucherem`.
* `{PROVOZ}`: `Bistro` | `Restaurant` | `CDL` | `B&G` | `Molo2`.
* `{ID}`: čas generace `yymmdd_hhmmss` (Europe/Prague).

RegEx validace (interně):

```
^Pokladna \d{1,2}\.\d{1,2}\.\d{4} - (Bistro|Restaurant|CDL|B&G|Molo2) - \d{6}_\d{6}\.xml$
^OstatniPohledavky \d{1,2}\.\d{1,2}\.\d{4} - (kartou|voucherem) - (Bistro|Restaurant|CDL|B&G|Molo2) - \d{6}_\d{6}\.xml$
```

---

## 10) Konfigurace (`config.json`) – skeleton

```json
{
  "version": "1.0",
  "timezone": "Europe/Prague",
  "naming": {
    "pokladna": "Pokladna {DD.M.YYYY} - {OUTLET} - {ID}.xml",
    "ostatni": "OstatniPohledavky {DD.M.YYYY} - {METHOD_LABEL} - {OUTLET} - {ID}.xml",
    "id_format": "yymmdd_hhmmss"
  },
  "global_rules": {
    "ignore_invoice_transfer": true,
    "rounding_tolerance": 0.01,
    "encoding": "windows-1250",
    "date_from_filename": true
  },
  "payment_ids": {
    "card":    { "ids": "Plat.kartou", "paymentType": "creditcard" },
    "voucher": { "ids": "Šekem",      "paymentType": "cheque" }
  },
  "outlets": {
    "Bistro": {
      "centre": "3", "cashAccount_ids": "Bistro",
      "accounts": {
        "inv": { "high": "315000/602116", "low": "315000/602114", "none": "315000/602117" },
        "vch": { "high": "211000/602116", "low": "211000/602114", "none": "211000/602117" }
      },
      "item_texts": {
        "cash":    { "high": "21% Beverage - hotově", "low": "12% Food - hotově", "none": "0% Service charge - hotově" },
        "card":    { "high": "21% Beverage - kartou", "low": "12% Food - kartou", "none": "0% Service charge - kartou" },
        "voucher": { "high": "21% Beverage - voucherem", "low": "12% Food - voucherem", "none": "0% Service charge - voucherem" }
      }
    },
    "Restaurant": {
      "centre": "1", "cashAccount_ids": "MOLO",
      "accounts": {
        "inv": { "high": "315000/602112", "low": "315000/602110", "none": "315000/602113" },
        "vch": { "high": "211000/602112", "low": "211000/602110", "none": "211000/602113" }
      },
      "item_texts": { /* stejné patterny jako výše */ }
    },
    "CDL": {
      "centre": "4", "cashAccount_ids": "CdL",
      "accounts": {
        "inv": { "high": "315000/602123", "low": "315000/602121", "none": "315000/602124" },
        "vch": { "high": "211000/602123", "low": "211000/602121", "none": "211000/602124" }
      },
      "item_texts": { /* stejné patterny */ }
    },
    "B&G": {
      "centre": "1", "cashAccount_ids": "BaG",
      "accounts": {
        "inv": { "high": "315000/602112", "low": "315000/602110", "none": "315000/602113" },
        "vch": { "high": "211000/602112", "low": "211000/602110", "none": "211000/602113" }
      },
      "item_texts": { /* stejné patterny */ }
    },
    "Molo2": {
      "centre": "2", "cashAccount_ids": "MOLO",
      "accounts": {
        "inv": { "high": "315000/602112", "low": "315000/602110", "none": "315000/602113" },
        "vch": { "high": "211000/602112", "low": "211000/602110", "none": "211000/602113" }
      },
      "item_texts": {
        "cash": { "high": "21% Beverage - hotově", "low": "12% Food - hotově", "none": "0% Service charge - hotově" },
        "card": { "high": "21% Beverage - kartou", "low": "12% Food - kartou", "none": "0% Service charge - kartou" }
      }
    }
  }
}
```

---

## 11) Validace & dorovnání

* **Souhrny = součet položek**; pokud |Δ| > **0,01 Kč**, **dorovnat** poslední položku metody a zalogovat.
* **Kontrola proti „Tržby s DPH … Celkem“** v sekci (pokud je k dispozici).
* **0 %** vždy s `UN (nonSubsume)`.
* **Likvidace**: karta **D+1 prac. den** (so/ne → Po), voucher **D**, hotově **D**.
* **Diakritika**: normalizace (žádné „hotovì“).

---

## 12) Chyby (kódy + akce)

| Kód              | Zpráva                                      | Akce UI / Log                   |
| ---------------- | ------------------------------------------- | ------------------------------- |
| `E_NO_SHEET`     | „Nenašel jsem list s přehledem“             | vybrat list / log               |
| `E_NO_DATE`      | „Nenalezl jsem datum v prvním sloupci“      | nabídnout ruční rok/měsíc / log |
| `E_MAP_HEADER`   | „Chybí povinné sloupce pro {method}/{rate}“ | ukázat chybějící názvy / log    |
| `E_ZERO_DOCS`    | „Pro vybrané dny nevznikl žádný doklad“     | info / log                      |
| `E_SUM_MISMATCH` | „Součet položek nesedí s celkem (>0,01)“    | auto-fix + WARN                 |
| `E_WRITE_IO`     | „Nelze zapsat do cílové složky“             | vybrat jinou složku             |
| `E_ENCODING`     | „Chyba při generování Windows-1250“         | log + instrukce                 |

---

## 13) Logování

* `Dokumenty\Pohoda XML\Logs\YYYY-MM\app_YYYYMMDD.txt`
* Log: verze app, vstupní soubor, outlet, dny, vyrobené soubory, dorovnání, chyby (trace).

---

## 14) Testy (golden files)

* **Bistro**: 3.6., 15.6. → 3 doklady/den; nové texty řádků.
* **Restaurant**: 28.6. → `centre=1`, `cashAccount=MOLO`, účty dle tabulky; nové texty.
* **CDL**: 28.6. → `centre=4`, účty `…/602123|121|124`; nové texty.
* **B\&G**: 21.6. → `centre=1`, `cashAccount=BaG`; nové texty.
* **Molo2**: 20.6. → card+cash; `centre=2`; nové texty.

**Kritéria:** validní dataPack, správné doklady, položky (texty/účty/rate/UN), likvidace, souhrny, naming.

---

## 15) Definition of Done

* Podepsané **MSI per-user**, **Quick Start PDF**, předvyplněný `config.json`.
* Golden scénáře pro 5 provozů projdou (bit-diff akceptován).
* UI/hlášky/logy v češtině, žádné internetové volání.
* Repo obsahuje `PRD.md`, `RTM.md`, `ACCEPTANCE.md`.

---

## 16) Release pojmenování

* Verze **SemVer**: `MAJOR.MINOR.PATCH` (např. `1.0.0`).
* Soubory:

  * `MoloXML-Setup-1.0.0.msi`
  * `QuickStart-1.0.0.pdf`
  * `config.json`

---

Hotovo. To celé si prostě zkopíruj do souboru `PRD.md` v IDE. Pokud chceš, doplním i „Quick Start.pdf“ text (1 stránka) v dalším kroku.
