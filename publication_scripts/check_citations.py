#!/usr/bin/env python3
"""
Diagnostic script: scan article bodies + footnotes for parenthetical citations
and attempt to match each to a citation entry in the article's _data YAML.

Usage:
    cd /path/to/tandp
    python3 publication_scripts/check_citations.py [short-name ...]

    With no arguments, processes all articles that have a _data YAML with citations.
"""

import re
import sys
import yaml
from pathlib import Path

POSTS_DIR  = Path("_posts")
DATA_DIR   = Path("_data")


# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------

def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_front_matter(text):
    """Return parsed YAML front matter dict, or {}."""
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(text[3:end]) or {}
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def normalize(s):
    """
    Lowercase, strip possessives, strip apostrophes, strip 'and'/'&',
    strip bracketed years, collapse whitespace.  Used for fuzzy matching only.
    """
    s = re.sub(r"'s\b", '', s)      # strip possessive 's  (Caplin's -> Caplin)
    s = re.sub(r"'", '', s)          # strip remaining apostrophes (O'Conner -> OConner)
    s = re.sub(r'-', ' ', s)         # hyphens to spaces (Godfrey-Smith -> Godfrey Smith)
    s = s.lower()
    s = re.sub(r'\band\b', ' ', s)
    s = re.sub(r'&', ' ', s)
    s = re.sub(r'\[.*?\]', '', s)   # remove [1794] brackets
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def key_to_match_string(key):
    """'Vande_Moortele_2013' -> 'Vande Moortele 2013'"""
    return key.replace('_', ' ')


# ---------------------------------------------------------------------------
# Citation extraction from text
# ---------------------------------------------------------------------------

# Matches one author-year chunk, e.g.:
#   "Vande Moortele 2013"
#   "Lerdahl and Jackendoff 1983"
#   "Smith et al. 2005"
#   "Bach [1753] 1762"
#   "Rothstein [1989] 2007"
#   "Bach 1753--62"
AUTHOR_YEAR = re.compile(
    r"""
    (
        [A-ZÀÁÂÄÆÇÈÉÊËÎÏÔŒÙÛÜ][a-zA-ZÀ-ÿ\-']+           # First word of first surname
        (?:\s+[A-ZÀÁÂÄÆÇÈÉÊËÎÏÔŒÙÛÜ][a-zA-ZÀ-ÿ\-']+)*   # Additional words (compound surname)
        (?:
            (?:\s+and\s+|\s+&\s+)                          # "and" / "&"
            [A-ZÀÁÂÄÆÇÈÉÊËÎÏÔŒÙÛÜ][a-zA-ZÀ-ÿ\-']+        # Second author surname
            (?:\s+[A-ZÀÁÂÄÆÇÈÉÊËÎÏÔŒÙÛÜ][a-zA-ZÀ-ÿ\-']+)*
        )*
        (?:\s+et\s+al\.?)?                                  # optional "et al."
    )
    \s+
    (?:\[[\d\-–]+\]\s*)?                                    # optional [original year]
    (
        \d{4}(?:--\d{2,4})?[a-z]?                          # year, possibly range/suffix
    )
    """,
    re.VERBOSE,
)


