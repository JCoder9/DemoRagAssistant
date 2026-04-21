# Use Node.js 20
FROM node:20-slim

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Expose port
EXPOSE 5173

# Run development server (for production, use 'npm run build' and serve with nginx)
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
