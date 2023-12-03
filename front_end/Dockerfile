FROM python:3.9.0

EXPOSE 8501

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

# Set up a volume to make the local "riverflow.csv" accessible inside the container
VOLUME ["/app"]

# Copy the rest of the application files
COPY . .

ENTRYPOINT [ "streamlit", "run" ]
CMD [ "app.py" ]

