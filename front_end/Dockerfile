FROM python:3.10

COPY . /app

WORKDIR /app

RUN /usr/local/bin/python -m pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit","run"]

CMD ["app.py"]



