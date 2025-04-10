from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

class RunConfig(BaseModel):
    host: str = "localhost"
    port: int = 8080

class ApiPrefix(BaseModel):
    prefix:str = "/api"

class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()

settings = Settings()