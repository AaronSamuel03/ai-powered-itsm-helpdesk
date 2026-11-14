from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str = "itsm_platform"
    HF_TOKEN: str
    HF_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"
    SNOW_INSTANCE: str = ""
    SNOW_USER: str = "admin"
    SNOW_PASSWORD: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
