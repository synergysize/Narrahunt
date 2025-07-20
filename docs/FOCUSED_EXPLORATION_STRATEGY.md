# Focused Exploration Strategy for Detective Agent

## Overview

This document describes the implementation of a Focused Exploration Strategy for the Detective Agent. The strategy shifts the agent from a scattered, breadth-first approach to a methodical, depth-first exploration pattern. This change significantly improves the quality and depth of artifacts discovered during an investigation.

## Key Components

### 1. ResearchStrategy Class

A new `ResearchStrategy` class has been implemented in `research_strategy.py` to manage the investigation targets and priorities. This class:

- Maintains a prioritized list of all investigation targets
- Tracks completed targets and their discoveries
- Collects leads discovered during investigation without immediately pursuing them
- Enables methodical exploration by focusing on one target at a time
- Periodically re-evaluates and reprioritizes targets based on discoveries

### 2. Core Detective Agent Changes

The `DetectiveAgent` class has been updated to use the `ResearchStrategy`:

- Replaced the simple research queue with the comprehensive `ResearchStrategy`
- Updated the initial research phase to create a complete TODO list
- Modified the main investigation loop to follow a depth-first approach
- Added lead extraction that notes discoveries without immediately pursuing them
- Implemented periodic strategy reviews to keep the investigation on track

### 3. Comprehensive Initial Strategy

The strategy initialization now:

- Prompts the LLM to create a comprehensive TODO list of ALL potential targets
- Assigns priority ratings (1-10) to each target
- Includes rationales for each target's investigation
- Covers multiple target types: websites, GitHub repos, forums, archives, etc.
- Documents potential artifacts that might be found in each target

### 4. Depth-First Investigation Process

The investigation process now follows these steps:

1. Generate a comprehensive prioritized TODO list at the start
2. Pick the highest priority target
3. Thoroughly investigate that target until completion
4. Note any discovered leads but don't pursue them immediately
5. Mark the target as complete and move to the next highest priority
6. Periodically process discovered leads and update priorities
7. Regularly review the overall strategy with the LLM

## Implementation Details

### New Files

- `research_strategy.py`: The core implementation of the focused exploration strategy
- `tests/test_focused_strategy.py`: Unit tests for the new strategy implementation
- `docs/FOCUSED_EXPLORATION_STRATEGY.md`: This documentation file

### Modified Files

- `detective_agent.py`: Updated to integrate the focused exploration strategy

### Key Methods Added

- `ResearchStrategy.add_target()`: Add a target to the master todo list
- `ResearchStrategy.get_next_target()`: Get the highest priority target
- `ResearchStrategy.mark_target_complete()`: Mark a target as completed
- `ResearchStrategy.add_discovered_lead()`: Add a lead discovered during investigation
- `ResearchStrategy.process_discovered_leads()`: Process collected leads
- `ResearchStrategy.update_priorities()`: Update priorities based on discoveries
- `DetectiveAgent._extract_leads_from_discovery()`: Extract potential leads from discoveries
- `DetectiveAgent._review_research_strategy()`: Perform a comprehensive strategy review

## Benefits

1. **Thoroughness**: Exhaustively investigates high-value targets instead of skipping around
2. **Depth**: Focuses on a single target until it's fully explored
3. **Organization**: Maintains a clear, prioritized list of all investigation targets
4. **Strategic**: Periodically reassesses priorities based on discoveries
5. **Efficiency**: Reduces redundant work and focuses on the most promising leads

## Example Flow

1. LLM generates comprehensive TODO list with all potential targets
2. Agent investigates highest priority target (e.g., GitHub profile) completely
3. During investigation, agent notes URLs, references, and other leads
4. After completing the GitHub profile investigation, agent adds discovered leads to TODO list
5. Agent reviews and updates strategy priorities
6. Agent moves to next highest priority target (e.g., personal blog)
7. Process repeats, building a more comprehensive understanding

## Testing

The implementation includes comprehensive unit tests that verify:

1. Adding targets to the strategy
2. Getting targets in priority order
3. Marking targets as complete
4. Adding and processing discovered leads
5. Updating priorities
6. Integration with the Detective Agent

## Future Improvements

Potential enhancements to the focused exploration strategy:

1. Learning from success/failure patterns to auto-adjust priorities
2. More sophisticated lead scoring based on previous discoveries
3. Automatic detection of investigation completion for each target type
4. Visualization of the exploration strategy and progress
5. Parallel investigation of independent targets to improve efficiency