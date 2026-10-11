# cat-now-me Web Dockerfile
# Multi-stage build for Next.js

# ============================================
# Base Stage
# ============================================
FROM node:20-alpine as base

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

# ============================================
# Dependencies Stage
# ============================================
FROM base as deps

# Copy package files
COPY package.json package-lock.json* ./
COPY ../../packages/shared ./packages/shared

# Install dependencies
RUN npm ci

# ============================================
# Builder Stage
# ============================================
FROM base as builder

COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/packages ./packages
COPY . .

# Build application
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ============================================
# Development Stage
# ============================================
FROM base as development

ENV NODE_ENV=development

COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/packages ./packages
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]

# ============================================
# Production Stage
# ============================================
FROM base as production

ENV NODE_ENV=production

# Create non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]