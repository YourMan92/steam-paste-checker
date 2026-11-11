#!/usr/bin/env python3
"""QA checker for one Steamworks paste-ready file.

Usage:
  python3 check_paste.py SOURCE_EN.txt TARGET_LANG.txt LANG [--glossary glossary.csv] [--avoid avoid.txt]

Both files use the paste format:
  ===== FIELD NAME =====
  text...
Fields checked: SHORT DESCRIPTION (<=300 chars, no URL, no line breaks, no BBCode,
no time-based phrases), ABOUT THIS GAME (BBCode tag multiset identical to source,
{STEAM_APP_IMAGE} lines byte-identical), glossary target terms present when the
source term is present, avoid-list terms absent, CJK punctuation sanity.
Exit code 0 = all PASS, 1 = at least one FAIL. WARN lines need a human decision.
"""
import csv, re, sys, collections, argparse

def fields(path):
    out, cur = collections.OrderedDict(), None
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^=====\s*(.+?)\s*=====\s*$", line)
        if m:
            cur = m.group(1).upper(); out[cur] = []; continue
        if cur is not None:
            out[cur].append(line.rstrip("\n"))
    return {k: "\n".join(v).strip() for k, v in out.items()}

def tags(text):
    return collections.Counter(t.lower() for t in re.findall(r"\[/?[a-z0-9*]+", text, re.I))

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("tgt"); ap.add_argument("lang")
ap.add_argument("--glossary"); ap.add_argument("--avoid")
a = ap.parse_args()
S, T = fields(a.src), fields(a.tgt)
fails = 0
def report(level, msg):
    global fails
    if level == "FAIL": fails += 1
    print(f"[{level}] {msg}")

sd = T.get("SHORT DESCRIPTION", "")
n = len(sd)
report("PASS" if 0 < n <= 300 else "FAIL", f"short description length {n}/300 code points")
if n > 270: report("WARN", "short description over 270; Steam may wrap to >6 lines on some layouts")
if re.search(r"https?://|www\.", sd): report("FAIL", "URL in short description (Valve: no external links)")
if "\n" in sd: report("FAIL", "line break in short description (plain one paragraph only)")
if re.search(r"\[/?[a-z*]+", sd, re.I): report("FAIL", "BBCode in short description (plain text only)")
time_words = {"zh-Hans": ["现已推出", "即将推出", "预购", "限时"], "ja": ["発売中", "近日発売", "予約受付", "期間限定"],
              "ko": ["지금 출시", "출시 예정", "사전 구매", "기간 한정"]}
for w in time_words.get(a.lang, []) + ["now available", "pre-purchase", "coming soon"]:
    if w.lower() in sd.lower(): report("FAIL", f"time-based phrase in short description: {w}")

src_about, tgt_about = S.get("ABOUT THIS GAME", ""), T.get("ABOUT THIS GAME", "")
if src_about:
    st, tt = tags(src_about), tags(tgt_about)
    report("PASS" if st == tt else "FAIL", f"About This Game BBCode tags {'match' if st == tt else 'DIFFER: src ' + str(dict(st)) + ' tgt ' + str(dict(tt))}")
    simg = re.findall(r"\[img[^\]]*\][^\[]*\[/img\]|\{STEAM_APP_IMAGE\}[^\s\]]*", src_about)
    for i in simg:
        if i not in tgt_about: report("FAIL", f"image line changed or missing: {i}")
    if simg: report("PASS", f"{len(simg)} image lines byte-identical")

if a.glossary:
    for row in csv.DictReader(open(a.glossary, encoding="utf-8")):
        src_term, tgt = row["term_en"], row.get(a.lang, "").strip()
        if not tgt: continue
        src_all = "\n".join(S.values()); tgt_all = "\n".join(T.values())
        if src_term.lower() in src_all.lower():
            alts = [x.strip() for x in tgt.split("|")]
            ok = any(x in tgt_all for x in alts)
            report("PASS" if ok else "FAIL", f"glossary '{src_term}' -> {tgt}")
if a.avoid:
    tgt_all = "\n".join(T.values())
    for line in open(a.avoid, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"): continue
        lang, _, term = line.partition(":")
        if lang.strip() in (a.lang, "*") and term.strip() and term.strip() in tgt_all:
            report("FAIL", f"avoid-list term present: {term.strip()}")

body = "\n".join(T.values())
if a.lang in ("zh-Hans", "ja"):
    half = len(re.findall(r"[\u3040-\u30ff\u4e00-\u9fff][,.!?;:]", body))
    report("PASS" if half == 0 else "WARN", f"half-width punctuation directly after CJK characters: {half}")
if a.lang == "zh-Hans":
    sp = len(re.findall(r"[\u4e00-\u9fff] [\u4e00-\u9fff]", body))
    report("PASS" if sp == 0 else "WARN", f"spaces between Chinese characters: {sp}")
if a.lang == "ko":
    hangul = len(re.findall(r"[\uac00-\ud7a3]", body))
    report("PASS" if hangul > 50 else "FAIL", f"Hangul characters present: {hangul}")
if a.lang == "ja":
    report("PASS" if re.search(r"[\u3040-\u309f]", body) else "FAIL", "hiragana present (not Chinese by mistake)")
    mix = ("です" in body or "ます" in body) and re.search(r"(だ|である)。", body)
    report("WARN" if mix else "PASS", "polite/plain register mix" if mix else "register consistent")
print(f"\n{'FAIL' if fails else 'PASS'}: {fails} failing checks")
sys.exit(1 if fails else 0)
