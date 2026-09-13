
from pathlib import Path

from ..base import ExperimentConfig, ModelSpecs
from ..base.exceptions import InvalidModelNameError, DataBuilderError

from ...dataloading import EpiConfig, BaseLineDataBuilder, GraphDataBuilder

from ...models.gnnmodels.gnnmodel import GNNModel

class ExperimentLoaderIOMixin:

    expcfg : ExperimentConfig
    epicfg : EpiConfig

    path_exp : Path 

    expcfg_filename : str 
    epicfg_filename : str

    def _load_experiment_config(self) -> ExperimentConfig:
        """returns ExperimentConfig"""
        return ExperimentConfig.load(self.path_exp / self.expcfg_filename)
    
    def _load_epiconfig(self) -> EpiConfig:
        """returns EpiConfig"""
        return EpiConfig.load_config(self.path_exp / self.epicfg_filename)        


    def _load_single_model(self, 
                           specs: ModelSpecs,  
                           databuilder: GraphDataBuilder | BaseLineDataBuilder) -> GNNModel:
        """ 
        based on ModelSpecs, and using the dlm, instantiate a model.
        """
        if isinstance(databuilder, BaseLineDataBuilder):
            raise DataBuilderError('Cannot load a baselinemodel. Please nistantiate like you normally would.')

        modeltype = f"{specs.model}model"
        childclass = GNNModel._childclasses[modeltype]
        loaded_model = childclass.load_model(
            model_name          = specs.name,
            dir                 = str(self.path_exp),
            databuilder   = databuilder,
        )
        return loaded_model


    def _parse_filename(self, filename: str) -> ModelSpecs:
        """ 
        splits filename into an instance of ModelSpecs with
        - variable (ex. hl)
        - varvalue (ex. 1)
        - modeltype (ex. lstm)
        - graph (default is None)
        - seed (ex 1)
        - name
        """
        splits      = filename.replace(".pt","").split(self.expcfg.filename_seperator)

        if len(splits) == 3:
            model, variable_value, sd = splits 
            graph = None
        
        elif len(splits) == 4:
            model, graph, variable_value, sd = splits         

        else:
            raise InvalidModelNameError(
                f'unexpected filename found: {filename}. Expected either 3 or 4 seperators (character: {self.expcfg.filename_seperator}) but got {len(splits)}.'
                )

        return ModelSpecs(name      = filename, 
                   variable_alias   = self.expcfg.variable_alias,
                   variable_value   = int(variable_value.replace(self.expcfg.variable_alias, "")), # should be more dynamically resolved: currently ints
                   model            = model,
                   graph            = graph, 
                   seed             = int(sd.replace('s',""))
                   )        
