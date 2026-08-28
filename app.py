
import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client

st.set_page_config(
    page_title="Spider-Man 41",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="expanded",
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

# ============================================================
# PREMIUM UI
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
.block-container {max-width:1280px;padding:2.2rem 2rem 4rem;}
[data-testid="stSidebar"] {border-right:1px solid rgba(128,128,128,.14);}
.hero {border:1px solid rgba(128,128,128,.15);border-radius:28px;padding:34px 36px;background:linear-gradient(145deg,rgba(128,128,128,.12),rgba(128,128,128,.035));}
.hero h1{font-size:2.6rem;letter-spacing:-.06em;margin:0;font-weight:800;}
.hero p{margin:8px 0 0;color:#777;font-size:1rem;}
.eyebrow{text-transform:uppercase;letter-spacing:.13em;font-size:.72rem;font-weight:700;color:#777;}
.card{border:1px solid rgba(128,128,128,.16);border-radius:22px;padding:22px;background:rgba(128,128,128,.025);}
.stat{border:1px solid rgba(128,128,128,.15);border-radius:20px;padding:18px;background:rgba(128,128,128,.025);}
.stat .label{font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;color:#777;font-weight:700;}
.stat .num{font-size:1.9rem;font-weight:800;letter-spacing:-.04em;margin-top:6px;}
.stat .delta{font-size:.83rem;margin-top:3px;color:#777;}
.exercise{padding:13px 0;border-bottom:1px solid rgba(128,128,128,.12);}
.exercise:last-child{border-bottom:0;}
.exercise b{font-size:1.02rem;}
.pill{display:inline-block;padding:7px 11px;border-radius:999px;border:1px solid rgba(128,128,128,.16);font-size:.75rem;color:#666;}
.stButton>button{border-radius:12px;font-weight:700;min-height:44px;}
div[data-testid="stMetric"]{border:1px solid rgba(128,128,128,.14);padding:14px 16px;border-radius:18px;}
</style>
""", unsafe_allow_html=True)

profile = profile_get()

with st.sidebar:
    st.markdown("## 🕷️ Spider-Man 41")
    st.caption("16-week transformation")
    page = st.radio("Menú",["🏠 Inicio","🏋️ Entrenamiento","📈 Progreso","🏁 Semana 0","📚 Programa"],label_visibility="collapsed")
    st.divider()
    st.markdown("**Objetivo**")
    st.caption("Perder grasa · ganar músculo")
    st.markdown("**Prioridades**")
    st.caption("Piernas · brazos · espalda")
    if DB_OK: st.success("● Datos sincronizados")
    else: st.error("● Supabase no conectado")

# ============================================================
# HOME
# ============================================================
if page == "🏠 Inicio":
    st.markdown('<div class="hero"><div class="eyebrow">16 WEEK TRANSFORMATION</div><h1>Tu entrenamiento.<br>Tu progreso.</h1><p>Una experiencia simple para entrenar duro, medir mejor y ver cómo cambias.</p></div>',unsafe_allow_html=True)
    st.write("")
    body=body_get(); logs=training_get()
    if profile:
        weight=float(body.iloc[-1]["weight"]) if len(body) else float(profile["start_weight"])
        dw=weight-float(profile["start_weight"])
        waist = body["waist"].dropna() if len(body) else pd.Series(dtype=float)
        waist_now=float(waist.iloc[-1]) if len(waist) else None
        a,b,c,d=st.columns(4)
        with a: st.markdown(f'<div class="stat"><div class="label">Peso</div><div class="num">{weight:.1f} kg</div><div class="delta">{dw:+.1f} kg desde inicio</div></div>',unsafe_allow_html=True)
        with b: st.markdown(f'<div class="stat"><div class="label">Cintura</div><div class="num">{waist_now:.1f} cm</div><div class="delta">última medición</div></div>' if waist_now else '<div class="stat"><div class="label">Cintura</div><div class="num">—</div><div class="delta">Añade tu medida</div></div>',unsafe_allow_html=True)
        with c: st.markdown(f'<div class="stat"><div class="label">Dominadas</div><div class="num">{profile["start_pullups"]}</div><div class="delta">marca inicial</div></div>',unsafe_allow_html=True)
        with d: st.markdown(f'<div class="stat"><div class="label">Semana</div><div class="num">1 / 16</div><div class="delta">a por ello</div></div>',unsafe_allow_html=True)
        st.write("")
        st.markdown('<div class="card"><div class="eyebrow">NEXT SESSION</div><h2 style="margin:6px 0 4px">Lunes · Piernas + espalda</h2><p style="color:#777">Sentadilla · AMRAP 20 min · mínimo 8 rondas</p></div>',unsafe_allow_html=True)
    else:
        st.warning("Empieza configurando tu Semana 0.")

# ============================================================
# TRAINING
# ============================================================
elif page == "🏋️ Entrenamiento":
    st.markdown('<div class="hero"><div class="eyebrow">WORKOUT</div><h1>Entrena.</h1><p>Fuerza primero. AMRAP después. Técnica siempre.</p></div>',unsafe_allow_html=True)
    st.write("")
    a,b=st.columns(2)
    with a: week=st.selectbox("Semana",range(1,17),format_func=lambda x:f"Semana {x} · {'descarga' if x==16 else 'entrenamiento'}")
    with b: day=st.selectbox("Día",list(DAYS.keys()))
    d=DAYS[day]
    st.markdown(f'<span class="pill">{d["focus"]}</span> <span class="pill">{block_name if False else "16 semanas"}</span>',unsafe_allow_html=True)
    st.write("")
    c1,c2,c3=st.columns(3)
    with c1: st.metric("Ejercicio principal",d["lift"])
    with c2: st.metric("Trabajo",d["sets"][week])
    with c3: st.metric("AMRAP",f'{d["time"]} min')
    st.divider()
    st.markdown("### 🏋️ Ejercicio principal")
    x1,x2,x3=st.columns(3)
    with x1: lw=st.number_input("Peso (kg)",0.0,300.0,0.0,1.25)
    with x2: sr=st.text_input("Series / reps",placeholder="8 / 8 / 7")
    with x3: rir=st.selectbox("RIR final",[0,1,2,3,4],index=2)
    st.markdown(f"### 🔥 AMRAP · {d['time']} min")
    for i,ex in enumerate(d["amrap"][week],1):
        st.markdown(f'<div class="exercise"><b>{i:02d}</b>&nbsp;&nbsp;{ex}</div>',unsafe_allow_html=True)
    x1,x2=st.columns(2)
    with x1: rounds=st.number_input("Rondas completas",0,100,0,1)
    with x2: extra=st.number_input("Repeticiones extra",0,100,0,1)
    if week<16:
        st.caption(f"🎯 Mínimo de la semana: {MIN[week]} rondas")
        if rounds>=MIN[week]: st.success("Mínimo conseguido.")
    else: st.info("Semana 16 · descarga + tests")
    notes=st.text_area("Notas",placeholder="Energía · técnica · molestias · sensaciones…")
    if st.button("Guardar entrenamiento",type="primary",use_container_width=True):
        if DB_OK:
            supabase.table("training_logs").insert({"log_date":str(date.today()),"week":week,"day":day,"lift":d["lift"],"weight":lw or None,"sets_reps":sr,"rir":rir,"rounds":rounds,"extra_reps":extra,"notes":notes}).execute()
            st.success("Guardado. Tu progreso queda sincronizado.")
        else: st.error("Supabase no está conectado.")

# ============================================================
# PROGRESS
# ============================================================
elif page == "📈 Progreso":
    st.markdown('<div class="hero"><div class="eyebrow">YOUR DATA</div><h1>Progreso.</h1><p>Semana 0 como referencia. Cada dato cuenta.</p></div>',unsafe_allow_html=True)
    st.write("")
    body=body_get(); logs=training_get()
    if not profile:
        st.warning("Primero configura tu Semana 0.")
    else:
        if len(body):
            body["week"]=pd.to_numeric(body["week"]); body["weight"]=pd.to_numeric(body["weight"]); body["waist"]=pd.to_numeric(body["waist"],errors="coerce")
            current=float(body.iloc[-1]["weight"]); delta=current-float(profile["start_weight"])
            waist=body["waist"].dropna(); cw=float(waist.iloc[-1]) if len(waist) else None
            a,b,c,d=st.columns(4)
            with a: st.metric("Peso",f"{current:.1f} kg",f"{delta:+.1f} kg vs inicio")
            with b: st.metric("Cintura",f"{cw:.1f} cm" if cw else "—",f"{cw-profile['start_waist']:+.1f} cm" if cw and profile.get("start_waist") else None)
            with c: st.metric("Dominadas",f"{profile['start_pullups']}","Semana 0")
            with d: st.metric("Flexiones",f"{profile['start_pushups']}","Semana 0")
            st.markdown("### ⚖️ Peso")
            weekly=body.groupby("week",as_index=False)["weight"].mean()
            chart=pd.concat([pd.DataFrame({"week":[0],"weight":[profile["start_weight"]]}),weekly],ignore_index=True).drop_duplicates("week",keep="last").sort_values("week").set_index("week")
            st.line_chart(chart["weight"],height=300)
            if profile.get("start_waist"):
                wd=body.dropna(subset=["waist"]).groupby("week",as_index=False)["waist"].last()
                if len(wd):
                    st.markdown("### 📏 Cintura")
                    chart2=pd.concat([pd.DataFrame({"week":[0],"waist":[profile["start_waist"]]}),wd],ignore_index=True).drop_duplicates("week",keep="last").sort_values("week").set_index("week")
                    st.line_chart(chart2["waist"],height=300)
        else:
            st.info("Todavía no hay mediciones corporales.")
        if len(logs):
            st.markdown("### 🏋️ Fuerza")
            for lift in logs["lift"].dropna().unique():
                q=logs[logs["lift"]==lift].copy(); q["weight"]=pd.to_numeric(q["weight"],errors="coerce"); q=q.dropna(subset=["weight"]).groupby("week",as_index=False)["weight"].max()
                if len(q):
                    st.write(f"**{lift}**"); st.line_chart(q.set_index("week")["weight"],height=180)
            st.markdown("### 🔥 AMRAP")
            q=logs.groupby(["week","day"],as_index=False)["rounds"].max()
            st.bar_chart(q.pivot(index="week",columns="day",values="rounds").fillna(0),height=280)
            st.markdown("### Historial")
            st.dataframe(logs.sort_values(["week","log_date"],ascending=[False,False]),use_container_width=True,hide_index=True)

# ============================================================
# WEEK 0
# ============================================================
elif page == "🏁 Semana 0":
    st.markdown('<div class="hero"><div class="eyebrow">BASELINE</div><h1>Empieza aquí.</h1><p>Guarda tu punto de partida. La aplicación medirá todo contra esta referencia.</p></div>',unsafe_allow_html=True)
    st.write("")
    with st.form("baseline"):
        a,b,c=st.columns(3)
        with a: sw=st.number_input("Peso (kg)",40.0,200.0,float(profile["start_weight"]) if profile else 87.0,.1); wa=st.number_input("Cintura (cm)",40.0,180.0,float(profile["start_waist"]) if profile and profile.get("start_waist") else None,.1)
        with b: pu=st.number_input("Dominadas máximas",0,50,int(profile["start_pullups"]) if profile else 8,1); fl=st.number_input("Flexiones máximas",0,100,int(profile["start_pushups"]) if profile else 15,1)
        with c: sq=st.number_input("Sentadilla (kg)",0.0,300.0,float(profile["start_squat"]) if profile and profile.get("start_squat") else 0.0,1.25); rdl=st.number_input("RDL (kg)",0.0,300.0,float(profile["start_rdl"]) if profile and profile.get("start_rdl") else 0.0,1.25)
        a,b=st.columns(2)
        with a: curl=st.number_input("Curl Z (kg)",0.0,150.0,float(profile["start_curl"]) if profile and profile.get("start_curl") else 0.0,1.25); tri=st.number_input("Tríceps Z (kg)",0.0,150.0,float(profile["start_triceps"]) if profile and profile.get("start_triceps") else 0.0,1.25)
        with b: cindy=st.number_input("Cindy · rondas",0.0,50.0,float(profile["start_cindy"]) if profile and profile.get("start_cindy") else 0.0,1.0); sd=st.date_input("Fecha",date.fromisoformat(profile["start_date"]) if profile and profile.get("start_date") else date.today())
        if st.form_submit_button("Guardar Semana 0",type="primary",use_container_width=True):
            supabase.table("profile").upsert({"id":1,"start_date":str(sd),"start_weight":sw,"start_waist":wa,"start_pullups":pu,"start_pushups":fl,"start_squat":sq or None,"start_rdl":rdl or None,"start_curl":curl or None,"start_triceps":tri or None,"start_cindy":cindy or None}).execute()
            st.success("Semana 0 guardada.")

# ============================================================
# PROGRAM
# ============================================================
else:
    st.markdown('<div class="hero"><div class="eyebrow">THE PROGRAM</div><h1>16 semanas.</h1><p>Cuatro bloques. Cuatro sesiones. Una progresión.</p></div>',unsafe_allow_html=True)
    st.write("")
    week=st.select_slider("Selecciona semana",options=list(range(1,17)),value=1)
    for day,d in DAYS.items():
        with st.expander(f"{day}  ·  {d['lift']}  ·  {d['sets'][week]}"):
            st.caption(f"AMRAP {d['time']} min · {'test / descarga' if week==16 else f'mínimo {MIN[week]} rondas'}")
            for ex in d["amrap"][week]: st.write("• "+ex)
