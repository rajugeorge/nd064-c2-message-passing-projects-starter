FROM python:3.7
LABEL maintainer="Raju George"

WORKDIR /app

COPY . .

RUN pip install -U pip wheel setuptools && \
    pip install -r requirements.txt

EXPOSE 5005

# command to run on container start
CMD [ "python", "main.py" ]