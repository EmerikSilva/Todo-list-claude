# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Comandos de desarrollo

El backend **debe ejecutarse desde dentro de `backend/`** porque `DB_FILE` usa la ruta relativa `../db/db.json`.

```bash
# Backend (FastAPI) — correr desde backend/
cd backend
python main.py
# O con hot-reload:
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Streamlit) — correr desde frontend/
cd frontend
streamlit run main.py

# Instalar dependencias
pip install -r requirements.txt
```

API interactiva disponible en `http://localhost:8000/docs` (Swagger generado por FastAPI).

## Arquitectura

Dos procesos independientes que se comunican por HTTP:

```
frontend/ (Streamlit :8501)
  └── api_client.py  →  HTTP  →  backend/ (FastAPI :8000)
                                    ├── api_user.py   /register /login /profile
                                    └── api_todo.py   /todos CRUD
                                              ↓
                                         db/db.json
```

### Backend

- `api_todo.py` importa `verify_token` de `api_user.py` — es la única dependencia entre módulos.
- `load_db()` y `save_db()` están **duplicadas** en `api_user.py` y `api_todo.py`; no existe un módulo compartido.
- El token JWT usa el **email** como claim `sub` (no el `user_id`). Cada endpoint protegido recibe el email del token y luego hace una búsqueda en la DB para obtener el `user_id`.
- `SECRET_KEY` está hardcodeada como `"your-secret-key-here"`.

### Frontend

- `api_client.py` es el único archivo que hace llamadas HTTP; todas las pantallas lo importan.
- El estado de sesión en Streamlit usa tres claves: `authenticated` (bool), `token` (str JWT), `user_email` (str).
- Después de cualquier mutación de datos, las pantallas llaman `st.rerun()` para refrescar la UI.

### Base de datos

Archivo JSON en `db/db.json`:

```json
{
  "users": {
    "<uuid>": { "id": "uuid", "name": "string", "email": "string", "password": "bcrypt_hash" }
  },
  "todos": {
    "<uuid>": { "id": "uuid", "title": "string", "description": "string", "completed": false, "user_id": "uuid", "created_at": "iso_datetime" }
  }
}
```

Existe también `backend/db.json` (archivo residual); la DB activa es siempre `db/db.json`.

## Notas importantes

- Los tokens JWT expiran a los 30 minutos; no hay refresh token.
- El endpoint `POST /login` tiene `print()` de debug sin eliminar (`api_user.py:90-92`).
- No hay tests automatizados en el proyecto.
