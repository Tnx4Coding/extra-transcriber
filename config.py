from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Gemini
    GEMINI_API_KEY: str

    # Google OAuth2 (מתקבל מ-get_token.py)
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REFRESH_TOKEN: str

    # Google Sheets — ה-ID מה-URL של ה-Spreadsheet
    SPREADSHEET_ID: str = "1sThbmk1HtlclmRf2M1in8wJpmZzdXvX4s0YihcdZkaY"

    # אבטחת ה-webhook (אופשיונלי)
    WEBHOOK_SECRET: str = ""

    # שרת
    PORT: int = 8000


settings = Settings()