def extract_citations_from_text(text):
    """
    Return a list of dicts  { 'author': str, 'year': str, 'text': str, 'context': str }
    for every author-year citation found inside parentheses (or after an author
    name followed by a parenthesised year).

    Handles:
      (Author Year)
      (Author Year, pages)
      (Author Year; Author2 Year2)
      (Author Year, Author2 Year2)          <- comma-separated citations
      Author (Year)                          <- narrative form
    """
    results = []

    # ---- 1. Parenthetical form: (... Author Year ...) ----
    for paren_match in re.finditer(r'\(([^)]{3,200})\)', text):
        paren_content = paren_match.group(1)
        context = paren_content.strip()

        # Skip obvious non-citation parens
        if re.match(r'^\s*(?:Example|Figure|Fig\.|mm\.|m\.|p\.|pp\.|ibid)', context, re.I):
            continue
        if re.search(r'include|figure_key|footnote', context):
            continue

        # Strip leading qualifiers: "see", "cf.", "see also", "e.g.,", "in", "as in"
        cleaned = re.sub(
            r'^(?:see\s+also\s+|see\s+|cf\.?\s+|also\s+|e\.g\.,?\s+|i\.e\.,?\s+|'
            r'as\s+in\s+|in\s+|as\s+translated\s+in\s+)',
            '', context, flags=re.I)

        # Split on semicolons first (clear separator between citations)
        for chunk in re.split(r';\s*', cleaned):
            chunk = chunk.strip()
            # Strip leading qualifiers again after split
            chunk = re.sub(
                r'^(?:see\s+also\s+|see\s+|cf\.?\s+|also\s+|e\.g\.,?\s+)',
                '', chunk, flags=re.I)

            # Find all author-year pairs in this chunk
            for m in AUTHOR_YEAR.finditer(chunk):
                author = re.sub(r"'s$", '', m.group(1).strip())  # strip possessive
                year_raw = m.group(2)
                # Take only the first 4-digit year if it's a range like 1753--62
                year = re.match(r'\d{4}', year_raw).group()
                # Append year suffix (a/b/c) if present
                suffix = re.search(r'\d{4}([a-z])', year_raw)
                if suffix:
                    year += suffix.group(1)
                results.append({
                    'author': author,
                    'year':   year,
                    'text':   f"{author} {year}",
                    'context': context,
                })

    # ---- 2. Narrative form: Author (Year) ----
    # Matches "Smith (2020)" or "Smith and Jones (2020)" directly preceding the
    # parenthetical year.  For full-name forms like "Steven Pinker and Paul
    # Bloom (1990)" this will only capture "Bloom 1990"; those cases are
    # handled by the last-surname matching strategy in try_match().
    for m in re.finditer(
        r'([A-ZÀÁÂÄÆÇÈÉÊËÎÏÔŒÙÛÜ][a-zA-ZÀ-ÿ\-\']+(?:\s+[A-ZÀÁÂÄÆÇÈÉÊËÎÏÔŒÙÛÜ][a-zA-ZÀ-ÿ\-\']+)*'
        r'(?:\s+and\s+[A-ZÀÁÂÄÆÇÈÉÊËÎÏÔŒÙÛÜ][a-zA-ZÀ-ÿ\-\']+(?:\s+[A-ZÀÁÂÄÆÇÈÉÊËÎÏÔŒÙÛÜ][a-zA-ZÀ-ÿ\-\']+)*)?)'
        r'\s*\(\s*(\d{4}[a-z]?)\s*(?:,\s*[^)]{0,40})?\)',
        text
    ):
        author = re.sub(r"'s$", '', m.group(1).strip())
        year   = m.group(2)
        results.append({
            'author':  author,
            'year':    year,
            'text':    f"{author} {year}",
            'context': m.group(0),
        })

    return results


# ---------------------------------------------------------------------------
# Matching logic
# ---------------------------------------------------------------------------

def build_match_maps(citations_data):
    """
    Accept either:
      - a list:  [{'name': 'Foo_2013', 'citation': '...'}, ...]
      - a dict:  {'Foo_2013': {'citation': '...'}, ...}
    Return two dicts:
      exact_map  : 'Foo 2013'  -> 'Foo_2013'
      normal_map : normalize('Foo 2013') -> 'Foo_2013'
    """
    exact_map  = {}
    normal_map = {}

    if isinstance(citations_data, list):
        keys = [entry.get('name', '') for entry in citations_data if isinstance(entry, dict)]
    elif isinstance(citations_data, dict):
        keys = list(citations_data.keys())
    else:
        return exact_map, normal_map

    for key in keys:
        if not key:
            continue
        match_str = key_to_match_string(key)
        exact_map[match_str] = key
        normal_map[normalize(match_str)] = key
    return exact_map, normal_map


def try_match(citation_text, exact_map, normal_map):
    """
    Return (key, match_type) or (None, None).
    match_type is 'exact' or 'fuzzy'.
    """
    # 1. Exact
    if citation_text in exact_map:
        return exact_map[citation_text], 'exact'

    # 2. Normalised (handles "and" vs nothing, brackets, etc.)
    norm = normalize(citation_text)
    if norm in normal_map:
        return normal_map[norm], 'fuzzy'

    # 3. First-author + year (handles "Smith and Jones 2013" matching "Smith_2013")
    year_m = re.search(r'(\d{4}[a-z]?)', citation_text)
    if year_m:
        year = year_m.group(1)
        first_author = citation_text.split()[0]
        for match_str, key in exact_map.items():
            parts = match_str.rsplit(' ', 1)
            if len(parts) == 2 and parts[1] == year and parts[0].startswith(first_author):
                return key, 'fuzzy'

    # 4. Last-word of author + year (handles "See Earp 1991", "Justin London 2012",
    #    "As Burstein 2020", "Matt BaileyShea 2021", etc.)
    year_end = re.search(r'(\d{4}[a-z]?)$', citation_text.strip())
    if year_end:
        author_part = citation_text[:year_end.start()].strip()
        if ' ' in author_part:  # only useful when there are multiple words
            last_word = author_part.split()[-1]
            candidate = f"{last_word} {year_end.group(1)}"
            if candidate in exact_map:
                return exact_map[candidate], 'fuzzy'
            norm_cand = normalize(candidate)
            if norm_cand in normal_map:
                return normal_map[norm_cand], 'fuzzy'

    return None, None


