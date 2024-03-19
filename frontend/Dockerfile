# # Step 1: Build your React app using Node.js
# FROM node:18 as build-stage

# # Set the working directory in the container
# WORKDIR /app

# # Copy the rest of your app's source code
# COPY . .

# # Install your dependencies
# RUN npm install

# # Build your React app
# RUN npm run build

# # Step 2: Serve your React app using Nginx
# FROM nginx:stable-alpine as production-stage

# # Copy the build output to replace the default nginx contents
# COPY --from=build-stage /app/dist /usr/share/nginx/html

# # Expose port 80 to the outside once the container has launched
# EXPOSE 80

# # Run Nginx with global directives and daemon off
# CMD ["nginx", "-g", "daemon off;"]

# Step 1: Build your React app using Node.js
FROM node:18 as build-stage

# Set the working directory in the container
WORKDIR /app

# Copy the rest of your app's source code
COPY . .

# Install your dependencies
RUN npm install

# Build your React app
RUN npm run build

# Step 2: Serve your React app using Nginx
FROM nginx:stable-alpine as production-stage

# Copy the custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy the build output to replace the default nginx contents
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Expose port 80 to the outside once the container has launched
EXPOSE 80

# Run Nginx with global directives and daemon off
CMD ["nginx", "-g", "daemon off;"]
