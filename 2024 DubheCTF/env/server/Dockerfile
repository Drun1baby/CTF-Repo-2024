FROM node:alpine
WORKDIR /app
COPY server .
COPY flag /flag
COPY readflag /readflag
RUN chmod 400 /flag
RUN chmod +xs /readflag

RUN adduser -D player
RUN chown -R player:player /app

USER player
RUN npm i
EXPOSE 3800 4800
CMD ["npm", "run", "dev"]