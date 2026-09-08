import os
from typing import assert_never

from .experimentconfig import ExperimentConfig
from .experimentcontainers import ExperimentDataBuilders
from .exceptions import ExperimentDirectoryInvalidError, DataBuilderError

from ...utils import PathManager, PathNotFound
from ...dataloading import EpiConfig, GraphDataBuilder, BaseLineDataBuilder

from ...models.gnnmodels.gnnmodel import GNNModel

class ExperimentHandler:

    databuilders: dict[int | str | float, ExperimentDataBuilders] | None = None
    epicfg : EpiConfig           
    expcfg : ExperimentConfig

    expcfg_filename : str = '_experiment_config.yaml'
    epicfg_filename : str = '_epiconfig.yaml'    

    def __init__(self, 
                 experiment_name : str):
        
        self.experiment          = experiment_name
        
        # paths
        self.pm                  = PathManager()
        self.path_exp_root       = self.pm.outcomes
        self.path_exp            = self.pm.outcomes / experiment_name
        self.exp_exists          = self._exp_directory_exists()   

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

    def _get_dlm(self, 
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