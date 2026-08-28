
import streamlit as st
import pandas as pd
import altair as alt
from datetime import date
from supabase import create_client, Client

st.set_page_config(
    page_title="Q4A Trainer",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="auto",  # colapsado en móvil, abierto en escritorio
)

# ============================================================
# DATA / SUPABASE
# ============================================================
@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

try:
    supabase = get_supabase()
    DB_OK = True
except Exception:
    DB_OK = False
    supabase = None

def profile_get():
    if not DB_OK: return None
    r = supabase.table("profile").select("*").eq("id", 1).limit(1).execute()
    return r.data[0] if r.data else None

def body_get():
    if not DB_OK: return pd.DataFrame()
    r = supabase.table("body_logs").select("*").order("log_date").execute()
    return pd.DataFrame(r.data)

def training_get():
    if not DB_OK: return pd.DataFrame()
    r = supabase.table("training_logs").select("*").order("log_date").execute()
    return pd.DataFrame(r.data)

# ============================================================
# PLAN
# ============================================================
DAYS = {
    "Lunes":{"focus":"Piernas + espalda","lift":"Sentadilla","time":20,
      "sets":{**{i:"3×6–8" for i in range(1,5)},**{i:"4×6–8" for i in range(5,9)},**{i:"4×5–7" for i in range(9,16)},16:"3×5 ligero"},
      "amrap":{**{i:["4 dominadas","8 flexiones","15 sentadillas","8 remos/lado","10 elevaciones de rodillas"] for i in range(1,5)},
               **{i:["4 dominadas","10 flexiones","15 sentadillas","10 remos/lado","10 elevaciones de rodillas"] for i in range(5,9)},
               **{i:["4 dominadas","10 flexiones","15 sentadillas","10 remos/lado","12 elevaciones de rodillas"] for i in range(9,13)},
               **{i:["5 dominadas","10 flexiones","15 sentadillas","10 remos/lado","12 elevaciones de rodillas"] for i in range(13,16)},
               16:["4 dominadas","8 flexiones","12 sentadillas","8 remos/lado","10 elevaciones de rodillas"]}},
    "Martes":{"focus":"Bíceps + hombros","lift":"Curl barra Z","time":20,
      "sets":{**{i:"4×8–10" for i in range(1,9)},**{i:"4×6–8" for i in range(9,16)},16:"3×8 ligero"},
      "amrap":{**{i:["8 pike push-ups","10 zancadas","10 curl martillo","15 sentadillas","20 mountain climbers","10 abdominales"] for i in range(1,5)},
               **{i:["8 pike push-ups","12 zancadas","10 curl martillo","15 sentadillas","20 mountain climbers","12 abdominales"] for i in range(5,9)},
               **{i:["10 pike push-ups","12 zancadas","12 curl martillo","15 sentadillas","20 mountain climbers","12 abdominales"] for i in range(9,13)},
               **{i:["10 pike push-ups","12 zancadas","12 curl martillo","15 goblet squats","20 mountain climbers","15 abdominales"] for i in range(13,16)},
               16:["6 pike push-ups","10 zancadas","8 curl martillo","12 sentadillas","15 mountain climbers","10 abdominales"]}},
    "Jueves":{"focus":"Cadena posterior + pecho","lift":"Peso muerto rumano","time":22,
      "sets":{**{i:"3×8–10" for i in range(1,5)},**{i:"4×8" for i in range(5,9)},**{i:"4×6–8" for i in range(9,16)},16:"3×6 ligero"},
      "amrap":{**{i:["4 dominadas supinas","10 flexiones","10 búlgaras","10 remos","15 abdominales"] for i in range(1,5)},
               **{i:["4 dominadas supinas","10 flexiones","12 búlgaras","10 remos","15 abdominales"] for i in range(5,9)},
               **{i:["4 dominadas supinas","10 flexiones","12 búlgaras","12 remos","15 abdominales"] for i in range(9,13)},
               **{i:["5 dominadas supinas","10 flexiones","12 búlgaras","12 remos","15 abdominales"] for i in range(13,16)},
               16:["3 dominadas supinas","8 flexiones","10 búlgaras","8 remos","12 abdominales"]}},
    "Sábado":{"focus":"Tríceps + cuerpo completo","lift":"Extensión tríceps barra Z","time":20,
      "sets":{**{i:"4×8–10" for i in range(1,9)},**{i:"4×6–8" for i in range(9,16)},16:"3×8 ligero"},
      "amrap":{**{i:["4 dominadas","8 flexiones cerradas","15 goblet squats","10 zancadas","10 elevaciones de piernas"] for i in range(1,5)},
               **{i:["4 dominadas","10 flexiones cerradas","15 goblet squats","12 zancadas","10 elevaciones de piernas"] for i in range(5,9)},
               **{i:["4 dominadas","10 flexiones cerradas","15 goblet squats","12 zancadas","12 elevaciones de piernas"] for i in range(9,13)},
               **{i:["5 dominadas","10 flexiones cerradas","15 goblet squats","12 zancadas","12 elevaciones de piernas"] for i in range(13,16)},
               16:["4 dominadas","8 flexiones cerradas","12 goblet squats","10 zancadas","10 elevaciones de piernas"]}}
}
MIN = {1:8,2:8,3:9,4:9,5:9,6:9,7:10,8:10,9:10,10:10,11:11,12:11,13:10,14:11,15:12,16:0}

# Las 4 sesiones semanales, en orden. La base de datos las guarda por nombre de día.
DAY_ORDER = ["Lunes","Martes","Jueves","Sábado"]
# En la interfaz las sesiones se llaman "Workout 1..4"; en la base de datos se
# siguen guardando por nombre de día (columna `day`), así que no hay migración.
WORKOUT_LABELS = [f"Workout {i+1}" for i in range(len(DAY_ORDER))]

def workout_label(day):
    return WORKOUT_LABELS[DAY_ORDER.index(day)] if day in DAY_ORDER else str(day)

