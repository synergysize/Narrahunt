# Detective Agent LLM Response Parsing Fix

## Problem

The detective agent was failing to parse the responses from Claude properly. The agent would successfully call the LLM, but all extracted data was empty (0 sources, 0 GitHub targets, etc.), even though logs showed "Successfully received response from Claude."

## Investigation

After examining the code and testing the LLM integration directly, we found:

1. Claude was returning valid JSON, but it was being truncated due to a too low `max_tokens` limit (1000)
2. The `_extract_json` method wasn't recognizing responses that were already valid JSON
3. When the JSON was truncated (missing closing braces/brackets), it failed silently and returned `{}`
4. There was insufficient error logging to diagnose the issue

## Solution

We implemented the following fixes:

### 1. Increased Max Tokens Limit

```python
# Increased from 1000 to 4000
data = {
    "model": "claude-3-sonnet-20240229",
    "max_tokens": 4000,  
    "messages": [
        {"role": "user", "content": prompt}
    ]
}
```

### 2. Better JSON Detection

```python
# Check if the raw text is already valid JSON
try:
    json.loads(text)
    logger.debug("Text is already valid JSON")
    return text.strip()
except:
    logger.debug("Text is not valid JSON on its own, attempting extraction")
```

### 3. JSON Repair Mechanism

Added a new method to repair truncated JSON by closing any unclosed structures:

```python
def _repair_incomplete_json(self, json_text: str) -> str:
    # Count open/close brackets and braces
    open_curly = json_text.count('{')
    close_curly = json_text.count('}')
    open_square = json_text.count('[')
    close_square = json_text.count(']')
    
    # Add missing closing braces/brackets
    repaired = json_text
    
    # Close any unclosed arrays
    for _ in range(open_square - close_square):
        if repaired.rstrip().endswith(','):
            # Remove trailing comma if present
            repaired = repaired.rstrip()[:-1]
        repaired += ']'
        
    # Close any unclosed objects
    for _ in range(open_curly - close_curly):
        if repaired.rstrip().endswith(','):
            # Remove trailing comma if present
            repaired = repaired.rstrip()[:-1]
        repaired += '}'
    
    return repaired
```

### 4. Better Error Logging

```python
# If all else fails, return an empty JSON object
logger.error("Could not extract valid JSON, returning empty object")
# Log a sample of the text to help with debugging
if len(text) > 200:
    logger.debug(f"Text sample (first 100 chars): {text[:100]}")
    logger.debug(f"Text sample (last 100 chars): {text[-100:]}")
else:
    logger.debug(f"Full text: {text}")
```

## Verification

We created test scripts to verify that:

1. Claude now returns complete, non-truncated responses
2. The JSON extraction correctly identifies and parses the responses
3. All expected fields are properly populated

## Files Modified

- `llm_integration.py` - Updated the JSON extraction, added repair mechanism, improved error logging
- Created `test_llm.py` - Test script to verify the fix
- Created `llm_fix_demo.py` - Demo script showing different JSON parsing scenarios
- Created `llm_fix_summary.html` - Visual summary of the issue and solution

## Next Steps

The detective agent should now be able to properly extract and use the research strategies from Claude's responses. This will allow it to generate comprehensive plans for investigation and effectively explore leads.