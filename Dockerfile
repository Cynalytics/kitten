FROM python:3.12-slim

WORKDIR /app

# System deps:
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Creating folders, and files for a project:
COPY ./kitten ./kitten

ENTRYPOINT ["python", "-m", "kitten"]
