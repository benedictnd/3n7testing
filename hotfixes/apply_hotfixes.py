#!/usr/bin/env python3
"""
Hotfix Application Script

This script manages the application of hotfixes to the 3&7 Training Platform API.
It supports:
1. Dynamic loading of hotfixes from the hotfixes directory
2. Schema versioning to ensure compatibility
3. Telemetry for monitoring hotfix effectiveness
4. Graceful activation/deactivation with error handling

Usage:
    python apply_hotfixes.py --list  # List available hotfixes
    python apply_hotfixes.py --apply email_validation  # Apply specific hotfix
    python apply_hotfixes.py --status  # Show status of all hotfixes
    python apply_hotfixes.py --deactivate email_validation  # Deactivate specific hotfix
    python apply_hotfixes.py --telemetry email_validation  # Show telemetry for specific hotfix
"""

import os
import sys
import time
import json
import logging
import argparse
import importlib
import traceback
from typing import Dict, List, Any, Optional, Type
from pathlib import Path

# Import base classes
from hotfixes.validation.base import ValidationHotfix

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('hotfixes.log')
    ]
)
logger = logging.getLogger('hotfixes.apply')

# Registry of active hotfixes
ACTIVE_HOTFIXES: Dict[str, ValidationHotfix] = {}

# Hotfix configuration file
HOTFIX_CONFIG_PATH = 'hotfixes/config.json'

