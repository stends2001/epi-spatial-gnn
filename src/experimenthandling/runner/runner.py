from typing import Any
from itertools import product
from tqdm import tqdm
from typing import assert_never

from ..base import ExperimentConfig, ExperimentDataBuilders, ExperimentHandler
from ...dataloading import EpiConfig, EpiDataOrchestrator, BaseLineDataBuilder, GraphDataBuilder
from ...models.gnnmodels.gnnmodel import GNNModel

from .model_mixin import ExperimentRunnerModelMixin
from .config_mixin import ExperimentRunnerConfigMixin

class ExperimentRunner(ExperimentRunnerConfigMixin,
                       ExperimentRunnerModelMixin,
                       ExperimentHandler):
    """ 
    """
    def __init__(self,
                 epiconfig : EpiConfig,
                 experimentconfig : ExperimentConfig,):

        super().__init__(experimentconfig.experiment_name)

        self.epicfg = epiconfig
        self.expcfg = experimentconfig       

        self.new_variable_values = experimentconfig.variable_values
        self.expcfg_to_save = self._update_experiment_cfg(epiconfig, experimentconfig)    

        self._set_databuilders()

    # ======= METHODS ======= #
    def run(self, global_hparams : dict[Any, Any], show_progress: bool = False):
        """
        """
        self._save_cfgs()
        
        graphlist = [None] if self.expcfg.graphs is None else self.expcfg.graphs

        iterator = product(self.new_variable_values, self.expcfg.models)      

        if show_progress:
            iterator =  tqdm(
                iterator,
                total=len(self.new_variable_values) * len(self.expcfg.models),
                desc="Training models",
            )

        for value, ml in iterator:

                modeltype  = f"{ml}model"
                childclass = GNNModel._childclasses[modeltype]
                for sd in self.expcfg.seeds:

                    match childclass._expected_databuilder:

                        case 'GraphDataBuilder':
                            for graph in graphlist:
                                modelname = self._get_model_name(ml, value, sd, graph)
                                self._train_and_save_model(modelname, childclass, value, ml, global_hparams, graph)

                        case 'BaseLineDataBuilder':
                            raise ValueError("got required databuilder as BaseLineDataBuilder: Baseline Models arent supposed to be run here.")

                        case _:
                            assert_never(childclass._expected_databuilder)
     

    def _set_databuilders(self) -> None:
        """"""
        dataloader_managers_dict: dict[int | str | float, ExperimentDataBuilders] = {}
        variable = self.expcfg.variable

        # looping over the values for the variable, the varvalues
        for varvalue in self.new_variable_values:
            epicfg = self.epicfg.copy({variable: varvalue})
            epidata_orchestrator = EpiDataOrchestrator(epicfg).build()

            graphs_list = [] if self.expcfg.graphs is None else self.expcfg.graphs

            # get a ``ExperimentDataBuilders`` of the databuilders for this varvalue
            varvalue_databuilders = ExperimentDataBuilders(
                baseline = BaseLineDataBuilder(epidata_orchestrator),
                graphs   = {
                    graph: GraphDataBuilder(epidata_orchestrator)
                            .retrieve_static_graph(graph)
                            .build()
                    for graph in graphs_list
                }
            )
            dataloader_managers_dict[varvalue] = varvalue_databuilders

        self.dataloadermanagers = dataloader_managers_dict