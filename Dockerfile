FROM python:3.10

WORKDIR /app

# System deps:
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Creating folders, and files for a project:
COPY . .
