"""
Configuración de la aplicación.

Todos los valores se leen de variables de entorno (normalmente desde un
archivo .env en la raíz del proyecto). Así no hace falta tocar el código
para cambiar de base de datos, clave de la API, etc.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Por defecto usa un archivo SQLite local: no requiere instalar nada más.
    # Para usar Azure SQL Server, cambia esto por algo como:
    # mssql+pyodbc://usuario:password@mvgmspain.database.windows.net/tu_bd?driver=ODBC+Driver+17+for+SQL+Server
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./plumia.db")

    secret_key: str = os.getenv("SECRET_KEY", "cambia-esto-por-una-cadena-aleatoria-larga")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    free_word_limit: int = int(os.getenv("FREE_WORD_LIMIT", "2000"))


settings = Settings()
