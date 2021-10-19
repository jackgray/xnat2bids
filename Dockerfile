FROM debian:buster-slim AS build 
RUN apt-get update && \
    apt-get install --no-install-suggests \
    --no-install-recommends \
    --yes python3-venv && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip

FROM build AS build-venv
COPY ./app /app

WORKDIR /app
RUN /venv/bin/pip install --disable-pip-version-check -r /app/requirements.txt

FROM gcr.io/distroless/python3-debian10
COPY --from=build-venv /venv /venv 
COPY --from=build-venv /app /app
COPY xnat2bids_private.pem /.xnat
# COPY ./xnat2bids_private.pem /MRI_DATA/nyspi/patensasc/.tokens
ENV PYTHONPATH=/venv
WORKDIR /app
ENTRYPOINT [ "xnat2bids.py", "patensasc" ]
