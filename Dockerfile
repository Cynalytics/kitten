FROM python:3.10

WORKDIR /app/kitten



RUN --mount=type=cache,target=/root/.cache \
    pip install --upgrade pip \
    && pip install httpx docker structlog pydantic pydantic-settings


COPY ./kitten ./kitten


ENTRYPOINT ["python", "-m", "kitten"]
