# URL Deduplication Fix for Detective Agent

## Problem

The detective agent was experiencing a critical bug causing URL explosion due to ineffective deduplication. This resulted in hundreds of duplicate URLs in the research queue, particularly from sites like Reddit. This issue caused:

1. Wasteful processing of the same content multiple times
2. Excessive API calls and bandwidth usage
3. Skewed research priorities due to queue flooding
4. Memory usage and performance issues

## Solution

The following enhancements were implemented to fix the URL explosion issue:

### 1. Added `_extract_same_domain_links` Method

Created a new method that efficiently extracts unique links from the same domain:
- Uses BeautifulSoup for more reliable link extraction instead of simple regex
- Stores links in a set to automatically eliminate duplicates
- Limits the number of links returned to 5 per page to prevent explosion
- Only returns links that haven't already been investigated

### 2. Added `_normalize_url_for_deduplication` Method

Created a URL normalization function to identify when different URL formats point to the same content:
- Removes query parameters (e.g., `?sort=new` vs `?sort=hot`)
- Removes URL fragments (e.g., `#comments` vs `#replies`)
- Removes trailing slashes (e.g., `/blog/` vs `/blog`)
- Converts to lowercase to handle case differences
- Preserves domain and path for accurate content identification

### 3. Enhanced `_update_research_queue` Method

Improved the research queue update method to prevent duplicate targets:
- Added target ID tracking to efficiently identify duplicates
- Added normalized URL tracking to prevent adding the same URL in different formats
- Added extra logging to show how many duplicates were filtered
- Automatically generates target IDs for targets that don't have them

### 4. Improved Forum and Blog Investigation

Updated both forum and blog investigation methods to use the same deduplication techniques:
- Normalized URLs before investigating threads/posts
- Used sets to track unique URLs
- Limited the number of threads/posts to investigate

## Benefits

1. **Reduced Queue Size**: Prevents the research queue from being flooded with duplicate URLs
2. **Resource Efficiency**: Avoids wasting resources on investigating the same content multiple times
3. **Better Focus**: Improves research efficiency by exploring a more diverse set of content
4. **Cleaner Logs**: Makes investigation logs more readable by removing duplicate entries

## Technical Details

The URL normalization technique handles common patterns that caused duplicates:
- `https://reddit.com/r/ethereum` vs `https://reddit.com/r/ethereum/`
- `https://bitcointalk.org/index.php?topic=1234` vs `https://bitcointalk.org/index.php?topic=1234&page=2`
- `https://medium.com/blog/post` vs `https://medium.com/blog/post#responses`

The implementation focuses on efficient lookup using sets for O(1) membership testing, which scales well with large numbers of URLs.