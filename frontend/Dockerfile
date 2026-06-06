# build env
FROM node:24
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps --force
COPY . ./
RUN npm run build
CMD cp -r build/* /static
