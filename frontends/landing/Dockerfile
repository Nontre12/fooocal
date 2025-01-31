FROM node:lts-alpine AS build

WORKDIR /app

COPY . .

RUN npm i -g pnpm

RUN pnpm i
RUN pnpm run build

FROM httpd:2.4 AS runtime

COPY --from=build /app/dist /usr/local/apache2/htdocs/

EXPOSE 80