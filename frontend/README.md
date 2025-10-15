# AI-Studio Frontend

Simple React frontend for AI-Studio.

## Run with Docker

```bash
# From project root
docker-compose up -d

# Access at http://localhost:3000
```

## Run Locally (Development)

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Access at http://localhost:3000
```

## Build for Production

```bash
npm run build
npm run preview
```

## Current Features

- ✅ List all available tools (analyzers and generators)
- ✅ Display tool metadata (cost, avg time, description)
- ✅ Grouped by category (analyzers vs generators)

## Tech Stack

- React 18
- Vite
- Vanilla CSS
