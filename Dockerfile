ARG BASE_IMAGE=python:3.10.5
FROM ${BASE_IMAGE} as base

WORKDIR /app
COPY requirements.txt /app/requirements.txt


RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY sreality_scraper/ /app

ENTRYPOINT ["streamlit"]
CMD ["run", "main.py"]