"""
EcoWatcher — Streamlit Dashboard Interface
============================================
# Day 5 Concept: Deployable User Interface & Agent Skills Demo
# Day 4 Concept: Security Sentry Visualization
# Day 3 Concept: Multi-Agent Pipeline Integration
# Day 2 Concept: MCP Tool Results Rendering

Premium minimalist Streamlit dashboard with dark/light mode toggle
for the EcoWatcher multi-agent circular economy optimization system.
Integrates:
  - Security pre-processing (security_guardrails.py)
  - Multi-agent pipeline (agent_engine.py)
  - Environmental Impact Dashboard (visual metrics reward)
  - Three-tab output visualization (Reuse / Recycle / Security)
  - Inline SVG graphics for the 3R principles
"""

import base64
import random
import time
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Day 5 Concept: Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="EcoWatcher — Circular Economy AI Agent",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------------------------
# Day 5 Concept: Load Feature Images
# ---------------------------------------------------------------------------
def _load_b64(filename: str) -> str:
    path = Path(__file__).parent / filename
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/png;base64,{data}"
    except FileNotFoundError:
        return ""

_B64_AGENTS = _load_b64("feature_agents.png")
_B64_SECURITY = _load_b64("feature_security.png")
_B64_MCP = _load_b64("feature_mcp.png")


# ---------------------------------------------------------------------------
# Day 5 Concept: Theme State Management
# ---------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"


# ---------------------------------------------------------------------------
# Day 5 Concept: Environmental Impact Estimation Engine
# Dynamically scales values based on the number and type of materials
# extracted by Agent A to make the simulation feel alive and rewarding.
# ---------------------------------------------------------------------------
_IMPACT_TABLE = {
    "Glass Jars":         {"co2_kg": 0.31, "mass_g": 350, "circularity": 0.92},
    "Cardboard Boxes":    {"co2_kg": 0.48, "mass_g": 420, "circularity": 0.88},
    "Broken Electronics": {"co2_kg": 2.45, "mass_g": 780, "circularity": 0.65},
    "Cotton Fabrics":     {"co2_kg": 1.15, "mass_g": 290, "circularity": 0.85},
}
_DEFAULT_IMPACT = {"co2_kg": 0.35, "mass_g": 250, "circularity": 0.70}


def _estimate_impact(materials: list) -> dict:
    if not materials:
        return {"co2_kg": 0.0, "landfill_g": 0, "circularity_pct": 0}

    total_co2 = 0.0
    total_mass = 0
    circularity_scores = []

    for mat in materials:
        matched = False
        mat_lower = mat.lower()
        for key, impact in _IMPACT_TABLE.items():
            if key.lower() in mat_lower or mat_lower in key.lower():
                total_co2 += impact["co2_kg"]
                total_mass += impact["mass_g"]
                circularity_scores.append(impact["circularity"])
                matched = True
                break
        if not matched:
            total_co2 += _DEFAULT_IMPACT["co2_kg"]
            total_mass += _DEFAULT_IMPACT["mass_g"]
            circularity_scores.append(_DEFAULT_IMPACT["circularity"])

    total_co2 = round(total_co2 * random.uniform(0.95, 1.05), 2)
    avg_circularity = sum(circularity_scores) / len(circularity_scores)
    circularity_pct = round(avg_circularity * 100, 1)

    return {
        "co2_kg": total_co2,
        "landfill_g": total_mass,
        "circularity_pct": circularity_pct,
    }


# ---------------------------------------------------------------------------
# Day 5 Concept: Inline SVG Icons
# ---------------------------------------------------------------------------
def _svg_reduce(stroke: str) -> str:
    return f"""<svg viewBox="0 0 64 64" width="42" height="42" xmlns="http://www.w3.org/2000/svg">
      <circle cx="32" cy="32" r="29" fill="none" stroke="{stroke}" stroke-width="1.5" opacity="0.35"/>
      <path d="M32 16 L32 44 M24 36 L32 44 L40 36" fill="none" stroke="{stroke}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>"""

