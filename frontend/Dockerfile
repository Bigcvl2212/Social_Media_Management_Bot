# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install all dependencies (including devDependencies needed for build)
RUN npm ci

# Copy application code
COPY . .

# Build the application using the full path to next
RUN ./node_modules/.bin/next build

# Prune devDependencies for smaller production image
RUN npm prune --omit=dev

# Expose port
EXPOSE 3000

# Run the application
CMD ["npm", "start"]