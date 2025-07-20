# Automatic Discovery Reporting

## Overview

The Narrative Discovery Matrix now includes automatic discovery reporting that generates concise summaries after each research cycle. This feature provides continuous visibility into what the system is discovering, helping to track progress and identify valuable findings.

## Implementation

The automatic discovery reporting is implemented in the `integrated_main.py` file, with the main functionality in the `generate_discovery_summary` method of the `IntegratedController` class.

## Output Format

Each discovery summary includes:

1. **Header**: Timestamp and current objective
2. **Research Stats**:
   - URLs processed
   - Artifacts found
   - High-scoring artifacts
   - Narrative-worthy discoveries
   - Research time

3. **Top Sources**: Most productive domains and page counts

4. **Discovery Highlights**: Top narrative-worthy discoveries with:
   - Name/identifier
   - Score
   - Type
   - Source domain

5. **Next Objectives**: Upcoming objectives in the queue

## Output Locations

The discovery summaries are output to three locations:

1. **Console**: Printed in real-time for immediate monitoring
2. **Session Summaries**: Saved to `results/session_summaries/YYYY-MM-DD-HH-MM.txt`
3. **Discovery Log**: Appended to `results/discovery_log.txt` for historical tracking

## When Summaries Are Generated

Summaries are automatically generated:

1. After each objective is completed in `run_with_objective`
2. After each objective in the autonomous mode in `run_autonomous`

## Customization

The summary format can be customized by modifying the `generate_discovery_summary` method in `integrated_main.py`. Some possible customizations:

- Adjust the number of top sources shown
- Change the number of discovery highlights included
- Add or remove sections from the summary
- Modify the formatting of discovery entries

## Example Usage

To see automatic discovery reporting in action:

1. Run a single objective:
   ```
   python integrated_main.py --objective "Find name artifacts around Vitalik Buterin"
   ```

2. Run in autonomous mode:
   ```
   python integrated_main.py --auto
   ```

3. Run the demo:
   ```
   python demo_auto_reporting.py
   ```

## Example Output

```
=== DISCOVERY SUMMARY: 2025-07-15-11-42 ===
Objective: Find name artifacts around Vitalik Buterin

Research Stats:
- URLs processed: 47
- Artifacts found: 12
- High-scoring artifacts: 8
- Narrative-worthy discoveries: 5
- Research time: 15.70 minutes

Top Sources:
- github.com: 18 pages
- web.archive.org: 12 pages
- bitcointalk.org: 7 pages
- vitalik.ca: 5 pages
- ethereum.org: 3 pages

Discovery Highlights:
- Colored Coins: Score 0.89 | Type: project_name | Source: vitalik.ca
- Ethereum Whitepaper: Score 0.92 | Type: document_name | Source: web.archive.org
- vitalik_btc: Score 0.95 | Type: username | Source: bitcointalk.org
- Frontier: Score 0.93 | Type: project_name | Source: ethereum.org

Next Objectives in Queue:
- Find wallet artifacts around Vitalik Buterin
- Find code artifacts around Ethereum Foundation
- Find name artifacts around Gavin Wood
```