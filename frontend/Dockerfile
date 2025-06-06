# Use Node.js 20 alpine image (latest LTS with security updates)
FROM node:20-alpine

# Install security updates
RUN apk update && apk upgrade

# Install pnpm globally
RUN npm install -g pnpm@latest

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json pnpm-lock.yaml* ./

# Install dependencies with pnpm
RUN pnpm install

# Copy project files
COPY . .

# Expose port
EXPOSE 5173

# Default command
CMD ["pnpm", "run", "dev", "--", "--host", "0.0.0.0"]