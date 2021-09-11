FROM mambaorg/micromamba:0.15.3
COPY --chown=micromamba:micromamba environment.yaml /tmp/environment.yaml
RUN micromamba install -y -n base -f /tmp/environment.yaml && \
    micromamba clean --all --yes && \
    python -m pip install xnatbidsfns
   

COPY ./src /src

CMD ["conda activate base"]
