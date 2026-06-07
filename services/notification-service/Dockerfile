# --- Stage 1: builder ---
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json .
RUN npm ci
COPY . .
RUN npm run build

# --- Stage 2: runtime ---
FROM node:20-alpine AS runtime

WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json .

EXPOSE 8004
CMD ["node", "dist/index.js"]