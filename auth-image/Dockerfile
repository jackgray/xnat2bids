# FROM python:3.8-slim-buster AS build 

# COPY . /app
# WORKDIR /app
# # RUN python3 -m venv /pyenv
# RUN python3 -m pip install \
# --disable-pip-version-check \
# -r requirements.txt && \
# mkdir /.xnat && \
# mv /app/xnat2bids_public.pem /.xnat

# # FROM gcr.io/distroless/python3-debian10
# # COPY --from=build /usr/local/python3 /python3
# # COPY --from=build /app /app
# # # COPY ./xnat2bids_private.pem /MRI_DATA/nyspi/patensasc/.tokens
# # WORKDIR /app
# ENTRYPOINT [ "bash", "&&", "python3", "auth.py", ]

FROM python:3.6-stretch AS build 
COPY app/requirements.txt /
RUN pip3 install -r /requirements.txt -t /pythonlibs

FROM gcr.io/distroless/python3-debian10
COPY --from=build /pythonlibs /pythonlibs 
COPY  app /app
COPY ./xnat2bids_public.pem /.xnat
ENV PYTHONPATH=/pythonlibs
WORKDIR /app
CMD ["auth.py"]