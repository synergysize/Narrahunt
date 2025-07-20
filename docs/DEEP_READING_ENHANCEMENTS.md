# Deep Reading Enhancements for Detective Agent

This enhancement adds deep content reading capabilities to the detective agent, enabling it to extract more information from forum sites, blogs, and documentation.

## Enhancements Added

1. **Site Type Detection**
   - Added `_detect_site_type(url, html_content)` method to classify websites into different categories:
     - Forums (e.g., BitcoinTalk, Reddit)
     - Blogs (e.g., Medium, sites with '/blog' in URL)
     - Documentation sites
     - Personal sites
     - Generic sites

2. **Deep Forum Investigation**
   - Added `_investigate_forum_deeply(url, html_content)` method to:
     - Extract thread links from forum pages
     - Follow and analyze up to 3 discussion threads
     - Specific handling for BitcoinTalk and Reddit forums
     - Extract artifacts from thread content

3. **Deep Blog Investigation**
   - Added `_investigate_blog_deeply(url, html_content)` method to:
     - Identify blog post links based on URL patterns
     - Follow and analyze up to 5 blog posts
     - Extract artifacts from each post

4. **Integration with Website Investigation**
   - Modified `_investigate_website()` method to:
     - Detect site type after extracting artifacts from the landing page
     - Call appropriate deep investigation method based on site type
     - Extend discoveries with content from deep investigation

## Benefits

- **More Comprehensive Data Collection**: Agent now reads beyond landing pages to discover artifacts in deeper content
- **Forum-Specific Analysis**: Better handling of discussion threads on forum sites
- **Blog Post Reading**: Systematically explores blog posts to find relevant information
- **Smarter Resource Allocation**: Tailors investigation approach based on site type

## Limitations & Future Work

- Currently handles only BitcoinTalk and Reddit specifically for forums
- Could add documentation-specific deep reading
- Could enhance personal site investigation
- Could implement pagination handling for forums and blogs