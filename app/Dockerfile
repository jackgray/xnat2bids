FROM python:3.6-stretch AS build 
USER root
COPY . /app
RUN pip3 install -r /app/requirements.txt -t /pythonlibs

FROM gcr.io/distroless/python3-debian10
USER root
COPY --from=build /pythonlibs /pythonlibs 
COPY --from=build /app /app
# COPY ./xnat2bids_private.pem /MRI_DATA/nyspi/patensasc/.tokens
ENV PYTHONPATH=/pythonlibs
WORKDIR /app
CMD ["main.py"]