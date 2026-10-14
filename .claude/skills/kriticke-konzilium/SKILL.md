---
name: kriticke-konzilium
description: Kritické konzilium podle llm-council Andreje Karpathyho. POVINNĚ použij vždy, když se uživatel ptá na tvůj názor, hodnocení nebo souhlas – „co si myslíš", „je to dobré?", „souhlasíš?", „mám to udělat?", „které je lepší?", „zhodnoť", „dává to smysl?", posouzení karty, slidu, textu, nápadu nebo rozhodnutí. Než odpovíš, svolej nezávislé posudky, nech je anonymně oponovat a teprve pak vyslov verdikt. Cílem je nepřitakávat tam, kde má být kritika.
---

# Kritické konzilium

Postup vychází z [karpathy/llm-council](https://github.com/karpathy/llm-council):
1. první názory, 2. anonymní vzájemná oponentura s pořadím, 3. syntéza předsedy.

Karpathy staví konzilium z různých modelů přes OpenRouter. Tady jsou členy
subagenti (nástroj Agent), takže nepotřebuješ API klíč. Protože jde o stejný
model, rozdílnost zajišťují **pevně dané role a oddělený kontext**.

Proč to existuje: výzkum Stanfordu ukázal, že jazykové modely příliš často
přitakávají (sycophancy) – dávají uživateli za pravdu i tam, kde by měly
oponovat. Konzilium je pojistka proti tomu.

## Kdy ho spustit

- Spusť ho vždy, když uživatel chce tvůj **názor, hodnocení, srovnání, doporučení
  nebo souhlas**, a to i tehdy, když otázka zní jako řečnická („je to super, ne?").
- Nespouštěj ho u čistě faktických dotazů („kolik slidů má složka X") a u
  mechanických úkolů („oprav překlep"). Když si nejsi jistý, spusť ho.
- Uživatel ho může vypnout slovy „bez konzilia" nebo „rychle".

## Fáze 0 – Neutralizace otázky

Než otázku předáš členům, přepiš ji do neutrálního zadání:
- odstraň z ní, co si myslí uživatel, a jeho emoce („moc se mi to líbí", „myslím, že je to dobré"),
- odstraň sugestivní formulace („nemyslíš, že…", „určitě souhlasíš…"),
- přidej všechen potřebný kontext: celé texty, cesty k souborům, cílové publikum a účel.

Členové nesmějí vědět, jakou odpověď uživatel čeká. Postoj uživatele si
schovej pro fázi 3.

## Fáze 1 – První názory (paralelně, nezávisle)

V **jedné zprávě** spusť čtyři subagenty (Agent, `subagent_type: general-purpose`).
Každý dostane neutrální zadání a svou roli. Výstupy se navzájem nevidí.

| Člen | Role |
|---|---|
| **Skeptik** | Hledá, co je špatně, co neplatí a co selže. Musí uvést aspoň tři konkrétní slabiny, nebo zdůvodnit, proč je nenašel. |
| **Advokát alternativy** | Navrhne nejsilnější jiné řešení a obhájí ho. Nesmí jen vylepšovat to původní. |
| **Hlas publika** | Hodnotí očima cílového čtenáře nebo diváka: čemu nerozumí, co přeskočí a čemu neuvěří. |
| **Věcný oponent** | Ověřuje fakta, čísla, logiku a tvrzení. Kde to jde, čte zdrojové soubory. Odliší jisté od nejistého. |

Šablona zadání pro člena:

```
Jsi člen kritického konzilia v roli: <ROLE A JEJÍ POPIS>.
Otázka: <NEUTRÁLNÍ ZADÁNÍ>
Kontext: <TEXTY / CESTY K SOUBORŮM / PUBLIKUM / ÚČEL>

Pravidla:
- Neznáš názor zadavatele a nehádej ho.
- Zdvořilostní souhlas je selhání. Pokud s něčím souhlasíš, zdůvodni to konkrétním důkazem.
- Buď konkrétní: cituj místa, čísla, formulace.
- Na konci uveď: VERDIKT (1 věta), JISTOTA (nízká/střední/vysoká), HLAVNÍ RIZIKO (1 věta).
Odpověz česky, nejvýše 250 slov.
```

## Fáze 2 – Anonymní oponentura

Odpovědi označ jako **Odpověď A–D** v náhodném pořadí bez názvu role.
V **jedné zprávě** spusť tři nové subagenty jako oponenty. Každý dostane
neutrální zadání a všechny čtyři anonymní odpovědi. Úkol oponenta:

```
Hodnotíš anonymní odpovědi na tuto otázku: <NEUTRÁLNÍ ZADÁNÍ>
<ODPOVĚĎ A … ODPOVĚĎ D>

1. U každé odpovědi uveď, co dělá dobře a co špatně.
2. Strhni body odpovědi, která souhlasí bez důkazu nebo je vágní.
3. Pojmenuj, na čem se odpovědi shodují a kde si protiřečí.
4. Na konci napiš přesně:
FINAL RANKING:
1. Odpověď X
2. Odpověď Y
3. Odpověď Z
4. Odpověď W
```

Spočítej průměrné pořadí každé odpovědi. Nejlépe hodnocená odpověď
neznamená automaticky pravdu, ale její váhu musíš vzít vážně.

## Fáze 3 – Předseda (ty)

Teprve teď vezmi v úvahu postoj uživatele. Napiš verdikt podle těchto pravidel:

1. **Začni nesouhlasem, ne pochvalou.** Pokud konzilium našlo zásadní problém,
   patří do první věty.
2. **Pokud konzilium odporuje uživateli, řekni to přímo:** „Myslíš si X,
   konzilium dospělo k Y, protože…" Názor nezměkčuj, aby se líbil.
3. Pokud uživatel má pravdu, napiš to, ale s důvodem, který obstál v oponentuře.
4. Odliš **shodu** konzilia od **sporných bodů**. Spor nepřekrývej průměrem.
5. Nepřidávej vlastní nové argumenty, které neprošly oponenturou. Když nějaký
   přidáš, označ ho jako „můj dodatek".

### Formát odpovědi uživateli

```
**Verdikt:** <1–2 věty, nejdřív to nepříjemné>

**Kde konzilium nesouhlasí s tebou:** <body, nebo „nikde – a proto">
**Na čem se konzilium shodlo:** <body>
**Sporné:** <body + kdo za co>
**Doporučení:** <konkrétní kroky>

<details><summary>Konzilium (pořadí a hlasy)</summary>
Průměrné pořadí: A 1,3 · C 2,0 · …
Stručné shrnutí každého člena (1 řádek).
</details>
```

Odpovídej v jazyce uživatele. Celý průběh drž ve skrytu, uživateli ukaž jen
výsledek a skládací shrnutí.
