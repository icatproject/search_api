from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Class that extends Pydantics base settings to read in
    environment variables from a file.
    """

    # used to connect to icat
    version: str

    opensearch_host: str
    opensearch_port: int

    jwt_secret_key: str
    jwt_algo: str

    scigateway_auth: str

    class Config:
        env_file = "./config.env"


# create a single instance on the class to import
settings = Settings()
