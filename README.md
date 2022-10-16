# [Stuff](https://stuff.csh.rit.edu)

Stuff is a database you can use to see the physical resources available to you in Computer Science House. You can see what we have available, who is/has been using it, and link to any relevant documentation or projects.

## Setup
**Requires Python & MongoDB**

### Python Dependencies
Use `pip install -r requirements.txt` to install the required python dependencies. Using virtualenv is recommeded when installing packages for python.

### Environment Variables
`Stuff` requires access to OIDC and s3 to operate properly. This is done by obtaining a client id and secret for each service.

Set these variables before attempting to start `Stuff`
* `IMAGE_URL` - URL where game thumbnails are hosted
* `MONGODB_DATABASE` - Set to whatever `Stuff` database will be called
* `SECRET_KEY` - Set to anything, but keep it a secret
* `SERVER_NAME` - Set to localhost:5000 for use with CSH auth
* `URL_SCHEME` - Set to `http` for CSH auth

For OIDC information contact a maintainer of `Stuff`
* `OIDC_CLIENT_ID`
* `OIDC_CLIENT_SECRET`
* `OIDC_ISSUER`

For s3 credentials contact a maintainer of `Stuff`
* `S3_BUCKET`
* `S3_KEY`
* `S3_SECRET`
* `S3_ENDPOINT`

## Running `Stuff`
Start `Stuff` by using `python wsgi.py` in the projects root directory

The project should be running at localhost:5000

