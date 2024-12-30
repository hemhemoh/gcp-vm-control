FROM python:3.12-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ARG PORT=9001
ENV PORT=$PORT

COPY . /gcp-vm-control
WORKDIR /gcp-vm-control

RUN uv sync

EXPOSE $PORT
ENTRYPOINT ["sh", "-c", "uv run uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
CMD ["--reload"]