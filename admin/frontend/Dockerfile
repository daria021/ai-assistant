FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json .
COPY package-lock.json .

RUN npm ci

COPY . .

RUN npx vite build --mode production

FROM nginx:stable-alpine

RUN rm -rf /usr/share/nginx/html/\*
# Set the TZ environment variable
ENV TZ=Europe/Moscow

# Install tzdata, configure the timezone, then remove tzdata if you don't need it at runtime
RUN apk add --no-cache tzdata \
 && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
 && echo $TZ > /etc/timezone \
 && apk del tzdata

COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
