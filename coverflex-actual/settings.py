from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
	model_config = SettingsConfigDict(case_sensitive=True, extra="allow", env_ignore_empty=True)

	ACTUAL_URL: str = "http://localhost:5006"
	ACTUAL_PASSWORD: str
	ACTUAL_FILE: str
	COVERFLEX_EMAIL: str
	COVERFLEX_PASSWORD: str
	COVERFLEX_ENDPOINT: str = "https://menhir-api.coverflex.com"
	COVERFLEX_AUTH_URL: str = f"{COVERFLEX_ENDPOINT}/api/employee/sessions"
	COVERFLEX_MOVEMENTS_URL: str = f"{COVERFLEX_ENDPOINT}/api/employee/movements"
	COVERFLEX_ACTUAL_ACCOUNT: str = "Coverflex"
