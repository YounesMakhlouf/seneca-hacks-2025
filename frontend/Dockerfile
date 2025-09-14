# Stage 1: Build React app
FROM node:18-alpine AS builder
WORKDIR /app

# Install deps
COPY package.json package-lock.json* ./
RUN npm ci || npm install

# Build
ARG REACT_APP_FORM_CORRECTOR_URL=/form-corrector
ENV REACT_APP_FORM_CORRECTOR_URL=${REACT_APP_FORM_CORRECTOR_URL}
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
