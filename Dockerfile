FROM python:3.9-slim-bullseye

RUN apt update
RUN apt install nano

# upgrade pip
RUN pip install --upgrade pip

# permissions and nonroot user for tightened security
RUN useradd nonroot
RUN mkdir /home/app/
RUN chown -R nonroot:nonroot /home/app
RUN mkdir -p /var/log/flask-app && touch /var/log/flask-app/flask-app.err.log && touch /var/log/flask-app/flask-app.out.log
RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /home/app

# copy all the files to the container
COPY --chown=nonroot:nonroot . .

RUN export FLASK_APP=app.py
RUN pip install -r requirements.txt

USER nonroot
CMD ["python", "app.py"]