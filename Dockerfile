FROM ubuntu:22.04

RUN apt update && apt install python3 python3-pip -y

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["python3", "plug.py"]