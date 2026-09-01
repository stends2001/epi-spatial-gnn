import pandas as pd

from ..utils.types import DataSetSplit

class EvaluationPredictionsCompilation:
    """ 
    Stores all predictions and metrics. Dictionary stored in ``_data`` represents:
    dict[DATASET: 
        dict[HORIZON: 
            dict["predictions"  : pd.DataFrame, 
                    "metrics"   : pd.DataFrame]]]

    Per combination of dataset and horizon, there is a long table as follows in
    dict[DATASET][HORIZON]['predictions']
    _____________________________________________
    | timestamp | node | target | model | pred |

    and _metric_compilations
    ___________________________________
    | node | model | metric-cols ... |

    Methods
    -------
    ``add_data()``
        Add data to ``EvaluationPredictionsCompilation``.
    ``get_data()``
        Get data (dictionary with keys 'metrics' and 'predictions').

    Attributes
    ----------
    ``datasets``
        Which of ``'train'``, ``'val'`` and ``'test'`` have data stored.
    ``horizons``
        For which horizons data is stored.

    See Also
    --------
    ``Evaluator``
        A single ``EvaluationPredictionsCompilation`` is associated with an 
        ``Evaluator``.

    Downstream
    ----------
    Multiple models are fed into the same ``Evaluator``, which evaluates them in unison,
    through compiling an ``EvaluationPredictionsCompilation``.
    """

    def __init__(self, model_names: list[str]):
        self.model_names = model_names
        self._data: dict[str, dict[str, dict[str, pd.DataFrame]]] = {}

    # ======== DATA WORKING ====== #
    def add_data(self, 
                 predictions: pd.DataFrame, 
                 metrics: pd.DataFrame, 
                 horizon: int, 
                 dataset: DataSetSplit):
        """
        Adds data to self._data to [dataset][horizon]

        Parameters
        ----------
        predictions : pd.DataFrame
            Predictions dataframe with columns
            - ``'timestamp'``
            - ``'node'``
            - ``'target'``
            - ``'pred'``         
            - ``'model'``
        metrics : pd.DataFrame
            Metrics dataframe with columns 
            - ``'node'``
            - ``'mode'``
            - a column for each metrics
        horizon : int
            Integer of horizon of prediction, starting at 0.
        dataset : Literal['train','val','test']
            Dataset of prediction.
        """
        horizon_str = f"horizon_{horizon}"
        
        if dataset not in self._data:
            self._data[dataset] = {} 
            
        self._data[dataset][horizon_str] = {'predictions': predictions, 'metrics' : metrics}

    def get_data(self, 
                 horizon: int, 
                 dataset: str) -> dict[str, pd.DataFrame]:
        """
        Gets data from self._data, from [dataset][horizon]

        Parameters
        ----------
        horizon: int
            integer of horizon of prediction
        dataset: Literal['train','val','test']
            dataset of prediction

        Returns
        -------
        Dict[str, pd.DataFrame]
            keys:
            - 'predictions'
            - 'metrics'
            values:
            - predictions_df: columns TODO
            - metrics_df: columns TODO
        """
        horizon_str = f"horizon_{horizon}"

        if dataset not in self._data:
            raise ValueError('data not found')
        
        return self._data[dataset][horizon_str]         
    
    @property
    def datasets(self) -> list[str]:
        """returns a list of datasets inside the main data dictionary"""
        return list(self._data.keys())

    @property
    def horizons(self) -> dict[str, list[str]]:
        """returns a list of horizons inside the main data dictionary. Outputted per dataset"""  
        dataset_horizons = {}
        for dataset in self.datasets:
            horizons                    = list(self._data[dataset].keys())
            dataset_horizons[dataset]   = horizons
        return dataset_horizons

    def __repr__(self) -> str:
        """repr of horizons-property basically"""
        representation = f"<{self.__class__.__name__}(" 
        
        representation += f"{self.horizons}" if len(self.horizons) else "empty"
        
        representation += ")>"
        return representation     