# ---------------------------------------------------------------------------
# Per-article scanning
# ---------------------------------------------------------------------------

def scan_article(short_name):
    data_path = DATA_DIR / f"{short_name}.yaml"
    if not data_path.exists():
        return None

    data = load_yaml(data_path) or {}
    citations_list = data.get('citations') or []
    if not citations_list:
        return None

    exact_map, normal_map = build_match_maps(citations_list)

    # Gather all text to scan: article body + all footnote values
    texts = []

    # Article post file
    post_files = list(POSTS_DIR.rglob(f"*-{short_name}.md"))
    if post_files:
        raw = post_files[0].read_text(encoding="utf-8")
        fm  = get_front_matter(raw)
        # Body only (strip front matter and liquid tags)
        body = re.sub(r'^---.*?---\s*', '', raw, flags=re.DOTALL)
        body = re.sub(r'\{[%{].*?[%}]\}', ' ', body, flags=re.DOTALL)
        texts.append(('body', body))
        # Also scan abstract
        if fm.get('abstract'):
            texts.append(('abstract', str(fm['abstract'])))

    # Footnotes from data YAML
    for key, val in data.items():
        if re.match(r'footnote_\d+', key) and isinstance(val, str):
            texts.append((key, val))

    # Collect and deduplicate citations across all text sources
    seen_texts = {}   # citation_text -> list of sources
    for source, text in texts:
        for cit in extract_citations_from_text(text):
            t = cit['text']
            seen_texts.setdefault(t, []).append(source)

    # Match each unique citation
    matched   = []  # (citation_text, key, match_type, sources)
    unmatched = []  # (citation_text, sources)

    for cit_text, sources in sorted(seen_texts.items()):
        key, mtype = try_match(cit_text, exact_map, normal_map)
        if key:
            matched.append((cit_text, key, mtype, sources))
        else:
            unmatched.append((cit_text, sources))

    # Keys that were never matched by anything
    matched_keys = {key for _, key, _, _ in matched}
    if isinstance(citations_list, list):
        all_keys = [e.get('name', '') for e in citations_list if isinstance(e, dict)]
    else:
        all_keys = list(citations_list.keys())
    unused_keys = [k for k in all_keys if k and k not in matched_keys]

    return {
        'matched':     matched,
        'unmatched':   unmatched,
        'unused_keys': unused_keys,
        'total_keys':  len(citations_list),
    }


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

def print_report(short_name, result):
    W = 65
    print(f"\n{'='*W}")
    print(f"  {short_name.upper()}")
    print(f"{'='*W}")
    print(f"  YAML citation keys : {result['total_keys']}")
    print(f"  Found in text      : {len(result['matched'])} matched, "
          f"{len(result['unmatched'])} unmatched")

    if result['matched']:
        print(f"\n  ✓ MATCHED ({len(result['matched'])})")
        for cit_text, key, mtype, sources in result['matched']:
            tag = ' [fuzzy]' if mtype == 'fuzzy' else ''
            src = ', '.join(sorted(set(sources)))
            if cit_text == key_to_match_string(key):
                print(f"    {cit_text}  [{src}]")
            else:
                print(f"    {cit_text}  →  {key}{tag}  [{src}]")

    if result['unmatched']:
        print(f"\n  ✗ UNMATCHED ({len(result['unmatched'])})  — no key found in YAML")
        for cit_text, sources in result['unmatched']:
            src = ', '.join(sorted(set(sources)))
            print(f"    {cit_text}  [{src}]")

    if result['unused_keys']:
        print(f"\n  ○ YAML KEYS NEVER CITED ({len(result['unused_keys'])})")
        for key in result['unused_keys']:
            print(f"    {key}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    targets = sys.argv[1:] if len(sys.argv) > 1 else None

    if targets is None:
        # Auto-discover: any _data YAML with a 'citations' list
        targets = []
        for p in sorted(DATA_DIR.glob("*.yaml")):
            name = p.stem
            d = load_yaml(p) or {}
            if d.get('citations'):
                targets.append(name)

    for name in targets:
        result = scan_article(name)
        if result is None:
            print(f"\n[{name}] — no citations data found, skipping")
            continue
        print_report(name, result)
