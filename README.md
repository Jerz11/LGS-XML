# LGS XML

Desktop aplikace pro generování XML souborů z Excel reportů pro systém Pohoda.

## Popis

LGS XML je Windows aplikace, která převádí Excel exporty ze systému Storyous na XML soubory kompatibilní s účetním systémem Pohoda. Aplikace podporuje různé provozy (Bistro, Restaurant, CDL, B&G, Molo2) a automaticky generuje správné XML struktury pro tržby hotově, kartou a vouchery.

## Funkce

- **Drag & Drop rozhraní** - jednoduché přetažení Excel souboru
- **Automatická detekce provozu** - rozpoznání provozu z názvu souboru
- **Automatická detekce měsíce/roku** - z obsahu Excel souboru nebo názvu
- **Výběr dnů** - možnost vybrat konkrétní dny pro generování
- **Konzistentní XML struktura** - vždy obsahuje všechny sazby DPH (21%, 12%, 0%)
- **Konfigurovatelné nastavení** - přes config.json soubor

## Podporované provozy

- **Bistro** - centrum 3, pokladna "Bistro"
- **Restaurant** - centrum 1, pokladna "MOLO"  
- **CDL** - centrum 4, pokladna "CdL"
- **B&G** - centrum 1, pokladna "BaG"
- **Molo2** - centrum 2, pokladna "MOLO"

## Systémové požadavky

- Windows 10/11
- .NET Framework (pro běh aplikace)

## Instalace

1. Stáhněte nejnovější release z GitHub Releases
2. Rozbalte archiv do složky podle výběru
3. Spusťte `LGS XML.exe`

## Použití

1. **Spusťte aplikaci**
2. **Vyberte provoz** z dropdown menu (nebo nechte automatickou detekci)
3. **Přetáhněte Excel soubor** do označené oblasti nebo použijte tlačítko "Vybrat soubor"
4. **Vyberte dny** pro které chcete generovat XML
5. **Klikněte "Generovat XML"**
6. **Otevřete výstupní složku** tlačítkem "Otevřít složku"

## Struktura výstupních souborů

Aplikace generuje tyto typy XML souborů:

### Pokladna (hotově)
- **Název**: `Pokladna {DD.M.YYYY} - {OUTLET} - {ID}.xml`
- **Obsah**: Tržby hotově (voucher dokument)

### OstatniPohledavky (kartou)
- **Název**: `OstatniPohledavky {DD.M.YYYY} - kartou - {OUTLET} - {ID}.xml`
- **Obsah**: Tržby kartou (faktura)

### OstatniPohledavky (voucherem)
- **Název**: `OstatniPohledavky {DD.M.YYYY} - voucherem - {OUTLET} - {ID}.xml`
- **Obsah**: Tržby vouchery (faktura)

## Konfigurace

Aplikace automaticky vytvoří konfigurační soubor v:
```
%USERPROFILE%\AppData\Local\LGS XML\Config\config.json
```

V tomto souboru můžete upravit:
- Účetní účty pro jednotlivé provozy
- Texty položek
- Nastavení číslování dokumentů
- Bankovní účty
- A další...

## Logy

Logy aplikace se ukládají do:
```
%USERPROFILE%\AppData\Local\LGS XML\Logs\
```

## Výstupní soubory

XML soubory se ukládají do:
```
%USERPROFILE%\Documents\Pohoda XML\
```

## Formát Excel souboru

Aplikace očekává Excel soubory s těmito sloupci:
- **První sloupec**: Datum ve formátu `D.M.` (např. `26.6.`, `21.6.`)
- **Další sloupce**: Tržby podle konfigurace header_map

### Doporučený formát názvu souboru:
```
nazev_M_YYYY.xlsx
```
Kde:
- `M` = měsíc (1-12)
- `YYYY` = rok (např. 2025)

## Vývoj

### Požadavky pro vývoj
```bash
pip install PySide6 pandas openpyxl lxml
```

### Build
```bash
pyinstaller --noconfirm --onedir --windowed --name "LGS XML" main.py
```

## Licence

© 2025 Lipno Gastro Services s.r.o.

## Podpora

Pro technickou podporu kontaktujte: [váš kontakt]

---

**Verze**: 1.0
**Posledni aktualizace**: {aktuální datum}
