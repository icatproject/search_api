from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Class that extends Pydantics base settings to read environment variables.
    These values are fall back values. If no environment variables are set, it will use these
    """

    version: str = "1.0"

    # When running the api locally against a compose stack
    #opensearch_host: str = "127.0.0.1"
    #scigateway_auth: str = "http://127.0.0.1:8008/verify"

    # When running the api, and everything else, from a compose stack
    opensearch_host: str = "opensearch"
    scigateway_auth: str = "http://scigateway_auth_container:8000/verify"

    opensearch_port: int = 9200
    opensearch_index: str = "my-index"

    jwt_public_key: str = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCj8UF0wr1OBqY52aKwEUNx/NOF6XorpADDj3fszm1Dw+LMmxfZ9IylkL7qbYfzh8bg/bhI4yphfyt/AfCWRScuFUbkaJO9urEV4Ru1UT16/nDl7efSG9e8Fvzg719y+XSSNT4PWamw7n8e+pMz/2baJcsQdnuSkH68qGj0mr/Yo62cZ5g0oKByd2LfJxNAjjcezXrFPLM+mKQuMcbqwM3cawlRnEKK1YUehewQAhvAsuUWsvVVLx70bggRsEjorqdoLPaYJa60fAL2Q7qLlIN9xD6vWfMQ2DZ8g+MttVGELnu+nStdgPznE9oiPqYr3VxR+NB7rBm2VbeY4MI6iT7h0XY7D6kofVDmU9vqPXVTHBMsSE8gIE3XinZRlHa//XNq0Qqf81a5KjpmKgwbK5IG3LIltBDf3AO1u4gJMhm7ltC4iDZUrbjC7SGBdwUC6/at9aZytbCRfMFBHNa/YkBzAf1ih5SpZ1n/D+AWzDlJLQ0l9Xr4cu9W1xhPeV9F+LM= scigateway-auth@7b8bc716bc39"
    jwt_algo: str = "RS256"


# create a single instance on the class to import
settings = Settings()
