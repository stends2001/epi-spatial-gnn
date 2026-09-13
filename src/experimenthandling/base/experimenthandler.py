import os
from typing import assert_never

from .experimentconfig import ExperimentConfig
from .experimentcontainers import ExperimentDataBuilders
from .exceptions import ExperimentDirectoryInvalidError, DataBuilderError

from ...utils import PathManager, PathNotFound
from ...dataloading import EpiConfig, GraphDataBuilder, BaseLineDataBuilder

from ...models.gnnmodels.gnnmodel import GNNModel

class ExperimentHandler:
    """ 
    Parent class of experiment-handling classes, namely:
    - ``ExperimentRunner``
    - ``ExperimentLoader``
    - ``ExperimentAnalyzer``(second degree; this is a sub-class to ExperimentLoader)
    
    This parent class only deals with the paths based on the experiment_name.
    This class should not be called in itself, but rather, its subclasses should.
    Also defines a `_get_databuilder()` method which is shared among the subclasses.

    Parameters
    ----------
    experiment_name: str 
        Name of the experiment. This string should be identical to the directory in 
        which the models and configs are saved.     
    
    Methods
    -------
    `_get_databuilder()`
        Returns a specific DataBuilder (BaseLineDataBuilder | GraphDataBuilder)
    
    Attributes
    ----------
    ``databuilders`` : dict[int | str | float, ExperimentDataBuilders] | None
        Dictionary of ExperimentDataBuilders per value of the experiment's variable.
        ``_get_databuilder`` returns a specific dataloadermanager from this attribute.
    ``epicfg``: EpiConfig
        Large configuration class that dictates which data to load. NOTE that
        ``ExperimentRunner`` and ``ExperimentLoader`` deal different with this class.
    ``expcfg`` : ExperimentConfig
        Configuration class that describes the experiment.

    See Also
    --------
    ``ExperimentConfig``
        Configuration class that describes the experiment.    
    ``EpiConfig``
        Large configuration class that dictates which data to load.
    ``ExperimentDataBuilders``
        Simple container that stores DataBuilders for each combination of parameters.

    Downstream
    ----------
    ``ExperimentHandler`` defines shared behavior for its sub classes. Mainly, ``ExperimentAnalyzer``
    and ``ExperimentRunner`` are used. 
    """    
    databuilders: dict[int | str | float, ExperimentDataBuilders] | None = None
    epicfg : EpiConfig           
    expcfg : ExperimentConfig

    expcfg_filename : str = '_experiment_config.yaml'
    epicfg_filename : str = '_epiconfig.yaml'    

    def __init__(self, 
                 experiment_name : str):
        
        self.experiment = experiment_name
        
        # paths
        self.pm = PathManager()
        self.path_exp_root = self.pm.outcomes
        self.path_exp = self.pm.outcomes / experiment_name
        self.exp_exists = self._exp_directory_exists()   

    def _exp_directory_exists(self) -> bool:
        """
        Tests the integrity of experiment-directory.
        if it does, also checks that both ``'_experiment_config.yaml'`` and 
        ``'_epiconfig.yaml'`` are present. 

        If the directory exists, without these two files being present, this directory
        is deemed invalid, and an exception is raised.

        Returns
        -------
        Boolena of whether the experiment exists or not.
        """
        # validate that the root of experiments - paths exists
        if not os.path.exists(self.path_exp_root):
            raise PathNotFound(self.path_exp_root)

        # test whether the path of the experiment already exists
        if not os.path.exists(self.path_exp):
            return False

        # if the experiment-path already exists, an expcfg and an epicfg NEED TO BE present
        files_to_check = [self.expcfg_filename, self.epicfg_filename]
        for ff in files_to_check:
            if ff not in os.listdir(self.path_exp):
                raise ExperimentDirectoryInvalidError(f'directory {self.experiment} already exists, but {ff} was not found.')        
                 
        return True          

    def _get_databuilder(self, 
                 modelclass : str, 
                 varvalue : int | float | str, 
                 graph : str | None = None) -> GraphDataBuilder | BaseLineDataBuilder:
        """
        Shared Databuilder lookup. Get the databuilder for the specific 
        parameters. Please NOTE that ``BaseLine

        Parameters
        ----------
        modelclass : str
            Name of the model class, i.e. ``'gcn'`` or ``'gat'``.
        varvalue : int | float | str
            Value that the ``variable`` in ``ExperimentConfig`` takes.
        graph : str | None = None
            Name of the graph used.
        """

        if self.databuilders is None:
            raise DataBuilderError(
                'databuilders attribute has not been set.'
                )

        childclass  = GNNModel._childclasses[f"{modelclass}model"]
        expected_dlm= childclass._expected_databuilder

        match expected_dlm:
        
            case "GraphDataBuilder":
                if graph is None:
                    raise DataBuilderError(
                        f"Graph required for {modelclass} but got none"
                        )
                
                return self.databuilders[varvalue].graphs[graph]
        
            case "BaseLineDataBuilder":
                if graph is not None:
                    raise DataBuilderError(
                        f"Graph should not be supplied for {modelclass} but got one"
                        )       
                
                return self.databuilders[varvalue].baseline
            
        assert_never(expected_dlm)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({self.experiment})>"        