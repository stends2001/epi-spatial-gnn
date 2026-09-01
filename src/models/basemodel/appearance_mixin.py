from __future__ import annotations

from typing import TYPE_CHECKING
import re

from ..utils import model_colors

if TYPE_CHECKING:
    from ...dataloading.columnregistration import ColumnRegistry
    from ...dataloading.epiconfig import EpiConfig

class ModelAppearanceMixin:
    """ 
    Mixin class to ``BaseModel`` that deals with the model's appearance.
    """
    name : str
    model_class : str
    epiconfig : EpiConfig
    column_registration : ColumnRegistry

    def _get_model_color(self) -> str:
        """returns model-color in string format based on the lookup in model_colors"""
        lookup_name = self.model_class.lower()
        
        if lookup_name not in model_colors:
            raise ValueError(f'no color set for model of class {lookup_name}')
        
        else:
            return model_colors[lookup_name]
        
    def _get_clean_name(self) -> str:
        """Return a filesystem-safe version of the model name."""
        name = self.name.lower()
        name = re.sub(r"\s+", "_", name)
        name = re.sub(r"[^a-z0-9_-]", "", name)
        name = re.sub(r"_+", "_", name)
    
        return name.strip("_")