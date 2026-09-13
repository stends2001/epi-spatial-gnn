from typing import Optional 
import pandas as pd 
import os
from pathlib import Path

from .exceptions import MetricsDFError

class MetricsDFStateMixin:
    """"
    """

    metrics_df : Optional[pd.DataFrame]
    path_exp : Path

    metrics_df_filename: str

    def save_metrics(self):
        if self.metrics_df is None:
            raise MetricsDFError(
                'no attribute metrics_df. Run `compile_metrics()` first.'
                )

        self.metrics_df.to_csv(os.path.join(self.path_exp, self.metrics_df_filename), index=False)    

    def load_metrics(self):
        if self.metrics_df is None:
            self.metrics_df = pd.read_csv(os.path.join(self.path_exp, self.metrics_df_filename)) 

        else:
            raise MetricsDFError('metrics_df already loaded')

        if not hasattr(self, 'model_names'):
            self.model_names = list(self.metrics_df['model'].unique())