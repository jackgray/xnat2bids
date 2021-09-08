FROM condaforge/mambaforge-pypy3

WORKDIR /input

ADD xnat2bids.py /input

RUN python3 -m pip install \
    xnatbidsfns \
    docopt \
    pathlib && \
    PATH=$PATH:/xnat2bids.py && \
    rm -r ${HOME}/.cache/pip 

CMD ["python3"]