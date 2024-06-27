FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# VOLUME ["/app"]

COPY . .

EXPOSE 8000
CMD [ "shiny", "run", "app.py" ]