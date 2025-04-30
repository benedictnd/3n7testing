/**
 * Drills Library System for 3&7 Integrated Training System
 * Handles saved drills management, including storage, retrieval, and manipulation
 */

// Initialize drills library from localStorage or use default empty structure
let drillsLibrary = JSON.parse(localStorage.getItem('drillsLibrary')) || {
    saved_drills: []
};

// Save drills library to localStorage
function saveDrillsLibrary() {
    localStorage.setItem('drillsLibrary', JSON.stringify(drillsLibrary));
}

// Add a new drill to the library
function addDrill(name, category, defaultTime) {
    // Check for duplicates
    const existingDrill = drillsLibrary.saved_drills.find(
        drill => drill.name.toLowerCase() === name.toLowerCase() && drill.category === category
    );
    
    if (existingDrill) {
        return { success: false, message: "This drill already exists. Edit or use the existing one." };
    }
    
    // Create new drill object
    const newDrill = {
        id: "DRILL_" + Date.now(),
        name: name,
        category: category,
        default_time: defaultTime,
        last_used: new Date().toISOString().split('T')[0]
    };
    
    // Add to library
    drillsLibrary.saved_drills.push(newDrill);
    saveDrillsLibrary();
    
    return { success: true, drill: newDrill };
}

// Edit an existing drill
function editDrill(id, newName, newCategory, newDefaultTime) {
    const drillIndex = drillsLibrary.saved_drills.findIndex(drill => drill.id === id);
    
    if (drillIndex === -1) {
        return { success: false, message: "Drill not found." };
    }
    
    // Check for duplicates (except the current drill)
    const duplicateDrill = drillsLibrary.saved_drills.find(
        drill => drill.name.toLowerCase() === newName.toLowerCase() && 
                drill.category === newCategory && 
                drill.id !== id
    );
    
    if (duplicateDrill) {
        return { success: false, message: "Another drill with this name already exists." };
    }
    
    // Update drill
    drillsLibrary.saved_drills[drillIndex].name = newName;
    drillsLibrary.saved_drills[drillIndex].category = newCategory;
    drillsLibrary.saved_drills[drillIndex].default_time = newDefaultTime;
    
    saveDrillsLibrary();
    
    return { success: true, drill: drillsLibrary.saved_drills[drillIndex] };
}

// Delete a drill
function deleteDrill(id) {
    const initialLength = drillsLibrary.saved_drills.length;
    drillsLibrary.saved_drills = drillsLibrary.saved_drills.filter(drill => drill.id !== id);
    
    if (drillsLibrary.saved_drills.length < initialLength) {
        saveDrillsLibrary();
        return { success: true };
    } else {
        return { success: false, message: "Drill not found." };
    }
}

// Get all drills
function getAllDrills() {
    return drillsLibrary.saved_drills;
}

// Get drills by category
function getDrillsByCategory(category) {
    return drillsLibrary.saved_drills.filter(drill => drill.category === category);
}

// Get most used drills (top 5)
function getMostUsedDrills() {
    // Sort by last_used date (most recent first)
    return [...drillsLibrary.saved_drills]
        .sort((a, b) => new Date(b.last_used) - new Date(a.last_used))
        .slice(0, 5);
}

// Search drills by name (case-insensitive, partial match)
function searchDrills(query, category = null) {
    if (!query) {
        return category ? getDrillsByCategory(category) : getAllDrills();
    }
    
    query = query.toLowerCase();
    
    return drillsLibrary.saved_drills.filter(drill => {
        const nameMatch = drill.name.toLowerCase().includes(query);
        const categoryMatch = !category || drill.category === category;
        return nameMatch && categoryMatch;
    });
}

// Update last used date when a drill is selected
function updateDrillUsage(id) {
    const drill = drillsLibrary.saved_drills.find(drill => drill.id === id);
    if (drill) {
        drill.last_used = new Date().toISOString().split('T')[0];
        saveDrillsLibrary();
    }
}

// Add some sample drills if library is empty (for demo purposes)
function initializeSampleDrills() {
    if (drillsLibrary.saved_drills.length === 0) {
        const sampleDrills = [
            { name: "5 Spots (3 Point)", category: "Main", default_time: "20" },
            { name: "3v3 Attack-to-Defense", category: "Main", default_time: "25" },
            { name: "Triangle Passing", category: "Warm-Up", default_time: "15" },
            { name: "High-Intensity Intervals", category: "Main", default_time: "30" },
            { name: "Dynamic Stretching", category: "Warm-Up", default_time: "15" },
            { name: "Static Stretching", category: "Cool-Down", default_time: "10" },
            { name: "Cool-Down Jog", category: "Cool-Down", default_time: "10" },
            { name: "Agility Ladder", category: "Warm-Up", default_time: "10" }
        ];
        
        sampleDrills.forEach(drill => {
            addDrill(drill.name, drill.category, drill.default_time);
        });
    }
}

// Initialize sample drills when script loads
initializeSampleDrills();
