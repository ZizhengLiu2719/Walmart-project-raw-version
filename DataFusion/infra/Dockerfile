# ---------- build stage ----------
FROM node:24.4.1-bullseye-slim AS builder

# Ensure reproducible npm version
RUN npm install -g npm@11.4.2

# Update apt
RUN apt update && apt upgrade -y

# Install `curl`
RUN apt install -y curl

WORKDIR /usr/src/app

# copy package files first to leverage Docker cache when deps don't change
COPY package.json package-lock.json* ./

# install dev deps so we can build (typescript, ts-node, etc.)
RUN npm ci

# copy source
COPY . .

# build produced JS into /usr/src/app/dist (assumes "build" script runs tsc)
RUN npm run build

# ---------- production runtime ----------
FROM node:24.4.1-bullseye-slim AS runner
RUN npm install -g npm@11.4.2

WORKDIR /usr/src/app

# copy only production deps from package-lock (we can do a clean install)
COPY package.json package-lock.json* ./
# Install only production dependencies to keep runtime small
RUN npm ci --omit=dev

# copy built artifacts from builder stage
COPY --from=builder /usr/src/app/dist ./dist

# copy any other required files (e.g. .env.example -> .env or static files)
# COPY config ./config

ENV NODE_ENV=production
ENV PORT=4000

EXPOSE 4000

# default command: run compiled node
CMD ["node", "dist/Index.js"]
