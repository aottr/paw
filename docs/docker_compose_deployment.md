# Deploying paw with Docker Compose

## Prerequisites

- [Docker installed](https://docs.docker.com/engine/install/) on your machine
- Docker Compose plugin installed on your machine

## Deployment with `sqlite` database

Example `docker-compose.yml` file:

```yaml
version: "3.8"
services:
  paw:
    image: ghcr.io/aottr/paw:latest
    container_name: paw-ticket-system
    restart: unless-stopped
    ports:
      - "127.0.0.1:8000:8000"
    volumes:
      - db:/usr/src/app/db.sqlite3
      - media:/usr/src/app/media
    environment:
      - DATABASE_ENGINE=sqlite3
      - DEBUG=true
      - ALLOWED_HOSTS=example.org,example.com
      - SECRET_KEY=your-secret-key
```

The env variable `DATABASE_ENGINE` must be set to `sqlite3`, otherwise paw expects database credentials and another supported engine, e.g. `postgresql`

### Production Deployment

If, for whatever reason, a production deployment should be used with **sqlite3**, the `media` files need to be served with a webserver / reverse proxy, e.g. nginx. This should also happen with static files.

For this we slightly modify the deployment volumes:

```yaml
---
volumes:
  - db:/usr/src/app/db.sqlite3
  - /opt/paw/media:/usr/src/app/media
  - /opt/paw/static:/usr/src/app/static
```

Now you write directives in your config to host these files, the following snipped shows an example nginx config:

```nginx
upstream paw {
    server localhost:8000;
}

server {

    server_name example.org example.com
    listen 80;
    listen [::]:80;

    location /media/ {
        # media files, uploaded by us
        alias /opt/paw/media/; # ending slash is required
    }

    location /static/ {
        # static files, uploaded by the system
        alias /opt/paw/static/; # ending slash is required
    }

    location / {
        proxy_pass http://paw;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_redirect off;
    }
}
```

That's it! You have successfully deployed your project using Docker Compose.
