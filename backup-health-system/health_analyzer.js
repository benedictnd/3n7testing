/**
 * Health and Recovery System Analyzer
 * 
 * This utility analyzes keywords entered by coaches regarding athlete discomfort or injuries
 * and provides relevant information about the type of fatigue or injury.
 */

class HealthAnalyzer {
    constructor(healthSystemData) {
        this.healthData = healthSystemData;
        this.initialized = false;
    }

    /**
     * Initialize the analyzer with health system data
     * @param {string|object} data - Health system data as JSON string or object
     * @returns {boolean} - Success status
     */
    async initialize(data = null) {
        try {
            if (data) {
                if (typeof data === 'string') {
                    this.healthData = JSON.parse(data);
                } else {
                    this.healthData = data;
                }
            } else if (!this.healthData) {
                // Load from default location if no data provided
                const response = await fetch('/backup-health-system/health_system.json');
                this.healthData = await response.json();
            }
            
            this.initialized = true;
            console.log('Health Analyzer initialized successfully');
            return true;
        } catch (error) {
            console.error('Failed to initialize Health Analyzer:', error);
            return false;
        }
    }

    /**
     * Analyze keywords to identify potential fatigue issues
     * @param {string} keywords - Space-separated keywords describing athlete's condition
     * @returns {object} - Analysis results for fatigue
     */
    analyzeFatigue(keywords) {
        if (!this.initialized) {
            throw new Error('Health Analyzer not initialized. Call initialize() first.');
        }

        const keywordList = keywords.toLowerCase().split(/[\s,]+/);
        const results = [];
        
        // Check for matching keywords in fatigue types
        for (const fatigueType in this.healthData.fatigueTypes) {
            const fatigue = this.healthData.fatigueTypes[fatigueType];
            const matchedKeywords = [];
            
            // Check if any keywords match this fatigue type's keywords
            fatigue.keywords.forEach(keyword => {
                keywordList.forEach(inputKeyword => {
                    if (keyword.toLowerCase().includes(inputKeyword) || 
                        inputKeyword.includes(keyword.toLowerCase())) {
                        if (!matchedKeywords.includes(keyword)) {
                            matchedKeywords.push(keyword);
                        }
                    }
                });
            });
            
            // If we found matches, add this fatigue type to results
            if (matchedKeywords.length > 0) {
                results.push({
                    id: fatigue.id,
                    name: fatigue.name,
                    description: fatigue.description,
                    causes: fatigue.causes,
                    symptoms: fatigue.symptoms,
                    matchedKeywords: matchedKeywords,
                    matchStrength: matchedKeywords.length / fatigue.keywords.length
                });
            }
        }
        
        // Also check the direct keyword mapping
        this.healthData.keywords.fatigue.forEach(mapping => {
            keywordList.forEach(inputKeyword => {
                if (mapping.keyword.toLowerCase().includes(inputKeyword) || 
                    inputKeyword.includes(mapping.keyword.toLowerCase())) {
                    
                    // Check if we already have this fatigue type in results
                    const existingResult = results.find(r => 
                        r.name === this.healthData.fatigueTypes[mapping.type].name);
                    
                    if (!existingResult) {
                        const fatigue = this.healthData.fatigueTypes[mapping.type];
                        results.push({
                            id: fatigue.id,
                            name: fatigue.name,
                            description: fatigue.description,
                            causes: fatigue.causes,
                            symptoms: fatigue.symptoms,
                            matchedKeywords: [mapping.keyword],
                            matchStrength: 1 / fatigue.keywords.length
                        });
                    } else {
                        // Update matched keywords if not already included
                        if (!existingResult.matchedKeywords.includes(mapping.keyword)) {
                            existingResult.matchedKeywords.push(mapping.keyword);
                            existingResult.matchStrength = existingResult.matchedKeywords.length / 
                                this.healthData.fatigueTypes[mapping.type].keywords.length;
                        }
                    }
                }
            });
        });
        
        // Sort results by match strength
        results.sort((a, b) => b.matchStrength - a.matchStrength);
        
        return {
            type: 'fatigue',
            query: keywords,
            results: results,
            managementStrategies: results.length > 0 ? this.getRelevantManagementStrategies(results) : []
        };
    }
    