def _svg_reuse(stroke: str) -> str:
    return f"""<svg viewBox="0 0 64 64" width="42" height="42" xmlns="http://www.w3.org/2000/svg">
      <circle cx="32" cy="32" r="29" fill="none" stroke="{stroke}" stroke-width="1.5" opacity="0.35"/>
      <path d="M32 16 A16 16 0 1 1 16 32" fill="none" stroke="{stroke}" stroke-width="2.5" stroke-linecap="round"/>
      <polygon points="16,25 16,39 23,32" fill="{stroke}"/>
    </svg>"""

def _svg_recycle(stroke: str) -> str:
    return f"""<svg viewBox="0 0 64 64" width="42" height="42" xmlns="http://www.w3.org/2000/svg">
      <circle cx="32" cy="32" r="29" fill="none" stroke="{stroke}" stroke-width="1.5" opacity="0.35"/>
      <path d="M32 18 L44 40 L20 40 Z" fill="none" stroke="{stroke}" stroke-width="2.5" stroke-linejoin="round"/>
    </svg>"""


# ---------------------------------------------------------------------------
# Day 5 Concept: Theme Palette Definitions
# ---------------------------------------------------------------------------
_THEMES = {
    "dark": {
        "bg":        "#1E1E1E",
        "card":      "#262626",
        "border":    "#333",
        "text":      "#E0E0E0",
        "muted":     "#999",
        "dim":       "#666",
        "accent":    "#6E8A7E",
        "accent2":   "#2D4A3E",
        "ok":        "#6E8A7E",
        "warn":      "#C4A35A",
        "err":       "#d47872",
        "slate":     "#8899A6",
        "svg":       "#6E8A7E",
        "inp_bg":    "#1E1E1E",
        "btn_bg":    "#2D4A3E",
        "btn_hover": "#3a5f50",
        "btn_bdr":   "#3a5f50",
        "tab_bg":    "#262626",
        "tab_sel":   "#1E1E1E",
    },
    "light": {
        "bg":        "#F4F7F4",
        "card":      "#FFFFFF",
        "border":    "#D0DCCE",
        "text":      "#1B4332",
        "muted":     "#52735E",
        "dim":       "#7A9484",
        "accent":    "#2D6A4F",
        "accent2":   "#40916C",
        "ok":        "#2D6A4F",
        "warn":      "#B58B2B",
        "err":       "#C0392B",
        "slate":     "#52735E",
        "svg":       "#2D6A4F",
        "inp_bg":    "#FFFFFF",
        "btn_bg":    "#2D6A4F",
        "btn_hover": "#40916C",
        "btn_bdr":   "#40916C",
        "tab_bg":    "#E8F0E8",
        "tab_sel":   "#FFFFFF",
    },
}

t = _THEMES[st.session_state.theme]

