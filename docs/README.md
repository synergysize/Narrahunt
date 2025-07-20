# Narrative Discovery Matrix System

A system that autonomously generates and manages research objectives to discover narratives around various entities and artifact types.

## System Overview

The Narrative Discovery Matrix system generates research objectives by combining different artifact types (code, wallet, personal info, etc.) with target entities (crypto developers, institutions, etc.). It then tracks the progress of each objective, auto-generates follow-up objectives, and organizes narrative-worthy findings.

### Components

1. **Narrative Matrix** (`narrative_matrix.py`)
   - Defines artifact types and target entities
   - Generates objective combinations
   - Tracks objective progress
   - Records discoveries and identifies narrative-worthy findings

2. **Objectives Manager** (`objectives_manager.py`)
   - Loads current objectives from the matrix
   - Executes research using existing crawler and LLM integration
   - Detects when objectives hit dead ends
   - Auto-generates related objectives based on discoveries
   - Moves to the next matrix combination when the current one is exhausted

## Directory Structure

```
/narrahunt_phase2/
├── config/
│   └── narrative_matrix.json      # Matrix configuration
├── results/
│   ├── current_objective.txt      # Current active objective
│   ├── completed_objectives/      # Archive of completed objectives
│   └── narratives/                # Narrative-worthy findings
├── logs/                          # System logs
├── backup/                        # Backup directory
├── narrative_matrix.py            # Matrix implementation
├── objectives_manager.py          # Objectives manager implementation
├── test_system.py                 # Test script
└── README.md                      # This documentation
```

## Usage

1. **Run the test script** to verify the system is working:
   ```
   python test_system.py
   ```

2. **Start autonomous operation** by running the objectives manager:
   ```
   python objectives_manager.py
   ```

3. **Check results** in the `results/narratives/` directory for narrative-worthy findings.

## Configuration

The system can be configured by editing the `config/narrative_matrix.json` file. You can:

- Add new artifact types
- Add new target entities
- Customize objective templates
- Adjust progress thresholds

## Integration

The system is designed to integrate with:
- Existing crawler modules
- LLM analysis tools
- Other research tools

It automatically tries to find and load these modules from the project directory.

## Expansion

The system automatically expands its knowledge by:
- Adding new entities discovered during research
- Adding new artifact types identified in findings
- Generating follow-up objectives based on relationships