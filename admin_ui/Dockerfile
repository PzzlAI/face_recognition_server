FROM node:17-alpine

WORKDIR /app

# more faster to build images
COPY package.json package-lock.json ./

RUN npm install

EXPOSE 4000
# required for docker desktop port mapping

CMD ["node", "app.js"]
