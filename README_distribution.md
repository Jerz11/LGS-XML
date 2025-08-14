# LGS XML - Quick Start

## Instalace

1. **Stáhněte installer:** `LGS-XML-Setup-1.0.0.exe`
2. **Spusťte installer:** Dvojklik na stažený soubor
3. **Potvrďte instalaci:** Postupujte podle průvodce
4. **Spusťte aplikaci:** Z nabídky Start nebo z plochy

> 💡 **Bez admin práv!** Instalace probíhá pouze pro váš uživatelský účet.

## Použití

### 🏢 **Krok 1: Vyber provoz**
- Bistro, Restaurant, CDL, B&G, nebo Molo2

### 📄 **Krok 2: Nahraj Excel**
- Přetáhni Excel ze Storyous do aplikace
- Nebo klikni "Vybrat soubor..."

### 📅 **Krok 3: Vyber dny**
- Automaticky detekované dny z Excelu
- Zaškrtni jen dny, které chceš zpracovat
- Rychlé volby: "Vše" nebo "Clear"

### 🚀 **Krok 4: Generuj XML**
- Klikni "Generovat XML"
- Soubory se uloží do `Documents\Pohoda XML`
- Klikni "Otevřít složku" pro zobrazení výsledků

## Výstupní soubory

### 📁 **Umístění:**
`C:\Users\[váš_účet]\Documents\Pohoda XML\`

### 📄 **Typy souborů:**
- **Pokladna:** `Pokladna DD.M.YYYY - PROVOZ - ID.xml`
- **Kartou:** `OstatniPohledavky DD.M.YYYY - kartou - PROVOZ - ID.xml`  
- **Voucher:** `OstatniPohledavky DD.M.YYYY - voucherem - PROVOZ - ID.xml`

## Nastavení

### 🔧 **Konfigurace:**
Aplikace si pamatuje vaše nastavení v:
`%APPDATA%\LGS Trzby\config.json`

### 📂 **Změna výstupní složky:**
1. Klikni "Změnit..." u výstupní složky
2. Vyber novou složku
3. Nastavení se automaticky uloží

## Řešení problémů

### ❌ **"Z názvu souboru nelze odvodit správný provoz"**
- Překontroluj, že máš vybraný správný provoz
- Zkus přepnout na správný provoz a nahraj Excel znovu

### ❌ **"Nelze odvodit měsíc/rok"**
- Ujisti se, že Excel obsahuje datumy ve formátu `dd.mm.`
- Nebo přejmenuj soubor na `název_M_YYYY.xlsx`

### 📊 **Nevidím žádné dny**
- Zkontroluj, že Excel obsahuje data v prvním sloupci
- Ujisti se, že máš vybraný správný provoz

## Podpora

- **GitHub:** https://github.com/Jerz11/LGS-XML
- **Verze:** 1.0.0
- **Datum:** 2025

---

*LGS XML - Generátor Pohoda XML ze Storyous exportů*
