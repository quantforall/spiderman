
import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Proyecto Spider-Man 41", page_icon="🕷️", layout="wide")

# =========================
# 16-week plan
# =========================
DAYS = {
    "Lunes": {
        "focus": "Piernas + espalda",
        "lift": "Sentadilla",
        "sets": {
            1:"3×6–8",2:"3×6–8",3:"3×6–8",4:"3×6–8",
            5:"4×6–8",6:"4×6–8",7:"4×6–8",8:"4×6–8",
            9:"4×5–7",10:"4×5–7",11:"4×5–7",12:"4×5–7",
            13:"4×5–7",14:"4×5–7",15:"4×5–7",16:"3×5 ligero"
        },
        "time": 20,
        "amrap": {
            1:["4 dominadas","8 flexiones","15 sentadillas","8 remos/lado","10 elevaciones de rodillas"],
            2:["4 dominadas","8 flexiones","15 sentadillas","8 remos/lado","10 elevaciones de rodillas"],
            3:["4 dominadas","8 flexiones","15 sentadillas","8 remos/lado","10 elevaciones de rodillas"],
            4:["4 dominadas","8 flexiones","15 sentadillas","8 remos/lado","10 elevaciones de rodillas"],
            5:["4 dominadas","10 flexiones","15 sentadillas","10 remos/lado","10 elevaciones de rodillas"],
            6:["4 dominadas","10 flexiones","15 sentadillas","10 remos/lado","10 elevaciones de rodillas"],
            7:["4 dominadas","10 flexiones","15 sentadillas","10 remos/lado","10 elevaciones de rodillas"],
            8:["4 dominadas","10 flexiones","15 sentadillas","10 remos/lado","10 elevaciones de rodillas"],
            9:["4 dominadas","10 flexiones","15 sentadillas","10 remos/lado","12 elevaciones de rodillas"],
            10:["4 dominadas","10 flexiones","15 sentadillas","10 remos/lado","12 elevaciones de rodillas"],
            11:["4 dominadas","10 flexiones","15 sentadillas","10 remos/lado","12 elevaciones de rodillas"],
            12:["4 dominadas","10 flexiones","15 sentadillas","10 remos/lado","12 elevaciones de rodillas"],
            13:["5 dominadas","10 flexiones","15 sentadillas","10 remos/lado","12 elevaciones de rodillas"],
            14:["5 dominadas","10 flexiones","15 sentadillas","10 remos/lado","12 elevaciones de rodillas"],
            15:["5 dominadas","10 flexiones","15 sentadillas","10 remos/lado","12 elevaciones de rodillas"],
            16:["4 dominadas","8 flexiones","12 sentadillas","8 remos/lado","10 elevaciones de rodillas"],
        },
    },
    "Martes": {
        "focus": "Bíceps + hombros",
        "lift": "Curl de bíceps con barra Z",
        "sets": {**{i:"4×8–10" for i in range(1,9)}, **{i:"4×6–8" for i in range(9,16)}, 16:"3×8 ligero"},
        "time": 20,
        "amrap": {
            **{i:["8 flexiones pike","10 zancadas","10 curl martillo (5+5)","15 sentadillas","20 mountain climbers","10 abdominales"] for i in range(1,5)},
            **{i:["8 flexiones pike","12 zancadas","10 curl martillo (5+5)","15 sentadillas","20 mountain climbers","12 abdominales"] for i in range(5,9)},
            **{i:["10 flexiones pike","12 zancadas","12 curl martillo (6+6)","15 sentadillas","20 mountain climbers","12 abdominales"] for i in range(9,13)},
            **{i:["10 flexiones pike","12 zancadas","12 curl martillo (6+6)","15 goblet squats","20 mountain climbers","15 abdominales"] for i in range(13,16)},
            16:["6 flexiones pike","10 zancadas","8 curl martillo","12 sentadillas","15 mountain climbers","10 abdominales"],
        },
    },
    "Jueves": {
        "focus": "Cadena posterior + pecho",
        "lift": "Peso muerto rumano",
        "sets": {
            1:"3×8–10",2:"3×8–10",3:"3×8–10",4:"3×8–10",
            5:"4×8",6:"4×8",7:"4×8",8:"4×8",
            9:"4×6–8",10:"4×6–8",11:"4×6–8",12:"4×6–8",
            13:"4×6–8",14:"4×6–8",15:"4×6–8",16:"3×6 ligero"
        },
        "time": 22,
        "amrap": {
            **{i:["4 dominadas supinas","10 flexiones","10 búlgaras (5+5)","10 remos","15 abdominales"] for i in range(1,5)},
            **{i:["4 dominadas supinas","10 flexiones","12 búlgaras (6+6)","10 remos","15 abdominales"] for i in range(5,9)},
            **{i:["4 dominadas supinas","10 flexiones","12 búlgaras (6+6)","12 remos","15 abdominales"] for i in range(9,13)},
            **{i:["5 dominadas supinas","10 flexiones","12 búlgaras (6+6)","12 remos","15 abdominales"] for i in range(13,16)},
            16:["3 dominadas supinas","8 flexiones","10 búlgaras","8 remos","12 abdominales"],
        },
    },
    "Sábado": {
        "focus": "Tríceps + cuerpo completo",
        "lift": "Extensión de tríceps con barra Z",
        "sets": {**{i:"4×8–10" for i in range(1,9)}, **{i:"4×6–8" for i in range(9,16)}, 16:"3×8 ligero"},
        "time": 20,
        "amrap": {
            **{i:["4 dominadas","8 flexiones cerradas","15 goblet squats","10 zancadas (5+5)","10 elevaciones de piernas"] for i in range(1,5)},
            **{i:["4 dominadas","10 flexiones cerradas","15 goblet squats","12 zancadas (6+6)","10 elevaciones de piernas"] for i in range(5,9)},
            **{i:["4 dominadas","10 flexiones cerradas","15 goblet squats","12 zancadas (6+6)","12 elevaciones de piernas"] for i in range(9,13)},
            **{i:["5 dominadas","10 flexiones cerradas","15 goblet squats","12 zancadas (6+6)","12 elevaciones de piernas"] for i in range(13,16)},
            16:["4 dominadas","8 flexiones cerradas","12 goblet squats","10 zancadas","10 elevaciones de piernas"],
        },
    },
}

