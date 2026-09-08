from dataclasses import dataclass

from ...utils import align
from ...dataloading import BaseLineDataBuilder, GraphDataBuilder

@dataclass(frozen= True)
class ExperimentDataBuilders:
    """ 
    For a single run (i.e. single value of a variable) this stores the databuilders.
    """
    baseline:   BaseLineDataBuilder
    graphs:     dict[str, GraphDataBuilder]

@dataclass(frozen= True)
class ModelSpecs:
    """ 
    Dataclass containing information for a given model.

    Parameters
    ----------
    name : str
        Name of the model.
    variable_alias : str
        Alias of the variable varied over in the experiment.
    variable_value : str
        The value that ``variable_alias`` was given in this model.
    model : str
        Model class (``'gcn'`` or ``'gat'``).
    graph : str | None
        Graph used by model.
    seed : int 
        Seed with which model is initiated.
    """
    name : str
    variable_alias : str 
    variable_value : int | float | str
    model : str 
    graph : str | None
    seed : int 

    def __str__(self) -> str:
        all_keys    = ['name', 'variable_alias', 'variable_value', 'model', 'graph', 'seed']
        width       = max(len(k) for k in all_keys) if all_keys else 20
        
        lines = [f'<{self.__class__.__name__}(']

        for key in all_keys:
            lines.append(align(key, getattr(self, key), width))

        lines.append(')>')
        
        return '\n'.join(lines)

    def __repr__(self) -> str:
        all_keys    = ['name', 'variable_alias', 'variable_value', 'model', 'graph', 'seed']

        line_0 = f'<{self.__class__.__name__}('
        line_1 = ')>'

        lines = []
        for key in all_keys:
            lines.append(f'{key} = {getattr(self, key)}')

        lines = ', '.join(lines)

        lines = line_0 + lines + line_1
        
        return lines