./bundlejs.sh
cd flask
docker stop flask cwby-flask_web_1
docker rm flask cwby-flask_web_1
docker build -t flask .
docker run -it --name flask --ip 172.70.0.2 -p 5000:5000 --network cwby-flask_legacy flask
