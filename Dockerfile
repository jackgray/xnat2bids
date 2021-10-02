FROM continuumio/miniconda:latest as conda

ADD ./src/locks/specific-linux-64.conda.lock /locks/specific-linux-64.conda.lock 

RUN conda create -p /opt/env --copy --file /locks/specific-linux-64.conda.lock

# Primary container: distroless to only keep system files needed for specific purpose
FROM gcr.io/distroless/base-debian10

COPY --from=conda /opt/env /opt/env