    /**
     * Analyze keywords to identify potential injury issues
     * @param {string} keywords - Space-separated keywords describing athlete's condition
     * @returns {object} - Analysis results for injuries
     */
    analyzeInjury(keywords) {
        if (!this.initialized) {
            throw new Error('Health Analyzer not initialized. Call initialize() first.');
        }
        
        const keywordList = keywords.toLowerCase().split(/[\s,]+/);
        const results = [];
        
        // Check each body location for potential injuries
        for (const locationKey in this.healthData.injuryTypes) {
            const location = this.healthData.injuryTypes[locationKey];
            
            location.commonInjuries.forEach(injury => {
                const matchedKeywords = [];
                
                // Check if any keywords match this injury's keywords
                injury.keywords.forEach(keyword => {
                    keywordList.forEach(inputKeyword => {
                        if (keyword.toLowerCase().includes(inputKeyword) || 
                            inputKeyword.includes(keyword.toLowerCase())) {
                            if (!matchedKeywords.includes(keyword)) {
                                matchedKeywords.push(keyword);
                            }
                        }
                    });
                });
                
                // If we found matches, add this injury to results
                if (matchedKeywords.length > 0) {
                    results.push({
                        location: location.name,
                        injury: injury.name,
                        description: location.description,
                        symptoms: injury.symptoms,
                        matchedKeywords: matchedKeywords,
                        matchStrength: matchedKeywords.length / injury.keywords.length
                    });
                }
            });
        }
        
        // Also check the direct keyword mapping
        this.healthData.keywords.injuries.forEach(mapping => {
            keywordList.forEach(inputKeyword => {
                if (mapping.keyword.toLowerCase().includes(inputKeyword) || 
                    inputKeyword.includes(mapping.keyword.toLowerCase())) {
                    
                    const location = this.healthData.injuryTypes[mapping.location];
                    
                    // Find the most relevant injury in this location based on the keyword
                    let bestMatch = null;
                    let bestMatchStrength = 0;
                    
                    location.commonInjuries.forEach(injury => {
                        const keywordMatches = injury.keywords.filter(keyword => 
                            keyword.toLowerCase().includes(inputKeyword) || 
                            inputKeyword.includes(keyword.toLowerCase()));
                        
                        if (keywordMatches.length > bestMatchStrength) {
                            bestMatch = injury;
                            bestMatchStrength = keywordMatches.length;
                        }
                    });
                    
                    if (bestMatch) {
                        // Check if we already have this injury in results
                        const existingResult = results.find(r => 
                            r.location === location.name && r.injury === bestMatch.name);
                        
                        if (!existingResult) {
                            results.push({
                                location: location.name,
                                injury: bestMatch.name,
                                description: location.description,
                                symptoms: bestMatch.symptoms,
                                matchedKeywords: [mapping.keyword],
                                matchStrength: bestMatchStrength / bestMatch.keywords.length
                            });
                        } else {
                            // Update matched keywords if not already included
                            if (!existingResult.matchedKeywords.includes(mapping.keyword)) {
                                existingResult.matchedKeywords.push(mapping.keyword);
                                existingResult.matchStrength = existingResult.matchedKeywords.length / 
                                    bestMatch.keywords.length;
                            }
                        }
                    } else {
                        // No specific injury matched, just add the location
                        results.push({
                            location: location.name,
                            injury: "Unspecified injury",
                            description: location.description,
                            symptoms: ["Pain", "Discomfort"],
                            matchedKeywords: [mapping.keyword],
                            matchStrength: 0.5 // Medium confidence without specific injury match
                        });
                    }
                }
            });
        });
        
        // Sort results by match strength
        results.sort((a, b) => b.matchStrength - a.matchStrength);
        
        return {
            type: 'injury',
            query: keywords,
            results: results
        };
    }
    
    /**
     * Get relevant management strategies based on fatigue analysis results
     * @param {Array} fatigueResults - Results from fatigue analysis
     * @returns {Array} - Relevant management strategies
     */
    getRelevantManagementStrategies(fatigueResults) {
        if (fatigueResults.length === 0) return [];
        
        const strategies = [];
        
        // Map fatigue types to relevant management strategies
        const strategyMapping = {
            "A": ["activeRecovery", "adequateSleep", "periodization"],
            "B": ["adequateSleep", "activeRecovery"],
            "C": ["nutritionAndHydration"],
            "D": ["activeRecovery", "periodization"],
            "E": ["mentalTraining", "psychologicalSupport"],
            "F": ["nutritionAndHydration", "periodization"],
            "G": ["mentalTraining", "periodization"]
        };
        
        // Get top 3 fatigue results
        const topResults = fatigueResults.slice(0, 3);
        
        // Add relevant strategies for each top result
        topResults.forEach(result => {
            if (strategyMapping[result.id]) {
                strategyMapping[result.id].forEach(strategyKey => {
                    const strategy = this.healthData.managementStrategies[strategyKey];
                    
                    // Check if this strategy is already added
                    const existingStrategy = strategies.find(s => s.name === strategy.name);
                    if (!existingStrategy) {
                        strategies.push({
                            name: strategy.name,
                            description: strategy.description,
                            recommendations: strategy.recommendations
                        });
                    }
                });
            }
        });
        
        return strategies;
    }
    
    /**
     * Perform a comprehensive health analysis for both fatigue and injuries
     * @param {string} keywords - Space-separated keywords describing athlete's condition
     * @returns {object} - Combined analysis results
     */
    analyze(keywords) {
        if (!this.initialized) {
            throw new Error('Health Analyzer not initialized. Call initialize() first.');
        }
        
        const fatigueResults = this.analyzeFatigue(keywords);
        const injuryResults = this.analyzeInjury(keywords);
        
        return {
            query: keywords,
            fatigueAnalysis: fatigueResults,
            injuryAnalysis: injuryResults,
            primaryConcern: fatigueResults.results.length > 0 && 
                           (injuryResults.results.length === 0 || 
                            fatigueResults.results[0].matchStrength > injuryResults.results[0].matchStrength) 
                           ? 'fatigue' : 'injury'
        };
    }
}

// Export for use in frontend applications
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = HealthAnalyzer;
} else {
    window.HealthAnalyzer = HealthAnalyzer;
}
