
import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client

st.set_page_config(
    page_title="Proyecto Spider-Man 41",
    page_icon="🕷️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# SUPABASE
# ============================================================
@st.cache_resource
def get_supabase() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )

try:
    supabase = get_supabase()
    DB_OK = True
except Exception as e:
    DB_OK = False
    supabase = None
    st.error(
        "No se ha podido conectar con Supabase. "
        "Revisa SUPABASE_URL y SUPABASE_KEY en Streamlit → Settings → Secrets."
    )

# ============================================================
# PLAN 16 SEMANAS
# ============================================================
DAYS = {
    "Lunes": {
        "focus": "Piernas + espalda",
        "lift": "Sentadilla",
        "time": 20,
        "sets": {
            **{i: "3×6–8" for i in range(1, 5)},
            **{i: "4×6–8" for i in range(5, 9)},
            **{i: "4×5–7" for i in range(9, 16)},
            16: "3×5 ligero",
        },
        "amrap": {
            **{i: ["4 dominadas", "8 flexiones", "15 sentadillas",
                   "8 remos/lado", "10 elevaciones de rodillas"] for i in range(1, 5)},
            **{i: ["4 dominadas", "10 flexiones", "15 sentadillas",
                   "10 remos/lado", "10 elevaciones de rodillas"] for i in range(5, 9)},
            **{i: ["4 dominadas", "10 flexiones", "15 sentadillas",
                   "10 remos/lado", "12 elevaciones de rodillas"] for i in range(9, 13)},
            **{i: ["5 dominadas", "10 flexiones", "15 sentadillas",
                   "10 remos/lado", "12 elevaciones de rodillas"] for i in range(13, 16)},
            16: ["4 dominadas", "8 flexiones", "12 sentadillas",
                 "8 remos/lado", "10 elevaciones de rodillas"],
        },
    },
    "Martes": {
        "focus": "Bíceps + hombros",
        "lift": "Curl de bíceps con barra Z",
        "time": 20,
        "sets": {
            **{i: "4×8–10" for i in range(1, 9)},
            **{i: "4×6–8" for i in range(9, 16)},
            16: "3×8 ligero",
        },
        "amrap": {
            **{i: ["8 pike push-ups", "10 zancadas (5+5)",
                   "10 curl martillo (5+5)", "15 sentadillas",
                   "20 mountain climbers", "10 abdominales"] for i in range(1, 5)},
            **{i: ["8 pike push-ups", "12 zancadas (6+6)",
                   "10 curl martillo (5+5)", "15 sentadillas",
                   "20 mountain climbers", "12 abdominales"] for i in range(5, 9)},
            **{i: ["10 pike push-ups", "12 zancadas (6+6)",
                   "12 curl martillo (6+6)", "15 sentadillas",
                   "20 mountain climbers", "12 abdominales"] for i in range(9, 13)},
            **{i: ["10 pike push-ups", "12 zancadas (6+6)",
                   "12 curl martillo (6+6)", "15 goblet squats",
                   "20 mountain climbers", "15 abdominales"] for i in range(13, 16)},
            16: ["6 pike push-ups", "10 zancadas", "8 curl martillo",
                 "12 sentadillas", "15 mountain climbers", "10 abdominales"],
        },
    },
    "Jueves": {
        "focus": "Cadena posterior + pecho",
        "lift": "Peso muerto rumano",
        "time": 22,
        "sets": {
            **{i: "3×8–10" for i in range(1, 5)},
            **{i: "4×8" for i in range(5, 9)},
            **{i: "4×6–8" for i in range(9, 16)},
            16: "3×6 ligero",
        },
        "amrap": {
            **{i: ["4 dominadas supinas", "10 flexiones",
                   "10 búlgaras (5+5)", "10 remos", "15 abdominales"] for i in range(1, 5)},
            **{i: ["4 dominadas supinas", "10 flexiones",
                   "12 búlgaras (6+6)", "10 remos", "15 abdominales"] for i in range(5, 9)},
            **{i: ["4 dominadas supinas", "10 flexiones",
                   "12 búlgaras (6+6)", "12 remos", "15 abdominales"] for i in range(9, 13)},
            **{i: ["5 dominadas supinas", "10 flexiones",
                   "12 búlgaras (6+6)", "12 remos", "15 abdominales"] for i in range(13, 16)},
            16: ["3 dominadas supinas", "8 flexiones",
                 "10 búlgaras", "8 remos", "12 abdominales"],
        },
    },
    "Sábado": {
        "focus": "Tríceps + cuerpo completo",
        "lift": "Extensión de tríceps con barra Z",
        "time": 20,
        "sets": {
            **{i: "4×8–10" for i in range(1, 9)},
            **{i: "4×6–8" for i in range(9, 16)},
            16: "3×8 ligero",
        },
        "amrap": {
            **{i: ["4 dominadas", "8 flexiones cerradas", "15 goblet squats",
                   "10 zancadas (5+5)", "10 elevaciones de piernas"] for i in range(1, 5)},
            **{i: ["4 dominadas", "10 flexiones cerradas", "15 goblet squats",
                   "12 zancadas (6+6)", "10 elevaciones de piernas"] for i in range(5, 9)},
            **{i: ["4 dominadas", "10 flexiones cerradas", "15 goblet squats",
                   "12 zancadas (6+6)", "12 elevaciones de piernas"] for i in range(9, 13)},
            **{i: ["5 dominadas", "10 flexiones cerradas", "15 goblet squats",
                   "12 zancadas (6+6)", "12 elevaciones de piernas"] for i in range(13, 16)},
            16: ["4 dominadas", "8 flexiones cerradas", "12 goblet squats",
                 "10 zancadas", "10 elevaciones de piernas"],
        },
    },
}

