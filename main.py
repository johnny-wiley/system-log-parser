#!/usr/bin/env python3
"""
System Log Parser & Report Generator
------------------------------------
Reads a .log (or any text) file, extracts ERROR/WARNING messages,
counts occurrences, and records first/last seen timestamps.

Usage:
  python main.py --input sample.log --format xlsx
  python main.py -i /path/to/your.log -f csv --levels ERROR WARNING INFO

Notes:
- Expects log lines like: "[2025-08-14 10:22:45] ERROR: Something happened"
- You can tweak the regex pattern(s) below to match your log style.
"""

import argparse
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

try:
    import pandas as pd
except ImportError as e:
    print("pandas is required. Install with: pip install -r requirements.txt")
    raise

# Supported datetime formats to try (add more if needed)
DATETIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S,%f",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
]

# Regex patterns to match common log styles.
# 1) Sample: "[2025-08-14 10:22:45] ERROR: Message text"
PATTERN_BRACKET = re.compile(
    r'^\[(?P<ts>.+?)\]\s*(?P<level>[A-Z]+)\s*:\s*(?P<msg>.*)$'
)

# 2) Sample: "2025-08-14 10:22:45,123 ERROR Message text"
PATTERN_SPACE = re.compile(
    r'^(?P<ts>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[,\.]\d{1,6})?)\s+(?P<level>[A-Z]+)\s+(?P<msg>.*)$'
)

PATTERNS = [PATTERN_BRACKET, PATTERN_SPACE]


def parse_args():
    p = argparse.ArgumentParser(description="System Log Parser & Report Generator")
    p.add_argument("-i", "--input", required=True, help="Path to log file")
    p.add_argument("-f", "--format", choices=["xlsx", "csv"], default="xlsx", help="Output format")
    p.add_argument("--levels", nargs="+", default=["ERROR", "WARNING", "INFO"], help="Log levels to include (e.g., ERROR WARNING INFO)")
    p.add_argument("-o", "--output", default=None, help="Output file path (optional). Defaults to johnny_log_parser_summary.xlsx or .csv")
    return p.parse_args()


def try_parse_dt(s: str):
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # As a last resort, try trimming fractional seconds quirks
    try:
        if "," in s:
            base = s.split(",")[0]
            return datetime.strptime(base, "%Y-%m-%d %H:%M:%S")
    except Exception:
        pass
    return None


def parse_line(line: str):
    line = line.rstrip("\n")
    for pat in PATTERNS:
        m = pat.match(line)
        if m:
            ts_raw = m.group("ts").strip()
            level = m.group("level").strip()
            msg = m.group("msg").strip()
            ts = try_parse_dt(ts_raw)
            return ts, level, msg
    return None, None, None


def main():
    args = parse_args()
    log_path = Path(args.input)
    if not log_path.exists():
        raise FileNotFoundError(f"Input file not found: {log_path}")

    allowed = set(l.upper() for l in args.levels)

    rows = []
    total_lines = 0

    with log_path.open("r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            total_lines += 1
            ts, level, msg = parse_line(line)
            if level is None:
                continue
            if level.upper() in allowed:
                rows.append((ts, level.upper(), msg))

    if not rows:
        print("No matching log entries found with the given levels/patterns.")
        return

    # Aggregate stats
    counts = Counter(msg for _, _, msg in rows)
    first_seen = defaultdict(lambda: None)
    last_seen = defaultdict(lambda: None)

    for ts, _, msg in rows:
        if ts is None:
            continue
        if first_seen[msg] is None or ts < first_seen[msg]:
            first_seen[msg] = ts
        if last_seen[msg] is None or ts > last_seen[msg]:
            last_seen[msg] = ts

    # Build DataFrame
    data = []
    for msg, cnt in counts.items():
        data.append({
            "Message": msg,
            "Count": cnt,
            "First Seen": first_seen[msg],
            "Last Seen": last_seen[msg],
        })

    df = pd.DataFrame(data)
    # Sort: most frequent first, then latest last seen
    df = df.sort_values(by=["Count", "Last Seen"], ascending=[False, False]).reset_index(drop=True)

    # Also compute a tiny high-level summary
    earliest = min((t for t in first_seen.values() if t is not None), default=None)
    latest = max((t for t in last_seen.values() if t is not None), default=None)
    high_level = {
        "Total lines": total_lines,
        "Matched entries": len(rows),
        "Unique messages": len(counts),
        "Time range start": earliest.isoformat(sep=" ") if earliest else "N/A",
        "Time range end": latest.isoformat(sep=" ") if latest else "N/A",
        "Levels included": ", ".join(sorted(allowed)),
    }

    # Determine output path
    out_path = Path(args.output) if args.output else log_path.with_name(f"johnny_log_parser_summary.{args.format}")
    if args.format == "xlsx":
        try:
            with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Summary")
                # Write the high-level summary on another sheet
                meta = pd.DataFrame(list(high_level.items()), columns=["Metric", "Value"])
                meta.to_excel(writer, index=False, sheet_name="Overview")
        except Exception as e:
            print("Failed writing .xlsx (missing openpyxl?). Try: pip install openpyxl")
            raise
    else:
        df.to_csv(out_path, index=False)

    print("✅ Done!")
    print(f"Output saved to: {out_path}")
    print("\nOverview:")
    for k, v in high_level.items():
        print(f"- {k}: {v}")


if __name__ == "__main__":
    main()
