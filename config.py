from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    EMAIL: str
    PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def GET_DATABASE_URL_psycopg(self):
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def GET_TABLE_NAME(self):
        return self.TABLE_NAME

    @property
    def GET_EMAIL_AND_PASSWORD(self) -> tuple[str, str]:
        return self.EMAIL, self.PASSWORD

    model_config = SettingsConfigDict(env_file="cfg.txt")


settings = Settings()


# PASSWORD=fibejeafobvrxmdh