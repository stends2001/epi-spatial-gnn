from __future__ import annotations

from dataclasses import dataclass, asdict, fields
from pathlib import Path
from typing import Self
import yaml

from .exceptions import IncompatibleExperimentConfigs
from ...utils import align, PathNotFound, InvalidExtension, AttributeNotFound

@dataclass
class ExperimentConfig:
    """
    Configuration class that contains information to run or load an experiment.

    Parameters
    ----------
    experiment_name : str
        Name of the experiment. A directory under in this name will be created, in which
        this ``ExperimentConfig`` is saved.
    filename_seperator : str    
        Character used in model-names between elements of the name.
    variable : str
        Variable that is being adjusted in the experiment. Should be a variable of 
        ``EpiConfig``.
    variable_alias : str
        Alias for the variable, saved in model-names. For example, ``'hl'`` for 
        'horizon_leadtime'.
    variable_values : list[int | str | float]
        List of the values that the ``variable`` takes.
    graphs: list[str] | None
        List of graph-structures to be included in the experiment. These need to
        correspond to saved graphstructures.
    models: list[str]
        List of model-names to be included, directly related to the modelclass-name. Use
        ``'gcn'`` for a ``GCNModel`` and ``'gat'`` for ``GATModel``.
    seeds: list[int]    
        List of seeds to be run.    
    
    Methods
    -------
    ``load()``
        Load an ``ExperimentConfig`` from file.
    ``save()``
        Save an ``ExperimentConfig`` to file.
    ``compare()``
        ``Test compatibility of two ``ExperimentConfig``s.
    ``merge()``
        ``Merge two ``ExperimentConfig``s into one configuration file.

    See Also
    --------
    ``PathManager``
        All (outcomes of) experiments are saved in ``outcomes`` of ``PathManager``.

    Downstream
    ----------
    An ``ExperimentConfig`` holds all information for an entire experiment. For example,
    for all horizons related to NUTS1 influenza predictions in Germany, a single
    ``ExperimentConfig`` dictates the values for ``horizon leadtime`` that will be run
    in the experiment.
    """

    experiment_name : str
    filename_seperator : str    
    variable : str
    variable_alias : str
    variable_values : list[int | str | float]
    graphs : list[str] | None
    models : list[str]
    seeds : list[int]    

    # these need to be identical within the same experiment.
    _FUNDAMENTAL_ATTRIBUTES = ['experiment_name', 
                              'variable', 
                              'variable_alias', 
                              'filename_seperator']

    @classmethod
    def load(cls, path : Path) -> ExperimentConfig:
        """load an ``ExperimentConfig``"""
        if not path.exists:
            raise PathNotFound(path)

        with open(path) as f:
            d = yaml.safe_load(f)      

        return cls(**d)   

    def save(self, path : Path) -> None: 
        """save ExperimentConfig to dedicated path (must include .yaml)"""

        if not path.parent.exists():
            path.parent.mkdir()

        if path.suffix != '.yaml':
            raise InvalidExtension('.yaml',path.suffix)

        config_dict = asdict(self)

        with open(path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)        

    def compare(self, 
               other_cfg : ExperimentConfig, 
               exclusion_attr : str | list[str] = []) -> bool:
        """
        Compare two ``ExperimentConfigs``, returns whether or not these are compatible.
        This is based on comparing certain attributes. An exception is raised when any
        of the attributes in ``_FUNDAMENTAL_ATTRIBUTES`` are different from each other.

        Parameters
        ----------
        other_cfg : Type[Self]
            The ``ExperimentConfig`` instance which to compare self to.
        exclusion_attr: str | list[str] = []
            The attributes not to take into account. May be any of:
            - 'variable_values'
            - 'graphs'
            - 'models'
            - 'seeds'.
            
            Additionally, ``exclusion_attr`` could be 'ALL'. That is to say,
            except for the fundamental attributes, none are taken into account.
            
            NOTE these may not include any of ``_FUNDAMENTAL_ATTRIBUTES``.
                if any of those are not identical, the instances of 
                ``ExperimentConfig`` are fundamentally different.
        """

        if exclusion_attr != 'ALL':

            # check that exclusion attribute is actually an attribute
            for attr in exclusion_attr:
                if attr not in dir(self):
                    raise AttributeNotFound(attr, self.__class__.__name__)

        for attr in self._FUNDAMENTAL_ATTRIBUTES:

            # check that exclusion attribute are not fundamental attributes         
            if attr in exclusion_attr:
                raise IncompatibleExperimentConfigs(
                    f'Invalid experimentconfig comparison. {attr} must be equal, cannot be put in exclusion_attr'
                    )
                   
        for attr in fields(self):

            # comparing attributes; attributes may be fundamental or not. 
            # Fundamental attributes: must be identical within the same experiment
            if attr.name in self._FUNDAMENTAL_ATTRIBUTES:
                if getattr(self, attr.name) != getattr(other_cfg, attr.name):
                    raise IncompatibleExperimentConfigs(
                        f'Attribute {attr.name} is unequal, while it must be!'
                        )
                
            # non-fundamental attributes: identical-ness may be enforced
            # if there's a difference; return False.
            if attr.name not in exclusion_attr and exclusion_attr != 'ALL':
                if getattr(self, attr.name) != getattr(other_cfg, attr.name):
                    return False 
                
        return True


    def merge(self, other_cfg : ExperimentConfig) -> ExperimentConfig:
        """ 
        Merge two ``ExperimentConfigs``. Is only possible when ``compare(other_cfg)`` is
        True based on only the fundamental attributes.
        """
        if not self.compare(other_cfg, 'ALL'):
            raise IncompatibleExperimentConfigs(
                'These two configs cannot be merged based on these appending attributes!'
                )
            
        # if identical, keep those from self, else append the list
        variable_values = self.variable_values  if self.variable_values == other_cfg.variable_values    else list(set(self.variable_values + other_cfg.variable_values))
        models          = self.models           if self.models == other_cfg.models                      else list(set(self.models +  other_cfg.models))
        seeds           = self.seeds            if self.seeds == other_cfg.seeds                        else list(set(self.seeds +  other_cfg.seeds))

        # with graphs it's slightly more complicated; may also be None
        if self.graphs == other_cfg.graphs:
            graphs              = self.graphs
        else:
            if self.graphs is None:
                graphs = other_cfg.graphs
            elif other_cfg.graphs is None:
                graphs = self.graphs 
            else:
                graphs = list(set(self.graphs + other_cfg.graphs))

        merged_expcfg = ExperimentConfig(
            # fundamental ones must be identical anyway
            experiment_name     = self.experiment_name,
            filename_seperator  = self.filename_seperator,
            variable            = self.variable,
            variable_alias      = self.variable_alias,

            # the added combinations of parameters
            variable_values     = variable_values,
            graphs              = graphs,
            models              = models,
            seeds               = seeds
            )

        return merged_expcfg

    def __str__(self) -> str:
        """nicely alined representation"""
        all_keys    = ['experiment_name', 'variable', 'variable_alias', 'variable_values', 'models', 'graphs', 'seeds']
        width       = max(len(k) for k in all_keys) if all_keys else 20
        
        lines = [f'<{self.__class__.__name__}(']

        for key in all_keys:
            lines.append(align(key, getattr(self, key), width))
        lines.append(')>')
        
        return '\n'.join(lines)

    def __repr__(self) -> str:
        """one-liner representation"""
        all_keys    = ['experiment_name', 
                       'variable', 
                       'variable_alias', 
                       'variable_values', 
                       'models', 
                       'graphs', 
                       'seeds']

        line_0 = f'<{self.__class__.__name__}('
        line_1 = ')>'

        lines = []
        for key in all_keys:
            lines.append(f'{key} = {getattr(self, key)}')
        lines = ', '.join(lines)

        lines = line_0 + lines + line_1
        
        return lines
