# System Log Parser & Report Generator

A beginner-friendly Python tool that reads `.log` files, extracts ERROR/WARNING entries,
counts how often each message appears, and records when it was first and last seen.
Outputs to **Excel (.xlsx)** or **CSV**.

## ✨ Features
- Parse common log formats (bracketed `[YYYY-MM-DD HH:MM:SS] LEVEL: message` and space-delimited)
- Include specific levels (default: `ERROR` and `WARNING`)
- Summary report with **Count**, **First Seen**, and **Last Seen**
- Saves to **`log_summary.xlsx`** (default) or CSV
- Extra **Overview** sheet with high-level stats (when using `.xlsx`)

## 🚀 Quick Start
1. **Install Python 3.9+**
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run with the included sample:
   ```bash
   python main.py --input sample.log --format xlsx
   ```
4. Open the generated `log_summary.xlsx`

## 🧪 Example Log (`sample.log`)
```
[2025-08-14 10:22:45] ERROR: Database connection failed
[2025-08-14 10:22:50] INFO: Retrying connection
[2025-08-14 10:23:05] ERROR: Database connection failed
[2025-08-14 10:25:00] WARNING: High memory usage detected
2025-08-14 10:26:00,123 ERROR Database connection failed
2025-08-14 10:27:11 WARNING Disk almost full
```

## 🧭 CLI Usage
```bash
python main.py --input /path/to/your.log --format xlsx
python main.py -i your.log -f csv --levels ERROR WARNING INFO
```

## 🧩 Customize Patterns
If your logs don't match the defaults, open `main.py` and edit/add regex patterns in `PATTERNS`.

## 📦 Requirements
See `requirements.txt`.

## 📄 License
MIT
