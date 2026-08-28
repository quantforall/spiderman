# Spider-Man 41 v4 — Premium UI + Supabase

## Deploy
1. Ejecuta `supabase_schema.sql` en Supabase SQL Editor.
2. En Streamlit Secrets:
SUPABASE_URL = "https://TU-PROYECTO.supabase.co"
SUPABASE_KEY = "TU_PUBLISHABLE_KEY"
3. Sube `app.py` y `requirements.txt` a GitHub.
4. Despliega `app.py` en Streamlit Community Cloud.

La app guarda la Semana 0, entrenamientos, peso/cintura y muestra gráficos de progreso.
Esta versión usa Supabase para persistencia.

IMPORTANTE: las políticas RLS incluidas son para una app personal. Para una app pública/multiusuario hay que añadir autenticación y RLS por usuario.
