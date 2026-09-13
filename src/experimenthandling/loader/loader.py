from tqdm import tqdm
import os

from ..base import ExperimentHandler, ExperimentDataBuilders
from ..base.exceptions import ExperimentDirectoryNotFoundError

from ...dataloading import EpiDataOrchestrator, BaseLineDataBuilder, GraphDataBuilder

from ...models.basemodel.basemodel import BaseModel

from .io_mixin import ExperimentLoaderIOMixin

class ExperimentLoader(ExperimentLoaderIOMixin, 
                       ExperimentHandler):
    """    
    """
    def __init__(self, 
                 experiment_name : str):
        
        super().__init__(experiment_name)     

        if not self.exp_exists:
            raise ExperimentDirectoryNotFoundError(f'directory for {experiment_name} not found under\n{self.path_exp}')

        self.epicfg = self._load_epiconfig()
        self.expcfg = self._load_experiment_config()
        self.models: dict[int | str | float, list[BaseModel]] | None = None
        self._set_databuilders()

    def _set_databuilders(self) -> None:
        """Shared dataloader construction — called by Runner and Loader. Sets dlms into `dlms`."""
        dataloadermanagers: dict[int | str | float, ExperimentDataBuilders] = {}
        variable  = self.expcfg.variable
        varvalues = self.expcfg.variable_values

        for varvalue in varvalues:
            cfg = self.epicfg.copy({variable: varvalue})
            epo = EpiDataOrchestrator(cfg).build()
            
            # graphs needs to be iterable: graph_list
            graphs_list = [] if self.expcfg.graphs is None else self.expcfg.graphs
    
            hl_dlms = ExperimentDataBuilders(
                baseline = BaseLineDataBuilder(epo),
                graphs   = {
                    graph: GraphDataBuilder(epo)
                               .retrieve_static_graph(graph)
                               .build()
                    for graph in graphs_list
                }
            )

            dataloadermanagers[varvalue] = hl_dlms

        self.dataloadermanagers = dataloadermanagers                   

    def load_models(self, show_progress: bool = False) -> None:
        """ 
        returns a dictionary with values of the variable in key, and the list
        of models in value.

        See Also
        --------
        ### Helper methods:
        - `_parse_filename()`
        - `_get_dlm()`
        - `_load_model()`
        """
        varalias = self.expcfg.variable_alias       
        varvalues= self.expcfg.variable_values
        sep_char = self.expcfg.filename_seperator

        results: dict[int | str | float, list[BaseModel]] = {}

        iterator = varvalues if not show_progress else tqdm(varvalues, desc="Loading models per varvalue")

        for varvalue in iterator:

            files = [
                f for f in os.listdir(self.path_exp)
                if f.endswith(".pt") and f"{sep_char}{varalias}{varvalue}{sep_char}" in f
            ]

            models: list[BaseModel] = []

            for fname in files:
                try:
                    spec    = self._parse_filename(fname)
                    databuilder     = self._get_databuilder(spec.model, spec.variable_value, spec.graph)
                    model   = self._load_single_model(spec, databuilder)
                    model.forecast()
                    models.append(model)

                except Exception as e:
                    print('Model %s could not be found', fname)

            results[varvalue] = models

        self.models = results
    