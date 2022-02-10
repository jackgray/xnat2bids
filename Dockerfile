FROM python:3.6-stretch AS build 
USER root
COPY /app /app
RUN pip3 install -r /app/requirements.txt -t /python-env

FROM gcr.io/distroless/python3-debian10
USER root
COPY --from=build /python-env /python-env
COPY --from=build /app /app

ENV PYTHONPATH=/python-env
WORKDIR /app
CMD ["main.py"]
