from fastapi import FastAPI, HTTPException, Query, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List, Dict, Any
import logging
import os

# Import the scraper function (adjust path if necessary)
try:
    from gmaps_scraper_server.scraper import scrape_google_maps
except ImportError:
    # Handle case where scraper might be in a different structure later
    logging.error("Could not import scrape_google_maps from scraper.py")
    # Define a dummy function to allow API to start, but fail on call
    def scrape_google_maps(*args, **kwargs):
        raise ImportError("Scraper function not available.")

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# API Key authentication setup
security = HTTPBearer()

def get_api_keys() -> List[str]:
    """Get valid API keys from environment variable."""
    api_keys_env = os.getenv("API_KEYS", "")
    if not api_keys_env:
        return []
    return [key.strip() for key in api_keys_env.split(",") if key.strip()]

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key from Authorization header."""
    valid_keys = get_api_keys()
    
    # If no API keys are configured, allow access
    if not valid_keys:
        logging.warning("No API keys configured - allowing unrestricted access")
        return True
    
    if credentials.credentials not in valid_keys:
        logging.warning(f"Invalid API key attempted: {credentials.credentials[:10]}...")
        raise HTTPException(
            status_code=401,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True

app = FastAPI(
    title="Google Maps Scraper API",
    description="API to trigger Google Maps scraping based on a query. Requires API key authentication.",
    version="0.1.0",
)

@app.post("/scrape", response_model=List[Dict[str, Any]])
async def run_scrape(
    query: str = Query(..., description="The search query for Google Maps (e.g., 'restaurants in New York')"),
    max_places: Optional[int] = Query(None, description="Maximum number of places to scrape. Scrapes all found if None."),
    lang: str = Query("en", description="Language code for Google Maps results (e.g., 'en', 'es')."),
    headless: bool = Query(True, description="Run the browser in headless mode (no UI). Set to false for debugging locally."),
    _: bool = Depends(verify_api_key)
):
    """
    Triggers the Google Maps scraping process for the given query.
    """
    logging.info(f"Received scrape request for query: '{query}', max_places: {max_places}, lang: {lang}, headless: {headless}")
    try:
        # Run the potentially long-running scraping task
        # Note: For production, consider running this in a background task queue (e.g., Celery)
        # to avoid blocking the API server for long durations.
        results = await scrape_google_maps( # Added await
            query=query,
            max_places=max_places,
            lang=lang,
            headless=headless # Pass headless option from API
        )
        logging.info(f"Scraping finished for query: '{query}'. Found {len(results)} results.")
        return results
    except ImportError as e:
         logging.error(f"ImportError during scraping for query '{query}': {e}")
         raise HTTPException(status_code=500, detail="Server configuration error: Scraper not available.")
    except Exception as e:
        logging.error(f"An error occurred during scraping for query '{query}': {e}", exc_info=True)
        # Consider more specific error handling based on scraper exceptions
        raise HTTPException(status_code=500, detail=f"An internal error occurred during scraping: {str(e)}")

@app.get("/scrape-get", response_model=List[Dict[str, Any]])
async def run_scrape_get(
    query: str = Query(..., description="The search query for Google Maps (e.g., 'restaurants in New York')"),
    max_places: Optional[int] = Query(None, description="Maximum number of places to scrape. Scrapes all found if None."),
    lang: str = Query("en", description="Language code for Google Maps results (e.g., 'en', 'es')."),
    headless: bool = Query(True, description="Run the browser in headless mode (no UI). Set to false for debugging locally."),
    _: bool = Depends(verify_api_key)
):
    """
    Triggers the Google Maps scraping process for the given query via GET request.
    """
    logging.info(f"Received GET scrape request for query: '{query}', max_places: {max_places}, lang: {lang}, headless: {headless}")
    try:
        # Run the potentially long-running scraping task
        # Note: For production, consider running this in a background task queue (e.g., Celery)
        # to avoid blocking the API server for long durations.
        results = await scrape_google_maps( # Added await
            query=query,
            max_places=max_places,
            lang=lang,
            headless=headless # Pass headless option from API
        )
        logging.info(f"Scraping finished for query: '{query}'. Found {len(results)} results.")
        return results
    except ImportError as e:
         logging.error(f"ImportError during scraping for query '{query}': {e}")
         raise HTTPException(status_code=500, detail="Server configuration error: Scraper not available.")
    except Exception as e:
        logging.error(f"An error occurred during scraping for query '{query}': {e}", exc_info=True)
        # Consider more specific error handling based on scraper exceptions
        raise HTTPException(status_code=500, detail=f"An internal error occurred during scraping: {str(e)}")


# Basic root endpoint for health check or info
@app.get("/")
async def read_root():
    return {"message": "Google Maps Scraper API is running."}

# Example for running locally (uvicorn main_api:app --reload)
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001)