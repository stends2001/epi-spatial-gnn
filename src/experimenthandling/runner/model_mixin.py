from pathlib import Path 
from typing import Any
import os

from ..base import ExperimentConfig
from ...dataloading import EpiConfig, BaseLineDataBuilder, GraphDataBuilder
from ...models.gnnmodels.gnnmodel import GNNModel

class ExperimentRunnerModelMixin:

    expcfg : ExperimentConfig
    epicfg : EpiConfig    
    path_exp : Path

    def _load_model(self, modelname: str, childclass: GNNModel, value: int | str | float, ml: str, graph: str | None) -> GNNModel:
        """load instance of model"""
        dlm = self._get_databuilder(ml, value, graph)            
        return childclass(name=modelname, dataloadermanager=dlm) 

    def _get_model_name(self, modeltype: str, varvalue: str | float | int, seed: int, graph : str | None = None) -> str:
        """return model name: to be saved as"""
        sep = self.expcfg.filename_seperator
        var = self.expcfg.variable_alias

        if graph is None:
            name = f"{modeltype}{sep}{var}{varvalue}{sep}s{seed}"

        else:
            name = f"{modeltype}{sep}{graph}{sep}{var}{varvalue}{sep}s{seed}"            
        
        return name

    def _model_to_run(self, modelname: str) -> bool:
        """boolean on whether the modelname already exists or not."""
        saved_models = {
            os.path.splitext(f)[0] 
            for f in os.listdir(self.path_exp) 
            if f.endswith('.pt')
        }
        if modelname in saved_models:
            print(f'Weights for model {modelname} already exist')
            return False
        return True

    def _train_and_save_model(self, 
                              modelname : str, 
                              childclass: GNNModel, 
                              value: int | str | float, 
                              ml: str, 
                              global_hparams : dict[Any, Any], 
                              graph : str | None):
        """
        loads, trains and saves single model
        """
        if not self._model_to_run(modelname):
            return

        model = self._load_model(modelname, childclass, value, ml, graph)

        model.set_model_hparams()
        model.set_global_hparams(**global_hparams)
        model.train()
        model.save_model(dir=self.path_exp)

    # stub
    def _get_databuilder(self, 
                 modelclass : str, 
                 varvalue : int | float | str, 
                 graph : str | None = None) -> GraphDataBuilder | BaseLineDataBuilder:
        ...