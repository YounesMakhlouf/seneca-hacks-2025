FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install the worker dependencies
COPY pyproject.toml README.md uv.lock ./
RUN uv sync --frozen --no-cache

# Copy worker source code
COPY src ./src

EXPOSE 8080

CMD ["uv", "run", "python", "-m", "src.feedback_worker.main"]