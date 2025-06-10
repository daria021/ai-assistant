MAIN_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

def set_main_db_url(url: str) -> None:
    global MAIN_DB_URL
    MAIN_DB_URL = url

def get_main_db_url() -> str:
    return MAIN_DB_URL
