# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Google Maps scraper API built with FastAPI and Playwright. The service extracts business data from Google Maps search results through automated browser interactions. It's designed for integration with n8n automation workflows and provides both POST and GET endpoints for flexible usage.

## Architecture

### Core Components

- **`gmaps_scraper_server/main_api.py`**: FastAPI application with `/scrape` (POST) and `/scrape-get` (GET) endpoints
- **`gmaps_scraper_server/scraper.py`**: Main scraping logic using async Playwright for browser automation
- **`gmaps_scraper_server/extractor.py`**: HTML parsing and data extraction from Google Maps pages

### Data Flow

1. API receives search query and parameters
2. `scraper.py` launches headless browser and navigates to Google Maps
3. Scrolls through search results to collect place links
4. Visits each place page and extracts HTML content
5. `extractor.py` parses the HTML to extract structured business data
6. Returns JSON array of business information

## Development Commands

### Local Development
```bash
# Quick start with Makefile
make dev

# Or step by step:
make venv      # Create virtual environment with uv
make install   # Install dependencies
make run       # Run development server with auto-reload

# Manual commands:
pip install -r requirements.txt
uvicorn gmaps_scraper_server.main_api:app --reload

# Run on specific host/port
uvicorn gmaps_scraper_server.main_api:app --host 0.0.0.0 --port 8001
```

### Docker Development
```bash
# Build and run with docker-compose
docker-compose up --build

# Build single service
docker-compose build scraper-api

# Run in detached mode
docker-compose up -d
```

### Network Setup
The Docker setup uses an external network called `shark`. Create it before running:
```bash
docker network create shark
```

## API Usage

### Endpoints
- `GET /`: Health check
- `POST /scrape`: Main scraping endpoint (JSON body)
- `GET /scrape-get`: GET version for n8n integration

### Parameters
- `query` (required): Search query (e.g., "hotels in 98392")
- `max_places` (optional): Limit number of results
- `lang` (optional, default "en"): Language code
- `headless` (optional, default true): Browser mode

## Technical Notes

### Async Implementation
All scraping functions are async and use `await` with Playwright operations. The main scraping function `scrape_google_maps()` must be called with `await`.

### Data Extraction Strategy
The extractor parses Google Maps' `window.APP_INITIALIZATION_STATE` JavaScript object from page HTML. It handles nested JSON structures and uses safe navigation with fallback error handling.

### Browser Automation Details
- Uses Playwright with Chromium browser
- Handles consent forms automatically
- Implements smart scrolling with end-of-results detection
- Includes rate limiting protection with configurable delays

### Error Handling
- Graceful degradation for missing data fields
- Debug file generation for troubleshooting extraction issues
- Comprehensive logging throughout the scraping process