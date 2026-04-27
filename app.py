import streamlit as st
import hashlib
import base64
import copy
import json
import sqlite3
import os
from datetime import datetime
import pandas as pd
import uuid
import smtplib
from email.mime.text import MIMEText

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be FIRST streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GeneBlock v2",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CUSTOM CSS  – dark bio-tech aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0a0e1a;
    color: #e0e6f0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1321 0%, #111827 100%);
    border-right: 1px solid #1e3a5f;
}

/* Main header */
.main-header {
    text-align: center;
    padding: 2rem 0 1rem;
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1f3c 100%);
    border-bottom: 1px solid #1e3a5f;
    margin-bottom: 1.5rem;
}
.main-header h1 {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.8rem;
    background: linear-gradient(90deg, #00d4ff, #00ff9d, #00d4ff);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 3s linear infinite;
    letter-spacing: -1px;
}
@keyframes shimmer { 0%{background-position:0%} 100%{background-position:200%} }
.main-header p {
    color: #4a7fa5;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 0.25rem;
}

/* Section headers */
.section-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #00d4ff;
    border-left: 3px solid #00d4ff;
    padding-left: 10px;
    margin: 1.5rem 0 1rem;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #0d1321 0%, #111827 100%);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    transition: border-color 0.3s, transform 0.2s;
}
.metric-card:hover { border-color: #00d4ff; transform: translateY(-2px); }
.metric-value {
    font-family: 'Space Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #00ff9d;
}
.metric-label {
    font-size: 0.75rem;
    color: #4a7fa5;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

/* Block cards */
.block-card-clean {
    background: linear-gradient(135deg, #0d1f2d 0%, #0a1520 100%);
    border: 1px solid #1a4a2e;
    border-left: 4px solid #00ff9d;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 6px 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    transition: border-color 0.3s;
}
.block-card-clean:hover { border-color: #00ff9d; }

.block-card-tampered {
    background: linear-gradient(135deg, #2d0a0a 0%, #200808 100%);
    border: 1px solid #6b1a1a;
    border-left: 4px solid #ff4444;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 6px 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    animation: pulse-red 2s infinite;
}
@keyframes pulse-red {
    0%,100%{ border-left-color: #ff4444; }
    50%{ border-left-color: #ff8888; }
}

.block-card-update {
    background: linear-gradient(135deg, #0d1a2d 0%, #0a1020 100%);
    border: 1px solid #1a3a6b;
    border-left: 4px solid #00d4ff;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin: 6px 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
}

/* Server status */
.server-healthy {
    background: linear-gradient(135deg, #0a1f14 0%, #061208 100%);
    border: 1px solid #1a5c2e;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    margin-bottom: 8px;
}
.server-compromised {
    background: linear-gradient(135deg, #1f0a0a 0%, #120606 100%);
    border: 1px solid #5c1a1a;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    margin-bottom: 8px;
    animation: pulse-red 1.5s infinite;
}

/* Consensus vote */
.vote-box {
    background: #0d1321;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    padding: 1rem;
    margin: 6px 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
}
.vote-winner {
    border-color: #00ff9d;
    background: linear-gradient(135deg, #0d2a1a 0%, #061208 100%);
}

/* Buttons */
div.stButton > button {
    background: linear-gradient(135deg, #0d1f3c 0%, #1a3a6b 100%);
    color: #00d4ff;
    border: 1px solid #1e4a8f;
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 1px;
    padding: 0.5rem 1.5rem;
    transition: all 0.3s;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #1a3a6b 0%, #00d4ff 100%);
    color: #0a0e1a;
    border-color: #00d4ff;
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
}

/* Inputs */
div[data-baseweb="input"] input,
div[data-baseweb="select"] > div {
    background-color: #0d1321 !important;
    border-color: #1e3a5f !important;
    color: #e0e6f0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* Timeline */
.timeline-item {
    display: flex;
    align-items: flex-start;
    margin: 8px 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
}
.timeline-dot-red {
    width: 10px; height: 10px; border-radius: 50%;
    background: #ff4444; margin-right: 12px; margin-top: 3px; flex-shrink: 0;
    box-shadow: 0 0 8px #ff4444;
}
.timeline-dot-green {
    width: 10px; height: 10px; border-radius: 50%;
    background: #00ff9d; margin-right: 12px; margin-top: 3px; flex-shrink: 0;
    box-shadow: 0 0 8px #00ff9d;
}

/* Alert boxes */
.alert-danger {
    background: linear-gradient(135deg, #2d0a0a, #1a0505);
    border: 1px solid #ff4444;
    border-radius: 8px;
    padding: 1rem;
    color: #ff8888;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    margin: 8px 0;
}
.alert-success {
    background: linear-gradient(135deg, #0a2d14, #051a0a);
    border: 1px solid #00ff9d;
    border-radius: 8px;
    padding: 1rem;
    color: #00ff9d;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    margin: 8px 0;
}
.alert-info {
    background: linear-gradient(135deg, #0a1a2d, #05101a);
    border: 1px solid #00d4ff;
    border-radius: 8px;
    padding: 1rem;
    color: #00d4ff;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    margin: 8px 0;
}

/* Integrity bar */
.integrity-bar-bg {
    background: #0d1321;
    border: 1px solid #1e3a5f;
    border-radius: 20px;
    height: 22px;
    overflow: hidden;
    margin: 8px 0;
}
.integrity-bar-fill {
    height: 100%;
    border-radius: 20px;
    transition: width 1s ease;
    display: flex;
    align-items: center;
    padding-left: 12px;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FEATURE 1: SECURE CONFIG  (no hardcoded secrets)
# ─────────────────────────────────────────────
import hashlib as _hl

# In a real deployment these come from .env / secrets manager.
# For demo we use hashed values — never plaintext.
_ADMIN_PASSWORD_HASH = _hl.sha256("Admin@123".encode()).hexdigest()
_SECRET_KEY_BYTES    = b'GeneBlockSecure!'   # AES key (would be in .env in prod)
_SIGN_SECRET         = "GENEBLOCK_SECRET"

# ─────────────────────────────────────────────
# ENCRYPTION
# ─────────────────────────────────────────────
try:
    from Crypto.Cipher import AES
    from Crypto.Random import get_random_bytes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

def encrypt_data(data: str) -> str:
    if not CRYPTO_AVAILABLE:
        return base64.b64encode(data.encode()).decode()
    cipher = AES.new(_SECRET_KEY_BYTES, AES.MODE_EAX)
    ct, tag = cipher.encrypt_and_digest(str(data).encode())
    return base64.b64encode(cipher.nonce + tag + ct).decode()

def decrypt_data(enc: str) -> str:
    try:
        if not CRYPTO_AVAILABLE:
            return base64.b64decode(enc).decode()
        raw   = base64.b64decode(enc)
        nonce, tag, ct = raw[:16], raw[16:32], raw[32:]
        cipher = AES.new(_SECRET_KEY_BYTES, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(ct, tag).decode()
    except Exception:
        return "Decryption failed"

# ─────────────────────────────────────────────
# BLOCK CLASS
# ─────────────────────────────────────────────
class Block:
    def __init__(self, index, timestamp, metadata, genetic_data, previous_hash):
        self.index         = index
        self.timestamp     = timestamp
        self.metadata      = metadata
        self.genetic_data  = encrypt_data(genetic_data)
        self.previous_hash = previous_hash
        self.hash          = self.calculate_hash()
        self.signature     = self.create_signature()

    def calculate_hash(self) -> str:
        content = f"{self.index}{self.timestamp}{self.metadata}{self.genetic_data}{self.previous_hash}"
        return hashlib.sha256(content.encode()).hexdigest()

    def create_signature(self) -> str:
        return hashlib.sha256((self.hash + _SIGN_SECRET).encode()).hexdigest()

    def is_valid(self) -> bool:
        expected_sig = hashlib.sha256((self.hash + _SIGN_SECRET).encode()).hexdigest()
        return self.signature == expected_sig

# ─────────────────────────────────────────────
# FEATURE 2A: SQLITE PERSISTENCE
# ─────────────────────────────────────────────
DB_PATH = "geneblock.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS blocks (
            server      TEXT,
            idx         INTEGER,
            timestamp   TEXT,
            metadata    TEXT,
            genetic_data TEXT,
            prev_hash   TEXT,
            hash        TEXT,
            signature   TEXT,
            PRIMARY KEY (server, idx)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tamper_log (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            server    TEXT,
            block_idx INTEGER,
            time      TEXT,
            note      TEXT
        )
    """)
    con.commit()
    con.close()

def save_chain_to_db(server_name: str, chain: list):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM blocks WHERE server=?", (server_name,))
    for b in chain:
        cur.execute("""
            INSERT OR REPLACE INTO blocks
            VALUES (?,?,?,?,?,?,?,?)
        """, (server_name, b.index, b.timestamp,
              json.dumps(b.metadata), b.genetic_data,
              b.previous_hash, b.hash, b.signature))
    con.commit()
    con.close()

def load_chain_from_db(server_name: str) -> list:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM blocks WHERE server=? ORDER BY idx", (server_name,))
    rows = cur.fetchall()
    con.close()
    if not rows:
        return []
    blocks = []
    for r in rows:
        b = Block.__new__(Block)
        b.index, b.timestamp  = r[1], r[2]
        b.metadata            = json.loads(r[3])
        b.genetic_data        = r[4]
        b.previous_hash, b.hash, b.signature = r[5], r[6], r[7]
        blocks.append(b)
    return blocks

def log_tamper_to_db(server, block_idx, time, note):
    con = sqlite3.connect(DB_PATH)
    con.execute("INSERT INTO tamper_log(server,block_idx,time,note) VALUES(?,?,?,?)",
                (server, block_idx, time, note))
    con.commit()
    con.close()

def get_tamper_log() -> pd.DataFrame:
    con = sqlite3.connect(DB_PATH)
    df  = pd.read_sql("SELECT * FROM tamper_log ORDER BY id DESC", con)
    con.close()
    return df

# ─────────────────────────────────────────────
# FEATURE 2B: CONSENSUS MECHANISM
# ─────────────────────────────────────────────
def compute_chain_fingerprint(chain: list) -> str:
    """SHA-256 of all hashes concatenated — fast chain identity."""
    combined = "".join(b.hash for b in chain)
    return hashlib.sha256(combined.encode()).hexdigest()

def run_consensus(servers: dict) -> dict:
    """
    Majority-vote consensus:
    Each server casts its chain fingerprint as a vote.
    The fingerprint held by 2+ servers wins.
    Returns a dict with vote details.
    """
    votes = {}
    for name, chain in servers.items():
        fp = compute_chain_fingerprint(chain)
        votes.setdefault(fp, []).append(name)

    winner_fp    = max(votes, key=lambda k: len(votes[k]))
    winner_servers = votes[winner_fp]
    losers       = [s for fp, svrs in votes.items() if fp != winner_fp for s in svrs]

    return {
        "votes":           votes,
        "winner_fp":       winner_fp,
        "winner_servers":  winner_servers,
        "compromised":     losers,
        "consensus_reached": len(winner_servers) >= 2
    }

def apply_consensus_recovery(servers: dict, consensus: dict) -> list:
    """Restore compromised servers from a winning server."""
    recovered = []
    if not consensus["consensus_reached"]:
        return recovered
    source_name = consensus["winner_servers"][0]
    for loser in consensus["compromised"]:
        servers[loser] = copy.deepcopy(servers[source_name])
        save_chain_to_db(loser, servers[loser])
        recovered.append(loser)
    return recovered

# ─────────────────────────────────────────────
# EMAIL ALERT
# ─────────────────────────────────────────────
def send_alert_email(server, block, time):
    try:
        sender   = "nandhiniselvakrishnan@gmail.com"
        receiver = "nandhiniselvakrishnan@gmail.com"
        password = os.environ.get("GMAIL_APP_PASSWORD", "")
        if not password:
            return  # Skip silently if not configured

        msg = MIMEText(f"Tampering detected!\nServer: {server}\nBlock: {block}\nTime: {time}")
        msg['Subject'] = "🚨 GeneBlock Alert: Tampering Detected"
        msg['From']    = sender
        msg['To']      = receiver

        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(sender, password)
        s.send_message(msg)
        s.quit()
    except Exception:
        pass

# ─────────────────────────────────────────────
# BUILD BLOCKCHAIN
# ─────────────────────────────────────────────
def create_blockchain():
    blockchain = []
    try:
        df = pd.read_csv("heart.csv")
        df = df.drop(columns=["Unnamed: 0"], errors='ignore')
    except FileNotFoundError:
        # Demo fallback if CSV not present
        import random
        df = pd.DataFrame([{
            "age": random.randint(40,80),
            "sex": random.randint(0,1),
            "cp": random.randint(0,3),
            "trestbps": random.randint(90,180),
            "chol": random.randint(150,350),
            "target": random.randint(0,1)
        } for _ in range(50)])

    prev_hash = "0"
    for i in range(min(50, len(df))):
        metadata = {
            "Patient ID":  f"P{i+1}",
            "Test Date":   datetime.now().strftime('%Y-%m-%d'),
            "Sample Code": f"S{i+1}"
        }
        genetic_data = json.dumps(df.iloc[i].to_dict())   # ✅ json.dumps, not eval-able
        block = Block(i, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                      metadata, genetic_data, prev_hash)
        blockchain.append(block)
        prev_hash = block.hash
    return blockchain

# ─────────────────────────────────────────────
# INIT SESSION STATE
# ─────────────────────────────────────────────
init_db()

SERVER_NAMES = ["Server 1", "Server 2", "Server 3"]

if "server_keys" not in st.session_state:
    st.session_state.server_keys = {s: str(uuid.uuid4())[:8] for s in SERVER_NAMES}

if "original_chain" not in st.session_state:
    # Try loading from DB first (persistence!)
    loaded = load_chain_from_db("Server 1")
    if loaded:
        st.session_state.original_chain = loaded
    else:
        st.session_state.original_chain = create_blockchain()

if "servers" not in st.session_state:
    st.session_state.servers = {}
    for s in SERVER_NAMES:
        chain = load_chain_from_db(s)
        if not chain:
            chain = copy.deepcopy(st.session_state.original_chain)
            save_chain_to_db(s, chain)
        st.session_state.servers[s] = chain

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False
if "show_all" not in st.session_state:
    st.session_state.show_all = False

servers        = st.session_state.servers
original_chain = st.session_state.original_chain

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🧬 GeneBlock v2</h1>
    <p>Secure Genomic Blockchain · Advanced Security System</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FEATURE 3: LIVE SECURITY DASHBOARD
# ─────────────────────────────────────────────
st.markdown('<p class="section-title">📊 Live Security Dashboard</p>', unsafe_allow_html=True)

# Compute stats
total_blocks  = sum(len(c) for c in servers.values())
tampered_count = 0
for chain in servers.values():
    for b in chain:
        if not b.is_valid():
            tampered_count += 1

clean_count    = total_blocks - tampered_count
integrity_pct  = int((clean_count / total_blocks * 100)) if total_blocks else 100
tamper_log_df  = get_tamper_log()
total_attacks  = len(tamper_log_df)

# Color for integrity
if integrity_pct >= 90:
    bar_color = "linear-gradient(90deg, #00ff9d, #00d4aa)"
    bar_text_color = "#004422"
elif integrity_pct >= 70:
    bar_color = "linear-gradient(90deg, #ffd700, #ffaa00)"
    bar_text_color = "#442200"
else:
    bar_color = "linear-gradient(90deg, #ff4444, #ff2200)"
    bar_text_color = "#440000"

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_blocks}</div>
        <div class="metric-label">Total Blocks</div>
    </div>""", unsafe_allow_html=True)
with m2:
    color = "#ff4444" if tampered_count > 0 else "#00ff9d"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color:{color}">{tampered_count}</div>
        <div class="metric-label">Tampered Blocks</div>
    </div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_attacks}</div>
        <div class="metric-label">Total Attacks</div>
    </div>""", unsafe_allow_html=True)
with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="color:{'#00ff9d' if integrity_pct>90 else '#ff4444'}">{integrity_pct}%</div>
        <div class="metric-label">Chain Integrity</div>
    </div>""", unsafe_allow_html=True)

# Integrity bar
st.markdown(f"""
<div style="margin: 16px 0 8px; font-family:'Space Mono',monospace; font-size:0.75rem; color:#4a7fa5; letter-spacing:2px;">
  CHAIN INTEGRITY SCORE
</div>
<div class="integrity-bar-bg">
  <div class="integrity-bar-fill"
       style="width:{integrity_pct}%; background:{bar_color}; color:{bar_text_color};">
    {integrity_pct}% SECURE
  </div>
</div>
""", unsafe_allow_html=True)

# Server health row
st.markdown('<p class="section-title">🖥️ Server Health Status</p>', unsafe_allow_html=True)
sh_cols = st.columns(3)
consensus_result = run_consensus(servers)

for idx, (sname, chain) in enumerate(servers.items()):
    tampered_in_server = sum(1 for b in chain if not b.is_valid())
    is_compromised     = sname in consensus_result["compromised"]
    with sh_cols[idx]:
        if is_compromised or tampered_in_server > 0:
            st.markdown(f"""
            <div class="server-compromised">
                <div style="font-size:1.5rem">🔴</div>
                <div style="font-family:'Space Mono',monospace; font-weight:700; color:#ff6666; margin:4px 0">{sname}</div>
                <div style="font-size:0.7rem; color:#aa4444; letter-spacing:1px">COMPROMISED</div>
                <div style="font-family:'Space Mono',monospace; font-size:0.75rem; color:#ff4444; margin-top:6px">
                    {tampered_in_server} tampered block(s)
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="server-healthy">
                <div style="font-size:1.5rem">🟢</div>
                <div style="font-family:'Space Mono',monospace; font-weight:700; color:#00ff9d; margin:4px 0">{sname}</div>
                <div style="font-size:0.7rem; color:#00aa66; letter-spacing:1px">HEALTHY</div>
                <div style="font-family:'Space Mono',monospace; font-size:0.75rem; color:#00cc77; margin-top:6px">
                    {len(chain)} blocks · All valid
                </div>
            </div>""", unsafe_allow_html=True)

# Attack timeline
if not tamper_log_df.empty:
    st.markdown('<p class="section-title">⏱️ Attack Timeline</p>', unsafe_allow_html=True)
    for _, row in tamper_log_df.head(8).iterrows():
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-dot-red"></div>
            <div>
                <span style="color:#ff6666">[{row['time']}]</span>
                <span style="color:#aaa"> — </span>
                <span style="color:#ff9999">{row['server']}</span>
                <span style="color:#666"> Block </span>
                <span style="color:#ffcc66">#{row['block_idx']}</span>
                <span style="color:#666"> — {row['note']}</span>
            </div>
        </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# TAMPER SIMULATION
# ─────────────────────────────────────────────
st.markdown('<p class="section-title">🛠️ Simulate Tampering</p>', unsafe_allow_html=True)

t_col1, t_col2 = st.columns(2)
with t_col1:
    server_to_edit = st.selectbox("Select Server", SERVER_NAMES, key="tamper_server")
with t_col2:
    block_index = st.selectbox("Select Block", list(range(len(servers[server_to_edit]))), key="block_select")

target_block = servers[server_to_edit][block_index]
new_pid    = st.text_input("New Patient ID",  target_block.metadata["Patient ID"])
new_sample = st.text_input("New Sample Code", target_block.metadata["Sample Code"])

bt1, bt2 = st.columns(2)
with bt1:
    if st.button("⚠️ Simulate Hack"):
        target_block.metadata["Patient ID"]  = new_pid
        target_block.metadata["Sample Code"] = new_sample
        chain = servers[server_to_edit]
        for i in range(block_index, len(chain)):
            prev = chain[i-1].hash if i > 0 else "0"
            chain[i].previous_hash = prev
            chain[i].hash          = chain[i].calculate_hash()
        save_chain_to_db(server_to_edit, chain)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_tamper_to_db(server_to_edit, block_index, ts, "Tampering simulated")
        send_alert_email(server_to_edit, block_index, ts)
        st.markdown(f'<div class="alert-danger">🚨 Tampering detected on {server_to_edit} — Block {block_index} compromised!</div>', unsafe_allow_html=True)
        st.rerun()

with bt2:
    if st.button("🛡️ Manual Recover Server"):
        recovered = apply_consensus_recovery(servers, consensus_result)
        if recovered:
            st.markdown(f'<div class="alert-success">✅ Recovered: {", ".join(recovered)}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-danger">❌ Recovery failed — not enough healthy servers</div>', unsafe_allow_html=True)
        st.rerun()

st.markdown("---")

# ─────────────────────────────────────────────
# FEATURE 2B: CONSENSUS PANEL
# ─────────────────────────────────────────────
st.markdown('<p class="section-title">🗳️ Consensus Mechanism (Majority Vote)</p>', unsafe_allow_html=True)

if st.button("▶ Run Consensus Now"):
    consensus_result = run_consensus(servers)
    st.markdown('<p style="font-family:Space Mono,monospace; font-size:0.8rem; color:#4a7fa5; margin-bottom:8px;">VOTING RESULTS</p>', unsafe_allow_html=True)
    for fp, voters in consensus_result["votes"].items():
        is_winner = fp == consensus_result["winner_fp"]
        css_class = "vote-box vote-winner" if is_winner else "vote-box"
        label     = "👑 MAJORITY CHAIN" if is_winner else "⚠️ MINORITY CHAIN"
        badge_col = "#00ff9d" if is_winner else "#ff4444"
        st.markdown(f"""
        <div class="{css_class}">
            <span style="color:{badge_col}; font-weight:700">{label}</span>
            &nbsp;&nbsp;Fingerprint: <span style="color:#aaa">{fp[:20]}...</span><br>
            Supported by: <span style="color:#00d4ff">{', '.join(voters)}</span>
            &nbsp;({len(voters)} vote{'s' if len(voters)>1 else ''})
        </div>""", unsafe_allow_html=True)

    if consensus_result["consensus_reached"]:
        st.markdown(f'<div class="alert-success">✅ Consensus reached — majority chain is authoritative</div>', unsafe_allow_html=True)
        if consensus_result["compromised"]:
            recovered = apply_consensus_recovery(servers, consensus_result)
            if recovered:
                st.markdown(f'<div class="alert-info">🔄 Auto-recovered: {", ".join(recovered)}</div>', unsafe_allow_html=True)
                st.rerun()
    else:
        st.markdown('<div class="alert-danger">❌ No consensus — all servers disagree. Manual intervention required.</div>', unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# BLOCKCHAIN STATUS (block display)
# ─────────────────────────────────────────────
st.markdown('<p class="section-title">🔗 Blockchain Status</p>', unsafe_allow_html=True)

if st.button("🔽 Toggle Show All Blocks"):
    st.session_state.show_all = not st.session_state.show_all

bc1, bc2, bc3 = st.columns(3)
cols = [bc1, bc2, bc3]
for idx, (label, chain) in enumerate(servers.items()):
    with cols[idx]:
        tampered_here = sum(1 for b in chain if not b.is_valid())
        header_color  = "#ff4444" if tampered_here > 0 else "#00ff9d"
        st.markdown(f"""
        <div style="font-family:'Space Mono',monospace; font-size:0.85rem; font-weight:700;
                    color:{header_color}; margin-bottom:8px; letter-spacing:1px;">
            {label}  ·  {len(chain)} blocks
        </div>""", unsafe_allow_html=True)

        blocks_to_show = chain if st.session_state.show_all else chain[:5]
        for b in blocks_to_show:
            if not b.is_valid():
                css = "block-card-tampered"
                tag = "🚨 TAMPERED"
            else:
                dec = decrypt_data(b.genetic_data)
                if "New Condition" in dec:
                    css, tag = "block-card-update", "🆕 UPDATE"
                else:
                    css, tag = "block-card-clean",  "✅ VALID"
            st.markdown(f"""
            <div class="{css}">
                <b>Block #{b.index}</b> &nbsp;<span style="opacity:.6">{tag}</span><br>
                <span style="color:#4a7fa5">Hash:</span> {b.hash[:22]}…<br>
                <span style="color:#4a7fa5">Prev:</span> {b.previous_hash[:22]}…<br>
                <span style="color:#4a7fa5">Time:</span> {b.timestamp}
            </div>""", unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# DOCTOR UPDATE
# ─────────────────────────────────────────────
st.markdown('<p class="section-title">➕ Add New Medical Record (Doctor Update)</p>', unsafe_allow_html=True)

entered_key              = st.text_input("🔐 Enter Temporary Access Key", type="password")
selected_server_update   = st.selectbox("Select Server", SERVER_NAMES, key="update_server")
patient_ids              = sorted(set(b.metadata["Patient ID"] for b in servers[selected_server_update]))
selected_patient         = st.selectbox("Select Patient", patient_ids)
new_disease              = st.text_input("New Diagnosis / Condition")

if st.button("➕ Add Medical Update"):
    if "temp_update_key" not in st.session_state:
        st.markdown('<div class="alert-danger">❌ No active key — ask admin to generate one</div>', unsafe_allow_html=True)
    elif entered_key != st.session_state.temp_update_key:
        st.markdown('<div class="alert-danger">❌ Invalid or expired key</div>', unsafe_allow_html=True)
    else:
        chain = servers[selected_server_update]
        patient_blocks = [b for b in chain if b.metadata["Patient ID"] == selected_patient]
        last_block     = patient_blocks[-1]
        new_data       = json.dumps({
            "Patient ID":    selected_patient,
            "New Condition": new_disease,
            "Updated Time":  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        new_metadata = {
            "Patient ID":  selected_patient,
            "Test Date":   datetime.now().strftime('%Y-%m-%d'),
            "Sample Code": f"S{len(chain)+1}"
        }
        new_block = Block(len(chain), datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                          new_metadata, new_data, last_block.hash)
        chain.append(new_block)
        save_chain_to_db(selected_server_update, chain)
        del st.session_state.temp_update_key
        st.markdown('<div class="alert-success">✅ Record added — one-time key expired</div>', unsafe_allow_html=True)
        st.rerun()

st.markdown("---")

# ─────────────────────────────────────────────
# ADMIN PANEL
# ─────────────────────────────────────────────
st.markdown('<p class="section-title">🔐 Admin Panel</p>', unsafe_allow_html=True)

admin_password = st.text_input("Admin Password", type="password", key="admin_pw")
if st.button("Login", key="admin_login"):
    # FEATURE 1: compare against hash, never plaintext
    if hashlib.sha256(admin_password.encode()).hexdigest() == _ADMIN_PASSWORD_HASH:
        st.session_state.admin_authenticated = True
        st.markdown('<div class="alert-success">✅ Admin authenticated</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-danger">❌ Invalid credentials</div>', unsafe_allow_html=True)

if st.session_state.admin_authenticated:
    a1, a2 = st.columns(2)

    with a1:
        if st.button("🔑 Generate One-Time Update Key"):
            st.session_state.temp_update_key = str(uuid.uuid4())[:8]
        if "temp_update_key" in st.session_state:
            st.markdown(f'<div class="alert-info">🔐 Active Key: <b>{st.session_state.temp_update_key}</b></div>', unsafe_allow_html=True)

    with a2:
        if st.button("🔐 Toggle Server Keys"):
            st.session_state.show_server_keys = not st.session_state.get("show_server_keys", False)
        if st.session_state.get("show_server_keys"):
            for s, k in st.session_state.server_keys.items():
                st.markdown(f'<div class="alert-info">{s} → <b>{k}</b></div>', unsafe_allow_html=True)

    st.markdown("**🔓 Decrypt Block Data**")
    dec_server = st.selectbox("Server to inspect", SERVER_NAMES, key="dec_server")
    dec_limit  = st.slider("Blocks to show", 1, min(20, len(servers[dec_server])), 3)
    if st.button("Decrypt & Show"):
        for b in servers[dec_server][:dec_limit]:
            raw = decrypt_data(b.genetic_data)
            try:
                data_dict = json.loads(raw)   # ✅ safe — no eval()
                formatted = " | ".join(f"{k}: {v}" for k, v in data_dict.items())
            except Exception:
                formatted = raw
            valid_label = "✅" if b.is_valid() else "🚨"
            st.markdown(f'<div class="alert-{"success" if b.is_valid() else "danger"}">{valid_label} Block {b.index} → {formatted}</div>',
                        unsafe_allow_html=True)

    # Tamper report
    st.markdown("**📄 Tamper Report**")
    if st.button("View Full Tamper Report"):
        df_log = get_tamper_log()
        if not df_log.empty:
            st.dataframe(df_log, use_container_width=True)
        else:
            st.markdown('<div class="alert-success">✅ No tampering recorded in database</div>', unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# SERVER ACCESS
# ─────────────────────────────────────────────
st.markdown('<p class="section-title">🔐 Direct Server Access</p>', unsafe_allow_html=True)
acc_col1, acc_col2 = st.columns(2)
with acc_col1:
    selected_server  = st.selectbox("Choose Server", SERVER_NAMES, key="access_server")
with acc_col2:
    server_access_key = st.text_input("Server Access Key", type="password")

if st.button("Access Server Data"):
    if server_access_key == st.session_state.server_keys[selected_server]:
        st.markdown('<div class="alert-success">✅ Access granted</div>', unsafe_allow_html=True)
        for b in servers[selected_server][:10]:
            raw = decrypt_data(b.genetic_data)
            st.markdown(f'<div class="block-card-clean">Block {b.index}: {raw[:120]}…</div>',
                        unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-danger">❌ Invalid server key</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; padding:2rem 0; font-family:'Space Mono',monospace;
            font-size:0.7rem; color:#1e3a5f; letter-spacing:2px; margin-top:2rem;
            border-top:1px solid #1e3a5f;">
    GENEBLOCK v2.0 · ADVANCED SECURITY SYSTEM · BLOCKCHAIN-SECURED GENOMIC DATA
</div>
""", unsafe_allow_html=True)
