# Q4A Trainer — programa de 16 semanas

App personal de entrenamiento: 4 sesiones por semana durante 16 semanas, registro de
peso/cintura, pasos diarios y gráficos de progreso. Streamlit + Supabase.

## Puesta en marcha

1. Ejecuta `supabase_schema.sql` en el **SQL Editor de Supabase**. Es re-ejecutable
   (usa `drop policy if exists` + `create policy`), así que puedes relanzarlo cuando quieras.
2. En **Streamlit Secrets** añade:
   ```
   SUPABASE_URL = "https://TU-PROYECTO.supabase.co"
   SUPABASE_KEY = "TU_PUBLISHABLE_KEY"
   ```
3. Sube a GitHub `app.py`, `requirements.txt`, `supabase_schema.sql` y la carpeta
   `.streamlit/` (lleva el tema; empieza por punto y es fácil olvidarla).
4. Despliega `app.py` en Streamlit Community Cloud.

## Pantallas

- **Inicio** — peso, cintura, dominadas, sesiones hechas y la próxima sesión.
- **Progreso** — gráficos de peso, cintura, fuerza por ejercicio, AMRAP e historial;
  permite corregir o borrar una sesión ya guardada.
- **Entrenamiento** — muestra siempre la siguiente sesión pendiente, sin selectores:
  las sesiones se hacen en orden y al guardar avanza sola. Precarga el peso de la
  última vez que hiciste ese mismo ejercicio.
- **Pasos** — registro diario con objetivo diario y semanal (semana natural, de lunes
  a domingo) y un anillo con las semanas del año.
- **Semana 0** — línea base del programa y zona de reinicio con doble confirmación.
- **Programa** — las 16 semanas completas, semana a semana.

## Notas

- El avance del programa se mide por **sesiones registradas**, no por el calendario:
  si dejas una semana sin entrenar no "pierdes" esa semana.
- Todas las escrituras comprueban el resultado en la base de datos antes de dar la
  operación por buena, para no mostrar falsos "guardado" si RLS las bloquea.
- La navegación es una barra superior fija; se oculta la cabecera propia de Streamlit
  para que quede anclada igual en local y en Streamlit Cloud.

## Seguridad

Las políticas RLS incluidas son para una **app personal de un solo usuario**: dan acceso
completo al rol anónimo. Para una app pública o multiusuario hay que añadir autenticación
y RLS por usuario.
