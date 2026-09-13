from pathlib import Path 
import os

from ..base import ExperimentConfig
from ...dataloading import EpiConfig

class ExperimentRunnerConfigMixin:

    epicfg : EpiConfig
    expcfg_to_save : ExperimentConfig

    exp_exists : bool 
    path_exp : Path 

    expcfg_filename : str 
    epicfg_filename : str
    
    def _update_experiment_cfg(self, 
                               new_epiconfig : EpiConfig, 
                               new_experimentconfig : ExperimentConfig) -> ExperimentConfig:
        """
        """
        # if path does exist 
        # save epiconfig and experimentconfig into pre-existing values (prex) and validate compatibility
        if self.exp_exists:
            current_expcfg = ExperimentConfig.load(self.path_exp / self.expcfg_filename)
            current_epicfg = EpiConfig.load_config(self.path_exp / self.epicfg_filename)
            current_epicfg.assert_equals(new_epiconfig)
            return current_expcfg.merge(new_experimentconfig)
        
        # else, experimentconfig doesn't change
        else:
            return new_experimentconfig        

        
    def _save_cfgs(self) -> None:
        """save experiment config and epi config. If exp path doesnt yet exist, will be created here."""
        if not self.exp_exists:
            os.mkdir(self.path_exp)    
            self.exp_exists = True

        self.epicfg.save_config(self.path_exp / self.epicfg_filename) 

        self.expcfg_to_save.save(self.path_exp / self.expcfg_filename)        
        