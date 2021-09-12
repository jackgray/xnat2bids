# conda-lock -p osx-64 -p osx-arm64 -p linux-64 -p linux-aarch64 -f environment.yaml
# conda-lock -p osx-64 -p osx-arm64 -p linux-64 -p linux-aarch64 -f predict-environment.yaml 

# conda list --explicit > spec-file.txt

conda-lock \
    --check-input-hash \
    -p osx-arm64 \
    -p linux-64 \
    -f ./src/environment.yaml \
    --filename-template 'specific-{platform}.conda.lock'