MIN_ROUNDS = {
    1:8,2:8,3:9,4:9,
    5:9,6:9,7:10,8:10,
    9:10,10:10,11:11,12:11,
    13:10,14:11,15:12,16:0
}

BLOCKS = {
    1:"🟢 Bloque 1 · Adaptación",
    2:"🔵 Bloque 2 · Volumen",
    3:"🟠 Bloque 3 · Intensificación",
    4:"🔴 Bloque 4 · Consolidación",
}

def block(week):
    if week <= 4: return BLOCKS[1]
    if week <= 8: return BLOCKS[2]
    if week <= 12: return BLOCKS[3]
    if week <= 15: return BLOCKS[4]
    return "⚪ Semana 16 · Descarga + test"

if "training_logs" not in st.session_state:
    st.session_state.training_logs = []
if "body_logs" not in st.session_state:
    st.session_state.body_logs = []

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.header("🗓️ Entrenamiento")
    week = st.selectbox("Semana", range(1,17), format_func=lambda x:f"Semana {x}")
    day = st.selectbox("Día", list(DAYS.keys()))
    st.info(block(week))
    if week < 16:
        st.metric("🎯 Mínimo AMRAP", f"{MIN_ROUNDS[week]} rondas")
    else:
        st.warning("Descarga. Sábado = test.")

    st.divider()
    st.header("📏 Medidas")
    bw = st.number_input("Peso de hoy (kg)", min_value=40.0, max_value=200.0, value=87.0, step=0.1)
    waist = st.number_input("Cintura (cm)", min_value=40.0, max_value=180.0, value=0.0, step=0.1)
    if st.button("Guardar medidas", use_container_width=True):
        if waist > 0:
            st.session_state.body_logs.append({"fecha":str(date.today()),"semana":week,"peso_kg":bw,"cintura_cm":waist})
        else:
            st.session_state.body_logs.append({"fecha":str(date.today()),"semana":week,"peso_kg":bw,"cintura_cm":None})
        st.success("Medidas guardadas.")

d = DAYS[day]

# =========================
# Header
# =========================
st.title("🕷️ Proyecto Spider-Man 41")
st.caption("16 semanas · 4 días/semana · musculación + AMRAP 20–22 min")

c1,c2,c3 = st.columns(3)
with c1: st.metric("Semana", week, block(week))
with c2: st.metric("Día", day, d["focus"])
with c3: st.metric("AMRAP", f'{d["time"]} min', f'Mín. {MIN_ROUNDS[week] if week<16 else "test"} rondas')

# =========================
# Workout
# =========================
st.subheader("🏋️ Ejercicio principal")
st.write(f"### {d['lift']}")
st.write(f"**{d['sets'][week]}** · Descanso 60–120 s · objetivo habitual: **RIR 1–2**")
w = st.number_input("Peso utilizado (kg)", min_value=0.0, max_value=300.0, value=0.0, step=1.25)
sets_done = st.text_input("Series/repeticiones realizadas", placeholder="Ej. 8 / 8 / 7")
rir = st.selectbox("RIR final", [0,1,2,3,4], index=2)

