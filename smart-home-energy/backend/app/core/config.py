# backend/app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    
    # By default, pydantic-settings is case-insensitive, so it will match
    # environment variables like `DATABASE_URL` to the field `database_url`.
    
    # --- Database Settings ---
    DATABASE_URL: str
    
    # --- JWT/Security Settings ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # --- LLM Integration Settings (for future use) ---
    # We can define them now so the application is aware of them.
    # The `| None = None` makes them optional.
    OPENAI_API_KEY: str | None = None
    
    # --- Pydantic Settings Configuration ---
    # This tells pydantic-settings to load variables from a .env file
    # if it exists, which is great for local development outside of Docker.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


# Create a single, importable instance of the settings
settings = Settings()