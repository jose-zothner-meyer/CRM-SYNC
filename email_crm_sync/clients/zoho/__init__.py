"""
Zoho client modules package.

This package contains modular components for the Zoho CRM client,
organized by functionality for better maintainability.
"""

from .notes import Notes
from .search import Search
from .modules import Modules
from .records import Records
from .developments import Developments

__all__ = [
    'Notes',
    'Search', 
    'Modules',
    'Records',
    'Developments'
]
