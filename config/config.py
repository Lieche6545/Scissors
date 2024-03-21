# Default Configuration Settings

from functools import lru_cache


class  Settings():
    # Default BaseSettings

    env_name: str = "Local"
    base_url: str = "http://localhost:8000/"
    db_url: str = "sqlite:///./Lieche_URL_Shortener.sqlite"


    # Postgresql SPecific
    # db_name: str = "Lieche_scissor_database" 
    # db_address: str = "localhost"
    # db_port: str = "5432"
    # db_user: str = "postgres"
    # db_pw: str = "admin" 

    # Default to SQLite
    db_backend: str = "postgresql"

    

    SECRET_KEY = "scissorsbdbc97f82bfe593d1e45cec19ad2591af315096665512564df9af"
    ALGORITHM = "HS256"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if settings.db_backend == "postgresql":
        settings.db_url = "postgresql://hqbrlupr:BY-1SMDAjTIx9oNlwwT0OvzgJzoqAO6h@ziggy.db.elephantsql.com/hqbrlupr"
        
    print(f"Loading settings for: {settings.env_name}")
    print(f"Database String: '{settings.db_url}'")
    return settings