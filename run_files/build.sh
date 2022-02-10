docker build \
-t jackgray/xnat_sync:latest \
../app

docker build -t jackgray/xnat_auth:latest -f ../app/auth.Dockerfile ../app

docker push jackgray/xnat_sync
docker push jackgray/xnat_auth