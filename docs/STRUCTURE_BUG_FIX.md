# Detective Agent Structure Bug Fix

## Problem

The detective agent's `_initialize_research()` method was failing to properly process the structured response from the LLM. When the LLM returned a more detailed structure (dictionaries with URLs and metadata instead of simple URL strings), the agent couldn't extract the URLs correctly.

## Bug Details

In `detective_agent.py`, the code was trying to treat dictionary objects as strings when extracting domains and validating URLs:

```python
# Original buggy code
for source in initial_strategy.get('sources', []):
    if self._is_valid_url(source):  # Bug: source might be a dict, not a string
        domain = self._extract_domain(source)  # Bug: source might be a dict, not a string
        # ...
```

The issue occurred because the LLM response format had evolved to be more detailed:

```python
# Old LLM response format (simple strings)
{
    "sources": ["https://vitalik.ca", "https://ethereum.org"]
}

# New LLM response format (dictionaries with metadata)
{
    "sources": [
        {
            "url": "https://vitalik.ca",
            "priority": 10,
            "rationale": "Primary personal blog with technical writings"
        }
    ]
}
```

But the code that processed this response hadn't been updated to handle the new structure.

## Fix

Updated all sections in `_initialize_research()` to properly handle both formats:

1. **Sources Section**:
   ```python
   # Extract URL from source dictionary or use directly if it's a string
   url = source.get('url') if isinstance(source, dict) else source
   
   if self._is_valid_url(url):
       # Use priority from source if available
       priority = source.get('priority', 10) if isinstance(source, dict) else 10
       # ...
   ```

2. **GitHub Repositories Section**:
   ```python
   # Extract URL from repo dictionary or use directly if it's a string
   url = repo.get('url') if isinstance(repo, dict) else repo
   
   if self._is_valid_url(url):
       # ...
   ```

3. **Wayback Targets Section**:
   ```python
   # Extract URL from wayback_target dictionary or use directly if it's a string
   url = wayback_target.get('url') if isinstance(wayback_target, dict) else wayback_target
   
   if self._is_valid_url(url):
       # ...
   ```

4. **Search Queries Section**:
   ```python
   # Extract query from search_item dictionary or use directly if it's a string
   query = search_item.get('query') if isinstance(search_item, dict) else search_item
   
   if query:
       # ...
   ```

## Benefits of the Fix

1. **Backward Compatibility**: The agent now handles both the old format (simple strings) and the new format (dictionaries with metadata).

2. **Better Metadata Use**: The agent now properly extracts and uses additional metadata provided by the LLM:
   - Priority ratings for better targeting
   - Rationales for better logging and understanding
   - Year ranges for more targeted Wayback Machine searches

3. **More Robust**: Added null checks and type checking to prevent similar errors in the future.

## Testing

The fix was verified by checking that the code can handle both formats:
- Simple strings (old format)
- Dictionaries with metadata (new format)

## Next Steps

With this fix in place, the detective agent should now be able to properly process the more detailed research strategies from the LLM, enabling more effective and prioritized investigations.