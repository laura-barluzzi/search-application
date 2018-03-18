# Enerknol

## Development setup

For running locally, create a file `.env` with the following contents:

```
PORT=8080
FLASK_CONFIG_DEBUG=True
FLASK_CONFIG_PASSWORD_SALT=changeme
FLASK_CONFIG_SECRET_KEY=changeme
MYSQL_USER=changeme
MYSQL_PASSWORD=changeme
MYSQL_ROOT_PASSWORD=changeme
```

Now run `docker-compose up --build` to start MySQL, NGINX, ElasticSearch,
MongoDB and Flask.

## Production setup

For running in production, create a file `.env` with the following contents:

```
PORT=80
FLASK_CONFIG_DEBUG=False
FLASK_CONFIG_PASSWORD_SALT=changeme
FLASK_CONFIG_SECRET_KEY=changeme
MYSQL_USER=changeme
MYSQL_PASSWORD=changeme
MYSQL_ROOT_PASSWORD=changeme
```

Remember to update all the `changeme` placeholders to secure random values!
