docker build \
-t jackgray/xnat_sync:latest \
--push
../app

docker build -t jackgray/xnat_auth:latest -f ../app/auth.Dockerfile ../app