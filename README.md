# Link Feed

A re-implementation of some of the features of del.icio.us that I miss the most.
Runs in a docker container based on python 3.9 at the moment.
Dockerfile and Docker Compose are included.

Here's some info on how to use it:
* create a new requirements file with: pipreqs --force .
* build the docker container with: docker build -t link-feed:latest .
* run local: docker run -name link-feed  -v .:/app --env-file .env -p 5000:5000 link-feed
* package firefox addon: zip -r static/linktool.xpi -j firefox-plugin/*
* sqlite instance: sqlite3 instance/inputs.db 

### bugs
* no loading settings after login

## Link Tool

* wishlist: use openai api to generate summary :)

## Deploy

* start docker-compose file