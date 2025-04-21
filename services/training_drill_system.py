"""
Basketball Training Drill Management System

This module provides a comprehensive system for managing basketball training drills,
including creating, saving, and reusing drills within training sessions.
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import os


class BasketballTrainingSystem:
    """
    A comprehensive system for managing basketball training drills and sessions.
    
    Allows coaches to:
    - Create and save training drills
    - Build training sessions using saved and custom drills
    - Track player performance in drills
    - Manage a persistent library of drills with metadata
    """
    
    def __init__(self):
        """Initialize the basketball training system with empty collections."""
        self.saved_drills: List[Dict[str, Any]] = []
        self.current_session: List[Dict[str, Any]] = []
        self.unsaved_drills: List[Dict[str, Any]] = []
        self.session_metadata: Dict[str, Any] = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "coach": "",
            "location": "",
            "team": "",
            "notes": ""
        }
        self._load_saved_drills()

    def _load_saved_drills(self) -> None:
        """Load saved drills from storage if available."""
        try:
            if os.path.exists("data/drills.json"):
                with open("data/drills.json", "r") as f:
                    self.saved_drills = json.load(f)
        except Exception as e:
            print(f"Error loading saved drills: {e}")
            self.saved_drills = []

    def _save_drills_to_storage(self) -> None:
        """Save the drills library to persistent storage."""
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/drills.json", "w") as f:
                json.dump(self.saved_drills, f, indent=2)
        except Exception as e:
            print(f"Error saving drills: {e}")

    def main_menu(self) -> None:
        """Display the main menu of the training system."""
        print("""
        🏀 Jaya Jakarta Training System 🏀
        
        [1] Start New Session
        [2] Saved Drills Library ({})
        [3] Previous Sessions
        [4] Player Management
        [5] Exit
        """.format(len(self.saved_drills)))

    def session_creation_flow(self) -> None:
        """Handle the session creation workflow."""
        # Initialize session metadata
        self._get_session_metadata()
        
        while True:
            print("""
            🏋️♂️ Session Creation Menu
            
            Current Session Duration: {}min
            Drills Added: {}
            
            [1] Add Saved Drill
            [2] Create New Drill
            [3] View/Edit Session
            [4] Save & Finish
            [5] Exit Without Saving
            """.format(self._calculate_duration(), len(self.current_session)))
            
            choice = input("Select option: ")
            
            if choice == '1':
                self._show_saved_drills()
            elif choice == '2':
                self._create_new_drill()
            elif choice == '3':
                self._view_edit_session()
            elif choice == '4':
                self._save_session_flow()
                break
            elif choice == '5':
                if self._confirm_exit():
                    self._reset_session()
                    break

    def _get_session_metadata(self) -> None:
        """Collect metadata for the current training session."""
        print("""
        📋 Session Details
        
        Please enter the following information:
        """)
        
        self.session_metadata["date"] = input(f"Date [default: {self.session_metadata['date']}]: ") or self.session_metadata["date"]
        self.session_metadata["coach"] = input("Coach name: ")
        self.session_metadata["team"] = input("Team name: ")
        self.session_metadata["location"] = input("Training location: ")

    def _calculate_duration(self) -> int:
        """Calculate the total duration of the current session."""
        return sum(drill.get("duration", 0) for drill in self.current_session)

    def _show_saved_drills(self) -> None:
        """Display the saved drills library for selection."""
        category_counts = self._get_category_counts()
        
        print("""
        📚 Saved Drills Library
        
        🔍 Search: [__________________________]
        
        Categories:
        🔫 Shooting ({}) | 🛡️ Defense ({}) | 🏃♂️ Transition ({})
        
        Recent Drills:
        """.format(*category_counts))
        
        # Display most recently used drills
        sorted_drills = sorted(
            self.saved_drills, 
            key=lambda x: x.get("last_used", "2000-01-01"), 
            reverse=True
        )
        
        for i, drill in enumerate(sorted_drills[:5], 1):
            rating = "⭐" * drill.get("rating", 3)
            print(f"{i}. {drill['name']} - {drill['duration']}min {rating}")
        
        print("\n[L] Load Drill   [E] Edit   [D] Duplicate   [B] Back")
        
        action = input("\nSelect option: ").upper()
        
        if action == 'L':
            drill_idx = int(input("Enter drill number: ")) - 1
            if 0 <= drill_idx < len(sorted_drills[:5]):
                self._add_drill_to_session(sorted_drills[drill_idx])
        elif action == 'E':
            drill_idx = int(input("Enter drill number to edit: ")) - 1
            if 0 <= drill_idx < len(sorted_drills[:5]):
                self._edit_drill(sorted_drills[drill_idx])
        elif action == 'D':
            drill_idx = int(input("Enter drill number to duplicate: ")) - 1
            if 0 <= drill_idx < len(sorted_drills[:5]):
                duplicate = sorted_drills[drill_idx].copy()
                duplicate["name"] = duplicate["name"] + " (Copy)"
                duplicate["id"] = f"D-{len(self.saved_drills)+1:03}"
                self._add_drill_to_session(duplicate)

    def _get_category_counts(self) -> tuple:
        """Get counts of drills by category."""
        shooting = sum(1 for d in self.saved_drills if "Shooting" in d.get("category", []))
        defense = sum(1 for d in self.saved_drills if "Defense" in d.get("category", []))
        transition = sum(1 for d in self.saved_drills if "Transition" in d.get("category", []))
        
        return shooting, defense, transition

    def _create_new_drill(self) -> None:
        """Flow for creating a new drill."""
        print("""
        🆕 New Drill Creation
        
        Drill Name: [__________________________]
        Duration: [__] minutes
        Primary Focus: [Shooting/Defense/Transition]
        Equipment Needed: [____________________]
        
        Drill Description:
        [_________________________________________]
        [_________________________________________]
        
        [S] Save to Library   [T] Temporary Drill   [C] Cancel
        """)
        
        # In a real implementation, we would collect these values
        # For simulation, let's create a sample drill
        new_drill = {
            "id": f"D-{len(self.saved_drills)+1:03}",
            "name": input("Drill name: "),
            "duration": int(input("Duration (minutes): ")),
            "category": input("Primary focus (Shooting/Defense/Transition): ").split('/'),
            "equipment": input("Equipment needed: ").split(','),
            "description": input("Description: "),
            "created_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        action = input("Choose action [S/T/C]: ").upper()
        
        if action == 'S':
            self._save_drill_prompt(new_drill)
            self._add_drill_to_session(new_drill)
        elif action == 'T':
            self.unsaved_drills.append(new_drill)
            self._add_drill_to_session(new_drill)

    def _add_drill_to_session(self, drill: Dict[str, Any]) -> None:
        """Add a drill to the current session."""
        session_drill = drill.copy()
        session_drill["notes"] = input("Session-specific notes for this drill (optional): ")
        session_drill["variation"] = input("Variation (Basic/Advanced/Custom): ") or "Basic"
        
        self.current_session.append(session_drill)
        print(f"✅ Added '{drill['name']}' to session")

    def _view_edit_session(self) -> None:
        """View and edit the current session."""
        print("""
        📋 Current Session
        
        Date: {}
        Team: {}
        Location: {}
        Total Duration: {}min
        
        Drills:
        """.format(
            self.session_metadata["date"],
            self.session_metadata["team"],
            self.session_metadata["location"],
            self._calculate_duration()
        ))
        
        for i, drill in enumerate(self.current_session, 1):
            save_status = "⚠️ Unsaved" if drill in self.unsaved_drills else "✅ Saved"
            print(f"{i}. {drill['name']} ({drill['duration']}min) - {save_status}")
            print(f"   Variation: {drill.get('variation', 'Standard')}")
            if drill.get("notes"):
                print(f"   Notes: {drill['notes']}")
            print()
        
        print("[R] Reorder   [E] Edit Drill   [D] Delete Drill   [B] Back")
        
        action = input("Select option: ").upper()
        
        if action == 'E':
            idx = int(input("Enter drill number to edit: ")) - 1
            if 0 <= idx < len(self.current_session):
                self._edit_session_drill(idx)
        elif action == 'D':
            idx = int(input("Enter drill number to delete: ")) - 1
            if 0 <= idx < len(self.current_session):
                drill = self.current_session.pop(idx)
                if drill in self.unsaved_drills:
                    self.unsaved_drills.remove(drill)
                print(f"✅ Removed '{drill['name']}' from session")

    def _edit_session_drill(self, index: int) -> None:
        """Edit a drill in the current session."""
        drill = self.current_session[index]
        
        print(f"""
        ✏️ Edit Drill: {drill['name']}
        
        [1] Change duration (currently: {drill['duration']}min)
        [2] Edit notes (currently: {drill.get('notes', 'None')})
        [3] Change variation (currently: {drill.get('variation', 'Standard')})
        [4] Back
        """)
        
        choice = input("Select option: ")
        
        if choice == '1':
            drill['duration'] = int(input("New duration (minutes): "))
        elif choice == '2':
            drill['notes'] = input("New notes: ")
        elif choice == '3':
            drill['variation'] = input("New variation: ")

    def _save_session_flow(self) -> None:
        """Handle saving the session and any unsaved drills."""
        if self.unsaved_drills:
            print(f"""
            💾 Save New Drills Before Finalizing
            
            Unsaved Drills:
            """)
            
            for i, drill in enumerate(self.unsaved_drills, 1):
                print(f"{i}. {drill['name']} - {drill['duration']}min")
            
            print("""
            [1] Save All to Library
            [2] Select Drills to Save
            [3] Discard Unsaved
            [4] Cancel
            """)
            
            choice = input("Select save option: ")
            
            if choice == '1':
                self._save_all_drills()
            elif choice == '2':
                self._selective_save()
            elif choice == '3':
                self.unsaved_drills = []
            elif choice == '4':
                return
        
        self._finalize_session()
        print("✅ Session Saved Successfully!")
        self._reset_session()

    def _save_drill_prompt(self, drill: Dict[str, Any]) -> None:
        """Prompt for saving a drill to the library with metadata."""
        print(f"""
        💾 Save Drill to Library
        
        Drill Name: [{drill['name']}]
        Categories (enter comma-separated):
        {', '.join(drill.get('category', []))}
        
        Key Players:
        [Enter player names separated by commas]
        
        Success Metrics to Track (enter comma-separated):
        Completion Time, Successful Transitions, Defensive Stops, Shot Accuracy
        
        """)
        
        # In a real implementation, we would collect these values
        drill['key_players'] = input("Key players (comma-separated): ").split(',')
        drill['success_metrics'] = input("Success metrics to track (comma-separated): ").split(',')
        
        self.saved_drills.append(drill)
        if drill in self.unsaved_drills:
            self.unsaved_drills.remove(drill)
        
        self._save_drills_to_storage()
        print(f"✅ Saved '{drill['name']}' to library")

    def _save_all_drills(self) -> None:
        """Save all unsaved drills to the library."""
        for drill in self.unsaved_drills.copy():
            drill['usage_count'] = 1
            drill['last_used'] = datetime.now().strftime("%Y-%m-%d")
            self.saved_drills.append(drill)
            self.unsaved_drills.remove(drill)
        
        self._save_drills_to_storage()
        print("✅ All drills saved to library")

    def _selective_save(self) -> None:
        """Allow selecting specific drills to save."""
        for i, drill in enumerate(self.unsaved_drills.copy(), 1):
            save_this = input(f"Save '{drill['name']}'? [Y/N]: ").upper()
            
            if save_this == 'Y':
                drill['usage_count'] = 1
                drill['last_used'] = datetime.now().strftime("%Y-%m-%d")
                self.saved_drills.append(drill)
                self.unsaved_drills.remove(drill)
        
        self._save_drills_to_storage()
        print("✅ Selected drills saved to library")

    def _finalize_session(self) -> None:
        """Finalize and save the complete training session."""
        session = {
            "id": f"S-{datetime.now().strftime('%Y%m%d%H%M')}",
            "metadata": self.session_metadata,
            "drills": self.current_session,
            "total_duration": self._calculate_duration(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Update usage statistics for drills
        for drill in self.current_session:
            for saved_drill in self.saved_drills:
                if saved_drill.get('id') == drill.get('id'):
                    saved_drill['usage_count'] = saved_drill.get('usage_count', 0) + 1
                    saved_drill['last_used'] = datetime.now().strftime("%Y-%m-%d")
        
        # In a real implementation, save the session to storage
        try:
            os.makedirs("data/sessions", exist_ok=True)
            with open(f"data/sessions/{session['id']}.json", "w") as f:
                json.dump(session, f, indent=2)
            
            # Also update the saved drills with new usage data
            self._save_drills_to_storage()
        except Exception as e:
            print(f"Error saving session: {e}")

    def _reset_session(self) -> None:
        """Reset the current session state."""
        self.current_session = []
        self.unsaved_drills = []
        self.session_metadata = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "coach": "",
            "location": "",
            "team": "",
            "notes": ""
        }

    def _confirm_exit(self) -> bool:
        """Confirm exiting without saving."""
        if not self.current_session:
            return True
            
        confirm = input("Exit without saving session? [Y/N]: ").upper()
        return confirm == 'Y'

    def _edit_drill(self, drill: Dict[str, Any]) -> None:
        """Edit a drill in the library."""
        print(f"""
        ✏️ Edit Drill: {drill['name']}
        
        [1] Rename (currently: {drill['name']})
        [2] Change duration (currently: {drill['duration']}min)
        [3] Update categories (currently: {', '.join(drill.get('category', []))})
        [4] Update equipment (currently: {', '.join(drill.get('equipment', []))})
        [5] Edit description
        [6] Save Changes
        [7] Cancel
        """)
        
        choice = input("Select option: ")
        
        if choice == '1':
            drill['name'] = input("New name: ")
        elif choice == '2':
            drill['duration'] = int(input("New duration (minutes): "))
        elif choice == '3':
            drill['category'] = input("New categories (comma-separated): ").split(',')
        elif choice == '4':
            drill['equipment'] = input("New equipment (comma-separated): ").split(',')
        elif choice == '5':
            drill['description'] = input("New description: ")
        elif choice == '6':
            self._save_drills_to_storage()
            print("✅ Changes saved")
        
        # In a real implementation, would save changes back to storage


def main():
    """Main entry point for the Basketball Training System."""
    system = BasketballTrainingSystem()
    system.main_menu()
    
    # For demonstration, start a session creation flow
    choice = input("Select option: ")
    if choice == '1':
        system.session_creation_flow()


if __name__ == "__main__":
    main() 