st.divider()
st.subheader(f"🔥 AMRAP · {d['time']} minutos")
st.caption("Completa tantas rondas como puedas manteniendo técnica. El mínimo es un objetivo de volumen, no una razón para hacer repeticiones malas.")
for i, ex in enumerate(d["amrap"][week], 1):
    st.write(f"**{i}.** {ex}")

r1,r2 = st.columns(2)
with r1:
    rounds = st.number_input("Rondas completas", min_value=0, max_value=100, value=0, step=1)
with r2:
    extra = st.number_input("Repeticiones extra", min_value=0, max_value=100, value=0, step=1)

minimum = MIN_ROUNDS[week]
if week < 16:
    if rounds >= minimum:
        st.success(f"✅ Mínimo conseguido: {rounds} rondas + {extra} reps")
    else:
        st.warning(f"Te faltan {minimum-rounds} rondas para el mínimo.")
else:
    st.info("Semana 16: prioriza recuperación. Usa el sábado para el test.")

notes = st.text_area("📝 Notas", placeholder="Sensaciones, técnica, molestias, energía...")

if st.button("💾 Guardar entrenamiento", type="primary", use_container_width=True):
    st.session_state.training_logs.append({
        "fecha":str(date.today()),"semana":week,"día":day,"ejercicio":d["lift"],
        "peso_kg":w,"series_reps":sets_done,"RIR":rir,
        "rondas":rounds,"extra_reps":extra,"notas":notes
    })
    st.success("Entrenamiento guardado.")

# =========================
# Dashboard
# =========================
st.divider()
st.header("📈 Dashboard de progreso")

if st.session_state.body_logs:
    body = pd.DataFrame(st.session_state.body_logs).sort_values(["semana","fecha"])
    body["peso_promedio"] = body.groupby("semana")["peso_kg"].transform("mean")
    st.subheader("⚖️ Peso y cintura")
    tab1,tab2 = st.tabs(["Peso","Cintura"])
    with tab1:
        st.line_chart(body.set_index("semana")["peso_promedio"])
    with tab2:
        waist_df = body.dropna(subset=["cintura_cm"]).drop_duplicates("semana", keep="last").set_index("semana")
        if len(waist_df):
            st.line_chart(waist_df["cintura_cm"])
        else:
            st.info("Registra la cintura para ver su evolución.")

    initial = body.iloc[0]
    latest = body.iloc[-1]
    delta_w = latest["peso_kg"] - initial["peso_kg"]
    st.metric("Cambio de peso vs inicio", f"{delta_w:+.1f} kg", "objetivo: descenso gradual")

if st.session_state.training_logs:
    logs = pd.DataFrame(st.session_state.training_logs).sort_values(["semana","fecha"])
    st.subheader("💪 Fuerza y AMRAP")
    lift_tab, amrap_tab = st.tabs(["Cargas","Rondas AMRAP"])
    with lift_tab:
        for lift in logs["ejercicio"].unique():
            q = logs[logs["ejercicio"] == lift][["semana","peso_kg"]].drop_duplicates("semana", keep="last").set_index("semana")
            if len(q):
                st.write(f"**{lift}**")
                st.line_chart(q["peso_kg"])
    with amrap_tab:
        q = logs.groupby(["semana","día"])["rondas"].max().reset_index()
        st.bar_chart(q.pivot(index="semana", columns="día", values="rondas").fillna(0))

    st.subheader("🕷️ Comparación con el inicio")
    latest_by_ex = logs.groupby("ejercicio").tail(1).set_index("ejercicio")
    first_by_ex = logs.groupby("ejercicio").head(1).set_index("ejercicio")
    rows=[]
    for ex in latest_by_ex.index:
        start=float(first_by_ex.loc[ex,"peso_kg"])
        current=float(latest_by_ex.loc[ex,"peso_kg"])
        rows.append({"Ejercicio":ex,"Inicio (kg)":start,"Actual (kg)":current,"Cambio (kg)":current-start})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.divider()
st.subheader("🧪 Semana 16 · Tests")
st.markdown("""
- Dominadas máximas estrictas
- Flexiones máximas estrictas
- Cindy 20 min: **5 dominadas + 10 flexiones + 15 sentadillas**
- Comparar semana 16 vs semana 1
""")

if st.session_state.training_logs:
    st.download_button(
        "⬇️ Descargar registro de entrenamientos CSV",
        pd.DataFrame(st.session_state.training_logs).to_csv(index=False).encode("utf-8"),
        "entrenamientos_spiderman16.csv",
        "text/csv",
        use_container_width=True,
    )
if st.session_state.body_logs:
    st.download_button(
        "⬇️ Descargar medidas CSV",
        pd.DataFrame(st.session_state.body_logs).to_csv(index=False).encode("utf-8"),
        "medidas_spiderman16.csv",
        "text/csv",
        use_container_width=True,
    )
