# Athlete Recovery and Health System

## Overview
The Athlete Recovery and Health System is designed to help coaches identify and manage athlete fatigue and injuries based on keywords. When coaches observe or receive feedback about athlete discomfort, they can enter simple keywords into the system, which will then provide analysis on the type of fatigue or injury the athlete might be experiencing.

## System Components

### 1. Health System Data (health_system.json)
This JSON file contains comprehensive data on:
- **Fatigue Types**: Seven categories of fatigue with their causes, symptoms, and associated keywords
- **Injury Types**: Common sports injuries categorized by body location
- **Management Strategies**: Six approaches to help athletes recover from fatigue
- **Keyword Mappings**: Associative arrays that map common terms to fatigue types or injury locations

### 2. Health Analyzer (health_analyzer.js)
A JavaScript utility that:
- Analyzes keywords to identify potential fatigue issues
- Analyzes keywords to identify potential injuries
- Recommends relevant management strategies based on analysis results
- Provides match confidence scores

### 3. Web Interface (recovery-analyzer.html)
An interactive web page that allows coaches to:
- Enter keywords describing athlete discomfort
- View analysis results for both fatigue and injury types
- See recommended management strategies
- Use sample keywords for quick testing

## How to Use

1. Open the `recovery-analyzer.html` file in a web browser
2. Enter keywords describing the athlete's discomfort in the search box
3. Click "Analyze" or press Enter
4. Review the analysis results:
   - Fatigue Analysis: Shows potential fatigue types with causes and symptoms
   - Injury Analysis: Shows potential injuries with symptoms
   - Management Strategies: Recommended approaches for recovery

## Integration with Training System

This system is designed to be integrated with the post-training feedback section of the integrated training system. When coaches note athlete discomfort, they can:

1. Enter the relevant keywords
2. Review the analysis
3. Document the appropriate intervention in the athlete's training plan
4. Monitor progress through subsequent feedback sessions

## Data Sources

The health and recovery data is based on scientific literature including:
- Calder, A. (2007). Canadian sport for life: Recovery and regeneration
- American Academy of Pediatrics (2018). Extreme temperatures: Heat and cold
- HCA Healthcare UK (2024). Sports fatigue
- National Institute of Arthritis and Musculoskeletal and Skin Diseases (2024). Sports injuries

## Future Enhancements

- Integration with athlete historical data for personalized analysis
- Machine learning capabilities to improve keyword matching over time
- Mobile application for on-the-field assessment
- Wearable device integration for real-time monitoring
