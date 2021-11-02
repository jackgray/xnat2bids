FROM python:3.6-stretch AS build 
COPY requirements.txt /
RUN pip3 install -r /requirements.txt -t /pythonlibs

FROM gcr.io/distroless/python3-debian10
COPY --from=build /pythonlibs /pythonlibs 
COPY  . /app
# COPY ./xnat2bids_private.pem /MRI_DATA/nyspi/patensasc/.tokens
ENV PYTHONPATH=/pythonlibs
WORKDIR /app
CMD ["dn_nifti.py"]