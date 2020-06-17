FROM python:3.7
ADD . /app
WORKDIR /app
EXPOSE 4000
RUN pip install --upgrade pip
RUN pip install jsonpickle
RUN pip install -r requirements.txt
ENTRYPOINT ["python","index.py"]