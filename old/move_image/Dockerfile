FROM python:3.6-stretch AS build 
USER root
COPY . /app
RUN pip3 install -t /pythonlibs -r /app/requirements.txt

FROM gcr.io/distroless/python3-debian10
USER root
COPY --from=build /pythonlibs /pythonlibs 
COPY --from=build /app /app
ENV PYTHONPATH=/pythonlibs
WORKDIR /app
CMD ["nifti2bids.py"]