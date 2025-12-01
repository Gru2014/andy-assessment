FROM node:20-alpine as build

WORKDIR /app

# Accept build arguments for environment variables
ARG VITE_API_URL=http://localhost:5000
ARG VITE_ENV=production

# Set environment variables for the build
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_ENV=$VITE_ENV

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

