# Proyecto Spider-Man 41 — 16 semanas

App Streamlit para registrar el plan de 16 semanas.

## Ejecutar
pip install -r requirements.txt
streamlit run app.py

## Deploy
Sube `app.py` y `requirements.txt` a un repositorio GitHub y despliega el archivo `app.py` en Streamlit Community Cloud.

La app incluye:
- Plan exacto de 16 semanas.
- 4 días de entrenamiento.
- Ejercicio principal con progresión.
- AMRAP por semana.
- Mínimo de rondas.
- Registro de peso, cintura, cargas, RIR, rondas y notas.
- Dashboard con evolución de peso, cintura, cargas y AMRAP.
- Comparación de cargas iniciales vs actuales.
- Exportación CSV.

Nota: esta versión guarda datos en la sesión activa de Streamlit. Para persistencia entre sesiones/dispositivos se puede conectar una base de datos o almacenamiento persistente.
