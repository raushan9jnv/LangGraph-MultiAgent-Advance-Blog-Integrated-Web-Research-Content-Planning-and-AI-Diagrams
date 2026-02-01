from __future__ import annotations
import json, os, re, zipfile
from datetime import date
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional, List, Iterator, Tuple
import pandas as pd
import streamlit as st
from agent_backend import app

# ==========================================
# 1. HIGH-END DESIGN SYSTEM (CSS)
# ==========================================
st.set_page_config(page_title="Scribe Architect", layout="wide", page_icon="⚡")

st.markdown("""
<style>
    /* Premium Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #E2E8F0;
    }

    /* Deep Space Theme */
    .stApp {
        background: #020617;
        background-image: 
            radial-gradient(at 0% 0%, rgba(30, 58, 138, 0.15) 0, transparent 50%), 
            radial-gradient(at 100% 100%, rgba(88, 28, 135, 0.15) 0, transparent 50%);
    }

    /* Sidebar - Industrial Dark */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B;
    }

    /* Navigation Tabs Custom Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #1E293B;
        border-radius: 8px 8px 0px 0px;
        color: #94A3B8;
        border: none;
        padding: 0px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #334155 !important;
        color: #F8FAFC !important;
        border-bottom: 2px solid #F59E0B !important;
    }

    /* Agentic Status Cards */
    .agent-node {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }

    /* Blueprint Task Cards - High Contrast */
    .task-card {
        background: #0F172A;
        border: 1px solid #1E293B;
        border-left: 4px solid #F59E0B;
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 15px;
    }
    .task-header {
        color: #F59E0B;
        font-weight: 800;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* Metrics & Pill Badges */
    .pill {
        background: #334155;
        color: #CBD5E1;
        padding: 2px 12px;
        border-radius: 100px;
        font-size: 0.7rem;
        font-weight: 600;
        border: 1px solid #475569;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #020617; }
    ::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIC & WORKFLOW (保持原样)
# ==========================================
def safe_slug(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"[^a-z0-9 _-]+", "", s)
    s = re.sub(r"\s+", "_", s).strip("_")
    return s or "blog"

def try_stream(graph_app, inputs: Dict[str, Any]) -> Iterator[Tuple[str, Any]]:
    try:
        for step in graph_app.stream(inputs, stream_mode="updates"):
            yield ("updates", step)
        yield ("final", graph_app.invoke(inputs))
    except Exception:
        yield ("final", graph_app.invoke(inputs))

# ==========================================
# 3. SIDEBAR (INDUSTRIAL UI)
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='color:#F59E0B; font-weight:800;'>SCRIBE ARC</h2>", unsafe_allow_html=True)
    st.caption("Agentic Intelligence Terminal")
    st.markdown("---")
    
    topic = st.text_area("TARGET TOPIC", height=120, placeholder="Define the research scope...")
    as_of = st.date_input("KNOWLEDGE CUTOFF", value=date.today())
    
    st.markdown("---")
    run_btn = st.button("▶ INITIALIZE PIPELINE", type="primary", use_container_width=True)
    
    st.markdown("### ARCHIVE")
    past_files = sorted([p for p in Path(".").glob("*.md")], key=lambda p: p.stat().st_mtime, reverse=True)
    if past_files:
        selected = st.selectbox("HISTORY", past_files, format_func=lambda x: x.name, label_visibility="collapsed")
        if st.button("LOAD SNAPSHOT", use_container_width=True):
            st.session_state["last_out"] = {"final": selected.read_text(encoding="utf-8")}
    st.markdown("---")
    st.info("Role: Senior Consultant / Gen AI Engineer")

# ==========================================
# 4. MAIN INTERFACE (COMMAND CENTER)
# ==========================================
st.markdown("<h1 style='letter-spacing:-1px;'>Content Orchestration System</h1>", unsafe_allow_html=True)

tab_preview, tab_plan, tab_research, tab_media = st.tabs([
    "📂 OUTPUT", "🗺️ BLUEPRINT", "🔍 INTELLIGENCE", "🖼️ ASSETS"
])

if run_btn:
    if not topic.strip():
        st.warning("SYSTEM REQ: Input Topic Missing")
        st.stop()

    inputs = {
        "topic": topic.strip(), "mode": "", "needs_research": False, "queries": [],
        "evidence": [], "plan": None, "as_of": as_of.isoformat(), "recency_days": 7,
        "sections": [], "merged_md": "", "md_with_placeholders": "", "image_specs": [], "final": ""
    }

    with st.status("📡 AGENT SWARM ACTIVE", expanded=True) as status:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.write("**NODE ACTIVITY**")
        
        current_state = {}
        for kind, payload in try_stream(app, inputs):
            if kind == "updates":
                node = next(iter(payload.keys()))
                st.markdown(f"<div class='agent-node'>⦿ Node: <span style='color:#F59E0B;'>{node}</span> completed.</div>", unsafe_allow_html=True)
                if isinstance(payload[node], dict): current_state.update(payload[node])
            elif kind == "final":
                st.session_state["last_out"] = payload
                status.update(label="PIPELINE COMPLETE", state="complete")

# ==========================================
# 5. RENDERER
# ==========================================
out = st.session_state.get("last_out")
if out:
    with tab_preview:
        st.markdown(out.get("final", "No output generated."))
        st.divider()
        st.download_button("⚡ EXPORT MARKDOWN", out.get("final", ""), file_name="export.md")

    with tab_plan:
        plan = out.get("plan")
        if plan:
            st.markdown(f"### SYSTEM PLAN: {plan.blog_title}")
            tasks = plan.tasks if hasattr(plan, 'tasks') else plan.get('tasks', [])
            for t in tasks:
                st.markdown(f"""
                <div class="task-card">
                    <div class="task-header">0{t.id} // {t.title}</div>
                    <div style="color:#94A3B8; font-family:'JetBrains Mono'; font-size:0.8rem; margin: 10px 0;">
                        SCOPE: {t.goal}
                    </div>
                    <div style="display:flex; gap:10px;">
                        <span class="pill">{t.target_words} WORDS</span>
                        {'<span class="pill" style="border-color:#F59E0B; color:#F59E0B;">CODE</span>' if t.requires_code else ''}
                        {'<span class="pill" style="border-color:#38BDF8; color:#38BDF8;">CITATIONS</span>' if t.requires_citations else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with tab_research:
        evidence = out.get("evidence", [])
        for e in evidence:
            st.markdown(f"""
            <div style="background:#0F172A; border: 1px solid #1E293B; padding:15px; border-radius:4px; margin-bottom:10px;">
                <a href="{e.url}" style="color:#38BDF8; text-decoration:none; font-weight:600;">{e.title}</a>
                <p style="color:#94A3B8; font-size:0.85rem; margin-top:8px;">{e.snippet}</p>
                <div style="font-size:0.7rem; color:#475569;">SOURCE: {e.source} | UPDATED: {e.published_at}</div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.info("TERMINAL IDLE. AWAITING TARGET TOPIC.")