# ---------------------------------------------------------------------------
# CSS Injection
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes subtleFloat {{
        0%, 100% {{ transform: translateY(0); }}
        50%      {{ transform: translateY(-3px); }}
    }}

    .stApp {{
        background-color: {t['bg']};
        color: {t['text']};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* Reduce default top padding */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }}

    /* --- Hero --- */
    .eco-hero {{
        background: {t['card']};
        border: 1px solid {t['border']};
        border-radius: 16px;
        padding: 2.2rem 2rem 1.8rem;
        margin-bottom: 2rem;
        text-align: center;
        animation: fadeIn 0.5s ease-out;
    }}
    .eco-hero h1 {{
        font-size: 2.4rem;
        font-weight: 800;
        color: {t['accent']};
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }}
    .eco-hero .subtitle {{
        color: {t['muted']};
        font-size: 0.95rem;
        line-height: 1.7;
        max-width: 660px;
        margin: 0 auto 1.3rem;
        font-weight: 400;
    }}

    /* --- Features Section --- */
    .features-section {{
        margin: 0 0 2rem 0;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }}
    .feature-row {{
        display: flex;
        align-items: center;
        gap: 2rem;
        background: {t['card']};
        border: 1px solid {t['border']};
        border-radius: 14px;
        padding: 1.5rem 2rem;
        animation: fadeIn 0.5s ease-out;
    }}
    .feature-row.reverse {{
        flex-direction: row-reverse;
    }}
    @media (max-width: 768px) {{
        .feature-row, .feature-row.reverse {{
            flex-direction: column;
            text-align: center;
        }}
    }}
    .feature-text {{
        flex: 1;
    }}
    .feature-text h3 {{
        color: {t['accent']} !important;
        font-size: 1.25rem !important;
        margin-bottom: 0.5rem !important;
        font-weight: 700 !important;
    }}
    .feature-text p {{
        color: {t['text']};
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 0;
    }}
    .feature-img {{
        width: 140px;
        height: 140px;
        border-radius: 12px;
        object-fit: cover;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid {t['border']};
    }}

    /* --- Theme Toggle Container --- */
    .theme-toggle-row {{
        display: flex;
        justify-content: flex-end;
        margin-bottom: 0.5rem;
    }}

    /* --- Input --- */
    .stTextArea textarea {{
        background-color: {t['inp_bg']} !important;
        color: {t['text']} !important;
        border: 1px solid {t['border']} !important;
        border-radius: 10px !important;
        font-size: 0.9rem !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.9rem !important;
    }}
    .stTextArea textarea:focus {{
        border-color: {t['accent']} !important;
        box-shadow: 0 0 0 2px {t['accent']}22 !important;
    }}
    .stTextArea textarea::placeholder {{ color: {t['dim']} !important; }}

    /* --- Button --- */
    .stButton > button {{
        background: {t['btn_bg']} !important;
        color: #FFFFFF !important;
        border: 1px solid {t['btn_bdr']} !important;
        border-radius: 10px !important;
        padding: 0.7rem 2rem !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }}
    .stButton > button:hover {{
        background: {t['btn_hover']} !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 14px {t['btn_bg']}44 !important;
    }}

    /* --- Tabs --- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        background: {t['tab_bg']};
        border-radius: 10px;
        padding: 4px;
        border: 1px solid {t['border']};
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        color: {t['muted']};
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        font-size: 0.8rem;
        font-family: 'Inter', sans-serif;
    }}
    .stTabs [data-baseweb="tab"]:hover {{ color: {t['text']}; }}
    .stTabs [aria-selected="true"] {{
        background: {t['tab_sel']} !important;
        color: {t['text']} !important;
        border: 1px solid {t['border']};
    }}

    /* --- Impact Dashboard --- */
    .impact-dashboard {{
        background: {t['card']};
        border: 1px solid {t['border']};
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin: 1.3rem 0;
        animation: fadeIn 0.4s ease-out;
    }}
    .impact-dashboard .impact-title {{
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: {t['accent']};
        margin-bottom: 1rem;
    }}
    .impact-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.9rem;
    }}
    @media (max-width: 640px) {{ .impact-grid {{ grid-template-columns: 1fr; }} }}
    .impact-card {{
        background: {t['bg']};
        border: 1px solid {t['border']};
        border-radius: 12px;
        padding: 1.2rem 0.8rem;
        text-align: center;
        transition: border-color 0.2s ease;
    }}
    .impact-card:hover {{ border-color: {t['accent']}; }}
    .impact-card .impact-emoji {{ font-size: 1.5rem; margin-bottom: 0.3rem; }}
    .impact-card .impact-value {{
        font-size: 1.8rem;
        font-weight: 800;
        color: {t['accent']};
        margin: 0.15rem 0;
    }}
    .impact-card .impact-unit {{
        font-size: 0.8rem;
        color: {t['muted']};
        font-weight: 500;
    }}
    .impact-card .impact-label {{
        font-size: 0.65rem;
        color: {t['dim']};
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
        margin-top: 0.3rem;
    }}

    /* --- Sentry Badge (compact) --- */
    .sentry-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.4rem 0.9rem;
        border-radius: 8px;
        font-size: 0.76rem;
        font-weight: 600;
        margin: 0.4rem 0;
    }}
    .sentry-clear {{
        background: {t['accent']}18;
        border: 1px solid {t['accent']}44;
        color: {t['ok']};
    }}
    .sentry-breach {{
        background: {t['err']}18;
        border: 1px solid {t['err']}44;
        color: {t['err']};
    }}

    /* --- Metric Grid --- */
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.7rem;
        margin: 0.8rem 0;
    }}
    @media (max-width: 768px) {{ .metric-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
    .metric-card {{
        background: {t['bg']};
        border: 1px solid {t['border']};
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }}
    .metric-card .m-val {{
        font-size: 1.4rem;
        font-weight: 800;
        margin: 0.15rem 0;
    }}
    .metric-card .m-lbl {{
        font-size: 0.62rem;
        color: {t['dim']};
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }}
    .v-ok   {{ color: {t['ok']}; }}
    .v-warn {{ color: {t['warn']}; }}
    .v-err  {{ color: {t['err']}; }}
    .v-sl   {{ color: {t['slate']}; }}

    /* --- Alert Boxes --- */
    .alert-box {{
        border-radius: 10px;
        padding: 0.8rem 1.1rem;
        margin: 0.5rem 0;
        font-size: 0.83rem;
        font-weight: 500;
        line-height: 1.6;
    }}
    .alert-ok   {{ background: {t['ok']}12; border: 1px solid {t['ok']}33; color: {t['ok']}; }}
    .alert-err  {{ background: {t['err']}12; border: 1px solid {t['err']}33; color: {t['err']}; }}
    .alert-warn {{ background: {t['warn']}12; border: 1px solid {t['warn']}33; color: {t['warn']}; }}
    .alert-info {{ background: {t['accent']}12; border: 1px solid {t['accent']}33; color: {t['accent']}; }}

    /* --- Tables --- */
    .s-table {{
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid {t['border']};
        margin: 0.7rem 0;
    }}
    .s-table th {{
        background: {t['card']};
        color: {t['dim']};
        font-size: 0.62rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 0.7rem 0.9rem;
        text-align: left;
        border-bottom: 1px solid {t['border']};
    }}
    .s-table td {{
        background: {t['bg']};
        color: {t['text']};
        padding: 0.6rem 0.9rem;
        font-size: 0.8rem;
        border-bottom: 1px solid {t['border']}88;
    }}
    .s-table tr:last-child td {{ border-bottom: none; }}

    /* --- Hide Streamlit branding --- */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header {{ visibility: hidden; }}

    /* --- Footer --- */
    .eco-footer {{
        text-align: center;
        color: {t['dim']};
        font-size: 0.72rem;
        padding: 1.8rem 0 0.8rem;
        border-top: 1px solid {t['border']}88;
        margin-top: 2rem;
    }}
    .eco-footer strong {{ color: {t['muted']}; }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Day 5 Concept: Theme Toggle (top-right)
# ---------------------------------------------------------------------------
_tcol1, _tcol2 = st.columns([9, 1])
with _tcol2:
    _is_light = st.toggle(
        "☀️" if st.session_state.theme == "light" else "🌙",
        value=(st.session_state.theme == "light"),
        help="Toggle light / dark mode",
    )
    _new_theme = "light" if _is_light else "dark"
    if _new_theme != st.session_state.theme:
        st.session_state.theme = _new_theme
        st.rerun()


# ---------------------------------------------------------------------------
# Day 5 Concept: Hero Section
# ---------------------------------------------------------------------------
st.markdown(f"""
<div class="eco-hero">
    <h1>🌍 EcoWatcher</h1>
    <p class="subtitle">
        An AI-powered multi-agent system optimizing the Circular Economy. Paste your waste logs and let our intelligent pipeline classify materials, generate upcycling blueprints, and verify compliance with local municipal recycling protocols.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Day 5 Concept: Feature Explanations with Illustrations
# ---------------------------------------------------------------------------
feat_agents_img = f'<img class="feature-img" src="{_B64_AGENTS}" />' if _B64_AGENTS else ''
feat_sec_img = f'<img class="feature-img" src="{_B64_SECURITY}" />' if _B64_SECURITY else ''
feat_mcp_img = f'<img class="feature-img" src="{_B64_MCP}" />' if _B64_MCP else ''

st.markdown(f"""
<div class="features-section">
    <div class="feature-row">
        <div class="feature-text">
            <h3>🤖 Multi-Agent AI Pipeline</h3>
            <p>Our system orchestrates multiple specialized AI models working in sequence. <strong>Agent A</strong> extracts and classifies raw materials from unstructured logs, while <strong>Agent B</strong> acts as the creative architect, generating actionable upcycling blueprints.</p>
        </div>
        {feat_agents_img}
    </div>
    <div class="feature-row reverse">
        <div class="feature-text">
            <h3>🛡️ Security & Privacy Guardrails</h3>
            <p>Data privacy is critical. Our offline <strong>Security Sentry</strong> intercepts and masks personally identifiable information (PII) like emails, SSNs, and API keys before any data is sent to the LLM cloud environment.</p>
        </div>
        {feat_sec_img}
    </div>
    <div class="feature-row">
        <div class="feature-text">
            <h3>📍 Grounded by Local MCP Rules</h3>
            <p><strong>Agent C</strong> serves as the sustainability auditor. It leverages a local <strong>Model Context Protocol (MCP)</strong> tool to cross-reference the generated blueprints against your exact municipal recycling rules, effectively preventing AI hallucinations.</p>
        </div>
        {feat_mcp_img}
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Day 5 Concept: Input Section
# ---------------------------------------------------------------------------
st.markdown("#### 📋 Waste Log Input")
user_input = st.text_area(
    label="Paste your waste description below:",
    height=120,
    placeholder=(
        "Example: I cleaned out my garage and found three old mason jars, "
        "a huge pile of Amazon shipping boxes, a broken Dell laptop with a "
        "cracked screen, and a bag of old cotton t-shirts..."
    ),
    label_visibility="collapsed",
)

st.markdown("#### 📍 Location")
user_location = st.text_input(
    label="Location for scrap dealer search",
    placeholder="e.g., Seattle, WA (Optional)",
    label_visibility="collapsed",
)

# ---------------------------------------------------------------------------
# Day 5 Concept: Process Button
# ---------------------------------------------------------------------------
process_clicked = st.button("🚀  Process Waste Matrix", use_container_width=True)


# ---------------------------------------------------------------------------
# Day 5 Concept: Main Processing Logic
# ---------------------------------------------------------------------------
if process_clicked:
    if not user_input or not user_input.strip():
        st.markdown(
            '<div class="alert-box alert-warn">⚠️ Please paste a waste description above.</div>',
            unsafe_allow_html=True,
        )
        st.stop()

    import importlib
    import security_guardrails
    import agent_engine
    
    # Force reload modules so Streamlit picks up our recent changes
    importlib.reload(security_guardrails)
    importlib.reload(agent_engine)
    
    from security_guardrails import execute_security_scan
    from agent_engine import run_pipeline

    # ===================================================================
    # PHASE 1: Security Pre-Processing
    # ===================================================================
    with st.spinner("🛡️ Running security sentry scan..."):
        st.session_state.security_result = execute_security_scan(user_input)

    # ===================================================================
    # PHASE 2: Multi-Agent Pipeline Execution
    # ===================================================================
    with st.spinner("🤖 Executing multi-agent pipeline (Agents A → B → C → D)..."):
        try:
            pr = run_pipeline(
                sanitized_input=st.session_state.security_result.sanitized_input,
                location=user_location
            )
            st.session_state.pipeline_result = pr
            
            # Surface agent-level errors directly to the UI
            if pr and not pr.pipeline_success:
                err_msgs = []
                for agent_res in [pr.agent_a_result, pr.agent_b_result, pr.agent_c_result, pr.agent_d_result]:
                    if agent_res and not agent_res.success and agent_res.error:
                        err_msgs.append(f"**{agent_res.agent_name} Error:** {agent_res.error}")
                
                st.session_state.pipeline_error = " \\n\\n ".join(err_msgs) if err_msgs else None
            else:
                st.session_state.pipeline_error = None

        except Exception as e:
            st.session_state.pipeline_error = str(e)
            st.session_state.pipeline_result = None

# ===================================================================
# PHASE 2.5 & 3: Render Results (Persists across reruns)
# ===================================================================
if "security_result" in st.session_state:
    security_result = st.session_state.security_result
    pipeline_result = st.session_state.get("pipeline_result")
    pipeline_error = st.session_state.get("pipeline_error")

    # ===================================================================
    # PHASE 2.5: Environmental Impact Dashboard
    # ===================================================================
    materials = pipeline_result.materials_extracted if pipeline_result else []
    impact = _estimate_impact(materials)

    if impact["co2_kg"] > 0:
        lf = impact["landfill_g"]
        lf_disp, lf_unit = (f"{lf / 1000:.1f}", "kg") if lf >= 1000 else (str(lf), "g")

        st.markdown(f"""
        <div class="impact-dashboard">
            <div class="impact-title">🌱 Environmental Impact Estimate</div>
            <div class="impact-grid">
                <div class="impact-card">
                    <div class="impact-emoji">📉</div>
                    <div class="impact-value">{impact['co2_kg']}</div>
                    <div class="impact-unit">kg CO₂e saved</div>
                    <div class="impact-label">Carbon Footprint Offset</div>
                </div>
                <div class="impact-card">
                    <div class="impact-emoji">📦</div>
                    <div class="impact-value">{lf_disp}</div>
                    <div class="impact-unit">{lf_unit} diverted</div>
                    <div class="impact-label">Landfill Diversion Mass</div>
                </div>
                <div class="impact-card">
                    <div class="impact-emoji">🌲</div>
                    <div class="impact-value">{impact['circularity_pct']}%</div>
                    <div class="impact-unit">circularity index</div>
                    <div class="impact-label">Circularity Impact Score</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ===================================================================
    # PHASE 3: Tab Display
    # ===================================================================
    tab1, tab2, tab4, tab3 = st.tabs([
        "♻️ Upcycle Blueprints",
        "📍 Local Triage Protocols",
        "🗺️ Local Scrap Dealers",
        "🛡️ Sentry Logs",
    ])

    # --- TAB 1: Agent B ---
    with tab1:
        if pipeline_error:
            st.markdown(f'<div class="alert-box alert-err">❌ {pipeline_error}</div>', unsafe_allow_html=True)
        elif pipeline_result and pipeline_result.agent_b_result:
            b = pipeline_result.agent_b_result
            if b.success:
                if materials:
                    st.markdown(
                        f'<div class="alert-box alert-info">🔍 <strong>Materials:</strong> {" · ".join(materials)}</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown(b.output)
            else:
                st.markdown(f'<div class="alert-box alert-err">❌ {b.error}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-warn">⚠️ No data available.</div>', unsafe_allow_html=True)

    # --- TAB 2: Agent C (MCP) ---
    with tab2:
        if pipeline_error:
            st.markdown(f'<div class="alert-box alert-err">❌ {pipeline_error}</div>', unsafe_allow_html=True)
        elif pipeline_result and pipeline_result.agent_c_result:
            c = pipeline_result.agent_c_result
            if c.success:
                st.markdown(
                    '<div class="alert-box alert-ok">'
                    "✅ <strong>MCP Verification Complete</strong> — Cross-referenced via "
                    "<code>query_local_registry()</code> tool binding."
                    "</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(c.output)
            else:
                st.markdown(f'<div class="alert-box alert-err">❌ {c.error}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box alert-warn">⚠️ No data available.</div>', unsafe_allow_html=True)

    # --- TAB 4: Agent D (Local Finder) ---
    with tab4:
        if pipeline_error:
            st.markdown(f'<div class="alert-box alert-err">❌ {pipeline_error}</div>', unsafe_allow_html=True)
        elif pipeline_result and pipeline_result.agent_d_result:
            d = pipeline_result.agent_d_result
            if d.success:
                st.markdown(
                    '<div class="alert-box alert-ok">'
                    "✅ <strong>Google Search Grounding Complete</strong> — Results fetched from live web search."
                    "</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(d.output)
            else:
                st.markdown(f'<div class="alert-box alert-err">❌ {d.error}</div>', unsafe_allow_html=True)
        else:
            if not user_location:
                st.markdown('<div class="alert-box alert-warn">⚠️ No location provided. Please enter a location to search for local scrap dealers.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="alert-box alert-warn">⚠️ No data available.</div>', unsafe_allow_html=True)

    # --- TAB 3: Security Sentry ---
    with tab3:
        if security_result.security_breach:
            st.markdown(
                f'<span class="sentry-badge sentry-breach">'
                f"🚨 PII intercepted — {security_result.redaction_count} redaction(s) applied"
                f"</span>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="sentry-badge sentry-clear">✅ Input clean — no sensitive data</span>',
                unsafe_allow_html=True,
            )

        st.markdown("### Execution Metrics")
        breach_c = "v-err" if security_result.security_breach else "v-ok"
        breach_t = "BREACH" if security_result.security_breach else "CLEAR"
        red_c = "v-warn" if security_result.redaction_count > 0 else "v-ok"
        p_lat = pipeline_result.total_latency_ms if pipeline_result else 0

        st.markdown(f"""
        <div class="metric-grid">
            <div class="metric-card"><div class="m-lbl">PII Scan</div><div class="m-val {breach_c}">{breach_t}</div></div>
            <div class="metric-card"><div class="m-lbl">Redactions</div><div class="m-val {red_c}">{security_result.redaction_count}</div></div>
            <div class="metric-card"><div class="m-lbl">Scan Latency</div><div class="m-val v-sl">{security_result.scan_latency_ms} ms</div></div>
            <div class="metric-card"><div class="m-lbl">Pipeline</div><div class="m-val v-sl">{p_lat:.0f} ms</div></div>
        </div>
        """, unsafe_allow_html=True)

        if security_result.security_breach and security_result.threat_categories:
            st.markdown(
                f'<div style="font-size:0.76rem;color:{t["muted"]};margin:0.4rem 0;">'
                f'<strong style="color:{t["err"]};">Threats:</strong> '
                f'{" · ".join(security_result.threat_categories)}</div>',
                unsafe_allow_html=True,
            )

        if security_result.detailed_log:
            st.markdown("### Threat Log")
            rows = ""
            for i, (tt, sn) in enumerate(security_result.detailed_log, 1):
                rows += (
                    f"<tr><td style='color:{t['dim']};'>{i}</td>"
                    f"<td style='color:{t['err']};font-weight:600;'>{tt}</td>"
                    f"<td><code style='background:{t['card']};padding:2px 6px;border-radius:4px;"
                    f"color:{t['warn']};font-size:0.78rem;'>{sn}</code></td>"
                    f"<td style='color:{t['ok']};font-weight:600;'>REDACTED</td></tr>"
                )
            st.markdown(
                f'<table class="s-table"><thead><tr>'
                f"<th>#</th><th>Threat</th><th>Pattern</th><th>Action</th>"
                f"</tr></thead><tbody>{rows}</tbody></table>",
                unsafe_allow_html=True,
            )

        st.markdown("### Pipeline Breakdown")
        agents = []
        if pipeline_result:
            for label, role, res in [
                ("A", "Classifier", pipeline_result.agent_a_result),
                ("B", "Maker", pipeline_result.agent_b_result),
                ("C", "Auditor (MCP)", pipeline_result.agent_c_result),
                ("D", "Local Finder (Web)", getattr(pipeline_result, "agent_d_result", None)),
            ]:
                if res:
                    s = f'<span style="color:{t["ok"]};">✓</span>' if res.success else f'<span style="color:{t["err"]};">✗ {res.error}</span>'
                    agents.append((label, role, f"{res.latency_ms:.0f} ms", s))

        if agents:
            rows = ""
            for aid, role, lat, status in agents:
                rows += (
                    f"<tr><td style='font-weight:700;color:{t['accent']};'>Agent {aid}</td>"
                    f"<td>{role}</td>"
                    f"<td style='font-weight:600;color:{t['slate']};'>{lat}</td>"
                    f"<td>{status}</td></tr>"
                )
            st.markdown(
                f'<table class="s-table"><thead><tr>'
                f"<th>Agent</th><th>Role</th><th>Latency</th><th>Status</th>"
                f"</tr></thead><tbody>{rows}</tbody></table>",
                unsafe_allow_html=True,
            )
        elif pipeline_error:
            st.markdown(f'<div class="alert-box alert-err">❌ {pipeline_error}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Day 5 Concept: Footer
# ---------------------------------------------------------------------------
st.markdown(f"""
<div class="eco-footer">
    <strong>EcoWatcher v1.0</strong> — Kaggle 5-Day AI Agents Intensive Capstone<br>
    <span style="display:inline-block;margin-top:0.3rem;">Google GenAI SDK · Gemini 2.5 Flash · Streamlit</span>
</div>
""", unsafe_allow_html=True)