def load_config() -> Dict[str, Any]:
    """
    Load hotfix configuration from the config file.
    
    Returns:
        Dictionary containing hotfix configuration
    """
    if not os.path.exists(HOTFIX_CONFIG_PATH):
        # Create default config if it doesn't exist
        default_config = {
            "enabled_hotfixes": [],
            "telemetry_enabled": True,
            "schema_versions": {},
            "last_updated": time.time()
        }
        save_config(default_config)
        return default_config
    
    try:
        with open(HOTFIX_CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading hotfix config: {str(e)}")
        return {
            "enabled_hotfixes": [],
            "telemetry_enabled": True,
            "schema_versions": {},
            "last_updated": time.time()
        }

def save_config(config: Dict[str, Any]) -> None:
    """
    Save hotfix configuration to the config file.
    
    Args:
        config: Dictionary containing hotfix configuration
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(HOTFIX_CONFIG_PATH), exist_ok=True)
    
    try:
        with open(HOTFIX_CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving hotfix config: {str(e)}")

def discover_hotfixes() -> Dict[str, Dict[str, Any]]:
    """
    Discover available hotfixes in the hotfixes directory.
    
    Returns:
        Dictionary of hotfix_name -> hotfix_info
    """
    hotfixes = {}
    hotfix_dirs = [
        ('validation', ValidationHotfix)
    ]
    
    for hotfix_type, base_class in hotfix_dirs:
        path = Path(f"hotfixes/{hotfix_type}")
        if not path.exists():
            continue
            
        for file_path in path.glob("*.py"):
            if file_path.name in ["__init__.py", "base.py"]:
                continue
                
            module_name = f"hotfixes.{hotfix_type}.{file_path.stem}"
            hotfix_id = f"{hotfix_type}/{file_path.stem}"
            
            try:
                module = importlib.import_module(module_name)
                
                # Find the hotfix class (subclass of base_class that isn't the base_class itself)
                hotfix_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, base_class) and 
                        attr != base_class):
                        hotfix_class = attr
                        break
                
                if hotfix_class:
                    hotfixes[hotfix_id] = {
                        "id": hotfix_id,
                        "name": hotfix_class.__name__,
                        "description": hotfix_class.__doc__.strip() if hotfix_class.__doc__ else "No description",
                        "module": module_name,
                        "class_name": hotfix_class.__name__,
                        "type": hotfix_type,
                        "base_class": base_class.__name__
                    }
            except Exception as e:
                logger.error(f"Error loading hotfix {hotfix_id}: {str(e)}")
                logger.debug(traceback.format_exc())
    
    return hotfixes

def load_hotfix(hotfix_id: str) -> Optional[ValidationHotfix]:
    """
    Load a specific hotfix by ID.
    
    Args:
        hotfix_id: The ID of the hotfix to load
        
    Returns:
        Hotfix instance or None if not found/error
    """
    available_hotfixes = discover_hotfixes()
    if hotfix_id not in available_hotfixes:
        logger.error(f"Hotfix {hotfix_id} not found")
        return None
    
    hotfix_info = available_hotfixes[hotfix_id]
    
    try:
        module = importlib.import_module(hotfix_info["module"])
        hotfix_class = getattr(module, hotfix_info["class_name"])
        
        # Get the schema version from config if available
        config = load_config()
        schema_version = config.get("schema_versions", {}).get(hotfix_id, "1.0")
        
        # Instantiate the hotfix with the correct schema version
        if hotfix_id == "validation/email_validation":
            # Email validation gets special parameters
            return hotfix_class(
                schema_version=schema_version,
                telemetry_enabled=config.get("telemetry_enabled", True),
                verify_mx=config.get("verify_mx", False)
            )
        else:
            # Generic instantiation
            return hotfix_class(schema_version=schema_version)
    except Exception as e:
        logger.error(f"Error instantiating hotfix {hotfix_id}: {str(e)}")
        logger.debug(traceback.format_exc())
        return None

def apply_hotfix(hotfix_id: str) -> bool:
    """
    Apply a specific hotfix.
    
    Args:
        hotfix_id: The ID of the hotfix to apply
        
    Returns:
        Boolean indicating if hotfix was successfully applied
    """
    # Check if already active
    if hotfix_id in ACTIVE_HOTFIXES:
        logger.info(f"Hotfix {hotfix_id} is already active")
        return True
    
    # Load the hotfix
    hotfix = load_hotfix(hotfix_id)
    if not hotfix:
        return False
    
    # Activate the hotfix
    try:
        hotfix.activate()
        ACTIVE_HOTFIXES[hotfix_id] = hotfix
        
        # Update config
        config = load_config()
        if hotfix_id not in config["enabled_hotfixes"]:
            config["enabled_hotfixes"].append(hotfix_id)
        config["schema_versions"][hotfix_id] = hotfix.get_schema_version()
        config["last_updated"] = time.time()
        save_config(config)
        
        logger.info(f"Hotfix {hotfix_id} applied successfully")
        return True
    except Exception as e:
        logger.error(f"Error activating hotfix {hotfix_id}: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def deactivate_hotfix(hotfix_id: str) -> bool:
    """
    Deactivate a specific hotfix.
    
    Args:
        hotfix_id: The ID of the hotfix to deactivate
        
    Returns:
        Boolean indicating if hotfix was successfully deactivated
    """
    # Check if active
    if hotfix_id not in ACTIVE_HOTFIXES:
        logger.info(f"Hotfix {hotfix_id} is not active")
        return True
    
    # Deactivate the hotfix
    try:
        hotfix = ACTIVE_HOTFIXES[hotfix_id]
        hotfix.deactivate()
        hotfix.cleanup()
        del ACTIVE_HOTFIXES[hotfix_id]
        
        # Update config
        config = load_config()
        if hotfix_id in config["enabled_hotfixes"]:
            config["enabled_hotfixes"].remove(hotfix_id)
        config["last_updated"] = time.time()
        save_config(config)
        
        logger.info(f"Hotfix {hotfix_id} deactivated successfully")
        return True
    except Exception as e:
        logger.error(f"Error deactivating hotfix {hotfix_id}: {str(e)}")
        logger.debug(traceback.format_exc())
        return False

def apply_all_enabled_hotfixes() -> None:
    """
    Apply all enabled hotfixes from the configuration.
    """
    config = load_config()
    for hotfix_id in config["enabled_hotfixes"]:
        apply_hotfix(hotfix_id)

def show_hotfix_status(hotfix_id: Optional[str] = None) -> None:
    """
    Show the status of hotfixes.
    
    Args:
        hotfix_id: Optional specific hotfix ID to show status for
    """
    available_hotfixes = discover_hotfixes()
    config = load_config()
    
    if hotfix_id:
        # Show status for specific hotfix
        if hotfix_id not in available_hotfixes:
            print(f"Hotfix {hotfix_id} not found")
            return
        
        hotfix_info = available_hotfixes[hotfix_id]
        active = hotfix_id in ACTIVE_HOTFIXES
        enabled = hotfix_id in config["enabled_hotfixes"]
        schema_version = config.get("schema_versions", {}).get(hotfix_id, "unknown")
        
        print(f"Hotfix: {hotfix_id}")
        print(f"Name: {hotfix_info['name']}")
        print(f"Description: {hotfix_info['description']}")
        print(f"Type: {hotfix_info['type']}")
        print(f"Status: {'Active' if active else 'Inactive'}")
        print(f"Enabled: {'Yes' if enabled else 'No'}")
        print(f"Schema Version: {schema_version}")
        
        # Show telemetry if available
        if active and hasattr(ACTIVE_HOTFIXES[hotfix_id], "get_telemetry_stats"):
            print("\nTelemetry Statistics:")
            stats = ACTIVE_HOTFIXES[hotfix_id].get_telemetry_stats()
            for key, value in stats.items():
                print(f"  {key}: {value}")
    else:
        # Show status for all hotfixes
        print(f"Found {len(available_hotfixes)} available hotfixes:")
        for hf_id, hf_info in available_hotfixes.items():
            active = hf_id in ACTIVE_HOTFIXES
            enabled = hf_id in config["enabled_hotfixes"]
            status = "Active" if active else ("Enabled" if enabled else "Inactive")
            print(f"  - {hf_id}: {hf_info['name']} [{status}]")

def main() -> None:
    """
    Main entry point for the hotfix application script.
    """
    parser = argparse.ArgumentParser(description="Apply and manage hotfixes")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List available hotfixes")
    group.add_argument("--apply", help="Apply a specific hotfix")
    group.add_argument("--apply-all", action="store_true", help="Apply all enabled hotfixes")
    group.add_argument("--deactivate", help="Deactivate a specific hotfix")
    group.add_argument("--status", nargs="?", const=None, help="Show status of all hotfixes or a specific one")
    group.add_argument("--telemetry", help="Show telemetry for a specific hotfix")
    
    args = parser.parse_args()
    
    if args.list:
        available_hotfixes = discover_hotfixes()
        print(f"Available hotfixes ({len(available_hotfixes)}):")
        for hotfix_id, info in available_hotfixes.items():
            print(f"  - {hotfix_id}: {info['name']}")
            print(f"    {info['description'][:60]}...")
    
    elif args.apply:
        if apply_hotfix(args.apply):
            print(f"Hotfix {args.apply} applied successfully")
        else:
            print(f"Failed to apply hotfix {args.apply}")
            sys.exit(1)
    
    elif args.apply_all:
        apply_all_enabled_hotfixes()
        print("All enabled hotfixes applied")
    
    elif args.deactivate:
        if deactivate_hotfix(args.deactivate):
            print(f"Hotfix {args.deactivate} deactivated successfully")
        else:
            print(f"Failed to deactivate hotfix {args.deactivate}")
            sys.exit(1)
    
    elif args.status is not None:
        show_hotfix_status(args.status)
    
    elif args.telemetry:
        if args.telemetry in ACTIVE_HOTFIXES and hasattr(ACTIVE_HOTFIXES[args.telemetry], "get_telemetry_stats"):
            stats = ACTIVE_HOTFIXES[args.telemetry].get_telemetry_stats()
            print(f"Telemetry for hotfix {args.telemetry}:")
            print(json.dumps(stats, indent=2))
        else:
            print(f"No telemetry available for hotfix {args.telemetry}")

if __name__ == "__main__":
    main() 