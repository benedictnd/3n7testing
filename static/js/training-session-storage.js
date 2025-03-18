/**
 * Training Session Storage Utility
 * Handles persisting training session data to localStorage
 * and synchronizing with the server when online
 */

class TrainingSessionStorage {
    constructor() {
        this.storageKey = '3and7_pending_training_sessions';
        this.serverEndpoint = '/api/training-sessions';
        this.isOnline = navigator.onLine;
        
        // Set up online/offline event listeners
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.syncPendingSessions();
        });
        
        window.addEventListener('offline', () => {
            this.isOnline = false;
        });
    }
    
    /**
     * Save a training session
     * @param {Object} sessionData - Training session data
     * @returns {Promise<Object>} - Result of save operation
     */
    async saveSession(sessionData) {
        try {
            // Add timestamp and status
            const enhancedSessionData = {
                ...sessionData,
                createdAt: new Date().toISOString(),
                status: 'pending'
            };
            
            // Try to save to server if online
            if (this.isOnline) {
                try {
                    const response = await fetch(this.serverEndpoint, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${this.getAuthToken()}`
                        },
                        body: JSON.stringify(enhancedSessionData)
                    });
                    
                    if (response.ok) {
                        const savedSession = await response.json();
                        return {
                            success: true,
                            message: 'Training session saved to server',
                            data: savedSession
                        };
                    } else {
                        // Save to local storage if server request fails
                        this.saveToLocalStorage(enhancedSessionData);
                        return {
                            success: true,
                            message: 'Server error. Training session saved locally and will sync when possible.',
                            data: enhancedSessionData
                        };
                    }
                } catch (error) {
                    // Save to local storage if fetch fails
                    this.saveToLocalStorage(enhancedSessionData);
                    return {
                        success: true,
                        message: 'Network error. Training session saved locally and will sync when possible.',
                        data: enhancedSessionData
                    };
                }
            } else {
                // Save to local storage if offline
                this.saveToLocalStorage(enhancedSessionData);
                return {
                    success: true,
                    message: 'You are offline. Training session saved locally and will sync when online.',
                    data: enhancedSessionData
                };
            }
        } catch (error) {
            console.error('Error saving training session:', error);
            return {
                success: false,
                message: 'Failed to save training session: ' + error.message
            };
        }
    }
    
    /**
     * Save session data to localStorage
     * @param {Object} sessionData - Training session data
     */
    saveToLocalStorage(sessionData) {
        const pendingSessions = this.getPendingSessions();
        pendingSessions.push(sessionData);
        localStorage.setItem(this.storageKey, JSON.stringify(pendingSessions));
    }
    
    /**
     * Get all pending sessions from localStorage
     * @returns {Array} - Array of pending sessions
     */
    getPendingSessions() {
        const savedSessions = localStorage.getItem(this.storageKey);
        return savedSessions ? JSON.parse(savedSessions) : [];
    }
    
    /**
     * Sync all pending sessions with the server
     * @returns {Promise<Object>} - Result of sync operation
     */
    async syncPendingSessions() {
        if (!this.isOnline) {
            return {
                success: false,
                message: 'Cannot sync while offline'
            };
        }
        
        const pendingSessions = this.getPendingSessions();
        if (pendingSessions.length === 0) {
            return {
                success: true,
                message: 'No pending sessions to sync'
            };
        }
        
        const results = {
            success: true,
            syncedCount: 0,
            failedCount: 0,
            message: ''
        };
        
        // Create a new array for sessions that fail to sync
        const stillPendingSessions = [];
        
        // Try to sync each session
        for (const session of pendingSessions) {
            try {
                const response = await fetch(this.serverEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${this.getAuthToken()}`
                    },
                    body: JSON.stringify(session)
                });
                
                if (response.ok) {
                    results.syncedCount++;
                } else {
                    results.failedCount++;
                    stillPendingSessions.push(session);
                }
            } catch (error) {
                results.failedCount++;
                stillPendingSessions.push(session);
            }
        }
        
        // Update localStorage with any sessions that failed to sync
        localStorage.setItem(this.storageKey, JSON.stringify(stillPendingSessions));
        
        // Generate result message
        results.message = `Synced ${results.syncedCount} sessions. ${results.failedCount} failed to sync.`;
        
        return results;
    }
    
    /**
     * Get authentication token from localStorage
     * @returns {string} - Authentication token
     */
    getAuthToken() {
        return localStorage.getItem('auth_token') || '';
    }
    
    /**
     * Clear all pending sessions
     */
    clearPendingSessions() {
        localStorage.removeItem(this.storageKey);
    }
}

// Create global instance
const trainingSessionStorage = new TrainingSessionStorage();
