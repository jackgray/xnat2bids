FROM mambaorg/micromamba:0.15.3 AS conda

COPY ./src /src
RUN micromamba install -y -n base -f /src/locks/specific-linux-64.conda.lock && \
    micromamba clean --all --yes && \
    python -m pip install -r /src/requirements.txt --no-deps

# Primary container

FROM gcr.io/distroless/base-debian10
COPY --from=conda /src /src

CMD ["conda activate base"]
