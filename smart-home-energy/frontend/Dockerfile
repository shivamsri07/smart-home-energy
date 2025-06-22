# --- Stage 1: The Builder ---
# This stage installs dependencies and builds our static assets.
FROM node:22-alpine as builder

# Set working directory
WORKDIR /app

# Copy dependency files and install
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of our source code
COPY . .

# Build the production-ready static files.
# This creates an optimized build in the /app/dist directory.
RUN npm run build


# --- Stage 2: The Final Runtime Image ---
# This stage serves the built assets using a lightweight Nginx server.
FROM nginx:stable-alpine as runtime

# Copy the built static files from the builder stage to Nginx's public HTML folder.
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy our custom Nginx configuration.
# This will overwrite the default Nginx config.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80, which is the default port Nginx listens on.
EXPOSE 80

# The default Nginx command will start the server.
CMD ["nginx", "-g", "daemon off;"]