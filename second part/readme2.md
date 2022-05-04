
# Dokumentace k 2. úloze do IPP 2021/2022

**Jméno a příjmení:** Marko Kubrachenko

**Login:** xkubra00

## Interpret XML reprezentace kódu

### Začátek
Nejprve zkontroluji vstupní parametry. Pokud byl zadán `--help` -- vytisknu nápovědu pro uživatele. Dále ověřím, že alespoň jeden vstupní soubor je specifikován (`--source` nebo `--input`) a zachovám se podle zadání, případně, pokud byl zadán `--input`, načtu vstupní data a uložím je do pole. Dále pomocí knihovny `xml.etree.ElementTree` zpracuji XML kód, který načtu ze souboru (pokud byl zadán `--source`) nebo ze standardního vstupu; ověřím zda nejsou záporné nebo duplicitní pořadí instrukcí a argumentů, a nakonec je seřadím vzestupně.

### Generování instrukcí
Výsledný argument předám funkci, která zavolá metodu `resolve()` třídy `Factory` nad každou instrukci a provede inicializaci (podle operačního kódu) instance příslušné třídy *(Factory Method)*. Dále nad každým argumentem instrukce zavolám metodu `append_arg()` nově vytvořené instance, která je však metodou její nadtřídy `Instruction`.

### Implementace skoku
Pro implementaci skoku na návěstí projdu všechny instrukce a pokud to je `LABEL`, tak uložím název návěští do slovníku spolu s pořadím instrukce, které se pak využije při vykonání samotné instrukce.

### Vykonání instrukcí
Ve `for` cyklu projdu všechny instrukce od začátku a zavolám pro každou zvlášť metodu `execute()`, která provede zpracování instrukce.

Při zpracování instrukcí používám pomocné funkce: `get_any()`, `get_bool()`, `get_int()`, `get_var()`, `store_var()`, které jsem implementoval pro snazší ukládání a získání dat z argumentů instrukce nebo datových rámců.

### Implementační detaily
Pro simulaci dočasných a lokálních rámců jsem implementoval třídu `Frame`, která má metody pro uložení nebo získání hodnoty proměnné. Globální rámec jsem implementoval pomocí globálního slovníku.

Třída `Nil` slouží pro simulaci datového typu `nil`, nemá žádné metody, ale je vhodná, aby byl lehce rozpoznatelný.


## Testovací rámec

### Začátek
Program začíná voláním funkce `check_args()`, která zpracuje vstupní parametry, pokud některé byly zadané, jinak je ponechá implicitními; ověří zda nejsou zakázané kombinace parametrů. Dále získám testy v závislosti na parametru `--recursive`. Funkce `print_start()` a `print_header()` vytisknou začátek `html` souboru a hlavičku tabulky pro zobrazení výsledků jednotlivých testů.

### Příprava
Ve `foreach` smyčce hledám pomocí funkce `pathinfo()` soubor s příponou `.src`. Pokud našel -- vygeneruji potřebné soubory (`.in`, `.out`, `.rc`), pokud nějaké neexistují.

### Testování a tisk výsledků testů
Vyjmu očekávaný návratový kód ze souboru s příponou `.rc` a podle parametrů uživatele vykonám buď pouze testy na testování parseru, nebo interpretu, anebo obou zároveň. Spuštění příkazů pro vyhodnocení testů jsem implementoval za použití funkce `exec()`.

Ověřím zda test uspěl a zavolám funkci `print_test()`, která vytiskne položku tabulky v `html` s informacemi o složce, ve které se test nachází, název testu, který byl naposledy spuštěn a jeho výsledek.

### Uklízení dočasných souborů a tisk konce `html`
Na konci programu v závislosti na parametru `--noclean` odstraním dočasně vygenerované soubory pomocí funkce `unlink()`. Spočítám procento testů, které uspěly, a vytisknu ho.
