FROM python:3.10-slim
LABEL authors="chris"

RUN mkdir app
RUN cd app
WORKDIR /app
ADD ./ /app

RUN pip install --upgrade pip
RUN pip install -r requirements/requirements.txt


CMD ["python", "main.py"]