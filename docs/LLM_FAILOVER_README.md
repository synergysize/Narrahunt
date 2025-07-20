# LLM Failover Fix

## Problem
When Claude returns a 401 error, `llm_integration._call_claude()` returns "{}" but detective_agent never knows to try OpenAI.

## Solution
We've implemented a dual-layer failover approach:

1. **Higher-level failover in detective_agent.py**:
   - Detect empty or "{}" responses from Claude
   - Automatically try OpenAI as backup
   - Log the failover

2. **Lower-level failover in llm_integration.py**:
   - Detect 401 authentication errors in Claude
   - Automatically fall back to OpenAI
   - Log the automatic failover

3. **Updated API key**:
   - Added the new Anthropic API key as a fallback

## How to Apply the Fix

### Fix 1: Update llm_integration.py

Add 401 error detection and automatic fallover in `_call_claude()`:

```python
if response.status_code == 200:
    # ... existing code ...
    return content
elif response.status_code == 401:
    logger.warning(f"Claude authentication failed (401) - automatically falling back to OpenAI")
    # If we have OpenAI access, use it as fallback
    if self.openai_api_key:
        return self._call_openai(prompt)
    else:
        logger.error("No OpenAI API key available for fallback")
        return "{}"
else:
    logger.error(f"Claude API error: {response.status_code} - {response.text}")
    return "{}"
```

Also update the API key:

```python
CLAUDE_API_KEY = get_api_key('CLAUDE_API_KEY') or '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'
```

### Fix 2: Update detective_agent.py

Modify all LLM call sections to add failover logic:

```python
if llm.use_claude:
    result = llm._call_claude(prompt)
    # If Claude fails, try OpenAI as backup
    if not result or result.strip() == "{}":
        logger.warning("Claude failed, trying OpenAI as backup")
        backup_llm = LLMIntegration(use_claude=False, use_openai=True)
        result = backup_llm._call_openai(prompt)
elif llm.use_openai:
    result = llm._call_openai(prompt)
```

Apply this pattern to:
- `_get_initial_research_strategy()`
- `_consult_llm_for_next_steps()`
- `_generate_new_leads()`

## Testing

You can test the failover mechanism using the provided `llm_failover.py` script, which implements the same pattern in a simpler context.

```bash
python llm_failover.py
```

This will attempt to call Claude first and then fall back to OpenAI if Claude fails.

## Conclusion

With these changes, the detective agent will automatically switch to OpenAI when Claude fails, ensuring that the investigation continues smoothly even when one LLM service is unavailable.