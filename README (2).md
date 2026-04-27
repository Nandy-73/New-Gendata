# 🧬 GeneBlock v2 — Secure Genomic Blockchain System

## What's New in v2

### ✅ Feature 1 — Security Fixes

|---|---|---|
| Hardcoded admin password | `"Admin@123"` in plaintext | SHA-256 hashed comparison |
| `eval()` on decrypted data | `eval(decrypted)` | `json.loads(decrypted)` |
| Email credentials exposed | Hardcoded in source | `os.environ.get("GMAIL_APP_PASSWORD")` |

### ✅ Feature 2 — Blockchain Persistence + Consensus
- **SQLite database** — blockchain survives page refresh
- **Majority-vote consensus** — 3 servers vote on their chain fingerprint; 2-of-3 wins
- Compromised servers auto-recovered from the majority chain

### ✅ Feature 3 — Live Security Dashboard
- Real-time integrity score bar (green → yellow → red)
- Per-server health status cards (HEALTHY / COMPROMISED)
- Live attack timeline with timestamps
- Metric cards: total blocks, tampered count, attacks, integrity %

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy env file
cp .env.example .env
# (optionally fill in GMAIL_APP_PASSWORD)

# 3. Make sure heart.csv is in the same folder
#    (or the app will generate demo data automatically)

# 4. Run
streamlit run app.py
```

---

## Demo Script (for your presentation)

### Step 1 — Show Dashboard
- Point out the integrity bar (100% green at start)
- Show all 3 servers as HEALTHY

### Step 2 — Simulate Attack
- Go to "Simulate Tampering"
- Pick Server 1, Block 3
- Change Patient ID → click "Simulate Hack"
- Dashboard updates: Server 1 goes RED, integrity drops

### Step 3 — Show Consensus
- Click "Run Consensus Now"
- Show voting results: Server 2 & 3 agree, Server 1 is minority
- Auto-recovery triggers → Server 1 restored

### Step 4 — Show Security Fixes
- Point out `.env.example` — no hardcoded secrets
- Show admin login uses hash comparison, not plaintext
- Show `json.loads()` instead of `eval()`

### Step 5 — Show Persistence
- Refresh the page
- Blockchain is still there (SQLite database)

---

## Admin Credentials (for demo)
Password: `Admin@123`
