from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Class that extends Pydantics base settings to read environment variables.
    These values are fall back values. If no environment variables are set, it will use these
    """

    version: str = "1.0"

    opensearch_host: str = "127.0.0.1"
    opensearch_port: int = 9200

    jwt_secret_key: str = "your-secret-key"
    jwt_algo: str = "HS256"

    scigateway_auth: str = "https://scigateway_auth/validate"


# create a single instance on the class to import
settings = Settings()
