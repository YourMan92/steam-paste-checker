# steam-paste-checker

A small, dependency-free Python script that checks a translated Steam store page before you paste it into Steamworks. It was built for Simplified Chinese, Japanese and Korean, but the length, link and BBCode checks work for any language.

It catches the mistakes that are easy to miss when you can't read the target language:

- Short description over **300 characters** (warns above 270), or containing line breaks, BBCode or a URL. Since Sept 2024 Valve doesn't allow external links in descriptions.
- Time-based phrases in the short description ("now available", 现已推出, 発売中, 지금 출시 …).
- **About This Game** BBCode tags that don't match the English source, and image lines that were changed or dropped.
- Glossary terms missing, or avoid-list terms present.
- CJK sanity: half-width punctuation after CJK characters, spaces between Chinese characters, Japanese with no hiragana (Chinese pasted by mistake), polite/plain register mixing, too little Hangul in a Korean file.

Exit code 0 means every check passed. 1 means at least one FAIL. WARN lines need a human decision.

## Usage

```bash
python3 check_paste.py examples/source-en.txt examples/steamworks-paste_ja.txt ja \
  --glossary examples/glossary.csv --avoid examples/avoid-list.txt
```

`lang` is one of `zh-Hans`, `ja`, `ko` (other values run only the language-neutral checks).

Both files use a simple paste format:

```
===== SHORT DESCRIPTION =====
One plain paragraph, max 300 characters.
===== ABOUT THIS GAME =====
[h2]...[/h2]
[list][*]...[/list]
```

`glossary.csv` has a `term_en` column plus one column per language (use `|` between accepted alternatives). `avoid-list.txt` has one `lang: term` per line (`*` = all languages).

## Reference

- [STEAM-LIMITS.md](STEAM-LIMITS.md): Steam store-page field rules with sources (short description cap, link ban, localized names and search, language codes such as `koreana`, AI disclosure in the Content Survey).
- [LANGUAGE-CHECKS.md](LANGUAGE-CHECKS.md): typography, register and sensitivity checks for zh-Hans, ja and ko.

Guides:
- [Localize your Steam page for China](https://steam-page-localization.vercel.app/localize-steam-page-china.html?utm_source=github&utm_medium=readme&utm_campaign=cjk-pack&utm_content=guide-china)
- [Localize your Steam page for Japan](https://steam-page-localization.vercel.app/localize-steam-page-japan.html?utm_source=github&utm_medium=readme&utm_campaign=cjk-pack&utm_content=guide-japan)
- [Localize your Steam page for Korea](https://steam-page-localization.vercel.app/localize-steam-page-korea.html?utm_source=github&utm_medium=readme&utm_campaign=cjk-pack&utm_content=guide-korea)
- [Short description checker (in the browser)](https://steam-page-localization.vercel.app/steam-short-description-checker.html?utm_source=github&utm_medium=readme&utm_campaign=cjk-pack&utm_content=checker)

## Want to see a finished example?

A free sample shows a full CJK translation of a store page: paste-ready files, back-translations, QA notes and keywords. Pay what you want, $0 is fine:
**https://pimpwen.gumroad.com/l/steam-translation-sample?utm_source=github&utm_medium=readme&utm_campaign=cjk-pack&utm_content=sample**

If you'd rather not do it yourself, the paid pack ($49) translates your short description, About This Game and keywords into zh-Hans, ja and ko, checked with this script:
https://pimpwen.gumroad.com/l/steam-page-translation-cjk?utm_source=github&utm_medium=readme&utm_campaign=cjk-pack&utm_content=pack

## Honest notes

- Translations in the pack and the sample are **AI-assisted**, then checked with this script and the checklists above. Steam's Content Survey asks you to disclose AI-generated localization, so disclose it.
- This script checks structure and common mistakes. It isn't a native-speaker review.
- Steam rules change. Re-check the linked Steamworks docs before you rely on a limit.

## License

MIT. See [LICENSE](LICENSE).
