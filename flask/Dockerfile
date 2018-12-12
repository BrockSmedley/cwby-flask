FROM alpine:3.8
EXPOSE 5000
RUN apk add --no-cache uwsgi-python3 python3 pkgconfig libffi gcc python3-dev musl-dev

RUN mkdir -p /src/app/
WORKDIR /src/app

# copy only requirements.txt to avoid re-building pip dependency layer on every build...
ADD ./requirements.txt /src/app/
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r requirements.txt

# ...then copy the rest (app files need frequent rebuilding)
COPY . /src/app

CMD [ "uwsgi",  "--socket", "0.0.0.0:5000", \
                "--uid", "uwsgi", \
                "--plugins", "python3", \
                "--protocol", "uwsgi", \
                "--wsgi", "app:app" ]
