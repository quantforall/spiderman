# Q4A Trainer v5 — Premium UI + Supabase

## Deploy
1. Ejecuta `supabase_schema.sql` en Supabase SQL Editor.
2. En Streamlit Secrets:
SUPABASE_URL = "https://TU-PROYECTO.supabase.co"
SUPABASE_KEY = "TU_PUBLISHABLE_KEY"
3. Sube `app.py`, `requirements.txt` y la carpeta `.streamlit/` (tema de la app) a GitHub.
4. Despliega `app.py` en Streamlit Community Cloud.

La app guarda la Semana 0, entrenamientos, peso/cintura y muestra gráficos de progreso.
Esta versión usa Supabase para persistencia.

## Novedades v5
- Rediseño completo (tema oscuro con acentos rojo/azul, tipografía Barlow Condensed + Inter, iconos vectoriales).
- La semana y el día de entrenamiento se calculan automáticamente a partir de la fecha de Semana 0.
- Nuevo formulario en "Progreso" para registrar peso/cintura semana a semana (antes solo existía en Semana 0).
- Barra de progreso visual para el mínimo de rondas AMRAP de cada semana.
- Zona de peligro con doble confirmación (casilla + texto "BORRAR") para reiniciar todo el progreso.

IMPORTANTE: las políticas RLS incluidas son para una app personal. Para una app pública/multiusuario hay que añadir autenticación y RLS por usuario.
