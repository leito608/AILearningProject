"""Top-10 candidates for the next 2-digit lottery draw, from lotto_history.csv.

Signals (each normalised to a probability over 00-99):
  freq    - all-time frequency
  recent  - exponentially decayed frequency (recent draws weigh more)
  overdue - how long a number has been absent
  digits  - tens/units digit frequency (recent window), multiplied together
  markov  - what followed the previous draw's number / its units digit
  calendar- numbers drawn on the same day-of-month (1st/16th) and weekday as the target date
Always-on bonuses (BONUS weights, added on top of the tuned blend):
  follow  - numbers that historically came right after the previous winner
  samedate- numbers drawn on the same day+month in other years
  sameweekday - numbers drawn on the same weekday as the input date
  repeat2y - numbers that appeared 2+ times in the 2 years before the input date
The signals are blended with weights picked by walk-forward backtesting.
NOTE: a fair lottery is random; expect hit rate near the 10% baseline for top-10.
"""
import csv
import datetime as dt
import itertools
import os
import sys
from collections import Counter, defaultdict

CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lotto_history.csv")
TOP_N = 10
NUMS = [f"{i:02d}" for i in range(100)]


def load(path):
    rows = []
    with open(path, encoding="utf-8-sig") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) < 3 or not row[2].strip().isdigit():
                continue
            d, m, y = row[0].split("/")
            rows.append(((int(y), int(m), int(d)), row[2].strip().zfill(2)))
    rows.sort()  # oldest -> newest
    return rows


def norm(d):
    s = sum(d.values()) or 1
    return {k: v / s for k, v in d.items()}


def to_date(ymd):
    y = ymd[0] - 543 if ymd[0] > 2400 else ymd[0]
    return dt.date(y, ymd[1], ymd[2])


def parse_date(text):
    d, m, y = (int(p) for p in text.strip().split("/"))
    return to_date((y, m, d))


def signals(hist, dates, target):
    """hist: numbers oldest -> newest; dates: matching dt.date list; target: draw date."""
    n = len(hist)
    cnt = Counter(hist)
    freq = norm({k: cnt[k] + 1 for k in NUMS})

    recent = {k: 1.0 for k in NUMS}
    w = 1.0
    for x in reversed(hist):
        recent[x] += w
        w *= 0.985
    recent = norm(recent)

    last_seen = {x: i for i, x in enumerate(hist)}
    overdue = norm({k: 1 + (n - last_seen.get(k, -1)) / 100.0 for k in NUMS})

    win = hist[-150:]
    t = Counter(x[0] for x in win)
    u = Counter(x[1] for x in win)
    digits = norm({k: (t[k[0]] + 1) * (u[k[1]] + 1) for k in NUMS})

    nxt, nxt_u = defaultdict(Counter), defaultdict(Counter)
    for a, b in zip(hist, hist[1:]):
        nxt[a][b] += 1
        nxt_u[a[1]][b] += 1
    prev = hist[-1]
    markov = norm({k: 1 + 2 * nxt[prev][k] + nxt_u[prev[1]][k] for k in NUMS})

    same_day, same_wd = Counter(), Counter()
    for x, d in zip(hist, dates):
        if d.day == target.day:
            same_day[x] += 1
        if d.weekday() == target.weekday():
            same_wd[x] += 1
    calendar = norm({k: 1 + 2 * same_day[k] + same_wd[k] for k in NUMS})

    follow = norm({k: 1 + 5 * nxt[prev][k] for k in NUMS})
    same_date = Counter(x for x, d in zip(hist, dates)
                        if (d.day, d.month) == (target.day, target.month))
    samedate = norm({k: 1 + 5 * same_date[k] for k in NUMS})
    sameweekday = norm({k: 1 + 5 * same_wd[k] for k in NUMS})

    try:
        cutoff = target.replace(year=target.year - 2)
    except ValueError:  # 29 Feb
        cutoff = target.replace(year=target.year - 2, day=28)
    last2y = Counter(x for x, d in zip(hist, dates) if d >= cutoff)
    repeat2y = norm({k: 1 + 5 * max(last2y[k] - 1, 0) for k in NUMS})

    return {"repeat2y": repeat2y, "follow": follow, "samedate": samedate, "sameweekday": sameweekday, "freq": freq, "recent": recent, "overdue": overdue,
            "digits": digits, "markov": markov, "calendar": calendar}


BONUS = {"follow": 1.0, "samedate": 1.0, "sameweekday": 1.0, "repeat2y": 1.0}


def blend(sig, weights):
    tw = sum(weights.values()) or 1
    return {k: sum(weights[s] * sig[s][k] for s in weights) / tw
            + sum(BONUS[b] * sig[b][k] for b in BONUS) for k in NUMS}


def top(score, k=TOP_N):
    return sorted(NUMS, key=lambda x: -score[x])[:k]


def tune(rows, k=TOP_N, test_draws=150):
    """Walk-forward backtest: precompute signals once per test draw."""
    names = ["freq", "recent", "overdue", "digits", "markov", "calendar"]
    start = max(len(rows) - test_draws, 100)
    cases = []
    for i in range(start, len(rows)):
        sig = signals([x[1] for x in rows[:i]], [to_date(x[0]) for x in rows[:i]],
                      to_date(rows[i][0]))
        cases.append((sig, rows[i][1]))
    best = None
    for combo in itertools.product([0, 1, 2], repeat=len(names)):
        if not any(combo):
            continue
        wts = dict(zip(names, combo))
        hits = sum(ans in top(blend(sig, wts), k) for sig, ans in cases)
        if best is None or hits > best[0]:
            best = (hits, wts)
    return best[0] / len(cases), best[1], len(cases)


def main():
    rows = load(CSV)
    arg = sys.argv[1] if len(sys.argv) > 1 else input("Next draw date (DD/MM/YYYY, e.g. 16/11/2026): ")
    target = parse_date(arg)
    rows = [r for r in rows if to_date(r[0]) < target]  # only draws before the target date
    if len(rows) < 120:
        sys.exit("Not enough history before that date (need at least 120 draws).")
    f, l = rows[0][0], rows[-1][0]
    print(f"Loaded {len(rows)} draws ({f[2]:02d}/{f[1]:02d}/{f[0]} -> {l[2]:02d}/{l[1]:02d}/{l[0]})")
    rate, wts, total = tune(rows)
    print(f"Backtest top-{TOP_N} hit rate: {rate:.1%} over {total} draws "
          f"(random baseline {TOP_N}.0%) | weights {wts}")

    score = blend(signals([x[1] for x in rows], [to_date(x[0]) for x in rows], target), wts)
    s = sum(score.values())
    print(f"\nTop {TOP_N} candidates for draw on {target:%d/%m/%Y}:")
    for i, k in enumerate(top(score), 1):
        print(f"  {i}. {k}   score {score[k] / s:.2%}")
    print(f"\nAll scores (00-99), ranked:")
    ranked = sorted(NUMS, key=lambda x: -score[x])
    for i in range(0, 100, 10):
        print("  " + "   ".join(f"{k}:{score[k] / s:5.2%}" for k in ranked[i:i + 10]))
    print("\nDisclaimer: draws are random; this is statistical pattern-matching, not a guarantee.")


if __name__ == "__main__":
    sys.exit(main())
