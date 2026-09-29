import re
from datetime import date

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

_DATE = r"(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?,?\s+\d{4}|\d{1,2}/\d{4}|\d{4})"
_END = rf"(?:{_DATE}|present|current|now|ongoing|till date|to date)"
RANGE_RE = re.compile(rf"({_DATE})\s*(?:-|–|—|to|until)\s*({_END})", re.IGNORECASE)

EXP_HEADING = re.compile(r"^\s*(?:professional\s+|work\s+|relevant\s+)?(?:experience|employment|work history|internships?)\b.*$", re.IGNORECASE)
OTHER_HEADING = re.compile(
    r"^\s*(?:education|academic.*|projects?|skills?|technical skills|certifications?|awards?|"
    r"achievements?|publications?|summary|profile|objective|languages|interests|references)\s*:?\s*$",
    re.IGNORECASE)


def _to_month_index(token: str, today: date) -> int:
    t = token.strip().lower().rstrip(",")
    if t in {"present", "current", "now", "ongoing", "till date", "to date"}:
        return today.year * 12 + today.month
    m = re.match(r"([a-z]+)\.?,?\s+(\d{4})", t)
    if m and m.group(1)[:3] in MONTHS:
        return int(m.group(2)) * 12 + MONTHS[m.group(1)[:3]]
    m = re.match(r"(\d{1,2})/(\d{4})", t)
    if m:
        return int(m.group(2)) * 12 + int(m.group(1))
    return int(t) * 12 + 1  # bare year


def _experience_section(text: str) -> str:
    """Return only the experience section, or the text with the education section removed."""
    lines = text.splitlines()
    in_exp, exp_lines = False, []
    for line in lines:
        if EXP_HEADING.match(line) and len(line.strip()) < 40:
            in_exp = True
            continue
        if OTHER_HEADING.match(line):
            in_exp = False
            continue
        if in_exp:
            exp_lines.append(line)
    if exp_lines:
        return "\n".join(exp_lines)

    kept, in_edu = [], False
    for line in lines:
        if re.match(r"^\s*(?:education|academic.*)\s*:?\s*$", line, re.IGNORECASE):
            in_edu = True
            continue
        if OTHER_HEADING.match(line) or EXP_HEADING.match(line):
            in_edu = False
        if not in_edu:
            kept.append(line)
    return "\n".join(kept)


def years_from_date_ranges(text: str, today: date | None = None) -> float:
    today = today or date.today()
    now = today.year * 12 + today.month
    intervals = []
    for m in RANGE_RE.finditer(_experience_section(text)):
        try:
            start, end = _to_month_index(m.group(1), today), _to_month_index(m.group(2), today)
        except ValueError:
            continue
        end = min(end, now)
        if end > start:
            intervals.append((start, end))
    intervals.sort()
    merged = []
    for s, e in intervals:  # merge overlaps so parallel roles aren't double-counted
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return round(sum(e - s for s, e in merged) / 12, 1)


EDU_PATTERNS = [
    ("phd", r"\bph\.?\s?d\b|\bdoctorate\b|\bdoctoral\b"),
    ("master", r"\bmaster(?:'s|s)?\s+(?:of|in|degree)\b|\bm\.?\s?sc\b|\bm\.?\s?s\.?\s+in\b|\bmba\b|\bm\.?\s?tech\b|\bm\.?\s?phil\b|\bmcs\b"),
    ("bachelor", r"\bbachelor(?:'s|s)?\b|\bb\.?\s?sc?\.?(?:\s*\(?(?:cs|hons)\)?)?(?=[\s,(:\-–—]|$)|\bb\.?\s?tech\b|\bbcs\b|\bbscs\b|\bb\.?e\.?\s+in\b|\bundergraduate\b"),
    ("associate", r"\bassociate\s+(?:degree|of)\b|\bdiploma\b"),
]


def education_level(text: str) -> str:
    for level, pattern in EDU_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return level
    return "none"
