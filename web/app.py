import streamlit as st
import pandas as pd
import time
import io
import os

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(page_title="Industrial IoT - BIG_LOG", layout="wide", initial_sidebar_state="collapsed")

# Inject Custom CSS for a Premium "Industrial" Look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #374151;
    }
    .stSubheader {
        color: #60a5fa;
        font-weight: 600;
    }
    h1 {
        background: linear-gradient(90deg, #60a5fa, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .status-tag {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .online { background-color: #065f46; color: #34d399; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA LOAD & STATE INITIALIZATION ---
CSV_FILE = "data_sample.csv"

if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.current_row = 1 # Start after header
    st.session_state.master_state = {"TOTAL_RECORDS": 0}
    st.session_state.start_time = time.time()
    
    # Load data once
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r') as f:
            st.session_state.raw_data = f.readlines()
    else:
        st.session_state.raw_data = []

def process_batch(lines):
    """Simulates the Mapper and Reducer logic in-memory."""
    # MAP PHASE
    intermediate_results = []
    for line in lines:
        parts = line.strip().split(',')
        if len(parts) < 5 or parts[0] == "timestamp":
            continue
            
        machine_id = parts[1]
        status = parts[3]
        error_code = parts[4]
        
        # Mapper logic
        if status == "ERROR":
            intermediate_results.append((f"ERR_MACHINE_{machine_id}", 1))
        if error_code != "NONE":
            intermediate_results.append((f"ERR_CODE_{error_code}", 1))
        intermediate_results.append(("TOTAL_RECORDS", 1))
        
    # REDUCE PHASE (Merge into master state)
    for key, value in intermediate_results:
        st.session_state.master_state[key] = st.session_state.master_state.get(key, 0) + value

# --- 3. THE VIRTUAL CLUSTER ENGINE ---
BATCH_SIZE = 30
NODES = ["DataNode-01", "DataNode-02", "DataNode-03"]

def virtual_map_reduce(batch_lines):
    """
    Simulates a distributed MapReduce job across 3 virtual nodes.
    Returns the aggregated results and the status of each node.
    """
    # Split batch into 3 chunks (one for each DataNode)
    chunk_size = len(batch_lines) // len(NODES)
    node_work = {node: batch_lines[i*chunk_size : (i+1)*chunk_size] for i, node in enumerate(NODES)}
    
    node_stats = {}
    aggregated_batch = []

    # 🔹 PHASE 1: DISTRIBUTED MAPPING (Simulated)
    for node in NODES:
        lines = node_work.get(node, [])
        node_stats[node] = "MAPPING" if lines else "IDLE"
        
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) < 5 or parts[0] == "timestamp": continue
            
            machine_id, status, error_code = parts[1], parts[3], parts[4]
            
            # The Mapper Logic
            if status == "ERROR": aggregated_batch.append((f"ERR_MACHINE_{machine_id}", 1))
            if error_code != "NONE": aggregated_batch.append((f"ERR_CODE_{error_code}", 1))
            aggregated_batch.append(("TOTAL_RECORDS", 1))

    # 🔹 PHASE 2: CENTRALIZED REDUCING
    for key, value in aggregated_batch:
        st.session_state.master_state[key] = st.session_state.master_state.get(key, 0) + value
        
    return node_stats

# Process next batch
node_status = {node: "IDLE" for node in NODES}
if st.session_state.current_row < len(st.session_state.raw_data):
    end_row = st.session_state.current_row + BATCH_SIZE
    batch = st.session_state.raw_data[st.session_state.current_row : end_row]
    node_status = virtual_map_reduce(batch)
    st.session_state.current_row = end_row

# --- 4. DASHBOARD UI ---
st.title("🏭 BIG_LOG: Distributed IoT Dashboard")
st.markdown("""
<div style="margin-bottom: 25px;">
    <span class="status-tag online">● HADOOP CLUSTER SIMULATION ACTIVE</span>
    <span style="color: #9ca3af; margin-left: 15px;">Simulating NameNode & 3 DataNodes</span>
</div>
""", unsafe_allow_html=True)

# Metrics Row
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
total_recs = st.session_state.master_state.get("TOTAL_RECORDS", 0)
uptime = int(time.time() - st.session_state.start_time)

with col_m1:
    st.metric("Total Records", f"{total_recs:,}")
with col_m2:
    error_count = sum(v for k, v in st.session_state.master_state.items() if k.startswith("ERR_MACHINE_"))
    st.metric("Total Errors", f"{error_count:,}")
with col_m3:
    st.metric("Cluster Health", "100%", delta="3 Live Nodes")
with col_m4:
    st.metric("Uptime", f"{uptime}s")

# --- VIRTUAL CLUSTER STATUS ---
st.markdown("### 🖥️ Virtual Cluster Status")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.info(f"**NameNode**\n\nStatus: COORDINATING\n\nTask: Splitting Batch {st.session_state.current_row//BATCH_SIZE}")
for i, node in enumerate(NODES):
    status = node_status[node]
    color = "green" if status == "MAPPING" else "gray"
    with [c2, c3, c4][i]:
        st.success(f"**{node}**\n\nStatus: {status}\n\nCPU: {75 if status == 'MAPPING' else 2}%")

st.divider()

# Visualization Row
col_left, col_right = st.columns(2)

# Extract data for charts
machines = {"Machine": [], "Errors": []}
codes = {"Code": [], "Frequency": []}

for k, v in st.session_state.master_state.items():
    if k.startswith("ERR_MACHINE_"):
        machines["Machine"].append(k.replace("ERR_MACHINE_", ""))
        machines["Errors"].append(v)
    elif k.startswith("ERR_CODE_"):
        codes["Code"].append(k.replace("ERR_CODE_", ""))
        codes["Frequency"].append(v)

df_machines = pd.DataFrame(machines).sort_values("Machine")
df_codes = pd.DataFrame(codes).sort_values("Frequency", ascending=False)

with col_left:
    st.subheader("🚨 Error Distribution per Machine")
    if not df_machines.empty:
        st.bar_chart(df_machines.set_index("Machine"), color="#60a5fa")

with col_right:
    st.subheader("🏷️ Error Code Frequency")
    if not df_codes.empty:
        st.bar_chart(df_codes.set_index("Code"), color="#a78bfa")

# --- 5. THE LOOP ---
if st.session_state.current_row < len(st.session_state.raw_data):
    time.sleep(1.2) 
    st.rerun()
else:
    st.success("✅ End of Stream Reached. All data processed via Distributed MapReduce simulation.")
    if st.button("Restart Stream"):
        st.session_state.current_row = 1
        st.session_state.master_state = {"TOTAL_RECORDS": 0}
        st.rerun()
