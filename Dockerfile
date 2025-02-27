FROM python:3.12-slim

# Set the working directory
WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./src /src

CMD ["fastapi", "run", "src/main.py", "--port", "80"]