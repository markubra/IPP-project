# Dokumentace k 1. úloze do IPP 2021/2022

**Jméno a příjmení:** Marko Kubrachenko 
**Login:** xkubra00

### start

Program `parse.php` začíná podmínkou, ve které zkontroluji hodnoty argumentů. Pokud byl zadán `--help` -- vytisknu nápovědu. Jinak pomocí funkce `ob_start` otevřu `buffer`, do kterého postupně vytisknu XML a spustim `main`. Pokud kontrola `IPPcode22` proběhla bez chyb, vytisknu obsah `buffer` na `stdout`. Pokud byl zadán argument `--stats=file` -- vytisknu do `file` požadované v následujících parametrech statistiky.

### main

Ve `while` smyčce neberu v úvahu nové řádky a komentáře, procházím postupně řádky a hledám hlavičku `.IPPcode22`. Odstraním možný komentář za hlavičkou a ověřím, že hlavička opravdu sedí. Vytisknu začátek XML reprezentace a procházím postupně každý řádek zvlášť. Odstraním komentáře a rozdělím instrukcí spolu s její argumenty do pole, které pak pošlu funkcí `check_instruction_and_print`.

### check_instruction_and_print

Funkce dostává pole `$instruction`, kde prvkem na indexu 0 je operační kód instrukce, který ověřím pomocí definovaných na začátku programu polí povolených instrukcí a funkce `in_array`, zároveň ověřím, zda sedí počet argumentů. Vytisknu název a číslo instrukce v XML reprezentaci. Pomocí kaskády `switch` sekcí ověřím, zda argumenty jsou ve správném tváře za použití regulárních výrazů a funkce `preg_match`. Nahradím problematické znaky v XML `"' < > &` za odpovídající XML entity funkcí `htmlspecialchars` a vytisknu argumenty v XML.
