# Input Validation and Logging Improvements

## Changes Made

### 1. Enhanced Debug Logging in `detective_agent.py`

Added comprehensive debug logging for LLM responses:

```python
# After LLM calls
logger.debug(f"RAW LLM RESPONSE: {response[:500]}...")

# After JSON extraction
logger.debug(f"EXTRACTED JSON: {json_str}")
```

This provides better visibility into:
- The actual raw response from LLM services
- The extracted JSON before parsing
- Helps debug JSON extraction and parsing issues

### 2. Improved URL Validation in `detective_agent.py`

Enhanced the `_is_valid_url()` method with more comprehensive validation:

```python
def _is_valid_url(self, url: str) -> bool:
    """Check if a URL is valid."""
    if not url or not isinstance(url, str):
        return False
    
    # Remove whitespace
    url = url.strip()
    if not url:
        return False
    
    try:
        result = urlparse(url)
        valid_format = all([result.scheme in ('http', 'https'), result.netloc])
        
        if not valid_format:
            logger.debug(f"Invalid URL format: {url}")
            return False
        
        # Rest of existing validation...
```

Benefits:
- Type checking for URL parameter
- Whitespace handling
- Strict scheme validation (http/https only)
- Better logging for invalid URLs

### 3. Response Validation in `fetch.py`

Added validation for response.text in the fetch_page() function:

```python
if response.status_code == 200:
    # Validate response has content
    if not hasattr(response, 'text') or response.text is None:
        logger.warning(f"Response from {url} has no text content")
        return None, {"error": "No text content in response"}
    
    # Check if content is HTML
    content_type = response.headers.get('Content-Type', '').lower()
    if 'text/html' in content_type or 'application/xhtml+xml' in content_type:
```

Benefits:
- Prevents crashes when response lacks text content
- Provides clear error messages when content is missing
- Better debugging information in logs

## Testing Results

Successfully tested with:
```
python detective_agent.py --objective "Find name artifacts around Vitalik Buterin" --max-iterations 1
```

The logs now show:
- Detailed debug information for LLM responses
- Better validation of URLs and responses
- Proper error handling for edge cases

These improvements make the system more robust against invalid inputs and provide better debugging information for troubleshooting.