MIN_ROUNDS = {
    1: 8, 2: 8, 3: 9, 4: 9,
    5: 9, 6: 9, 7: 10, 8: 10,
    9: 10, 10: 10, 11: 11, 12: 11,
    13: 10, 14: 11, 15: 12, 16: 0,
}

BLOCKS = {
    1: "🟢 Adaptación",
    2: "🔵 Volumen",
    3: "🟠 Intensificación",
    4: "🔴 Consolidación",
    5: "⚪ Descarga + test",
}

def block_name(week):
    if week <= 4:
        return BLOCKS[1]
    if week <= 8:
        return BLOCKS[2]
    if week <= 12:
        return BLOCKS[3]
    if week <= 15:
        return BLOCKS[4]
    return BLOCKS[5]

# ============================================================
# DATA HELPERS
# ============================================================
def fetch_profile():
    if not DB_OK:
        return None
    res = supabase.table("profile").select("*").eq("id", 1).limit(1).execute()
    return res.data[0] if res.data else None

def save_profile(data):
    return supabase.table("profile").upsert(data).execute()

def fetch_body_logs():
    if not DB_OK:
        return pd.DataFrame()
    res = supabase.table("body_logs").select("*").order("log_date").execute()
    return pd.DataFrame(res.data)

def save_body_log(data):
    return supabase.table("body_logs").insert(data).execute()

def fetch_training_logs():
    if not DB_OK:
        return pd.DataFrame()
    res = supabase.table("training_logs").select("*").order("log_date").execute()
    return pd.DataFrame(res.data)

