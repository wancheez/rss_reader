FROM python:3.11.2-alpine as base

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

FROM base AS python-deps
# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apk update
RUN apk --no-cache --update add libffi libressl postgresql-libs gcc libc-dev libpq-dev
RUN apk update && apk add --no-cache supervisor
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# Create and switch to a new user
RUN adduser --disabled-password  wancheez
WORKDIR /home/wancheez
USER wancheez

# Install application into container
COPY . .