def current_week(start_date_str):
    """Semana del programa (1-16) calculada a partir de la fecha de Semana 0."""
    if not start_date_str: return 1
    delta = (date.today() - date.fromisoformat(start_date_str)).days
    if delta < 0: return 1
    return min(16, delta // 7 + 1)

def next_pending(logs):
    """Siguiente sesión pendiente siguiendo el orden del programa:
    semana 1 → Workout 1,2,3,4; semana 2 → Workout 1,2,3,4; etc.
    Se basa en lo que has registrado, NO en el día de la semana de hoy."""
    hechas = set()
    if logs is not None and len(logs):
        for _, r in logs.iterrows():
            if r.get("day") in DAY_ORDER and pd.notna(r.get("week")):
                hechas.add((int(r["week"]), DAY_ORDER.index(r["day"])))
    for w in range(1, 17):
        for i in range(len(DAY_ORDER)):
            if (w, i) not in hechas:
                return w, i
    return 16, len(DAY_ORDER) - 1   # programa completo

# ============================================================
# ICONS (inline SVG, stroke-based — no emoji as functional icons)
# ============================================================
_ICON_PATHS = {
    "scale": '<path d="M12 3v18M7 21h10"/><path d="M5 7h14"/><path d="M5 7 2 15a3 3 0 0 0 6 0L5 7Z"/><path d="M19 7l-3 8a3 3 0 0 0 6 0l-3-8Z"/>',
    "ruler": '<rect x="2.5" y="8" width="19" height="8" rx="1.5"/><line x1="6.5" y1="8" x2="6.5" y2="11.5"/><line x1="10.5" y1="8" x2="10.5" y2="11.5"/><line x1="14.5" y1="8" x2="14.5" y2="11.5"/><line x1="18.5" y1="8" x2="18.5" y2="11.5"/>',
    "dumbbell": '<rect x="1" y="9" width="4" height="6" rx="1"/><rect x="19" y="9" width="4" height="6" rx="1"/><rect x="5.5" y="10.3" width="3" height="3.4"/><rect x="15.5" y="10.3" width="3" height="3.4"/><line x1="8.5" y1="12" x2="15.5" y2="12"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "flame": '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    "trending-up": '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/>',
    "trending-down": '<polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5.2"/><circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none"/>',
    "check-circle": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    "activity": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "chevron-right": '<polyline points="9 6 15 12 9 18"/>',
    "web": '<circle cx="12" cy="12" r="10"/><path d="M12 2v20M2 12h20M4.5 4.5l15 15M19.5 4.5l-15 15"/><path d="M7 4.2A9.9 9.9 0 0 0 4.2 7M20 7a9.9 9.9 0 0 0-2.8-2.8M4.2 17a9.9 9.9 0 0 0 2.8 2.8M17 20a9.9 9.9 0 0 0 2.8-2.8"/>',
    "alert-triangle": '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "trash": '<polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
}

def icon(name, size=18, stroke=1.9):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" class="icn" '
            f'aria-hidden="true" focusable="false">{_ICON_PATHS.get(name, "")}</svg>')

# ============================================================
# PREMIUM UI — design tokens matched to .streamlit/config.toml
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

:root{
  --bg:#0B1120; --surface:#121A2B; --surface-2:#182236;
  --border:rgba(241,245,249,.09); --border-strong:rgba(241,245,249,.16);
  --ink:#F1F5F9; --ink-muted:#93A0B4; --ink-faint:#5B6B84;
  --red:#E4362F; --red-strong:#C6231D; --red-soft:rgba(228,54,47,.14);
  --blue:#3E68F0; --blue-strong:#2447C6; --blue-soft:rgba(62,104,240,.15);
  --green:#22C55E; --green-strong:#16A34A; --green-soft:rgba(34,197,94,.14);
  --amber:#F59E0B; --amber-soft:rgba(245,158,11,.14);
  --r-sm:10px; --r-md:16px; --r-lg:22px; --r-xl:28px;
}

