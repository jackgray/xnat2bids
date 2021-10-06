# https://github.com/conda-incubator/conda-lock/blob/main/README.md
# make sure conda-lock is installed 
# pip install conda-lock
# conda install -c conda-forge conda-lock

# needs environment.yaml file placed inside ./src and saves env lock files to ./src/locks


# generate lock files
# (can remove platforms not needed)
conda-lock \
    --check-input-hash \
    -p osx-arm64 \
    -p osx-64 \
    -p linux-64 \
    -p linux-aarch64 \
    -p win-64 \
    -p win-32 \
    -f ../src/environment.yaml \
    --filename-template '../src/locks/specific-{platform}.conda.lock'


