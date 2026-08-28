#!/usr/bin/env python3
"""Daily rating sync for daydrop.beatroot.dev.

Sums DayDrop's App Store ratings across every storefront via the iTunes lookup
API, then rewrites the numbers everywhere the site states them (visible hero
line, sticky bar, JSON-LD aggregateRating, roundup row). Commits and pushes
only when a number actually changed, so the GH Pages deploy and IndexNow ping
happen at most once per real change.

Per-country results are cached in scripts/rating_state.json; a storefront that
errors on a given run reuses its last-known count instead of deflating the
worldwide total.
"""

import json, re, sys, time, subprocess, urllib.request
from pathlib import Path

APP_ID = "6759470132"
REPO = Path(__file__).resolve().parent.parent
STATE = Path(__file__).resolve().parent / "rating_state.json"

COUNTRIES = (
    "us gb ca au nz ie in pk bd lk np de fr it es pt nl be lu at ch dk se no fi "
    "is pl cz sk hu ro bg gr hr si lt lv ee ua md rs ba mk al me tr ru kz uz az "
    "am ge by jp kr cn hk tw sg my th vn ph id kh la mm bn mn br mx ar cl co pe "
    "ve ec uy py bo cr pa do gt hn sv ni jm tt bs bb ae sa il qa kw bh om jo lb "
    "eg ma dz tn ly za ng ke gh tz ug zw zm mz ao sn ci cm cd mg mu na bw rw"
).split()


def fetch_country(cc):
    url = f"https://itunes.apple.com/lookup?id={APP_ID}&country={cc}"
    with urllib.request.urlopen(url, timeout=15) as r:
        data = json.load(r)
    if not data.get("results"):
        return None
    a = data["results"][0]
    return {"count": a.get("userRatingCount", 0),
            "avg": a.get("averageUserRating", 0.0)}


def collect():
    state = json.loads(STATE.read_text()) if STATE.exists() else {}
    for cc in COUNTRIES:
        try:
            res = fetch_country(cc)
            if res is not None:
                state[cc] = res
            elif cc not in state:
                state[cc] = {"count": 0, "avg": 0.0}
        except Exception:
            pass  # keep last-known value for this storefront
        time.sleep(0.4)  # stay far under the iTunes API rate limit
    STATE.write_text(json.dumps(state, indent=1, sort_keys=True))
    total = sum(v["count"] for v in state.values())
    weighted = sum(v["count"] * v["avg"] for v in state.values())
    avg = round(weighted / total, 1) if total else 0.0
    return avg, total


def sub_all(path, patterns):
    s = path.read_text()
    orig = s
    for pat, repl in patterns:
        s = re.sub(pat, repl, s)
    if s != orig:
        path.write_text(s)
        return True
    return False


def main():
    avg, total = collect()
    if total < 50:  # sanity floor: a bad run must never publish a tiny number
        print(f"refusing implausible total {total}", file=sys.stderr)
        sys.exit(1)
    print(f"worldwide: {avg} from {total}")

    changed = False
    idx = REPO / "index.html"
    changed |= sub_all(idx, [
        (r'(id="rating-value">)[\d.]+', rf"\g<1>{avg}"),
        (r'(id="rating-count">)[\d,]+', rf"\g<1>{total}"),
        (r'("ratingValue": ")[\d.]+', rf"\g<1>{avg}"),
        (r'("ratingCount": ")\d+', rf"\g<1>{total}"),
        (r'(id="sticky-rating">)[\d.]+', rf"\g<1>{avg}"),
        (r'(id="stat-rating-value">)[\d.]+', rf"\g<1>{avg}"),
        (r'(id="stat-rating-count">)[\d,]+', rf"\g<1>{total}"),
    ])
    roundup = REPO / "blog" / "best-countdown-apps-2026.html"
    changed |= sub_all(roundup, [
        (r'(<strong>DayDrop</strong> \(v[\d.]+\)</td>\s*<td>)[\d.]+★ \(\d+\)',
         rf"\g<1>{avg}★ ({total})"),
    ])

    if not changed:
        print("no change")
        return

    subprocess.run(["git", "-C", str(REPO), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(REPO), "commit", "-q", "-m",
                    f"Auto-update App Store rating: {avg} from {total}"], check=True)
    subprocess.run(["git", "-C", str(REPO), "push", "-q", "origin", "main"], check=True)
    subprocess.run([str(REPO / "indexnow-submit.sh")], cwd=str(REPO), check=False)
    print("published")


if __name__ == "__main__":
    main()
