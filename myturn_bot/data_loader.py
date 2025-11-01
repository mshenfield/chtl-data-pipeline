"""
Data loader utility for abstracting data loading and configuration.

This module provides a unified interface for loading processed data files
and accessing configuration values across notebooks and scripts.
"""

import os
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
import importlib.util


class DataLoader:
    """Centralized data loader for processed MyTurn data."""
    
    def __init__(self, data_home: Optional[str] = None, config_module: Optional[str] = None):
        """
        Initialize the data loader.
        
        Args:
            data_home: Base directory for processed data. Defaults to ~/chtl/data
            config_module: Module name for configuration (e.g., 'myturn_bot.chtl')
        """
        if data_home is None:
            data_home = os.getenv('MYTURN_DATA_HOME', os.path.expanduser("~/seattleReconomy/chtl-data-pipeline/output/seattleReconomy/data"))
        
        self.data_home = Path(data_home)
        self.processed_dir = self.data_home / "processed"
        
        # Load configuration module if specified or from environment
        self.config = {}
        if config_module is None:
            config_module = os.getenv('MYTURN_CONFIG', 'myturn_bot.chtl')
        
        if config_module:
            self._load_config(config_module)
    
    def _load_config(self, config_module: str):
        """Dynamically load configuration from specified module."""
        try:
            spec = importlib.util.find_spec(config_module)
            if spec is None:
                raise ImportError(f"Module {config_module} not found")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Extract configuration values
            self.config = {
                'open_years': getattr(module, 'OPEN_YEARS', None),
                'subdomain': getattr(module, 'SUBDOMAIN', 'capitolhill'),
                'organization_name': getattr(module, 'ORGANIZATION_NAME', 'Capitol Hill Tool Library'),
            }
        except Exception as e:
            print(f"Warning: Could not load config from {config_module}: {e}")
    
    def get_open_years(self):
        """Get the list of years the organization has been open."""
        return self.config.get('open_years', tuple(range(2016, 2025)))
    
    def get_subdomain(self):
        """Get the MyTurn subdomain."""
        return self.config.get('subdomain', 'capitolhill')
    
    def get_organization_name(self):
        """Get the organization name."""
        return self.config.get('organization_name', 'Capitol Hill Tool Library')
    
    def load_users(self) -> pd.DataFrame:
        """Load users/members data."""
        return pd.read_pickle(self.processed_dir/ "users.pkl")
    
    def load_transactions(self) -> pd.DataFrame:
        """Load transactions data."""
        return pd.read_pickle(self.processed_dir / "transactions.pkl")
    
    def load_loans(self) -> pd.DataFrame:
        """Load loans data."""
        return pd.read_pickle(self.processed_dir / "loans.pkl")
    
    def load_inventory(self) -> pd.DataFrame:
        """Load inventory data."""
        return pd.read_pickle(self.processed_dir / "inventory.pkl")
    
    def load_checkouts(self) -> pd.DataFrame:
        """Load checkouts data."""
        return pd.read_pickle(self.processed_dir / "checkouts.pkl")
    
    def load_item_types(self) -> pd.DataFrame:
        """Load item types data."""
        return pd.read_pickle(self.processed_dir / "item-types.pkl")
    
    def get_data_path(self, filename: str) -> Path:
        """Get the full path to a processed data file."""
        return self.processed_dir / filename
    
    def list_available_files(self) -> list:
        """List all available processed data files."""
        if not self.processed_dir.exists():
            return []
        return [f.name for f in self.processed_dir.glob("*.pkl")]


# Convenience functions for quick access
def get_data_loader(config_module: str = "myturn_bot.chtl") -> DataLoader:
    """Get a configured data loader instance."""
    return DataLoader(config_module=config_module)


def load_data(data_home: Optional[str] = None, config_module: str = "myturn_bot.chtl") -> Dict[str, pd.DataFrame]:
    """
    Load all available data files at once.
    
    Returns:
        Dictionary mapping data type names to DataFrames
    """
    loader = DataLoader(data_home=data_home, config_module=config_module)
    
    data = {}
    available_files = loader.list_available_files()
    
    # Map common file patterns to data types
    file_mapping = {
        'users.pkl': 'users',
        'transactions.pkl': 'transactions', 
        'loans.pkl': 'loans',
        'inventory.pkl': 'inventory',
        'checkouts.pkl': 'checkouts',
        'item-types.pkl': 'item_types'
    }
    
    for filename, data_type in file_mapping.items():
        if filename in available_files:
            try:
                data[data_type] = pd.read_pickle(loader.get_data_path(filename))
            except Exception as e:
                print(f"Warning: Could not load {filename}: {e}")
    
    return data

