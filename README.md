# Game-Night

Game-Night is a web-app used to archive boardgames used by members of the Computer Science House. Game-Night is currently running [Here](https://game-night.csh.rit.edu)

## Setup
**Requires Python & MongoDB**

### Python Dependencies
Use `pip install -r requirements.txt` to install the required python dependencies. Using virtualenv is recommeded when installing packages for python.

### Environment Variables
Game-Night requires access to OIDC and s3 to operate properly. This is done by obtaining a client id and secret for each service.

Set these variables before attempting to start Game-Night
* `IMAGE_URL` - URL where game thumbnails are hosted
* `MONGODB_DATABASE` - Set to whatever Game-Night database will be called
* `SECRET_KEY` - Set to anything, but keep it a secret
* `SERVER_NAME` - Set to localhost:5000 for use with CSH auth
* `URL_SCHEME` - Set to `http` for CSH auth

For OIDC information contact a maintainer of Game-Night
* `OIDC_CLIENT_ID`
* `OIDC_CLIENT_SECRET`
* `OIDC_ISSUER`

For s3 credentials contact a maintainer of Game-Night
* `S3_BUCKET`
* `S3_KEY`
* `S3_SECRET`
* `S3_ENDPOINT`

## Running Game-Night
Start Game-Night by using `python wsgi.py` in the projects root directory

The project should be running at localhost:5000

