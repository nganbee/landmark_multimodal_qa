from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):

    # =====================================================
    # APP
    # =====================================================

    APP_NAME: str = "landmark-agent"

    ENV: str = "development"

    DEBUG: bool = True

    # =====================================================
    # DEVICE
    # =====================================================

    DEVICE: str = "cpu"

    # =====================================================
    # VISION MODEL
    # =====================================================

    BASE_MODEL: str

    LORA_PATH: str

    HF_HOME: str

    HF_TOKEN: str = Field(...)

    # =====================================================
    # REMOTE INFERENCE
    # =====================================================

    PINGGY_URL: str = Field(...)

    # =====================================================
    # LLM PROVIDERS
    # =====================================================

    OPENAI_API_KEY: str = Field(...)

    GROQ_API_KEY: str = Field(...)

    # =====================================================
    # WEATHER API
    # =====================================================

    WEATHER_API_KEY: str = Field(...)

    # =====================================================
    # LANGSMITH
    # =====================================================

    LANGCHAIN_TRACING_V2: bool = False

    LANGCHAIN_API_KEY: str | None = None

    LANGCHAIN_PROJECT: str = "landmark-agent"

    # =====================================================
    # Pydantic Config
    # =====================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    # =========================================================
    # OPEN WEATHER
    # =====================================================

    OPENWEATHER_API_KEY: str

    OPENWEATHER_CURRENT_URL: str

    OPENWEATHER_FORECAST_URL: str

    OPENWEATHER_GEOCODING_URL: str
    
    # =========================================================
    SERPAPI_API_KEY: str


# =========================================================
# GLOBAL SETTINGS OBJECT
# =========================================================

settings = Settings()