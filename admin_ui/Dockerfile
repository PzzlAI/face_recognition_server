FROM node:17-alpine

WORKDIR /app

# more faster to build images
COPY package.json package-lock.json ./

RUN npm install

# required for docker desktop port mapping
COPY . .

EXPOSE 3000

CMD ["node", "app.js"]
