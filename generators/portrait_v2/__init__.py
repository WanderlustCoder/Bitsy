"""
Template-Based Portrait Generator v2

A flexible portrait system using pre-designed templates
instead of pure procedural generation.
"""

from .composer import TemplatePortraitGenerator
from .loader import TemplateLoader
from .recolor import recolor_template

__all__ = [
    "TemplatePortraitGenerator",
    "TemplateLoader",
    "recolor_template",
]
