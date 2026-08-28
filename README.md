# Proyecto Spider-Man 41 — v3 Supabase

Versión preparada para Supabase y Streamlit.

## 1. Crear tablas
Abre Supabase → SQL Editor y ejecuta `supabase_schema.sql`.

Si ya tienes tablas `profile`, `body_logs` o `training_logs`, NO las borres.
Comprueba primero sus columnas y adapta el esquema si fuera necesario.

## 2. Streamlit Secrets
En Streamlit Community Cloud → App → Settings → Secrets:

SUPABASE_URL = "https://TU-PROYECTO.supabase.co"
SUPABASE_KEY = "TU_PUBLISHABLE_KEY"

Usa la publishable/anon key, NO la service_role key.

## 3. Dependencias
`requirements.txt` ya incluye:
- streamlit
- pandas
- supabase

## 4. Ejecutar
streamlit run app.py

## 5. Funciones
- Semana 0 / situación inicial.
- Plan exacto de 16 semanas.
- Registro de entrenamientos.
- Registro de peso y cintura.
- Datos persistentes en Supabase.
- Dashboard de peso, cintura, cargas y AMRAP.
- Comparación con la situación inicial.

## Seguridad
Esta versión está pensada para uso personal y las tablas usan políticas RLS abiertas a `anon`.
NO publiques esta configuración como una app multiusuario.
Para una app multiusuario hay que añadir autenticación y RLS por usuario.

## Nota sobre Supabase
Si ya tienes tablas creadas, el script usa `CREATE TABLE IF NOT EXISTS`, pero eso no modifica columnas existentes.
Si tus tablas existentes no tienen las columnas necesarias, hay que hacer una migración.
