# Thinking Platform - Project Structure

## Overview

This document outlines the optimized project structure for the Thinking platform, designed to improve development efficiency and tool performance.

## Directory Structure

```
thinking/
├── backend/               # Python FastAPI backend
│   ├── routers/           # API route handlers
│   ├── utils/             # Utility functions and helpers
│   │   ├── model_helpers.py  # Model API client functions
│   │   └── ...
│   ├── models.py          # Data models
│   └── main.py            # Application entry point
├── frontend/              # React frontend
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utility libraries
│   │   └── ...
│   └── ...
├── deploy/                # Deployment configurations
├── specs/                 # API specifications
└── docs/                  # Documentation
```

## Performance Optimization

### Ignored Directories

The following directories are excluded from indexing by development tools to improve performance:

- `frontend/node_modules/`
- `frontend/dist/`
- `**/__pycache__/`
- `**/dist/`
- `**/.cache/`

### Best Practices

1. **Keep dependencies minimal**: Only install necessary packages
2. **Clean builds regularly**: Remove build artifacts when not needed
3. **Use virtual environments**: Isolate Python dependencies
4. **Optimize imports**: Only import what's needed
5. **Follow consistent code organization**: Maintain the structure outlined above

## Development Workflow

1. Backend development:
   - Use the FastAPI structure with routers and utilities
   - Keep model helper functions modular and consistent

2. Frontend development:
   - Follow component-based architecture
   - Use contexts and hooks for state management

## Tool-Specific Optimizations

### Windsurf

- Uses `.windsurf-ignore` to exclude large directories
- Performs better with clean Python cache files

### Cascade

- Uses `.cascadeignore` to focus on relevant code
- Works best with well-structured, modular code
