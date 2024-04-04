FROM mongo:latest
ENV MONGO_INITDB_ROOT_USERNAME=wcadmin
ENV MONGO_INITDB_ROOT_PASSWORD=123456
COPY init-mongo.sh /docker-entrypoint-initdb.d/
RUN chmod +x /docker-entrypoint-initdb.d/init-mongo.sh
EXPOSE 27017