# Stage 1: Build the React Application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package management files
COPY package*.json ./

# Install dependencies strictly
RUN npm ci

# Copy the rest of the frontend source code
COPY . .

# Build the production application
RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:alpine

# Copy the build output from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Overwrite the default Nginx configuration with our SPA-enabled config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 to the Docker host
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