def save_training_log(data):
    return supabase.table("training_logs").insert(data).execute()

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
.block-container {max-width: 1250px; padding-top: 2rem; padding-bottom: 3rem;}
.hero {
    padding: 30px 32px;
    border: 1px solid rgba(128,128,128,.18);
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(128,128,128,.12), rgba(128,128,128,.035));
}
.hero h1 {font-size: 2.35rem; margin:0 0 6px 0;}
.hero p {color:#777; margin:0; font-size:1rem;}
.card {
    border:1px solid rgba(128,128,128,.18);
    border-radius:18px;
    padding:18px;
}
.exercise-row {
    padding:11px 14px;
    border-bottom:1px solid rgba(128,128,128,.14);
}
.exercise-row:last-child {border-bottom:0;}
.small {color:#777; font-size:.88rem;}
</style>
""", unsafe_allow_html=True)

profile = fetch_profile()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🕷️ Spider-Man 41")
    page = st.radio(
        "Navegación",
        ["🏋️ Hoy", "📈 Progreso", "🏁 Situación inicial", "📚 Plan 16 semanas"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Objetivo")
    st.write("Perder grasa + ganar músculo")
    st.caption("Prioridad")
    st.write("🦵 Piernas · 💪 Brazos · 🧱 Espalda")
    if DB_OK:
        st.success("☁️ Supabase conectado")
    else:
        st.error("Sin conexión")

# ============================================================
# SITUACIÓN INICIAL
# ============================================================
if page == "🏁 Situación inicial":
    st.markdown(
        '<div class="hero"><h1>🏁 Situación inicial</h1>'
        '<p>Semana 0 · Tu referencia para medir las 16 semanas.</p></div>',
        unsafe_allow_html=True
    )
    st.write("")

    if profile:
        st.info("Ya existe una situación inicial. Guardar el formulario actualizará esa referencia.")

    with st.form("initial_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            sw = st.number_input("Peso (kg)", 40.0, 200.0,
                                 float(profile["start_weight"]) if profile else 87.0, 0.1)
            waist_default = float(profile["start_waist"]) if profile and profile.get("start_waist") is not None else None
            s_waist = st.number_input("Cintura (cm)", 40.0, 180.0, waist_default, 0.1)
        with c2:
            sp = st.number_input("Dominadas máximas", 0, 50,
                                 int(profile["start_pullups"]) if profile else 8, 1)
            sf = st.number_input("Flexiones máximas", 0, 100,
                                 int(profile["start_pushups"]) if profile else 15, 1)
        with c3:
            ss = st.number_input("Sentadilla (kg)", 0.0, 300.0,
                                 float(profile["start_squat"]) if profile and profile.get("start_squat") else 0.0, 1.25)
            sr = st.number_input("Peso muerto rumano (kg)", 0.0, 300.0,
                                 float(profile["start_rdl"]) if profile and profile.get("start_rdl") else 0.0, 1.25)
        c4, c5 = st.columns(2)
        with c4:
            sc = st.number_input("Curl barra Z (kg)", 0.0, 150.0,
                                 float(profile["start_curl"]) if profile and profile.get("start_curl") else 0.0, 1.25)
            stt = st.number_input("Tríceps barra Z (kg)", 0.0, 150.0,
                                  float(profile["start_triceps"]) if profile and profile.get("start_triceps") else 0.0, 1.25)
        with c5:
            sci = st.number_input("Cindy · rondas", 0.0, 50.0,
                                  float(profile["start_cindy"]) if profile and profile.get("start_cindy") else 0.0, 1.0)
            sd = st.date_input("Fecha de inicio",
                               date.fromisoformat(profile["start_date"]) if profile and profile.get("start_date") else date.today())

        ok = st.form_submit_button("💾 Guardar situación inicial", type="primary", use_container_width=True)
        if ok:
            payload = {
                "id": 1,
                "start_date": str(sd),
                "start_weight": sw,
                "start_waist": s_waist,
                "start_pullups": sp,
                "start_pushups": sf,
                "start_squat": ss if ss > 0 else None,
                "start_rdl": sr if sr > 0 else None,
                "start_curl": sc if sc > 0 else None,
                "start_triceps": stt if stt > 0 else None,
                "start_cindy": sci if sci > 0 else None,
            }
            save_profile(payload)
            st.success("Situación inicial guardada en Supabase.")
            st.rerun()

# ============================================================
# HOY
# ============================================================
elif page == "🏋️ Hoy":
    st.markdown(
        '<div class="hero"><h1>🕷️ Entrenamiento</h1>'
        '<p>Fuerza primero · AMRAP después · registra cada sesión.</p></div>',
        unsafe_allow_html=True
    )
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        week = st.selectbox("Semana", range(1, 17), format_func=lambda x: f"Semana {x}")
    with c2:
        day = st.selectbox("Día", list(DAYS.keys()))

    d = DAYS[day]
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("Bloque", block_name(week))
    with m2: st.metric("Ejercicio", d["lift"])
    with m3: st.metric("AMRAP", f"{d['time']} min")

    st.divider()
    st.markdown("### 🏋️ Ejercicio principal")
    st.write(f"**{d['lift']} · {d['sets'][week]}**")
    c1, c2, c3 = st.columns(3)
    with c1: lw = st.number_input("Peso utilizado (kg)", 0.0, 300.0, 0.0, 1.25)
    with c2: sr = st.text_input("Series / reps", placeholder="Ej. 8 / 8 / 7")
    with c3: rir = st.selectbox("RIR final", [0, 1, 2, 3, 4], index=2)

    st.markdown(f"### 🔥 AMRAP · {d['time']} min")
    for i, ex in enumerate(d["amrap"][week], 1):
        st.markdown(f'<div class="exercise-row"><b>{i}.</b> {ex}</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1: rounds = st.number_input("Rondas completas", 0, 100, 0, 1)
    with c2: extra = st.number_input("Repeticiones extra", 0, 100, 0, 1)

    if week < 16:
        if rounds >= MIN_ROUNDS[week]:
            st.success(f"🎯 Mínimo conseguido: {rounds} + {extra} reps")
        else:
            st.warning(f"Faltan {MIN_ROUNDS[week] - rounds} rondas para el mínimo.")
    else:
        st.info("Semana 16: descarga. El sábado se utiliza para los tests.")

    notes = st.text_area("📝 Notas", placeholder="Sensaciones, técnica, molestias, energía…")

    if st.button("💾 Guardar entrenamiento", type="primary", use_container_width=True):
        save_training_log({
            "log_date": str(date.today()),
            "week": week,
            "day": day,
            "lift": d["lift"],
            "weight": lw if lw > 0 else None,
            "sets_reps": sr,
            "rir": rir,
            "rounds": rounds,
            "extra_reps": extra,
            "notes": notes,
        })
        st.success("Entrenamiento guardado permanentemente en Supabase.")

# ============================================================
# PROGRESO
# ============================================================
elif page == "📈 Progreso":
    st.markdown(
        '<div class="hero"><h1>📈 Progreso</h1>'
        '<p>Compara tu evolución con la Semana 0.</p></div>',
        unsafe_allow_html=True
    )
    st.write("")

    body = fetch_body_logs()
    logs = fetch_training_logs()

    if not profile:
        st.warning("Primero introduce tu situación inicial.")
    else:
        if len(body):
            body["week"] = pd.to_numeric(body["week"])
            body["weight"] = pd.to_numeric(body["weight"])
            body["waist"] = pd.to_numeric(body["waist"], errors="coerce")
            current_weight = float(body.iloc[-1]["weight"])
            delta_weight = current_weight - float(profile["start_weight"])

            waist_values = body["waist"].dropna()
            current_waist = float(waist_values.iloc[-1]) if len(waist_values) else None
            delta_waist = current_waist - float(profile["start_waist"]) if current_waist is not None and profile.get("start_waist") else None

            a,b,c,d = st.columns(4)
            with a: st.metric("⚖️ Peso actual", f"{current_weight:.1f} kg", f"{delta_weight:+.1f} kg")
            with b: st.metric("📏 Cintura", f"{current_waist:.1f} cm" if current_waist else "—",
                              f"{delta_waist:+.1f} cm" if delta_waist is not None else None)
            with c: st.metric("💪 Dominadas iniciales", profile["start_pullups"])
            with d: st.metric("💪 Flexiones iniciales", profile["start_pushups"])

            st.markdown("### ⚖️ Evolución del peso")
            weekly = body.groupby("week", as_index=False)["weight"].mean()
            start_row = pd.DataFrame({"week":[0], "weight":[profile["start_weight"]]})
            chart = pd.concat([start_row, weekly], ignore_index=True).drop_duplicates("week", keep="last").sort_values("week").set_index("week")
            st.line_chart(chart["weight"], height=300)

            waistdf = body.dropna(subset=["waist"]).groupby("week", as_index=False)["waist"].last()
            if len(waistdf) and profile.get("start_waist"):
                st.markdown("### 📏 Evolución de cintura")
                start_w = pd.DataFrame({"week":[0], "waist":[profile["start_waist"]]})
                chart2 = pd.concat([start_w, waistdf], ignore_index=True).drop_duplicates("week", keep="last").sort_values("week").set_index("week")
                st.line_chart(chart2["waist"], height=300)
        else:
            st.info("Registra tu primer peso/cintura desde el panel de progreso.")

        if len(logs):
            st.markdown("### 🏋️ Evolución de cargas")
            for lift in logs["lift"].dropna().unique():
                q = logs[logs["lift"] == lift].copy()
                q["weight"] = pd.to_numeric(q["weight"], errors="coerce")
                q = q.dropna(subset=["weight"]).groupby("week", as_index=False)["weight"].max()
                if len(q):
                    st.write(f"**{lift}**")
                    st.line_chart(q.set_index("week")["weight"], height=180)

            st.markdown("### 🔥 Evolución AMRAP")
            q = logs.groupby(["week", "day"], as_index=False)["rounds"].max()
            if len(q):
                st.bar_chart(q.pivot(index="week", columns="day", values="rounds").fillna(0), height=280)

            st.markdown("### 🧾 Historial")
            st.dataframe(logs.sort_values(["week", "log_date"], ascending=[False, False]),
                         use_container_width=True, hide_index=True)

# ============================================================
# PLAN
# ============================================================
else:
    st.markdown(
        '<div class="hero"><h1>📚 Plan 16 semanas</h1>'
        '<p>Consulta cualquier semana y entrenamiento.</p></div>',
        unsafe_allow_html=True
    )
    st.write("")
    week = st.select_slider("Semana", options=list(range(1, 17)), value=1)
    for day, d in DAYS.items():
        with st.expander(f"{day} · {d['lift']} · {d['sets'][week]}"):
            st.write(f"**AMRAP {d['time']} min · mínimo: {'test' if week == 16 else str(MIN_ROUNDS[week]) + ' rondas'}**")
            for ex in d["amrap"][week]:
                st.write("• " + ex)

st.caption("Proyecto Spider-Man 41 · 16 semanas · Supabase · Sin suplementos")
