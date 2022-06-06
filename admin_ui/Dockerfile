FROM node:17-alpine

WORKDIR /app

# more faster to build images
COPY package.json package-lock.json ./

RUN npm install

<<<<<<< HEAD
COPY . .

EXPOSE 4000
=======
EXPOSE 3000
>>>>>>> 348a7254cedf10c7ff288c57ee9ec54d13f685ad
# required for docker desktop port mapping

CMD ["node", "app.js"]