html, body, [class*="css"]{ font-family:'Inter',-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
/* Streamlit inyecta su propia familia con mayor especificidad: forzamos Inter en los componentes propios */
.stat, .stat .label, .stat .delta, .exercise, .exercise .t, .pill, .side-block, .side-block .k, .side-block .v,
.status-pill, .goalbar, .goalbar .row, .hero .eyebrow, .hero p, .card, .card .eyebrow, .session-card .meta,
.empty, .danger-card, .danger-card p{ font-family:'Inter',-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
.stApp{ background:var(--bg); }
.block-container{ max-width:1240px; padding:2rem 2rem 4rem; }
h1,h2,h3{ font-family:'Barlow Condensed',Inter,sans-serif; letter-spacing:-.01em; }
::selection{ background:var(--red-soft); }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"]{ background:var(--surface); border-right:1px solid var(--border); }
.brand{ display:flex; align-items:center; gap:10px; padding:4px 2px 2px; }
.brand .mark{ width:38px; height:38px; border-radius:11px; background:linear-gradient(150deg,var(--red),var(--red-strong)); display:flex; align-items:center; justify-content:center; color:#fff; flex:none; box-shadow:0 6px 16px rgba(228,54,47,.35); }
.brand .name{ font-family:'Barlow Condensed',sans-serif; font-weight:800; font-size:1.32rem; line-height:1.05; color:var(--ink); }
.brand .sub{ font-size:.74rem; color:var(--ink-muted); letter-spacing:.03em; }
[data-testid="stSidebar"] .stButton{ width:100%; margin-bottom:6px; }
[data-testid="stSidebar"] .stButton>button{ width:100%; justify-content:flex-start; gap:10px; padding:11px 14px;
  border-radius:var(--r-md); font-size:.92rem; font-weight:600; min-height:44px; transition:transform .1s ease; }
[data-testid="stSidebar"] .stButton>button:active{ transform:scale(.98); }
[data-testid="stSidebar"] .stButton>button[kind="secondary"]{ background:var(--surface-2); border-color:var(--border); color:var(--ink); }
[data-testid="stSidebar"] .stButton>button[kind="secondary"]:hover{ border-color:var(--border-strong); color:var(--ink); }
[data-testid="stSidebar"] .stButton>button[kind="primary"]{ box-shadow:0 8px 18px -6px rgba(228,54,47,.55); }
.side-block{ margin-top:2px; }
.side-block .k{ font-size:.68rem; text-transform:uppercase; letter-spacing:.11em; color:var(--ink-faint); font-weight:700; }
.side-block .v{ font-size:.86rem; color:var(--ink-muted); margin-top:2px; }
.status-pill{ display:inline-flex; align-items:center; gap:7px; padding:7px 12px; border-radius:999px; font-size:.78rem; font-weight:600; border:1px solid var(--border); }
.status-pill .dot{ width:7px; height:7px; border-radius:50%; flex:none; }
.status-ok{ background:var(--green-soft); color:#7CE2A0; } .status-ok .dot{ background:var(--green); box-shadow:0 0 0 3px var(--green-soft); }
.status-bad{ background:var(--red-soft); color:#FF9E98; } .status-bad .dot{ background:var(--red); box-shadow:0 0 0 3px var(--red-soft); }

/* ---------- hero ---------- */
.hero{ position:relative; overflow:hidden; border:1px solid var(--border); border-radius:var(--r-xl); padding:38px 40px;
  background:radial-gradient(120% 160% at 0% 0%, var(--red-soft) 0%, transparent 55%), radial-gradient(120% 160% at 100% 0%, var(--blue-soft) 0%, transparent 55%), var(--surface); }
.hero::after{ content:""; position:absolute; inset:0; opacity:.35; pointer-events:none;
  background-image:repeating-linear-gradient(45deg, transparent 0 26px, var(--border-strong) 26px 27px), repeating-linear-gradient(-45deg, transparent 0 26px, var(--border-strong) 26px 27px);
  mask-image:radial-gradient(70% 90% at 100% 0%, black, transparent); }
.hero .eyebrow{ position:relative; display:inline-flex; align-items:center; gap:7px; text-transform:uppercase; letter-spacing:.14em; font-size:.72rem; font-weight:800; color:var(--red); }
.hero .eyebrow::before{ content:""; width:16px; height:2px; background:var(--red); border-radius:2px; }
.hero h1{ position:relative; font-size:2.75rem; font-weight:800; line-height:1.02; margin:10px 0 0; color:var(--ink);
  overflow-wrap:normal; word-break:normal; hyphens:none; }
.hero p{ position:relative; margin:10px 0 0; color:var(--ink-muted); font-size:1.02rem; max-width:520px; }

/* ---------- móvil: recuperar ancho útil ---------- */
@media (max-width:640px){
  .block-container{ padding:1rem .75rem 3rem; }
  .hero{ padding:22px 18px; border-radius:var(--r-lg); }
  .hero h1{ font-size:2rem; }
  .hero p{ font-size:.96rem; }
  .stat{ padding:18px 16px; }
  .card, .session-card{ padding:18px 16px; }
  .stat{ height:auto; }
}
/* Streamlit pone margin-bottom:-1rem en stMarkdownContainer (pensado para párrafos).
   En nuestras tarjetas HTML ese margen negativo se come la separación y las pega. */
[data-testid="stMarkdownContainer"]:has(> .stat){ margin-bottom:0 !important; }

/* ---------- cards & stats ---------- */
.card{ border:1px solid var(--border); border-radius:var(--r-lg); padding:22px 24px; background:var(--surface); }
.card .eyebrow{ text-transform:uppercase; letter-spacing:.12em; font-size:.7rem; font-weight:800; color:var(--ink-faint); }
.stat{ border:1px solid var(--border); border-radius:var(--r-lg); padding:18px 20px; background:var(--surface); display:flex; flex-direction:column; gap:6px; height:100%; }
.stat .top{ display:flex; align-items:center; justify-content:space-between; min-height:26px; }
.stat .label{ font-size:.8rem; text-transform:uppercase; letter-spacing:.08em; color:var(--ink-faint); font-weight:700; white-space:nowrap; }
.stat .badge{ width:26px; height:26px; border-radius:8px; display:flex; align-items:center; justify-content:center; flex:none; }
.stat .num{ font-family:'Barlow Condensed',sans-serif; font-size:1.75rem; font-weight:800; letter-spacing:-.02em; color:var(--ink); font-variant-numeric:tabular-nums; line-height:1.2; white-space:nowrap; }
.stat .delta{ display:inline-flex; align-items:center; gap:5px; font-size:.83rem; font-weight:600; width:fit-content; }
.badge-red{ background:var(--red-soft); color:var(--red); } .badge-blue{ background:var(--blue-soft); color:var(--blue); }
.badge-green{ background:var(--green-soft); color:var(--green); } .badge-amber{ background:var(--amber-soft); color:var(--amber); }
.d-good{ color:var(--green); } .d-bad{ color:#FF9E98; } .d-flat{ color:var(--ink-muted); }

/* ---------- session / exercise list ---------- */
.session-card{ border:1px solid var(--border); border-radius:var(--r-lg); padding:24px 26px; background:linear-gradient(155deg,var(--surface),var(--surface) 60%,var(--surface-2)); }
.session-card .day{ font-family:'Barlow Condensed',sans-serif; font-size:1.7rem; font-weight:800; color:var(--ink); margin:2px 0 2px; }
.session-card .meta{ color:var(--ink-muted); font-size:.92rem; }
.exercise{ display:flex; align-items:center; gap:14px; padding:14px 4px; border-bottom:1px solid var(--border); }
.exercise:last-child{ border-bottom:0; }
.exercise .n{ width:30px; height:30px; border-radius:9px; background:var(--surface-2); color:var(--ink-muted); font-size:.83rem; font-weight:800; display:flex; align-items:center; justify-content:center; flex:none; font-variant-numeric:tabular-nums; }
.exercise .t{ font-size:1.19rem; color:var(--ink); font-weight:500; }

/* ---------- pills / badges ---------- */
.pill{ display:inline-flex; align-items:center; gap:6px; padding:7px 13px; border-radius:999px; border:1px solid var(--border); font-size:.76rem; color:var(--ink-muted); font-weight:600; background:var(--surface-2); }
.pill-red{ background:var(--red-soft); color:var(--red); border-color:transparent; }

/* ---------- goal / mini progress bar ---------- */
.goalbar{ margin-top:6px; }
.goalbar .row{ display:flex; justify-content:space-between; font-size:.78rem; color:var(--ink-muted); margin-bottom:6px; }
.goalbar .row b{ color:var(--ink); font-weight:700; }
.goalbar .track{ height:8px; border-radius:999px; background:var(--surface-2); overflow:hidden; }
.goalbar .fill{ height:100%; border-radius:999px; background:linear-gradient(90deg,var(--red),var(--blue)); transition:width .4s ease; }
.goalbar.done .fill{ background:linear-gradient(90deg,var(--green),#3fe08a); }

/* ---------- streamlit widget polish ---------- */
.stButton>button, .stFormSubmitButton>button{ border-radius:12px; font-weight:700; min-height:46px; border:1px solid transparent; }
div[data-baseweb="select"]>div, .stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input{ border-radius:12px !important; }
div[data-testid="stMetric"]{ border:1px solid var(--border); padding:14px 16px; border-radius:var(--r-md); background:var(--surface); }
div[data-testid="stMetricValue"]{ white-space:normal !important; overflow:visible !important; text-overflow:unset !important; word-break:break-word; font-size:1.6rem !important; line-height:1.2 !important; }
div[data-testid="stExpander"]{ border:1px solid var(--border); border-radius:var(--r-md); background:var(--surface); }
hr{ border-color:var(--border) !important; }
.icn{ display:inline-block; vertical-align:middle; }
.empty{ text-align:center; padding:34px 20px; color:var(--ink-muted); border:1px dashed var(--border-strong); border-radius:var(--r-lg); }
.empty .icn{ opacity:.6; margin-bottom:8px; }

/* ---------- danger zone ---------- */
.danger-card{ border:1px solid rgba(228,54,47,.35); background:var(--red-soft); border-radius:var(--r-lg); padding:18px 20px; margin-bottom:14px; }
.danger-card .danger-title{ display:flex; align-items:center; gap:8px; color:var(--red); font-weight:800; font-size:1rem; }
.danger-card p{ color:var(--ink-muted); font-size:.87rem; margin:8px 0 0; }
[data-testid="stExpander"]:has(.danger-card) summary{ color:var(--red); }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================
def stat_card(icon_name, badge, label, value, delta_text=None, delta_kind="flat"):
    delta_html = ""
    if delta_text:
        arrow = {"good":"trending-down" if "kg" in str(value) or "cm" in str(value) else "trending-up",
                 "bad":"trending-up", "flat":"activity"}.get(delta_kind, "activity")
        cls = {"good":"d-good","bad":"d-bad","flat":"d-flat"}.get(delta_kind,"d-flat")
        delta_html = f'<span class="delta {cls}">{icon(arrow,13)}{delta_text}</span>'
    return (f'<div class="stat"><div class="top"><span class="label">{label}</span>'
            f'<span class="badge badge-{badge}">{icon(icon_name,16)}</span></div>'
            f'<div class="num">{value}</div>{delta_html}</div>')

def trend_kind(delta, lower_is_better=True):
    """Sin cambio = neutro. Evita pintar de verde un 0.0 como si fuera progreso."""
    if delta is None: return "flat"
    if abs(delta) < 0.05: return "flat"
    mejora = delta < 0 if lower_is_better else delta > 0
    return "good" if mejora else "bad"

def trend_chart(df, y, titulo, color="#E4362F", fmt=".1f", height=300):
    """Línea con eje ajustado a los datos. st.line_chart fuerza el 0 en el eje,
    lo que aplana por completo cambios pequeños (ej. 87 -> 84.9 kg)."""
    lo, hi = float(df[y].min()), float(df[y].max())
    pad = max((hi - lo) * 0.25, 0.5)
    base = alt.Chart(df).encode(
        x=alt.X("week:Q", title="Semana",
                axis=alt.Axis(tickMinStep=1, format="d", grid=False)),
        y=alt.Y(f"{y}:Q", title=titulo,
                scale=alt.Scale(domain=[lo - pad, hi + pad], nice=False)),
        tooltip=[alt.Tooltip("week:Q", title="Semana", format="d"),
                 alt.Tooltip(f"{y}:Q", title=titulo, format=fmt)],
    )
    linea = base.mark_line(color=color, strokeWidth=2.5,
                           point=alt.OverlayMarkDef(color=color, size=60))
    return (linea.properties(height=height)
            .configure_axis(labelColor="#93A0B4", titleColor="#5B6B84",
                            gridColor="rgba(241,245,249,.09)",
                            domainColor="rgba(241,245,249,.16)", labelFontSize=12)
            .configure_view(strokeWidth=0))

def goal_bar(current, target, unit="rondas", done_label="Objetivo conseguido"):
    pct = 0 if target <= 0 else max(0, min(100, round(current/target*100)))
    done = current >= target and target > 0
    label = done_label if done else f"{current}/{target} {unit}"
    return (f'<div class="goalbar {"done" if done else ""}"><div class="row"><span>Progreso semanal</span>'
            f'<b>{label}</b></div><div class="track"><div class="fill" style="width:{pct}%"></div></div></div>')

def empty_state(icon_name, text):
    st.markdown(f'<div class="empty">{icon(icon_name,26)}<div>{text}</div></div>', unsafe_allow_html=True)

NAV = [
    ("home", "Inicio", ":material/home:"),
    ("training", "Entrenamiento", ":material/fitness_center:"),
    ("progress", "Progreso", ":material/monitoring:"),
    ("week0", "Semana 0", ":material/flag:"),
    ("program", "Programa", ":material/menu_book:"),
]

profile = profile_get()
week_now = current_week(profile["start_date"]) if profile else 1   # semana de calendario
# Sesión pendiente según lo entrenado (no según el día de hoy).
logs_all = training_get()
pend_week, pend_wk = next_pending(logs_all)

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "home"

with st.sidebar:
    st.markdown(f'<div class="brand"><div class="mark">{icon("web",20)}</div>'
                f'<div><div class="name">Q4A Trainer</div><div class="sub">16-week transformation</div></div></div>',
                unsafe_allow_html=True)
    st.write("")
    for key, label, micon in NAV:
        if st.button(label, icon=micon, key=f"nav_{key}", use_container_width=True,
                     type="primary" if st.session_state.nav_page == key else "secondary"):
            st.session_state.nav_page = key
            st.rerun()
    page = st.session_state.nav_page
    st.divider()
    st.markdown('<div class="side-block"><div class="k">Objetivo</div><div class="v">Perder grasa · ganar músculo</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-block" style="margin-top:12px"><div class="k">Prioridades</div><div class="v">Piernas · brazos · espalda</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-block" style="margin-top:12px"><div class="k">Semana actual</div><div class="v">Semana '+str(week_now)+' de 16</div></div>', unsafe_allow_html=True)
    st.write("")
    if DB_OK:
        st.markdown('<span class="status-pill status-ok"><span class="dot"></span>Datos sincronizados</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-pill status-bad"><span class="dot"></span>Supabase no conectado</span>', unsafe_allow_html=True)

# ============================================================
# HOME
# ============================================================
if page == "home":
    st.markdown(f'<div class="hero"><div class="eyebrow">16 WEEK TRANSFORMATION</div>'
                f'<h1>Tu entrenamiento.<br>Tu progreso.</h1>'
                f'<p>Una experiencia simple para entrenar duro, medir mejor y ver cómo cambias.</p></div>',
                unsafe_allow_html=True)
    st.write("")
    body=body_get(); logs=logs_all
    if profile:
        weight=float(body.iloc[-1]["weight"]) if len(body) else float(profile["start_weight"])
        dw=weight-float(profile["start_weight"])
        waist = body["waist"].dropna() if len(body) else pd.Series(dtype=float)
        waist_now=float(waist.iloc[-1]) if len(waist) else None
        a,b,c,d=st.columns(4)
        with a:
            st.markdown(stat_card("scale","red","Peso",f"{weight:.1f} kg",
                        f"{dw:+.1f} kg desde inicio", trend_kind(dw)), unsafe_allow_html=True)
        with b:
            if waist_now is not None:
                dwa = waist_now - float(profile["start_waist"]) if profile.get("start_waist") else None
                dtext = f"{dwa:+.1f} cm desde inicio" if dwa is not None else "última medición"
                kind = trend_kind(dwa)
                st.markdown(stat_card("ruler","blue","Cintura",f"{waist_now:.1f} cm", dtext, kind), unsafe_allow_html=True)
            else:
                st.markdown(stat_card("ruler","blue","Cintura","—", "Añade tu medida", "flat"), unsafe_allow_html=True)
        with c:
            st.markdown(stat_card("dumbbell","green","Dominadas",str(profile["start_pullups"]), "marca inicial", "flat"), unsafe_allow_html=True)
        with d:
            # Progreso real = sesiones registradas, no tiempo transcurrido.
            hechas = len(logs)
            total_sesiones = 16 * len(DAYS)
            st.markdown(stat_card("check-circle","amber","Sesiones", f"{hechas} / {total_sesiones}",
                                  f"semana {week_now} de 16", "flat"), unsafe_allow_html=True)
        st.write("")
        d_info = DAYS[DAY_ORDER[pend_wk]]
        st.markdown(f'<div class="session-card"><div class="eyebrow" style="color:var(--red);text-transform:uppercase;letter-spacing:.12em;font-size:.72rem;font-weight:800">'
                    f'{icon("flame",13)} PRÓXIMA SESIÓN</div>'
                    f'<div class="day">Semana {pend_week} · Workout {pend_wk+1}</div>'
                    f'<div class="meta">{d_info["focus"]} · {d_info["lift"]} · AMRAP {d_info["time"]} min '
                    f'· mínimo {MIN[pend_week]} rondas</div></div>',
                    unsafe_allow_html=True)
    else:
        empty_state("target", "Empieza configurando tu Semana 0 para activar tu panel de progreso.")

# ============================================================
# TRAINING
# ============================================================
elif page == "training":
    st.markdown('<div class="hero"><div class="eyebrow">WORKOUT</div><h1>Entrena.</h1><p>Fuerza primero. AMRAP después. Técnica siempre.</p></div>',unsafe_allow_html=True)
    st.write("")
    _aviso = st.session_state.pop("aviso_guardado", None)
    if _aviso:
        st.success(_aviso, icon="✅")

    # Sin selectores: siempre toca la siguiente sesión pendiente, en orden.
    # No se puede saltar adelante; el avance sale de lo que hay registrado.
    total_sesiones = 16 * len(DAY_ORDER)
    completadas = len(logs_all)
    programa_completo = completadas >= total_sesiones

    if programa_completo:
        st.success("🏁 Has completado las 16 semanas. Para retocar una sesión, ve a Progreso → "
                   "*Corregir o borrar una sesión guardada*.")
        st.stop()

    week, wk_idx = pend_week, pend_wk
    day = DAY_ORDER[wk_idx]
    d = DAYS[day]

    st.markdown(f'<span class="pill pill-red">Semana {week} · Workout {wk_idx+1}</span> '
                f'<span class="pill">{d["focus"]}</span> '
                f'<span class="pill">{completadas} de {total_sesiones} hechas</span>',
                unsafe_allow_html=True)
    st.caption("Las sesiones se hacen en orden: al guardar esta, pasarás automáticamente a la siguiente.")
    st.write("")
    st.markdown(stat_card("dumbbell","red","Ejercicio", d["lift"]), unsafe_allow_html=True)
    c2,c3=st.columns(2)
    with c2: st.markdown(stat_card("activity","blue","Trabajo", d["sets"][week]), unsafe_allow_html=True)
    with c3: st.markdown(stat_card("flame","green","AMRAP", f'{d["time"]} min'), unsafe_allow_html=True)
    st.divider()
    st.markdown(f'### {icon("dumbbell",20)} Ejercicio principal', unsafe_allow_html=True)
    x1,x2,x3=st.columns(3)
    with x1: lw=st.number_input("Peso (kg)",0.0,300.0,0.0,1.25)
    with x2: sr=st.text_input("Series / reps",placeholder="8 / 8 / 7")
    with x3: rir=st.selectbox("RIR final",[0,1,2,3,4],index=2,
        help=("**RIR** = *Reps In Reserve* (repeticiones en reserva). Cuántas repeticiones más "
              "**podrías haber hecho** al acabar la última serie, antes de llegar al fallo.\n\n"
              "- **0** · al fallo, no podías ni una más\n"
              "- **1** · te quedaba una\n"
              "- **2** · te quedaban dos (lo habitual en este programa)\n"
              "- **3–4** · serie cómoda, lejos del fallo\n\n"
              "Si te sobran 4, el peso se te ha quedado corto. Si acabas a 0 todas las series, "
              "probablemente acumules más fatiga de la que puedes recuperar."))
    st.markdown(f'### {icon("flame",20)} AMRAP · {d["time"]} min', unsafe_allow_html=True)
    for i,ex in enumerate(d["amrap"][week],1):
        st.markdown(f'<div class="exercise"><span class="n">{i:02d}</span><span class="t">{ex}</span></div>',unsafe_allow_html=True)
    x1,x2=st.columns(2)
    with x1: rounds=st.number_input("Rondas completas",0,100,0,1)
    with x2: extra=st.number_input("Repeticiones extra",0,100,0,1)
    if week<16:
        st.markdown(goal_bar(rounds, MIN[week]), unsafe_allow_html=True)
    else:
        st.info("Semana 16 · descarga + tests")
    notes=st.text_area("Notas",placeholder="Energía · técnica · molestias · sensaciones…")
    if st.button("Guardar entrenamiento",type="primary",use_container_width=True):
        # Red de seguridad: si se reenvía el formulario (p. ej. refrescando la página
        # justo después de guardar) no se duplica la sesión.
        _actuales = training_get()
        if len(_actuales) and len(_actuales[(_actuales["week"]==week) & (_actuales["day"]==day)]):
            st.warning("Esa sesión ya estaba registrada. Recarga la página para ver la siguiente.")
            st.stop()
        if DB_OK:
            try:
                supabase.table("training_logs").insert({"log_date":str(date.today()),"week":week,"day":day,"lift":d["lift"],"weight":lw or None,"sets_reps":sr,"rir":rir,"rounds":rounds,"extra_reps":extra,"notes":notes}).execute()
            except Exception as ex:
                st.error(f"No se pudo guardar: {ex}"); st.stop()
            # La siguiente se calcula releyendo lo registrado, no con un +1: si
            # había un hueco anterior, el mensaje debe decir la sesión real.
            n_week, n_wk = next_pending(training_get())
            st.session_state.aviso_guardado = (
                f"Workout {wk_idx+1} de la semana {week} guardado. "
                f"Siguiente: Workout {n_wk+1} de la semana {n_week}."
            )
            st.toast("Entrenamiento guardado", icon="✅")
            st.rerun()
        else: st.error("Supabase no está conectado.")

# ============================================================
# PROGRESS
# ============================================================
elif page == "progress":
    st.markdown('<div class="hero"><div class="eyebrow">YOUR DATA</div><h1>Progreso.</h1><p>Semana 0 como referencia. Cada dato cuenta.</p></div>',unsafe_allow_html=True)
    st.write("")
    body=body_get(); logs=logs_all
    if not profile:
        empty_state("target", "Primero configura tu Semana 0 en el menú lateral.")
    else:
        with st.expander(f"➕ Registrar peso / cintura de esta semana", expanded=(len(body)==0)):
            f1,f2,f3,f4=st.columns([1,1,1,1])
            with f1: log_week=st.selectbox("Semana",range(1,17),index=week_now-1,key="bw_week")
            with f2: log_date=st.date_input("Fecha",date.today(),key="bw_date")
            with f3: log_weight=st.number_input("Peso (kg)",30.0,250.0,float(profile["start_weight"]),0.1,key="bw_weight")
            with f4: log_waist=st.number_input("Cintura (cm)",40.0,180.0,value=None,step=0.1,key="bw_waist",
                                               placeholder="opcional", help="Déjalo vacío si hoy no te has medido.")
            if st.button("Guardar medición", type="primary", use_container_width=True):
                if DB_OK:
                    supabase.table("body_logs").insert({"log_date":str(log_date),"week":log_week,"weight":log_weight,"waist":log_waist}).execute()
                    st.toast("Medición guardada", icon="✅")
                    st.rerun()
                else:
                    st.error("Supabase no está conectado.")
        if len(body):
            body["week"]=pd.to_numeric(body["week"]); body["weight"]=pd.to_numeric(body["weight"]); body["waist"]=pd.to_numeric(body["waist"],errors="coerce")
            current=float(body.iloc[-1]["weight"]); delta=current-float(profile["start_weight"])
            waist=body["waist"].dropna(); cw=float(waist.iloc[-1]) if len(waist) else None
            a,b=st.columns(2)
            with a: st.markdown(stat_card("scale","red","Peso",f"{current:.1f} kg",
                        f"{delta:+.1f} kg vs inicio", trend_kind(delta)), unsafe_allow_html=True)
            with b:
                dwa = (cw - float(profile["start_waist"])) if (cw and profile.get("start_waist")) else None
                st.markdown(stat_card("ruler","blue","Cintura", f"{cw:.1f} cm" if cw else "—",
                            f"{dwa:+.1f} cm vs inicio" if dwa is not None else "última medición",
                            trend_kind(dwa)), unsafe_allow_html=True)
            c,d=st.columns(2)
            with c: st.markdown(stat_card("dumbbell","green","Dominadas",f"{profile['start_pullups']}","Semana 0","flat"), unsafe_allow_html=True)
            with d: st.markdown(stat_card("activity","amber","Flexiones",f"{profile['start_pushups']}","Semana 0","flat"), unsafe_allow_html=True)
            st.markdown(f'### {icon("scale",20)} Peso', unsafe_allow_html=True)
            weekly=body.groupby("week",as_index=False)["weight"].mean()
            chart=pd.concat([pd.DataFrame({"week":[0],"weight":[float(profile["start_weight"])]}),weekly],ignore_index=True).drop_duplicates("week",keep="last").sort_values("week")
            st.altair_chart(trend_chart(chart,"weight","Peso (kg)","#E4362F"),use_container_width=True)
            if profile.get("start_waist"):
                wd=body.dropna(subset=["waist"]).groupby("week",as_index=False)["waist"].last()
                if len(wd):
                    st.markdown(f'### {icon("ruler",20)} Cintura', unsafe_allow_html=True)
                    chart2=pd.concat([pd.DataFrame({"week":[0],"waist":[float(profile["start_waist"])]}),wd],ignore_index=True).drop_duplicates("week",keep="last").sort_values("week")
                    st.altair_chart(trend_chart(chart2,"waist","Cintura (cm)","#3E68F0"),use_container_width=True)
        else:
            empty_state("scale", "Todavía no hay mediciones corporales. Registra la primera arriba.")
        if len(logs):
            st.markdown(f'### {icon("dumbbell",20)} Fuerza', unsafe_allow_html=True)
            for lift in logs["lift"].dropna().unique():
                q=logs[logs["lift"]==lift].copy(); q["weight"]=pd.to_numeric(q["weight"],errors="coerce"); q=q.dropna(subset=["weight"]).groupby("week",as_index=False)["weight"].max()
                if len(q):
                    st.write(f"**{lift}**")
                    st.altair_chart(trend_chart(q,"weight","kg","#22C55E",height=180),use_container_width=True)
            st.markdown(f'### {icon("flame",20)} AMRAP', unsafe_allow_html=True)
            # Barras AGRUPADAS por día: apilarlas sumaría rondas de sesiones distintas,
            # y esa suma no significa nada.
            q=logs.groupby(["week","day"],as_index=False)["rounds"].max()
            q["workout"]=q["day"].map(workout_label)
            amrap=(alt.Chart(q).mark_bar(cornerRadiusTopLeft=3,cornerRadiusTopRight=3)
                   .encode(
                       x=alt.X("week:O", title="Semana", axis=alt.Axis(labelAngle=0)),
                       xOffset=alt.XOffset("workout:N", sort=WORKOUT_LABELS),
                       y=alt.Y("rounds:Q", title="Rondas"),
                       color=alt.Color("workout:N", title="Sesión", sort=WORKOUT_LABELS,
                                       scale=alt.Scale(domain=WORKOUT_LABELS,
                                                       range=["#E4362F","#3E68F0","#22C55E","#F59E0B"])),
                       tooltip=[alt.Tooltip("week:O",title="Semana"),alt.Tooltip("workout:N",title="Sesión"),
                                alt.Tooltip("rounds:Q",title="Rondas")])
                   .properties(height=280)
                   .configure_axis(labelColor="#93A0B4",titleColor="#5B6B84",
                                   gridColor="rgba(241,245,249,.09)",
                                   domainColor="rgba(241,245,249,.16)",labelFontSize=12)
                   .configure_legend(labelColor="#93A0B4",titleColor="#5B6B84")
                   .configure_view(strokeWidth=0))
            st.altair_chart(amrap,use_container_width=True)
            st.markdown(f'### {icon("activity",20)} Historial', unsafe_allow_html=True)
            hist=logs.sort_values(["week","log_date"],ascending=[False,False]).copy()
            hist["day"]=hist["day"].map(workout_label)
            hist=(hist.drop(columns=[c for c in ("id",) if c in hist.columns])
                      .rename(columns={"log_date":"Fecha","week":"Semana","day":"Sesión","lift":"Ejercicio",
                                       "weight":"Peso (kg)","sets_reps":"Series/reps","rir":"RIR",
                                       "rounds":"Rondas","extra_reps":"Reps extra","notes":"Notas"}))
            st.dataframe(hist,use_container_width=True,hide_index=True)

            # ---------- editar / borrar una sesión ya guardada ----------
            with st.expander("✏️ Corregir o borrar una sesión guardada"):
                ed = logs.sort_values(["week","log_date"],ascending=[False,False])
                def _etiqueta(r):
                    wnum = DAY_ORDER.index(r["day"])+1 if r["day"] in DAY_ORDER else "?"
                    return f'Semana {int(r["week"])} · Workout {wnum} · {r["lift"]} ({r["log_date"]})'
                opciones = {int(r["id"]): _etiqueta(r) for _, r in ed.iterrows()}
                sid = st.selectbox("Sesión", list(opciones), format_func=lambda k: opciones[k], key="ed_sel")
                fila = logs[logs["id"] == sid].iloc[0]

                with st.form("editar_sesion"):
                    e1,e2,e3 = st.columns(3)
                    with e1:
                        e_week = st.number_input("Semana",1,16,int(fila["week"]),1)
                    with e2:
                        e_idx = st.selectbox("Workout",range(len(DAY_ORDER)),
                                             index=DAY_ORDER.index(fila["day"]) if fila["day"] in DAY_ORDER else 0,
                                             format_func=lambda i:f"Workout {i+1} · {DAYS[DAY_ORDER[i]]['focus']}")
                        e_day = DAY_ORDER[e_idx]
                    with e3:
                        e_fecha = st.date_input("Fecha", date.fromisoformat(str(fila["log_date"])[:10]))
                    g1,g2,g3 = st.columns(3)
                    with g1:
                        e_peso = st.number_input("Peso (kg)",0.0,300.0,
                                                 float(fila["weight"]) if pd.notna(fila["weight"]) else 0.0,1.25)
                    with g2:
                        e_sr = st.text_input("Series / reps", fila["sets_reps"] if pd.notna(fila["sets_reps"]) else "")
                    with g3:
                        e_rir = st.selectbox("RIR final",[0,1,2,3,4],
                                             index=int(fila["rir"]) if pd.notna(fila["rir"]) and 0<=int(fila["rir"])<=4 else 2)
                    h1,h2 = st.columns(2)
                    with h1:
                        e_rondas = st.number_input("Rondas completas",0,100,
                                                   int(fila["rounds"]) if pd.notna(fila["rounds"]) else 0,1)
                    with h2:
                        e_extra = st.number_input("Repeticiones extra",0,100,
                                                  int(fila["extra_reps"]) if pd.notna(fila["extra_reps"]) else 0,1)
                    e_notas = st.text_area("Notas", fila["notes"] if pd.notna(fila["notes"]) else "")

                    b1,b2 = st.columns(2)
                    guardar = b1.form_submit_button("Guardar cambios",type="primary",use_container_width=True)
                    borrar  = b2.form_submit_button("Borrar esta sesión",use_container_width=True)

                if guardar:
                    if not DB_OK:
                        st.error("Supabase no está conectado.")
                    else:
                        try:
                            supabase.table("training_logs").update({
                                "log_date":str(e_fecha),"week":e_week,"day":e_day,
                                "lift":DAYS[e_day]["lift"],"weight":e_peso or None,"sets_reps":e_sr,
                                "rir":e_rir,"rounds":e_rondas,"extra_reps":e_extra,"notes":e_notas,
                            }).eq("id",sid).execute()
                        except Exception as ex:
                            st.error(f"No se pudo guardar: {ex}"); st.stop()
                        nuevo = training_get()
                        fila_n = nuevo[nuevo["id"]==sid]
                        if len(fila_n) and int(fila_n.iloc[0]["rounds"] or 0)==e_rondas and str(fila_n.iloc[0]["day"])==e_day:
                            st.toast("Sesión actualizada", icon="✅"); st.rerun()
                        else:
                            st.error("**No se ha guardado el cambio.** Falta la política UPDATE en Supabase: "
                                     "vuelve a ejecutar `supabase_schema.sql` en el SQL Editor.")
                if borrar:
                    if not DB_OK:
                        st.error("Supabase no está conectado.")
                    else:
                        try:
                            supabase.table("training_logs").delete().eq("id",sid).execute()
                        except Exception as ex:
                            st.error(f"No se pudo borrar: {ex}"); st.stop()
                        if len(training_get()[training_get()["id"]==sid])==0:
                            st.toast("Sesión borrada", icon="🗑️"); st.rerun()
                        else:
                            st.error("**No se ha borrado.** Falta la política DELETE en Supabase: "
                                     "vuelve a ejecutar `supabase_schema.sql` en el SQL Editor.")
        else:
            empty_state("activity", "Todavía no hay entrenamientos registrados.")

# ============================================================
# WEEK 0
# ============================================================
elif page == "week0":
    st.markdown('<div class="hero"><div class="eyebrow">BASELINE</div><h1>Empieza aquí.</h1><p>Guarda tu punto de partida. La aplicación medirá todo contra esta referencia.</p></div>',unsafe_allow_html=True)
    st.write("")
    with st.form("baseline"):
        a,b,c=st.columns(3)
        with a: sw=st.number_input("Peso (kg)",40.0,200.0,float(profile["start_weight"]) if profile else 87.0,.1); wa=st.number_input("Cintura (cm)",40.0,180.0,float(profile["start_waist"]) if profile and profile.get("start_waist") else 90.0,.1)
        with b: pu=st.number_input("Dominadas máximas",0,50,int(profile["start_pullups"]) if profile else 8,1); fl=st.number_input("Flexiones máximas",0,100,int(profile["start_pushups"]) if profile else 15,1)
        with c: sq=st.number_input("Sentadilla (kg)",0.0,300.0,float(profile["start_squat"]) if profile and profile.get("start_squat") else 0.0,1.25); rdl=st.number_input("Peso muerto rumano (kg)",0.0,300.0,float(profile["start_rdl"]) if profile and profile.get("start_rdl") else 0.0,1.25)
        a,b=st.columns(2)
        with a: curl=st.number_input("Curl Z (kg)",0.0,150.0,float(profile["start_curl"]) if profile and profile.get("start_curl") else 0.0,1.25); tri=st.number_input("Tríceps Z (kg)",0.0,150.0,float(profile["start_triceps"]) if profile and profile.get("start_triceps") else 0.0,1.25)
        with b:
            cindy=st.number_input("Cindy · rondas",0.0,50.0,float(profile["start_cindy"]) if profile and profile.get("start_cindy") else 0.0,1.0,
                help=("**Cindy** es un test de referencia clásico: AMRAP de **20 minutos** repitiendo esta ronda "
                      "tantas veces como puedas.\n\n"
                      "- 5 dominadas\n"
                      "- 10 flexiones\n"
                      "- 15 sentadillas\n\n"
                      "Anota las **rondas completas** que consigas. Sirve como marca inicial para comparar tu "
                      "resistencia al final de las 16 semanas."))
            sd=st.date_input("Fecha",date.fromisoformat(profile["start_date"]) if profile and profile.get("start_date") else date.today())
        if st.form_submit_button("Guardar Semana 0",type="primary",use_container_width=True):
            if DB_OK:
                supabase.table("profile").upsert({"id":1,"start_date":str(sd),"start_weight":sw,"start_waist":wa,"start_pullups":pu,"start_pushups":fl,"start_squat":sq or None,"start_rdl":rdl or None,"start_curl":curl or None,"start_triceps":tri or None,"start_cindy":cindy or None}).execute()
                st.toast("Semana 0 guardada", icon="✅")
                st.success("Semana 0 guardada.")
            else:
                st.error("Supabase no está conectado.")

    st.write("")
    with st.expander("⚠️ Zona de peligro · Reiniciar progreso"):
        st.markdown(f'<div class="danger-card"><div class="danger-title">{icon("alert-triangle",18)} Esto no se puede deshacer</div>'
                    f'<p>Borra tu Semana 0, todos los entrenamientos y todas las mediciones de peso/cintura para volver a empezar desde cero.</p></div>',
                    unsafe_allow_html=True)
        r1 = st.checkbox("Entiendo que esta acción es irreversible y quiero borrar todo mi progreso.", key="reset_confirm_check")
        r2 = st.text_input('Escribe "BORRAR" para confirmar', key="reset_confirm_text", placeholder="BORRAR")
        reset_ready = r1 and r2.strip() == "BORRAR"
        if st.button(f'{"🗑️ "}Borrar todos mis datos', type="primary", use_container_width=True,
                     disabled=not reset_ready, key="reset_confirm_btn"):
            if DB_OK:
                try:
                    supabase.table("training_logs").delete().gte("id", 0).execute()
                    supabase.table("body_logs").delete().gte("id", 0).execute()
                    supabase.table("profile").delete().eq("id", 1).execute()
                except Exception as e:
                    st.error(f"No se pudo borrar: {e}")
                    st.stop()
                # Con RLS activo y sin política DELETE, Supabase responde OK pero no
                # borra nada. Comprobamos de verdad antes de decir que se ha borrado.
                quedan = len(training_get()) + len(body_get()) + (1 if profile_get() else 0)
                if quedan == 0:
                    st.toast("Todos los datos han sido borrados", icon="🗑️")
                    st.success("Progreso reiniciado. Configura tu nueva Semana 0 cuando quieras.")
                    st.rerun()
                else:
                    st.error(
                        f"**No se ha borrado nada** ({quedan} registros siguen ahí). "
                        "Supabase acepta la petición pero la bloquea: falta la política DELETE. "
                        "Ejecuta `supabase_schema.sql` de nuevo en el SQL Editor de Supabase "
                        "para crear las políticas de borrado."
                    )
            else:
                st.error("Supabase no está conectado.")
        if not reset_ready:
            st.caption("Marca la casilla y escribe BORRAR (en mayúsculas) para habilitar el botón.")

# ============================================================
# PROGRAM
# ============================================================
else:
    st.markdown('<div class="hero"><div class="eyebrow">THE PROGRAM</div><h1>16 semanas.</h1><p>Cuatro bloques. Cuatro sesiones. Una progresión.</p></div>',unsafe_allow_html=True)
    st.write("")
    week=st.select_slider("Selecciona semana",options=list(range(1,17)),value=week_now)
    for i,day in enumerate(DAY_ORDER,1):
        d=DAYS[day]
        with st.expander(f"Workout {i}  ·  {d['lift']}  ·  {d['sets'][week]}", expanded=(i-1==pend_wk and week==pend_week)):
            st.caption(f"AMRAP {d['time']} min · {'test / descarga' if week==16 else f'mínimo {MIN[week]} rondas'}")
            for ex in d["amrap"][week]: st.write("• "+ex)
