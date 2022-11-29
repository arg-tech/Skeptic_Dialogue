FROM python:3

RUN mkdir -p /home/skeptic-dialogue
WORKDIR /home/skeptic-dialogue

RUN pip install --upgrade pip

ADD requirements.txt .
RUN pip install -r requirements.txt
RUN pip install gunicorn

ADD app app
ADD boot.sh ./
RUN chmod +x boot.sh


ENV FLASK_APP app


EXPOSE 5000
ENTRYPOINT ["./boot.sh"]