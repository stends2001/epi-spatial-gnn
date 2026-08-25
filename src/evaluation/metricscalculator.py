import numpy as np
from typing import cast
from scipy.stats import spearmanr, pearsonr

import inspect

class MetricsCalculatorBase:
    """
    Parent class for MetricsCalculators.

    Parameters
    ----------
    target_col: str
        ground truth column. Typically "incidence"
    pred_cols: str 
        prediction column. Typically "pred_q0" ... "pred_qQ"
    id_col: str
        geographical nodes column. Typically "node"
    temporal_col: str
        timestamps column. Typically "timestamp"

    Metrics-calculator for point predictions
    
    Includes the following (12) metrics in methods, each
    of which takes in y and yhats, and returns a float

    Methods
    -------
    - rmse    
    - mse
    - mae
    - smape
    - mape   
    - ccc     
    - r2
    - pearson
    - spearman
    - mbe 
    - vr
    - bcf
    """
    def __init__(self, 
                 target_col:    str,
                 pred_cols:     list[str],
                 id_col:        str,
                 temporal_col:  str,
                 ):
        
        self.target_col         = target_col
        self.pred_cols          = pred_cols
        self.id_col             = id_col
        self.temporal_col       = temporal_col

        self.supported_metrics  = self._return_supported_metrics()

    def _return_supported_metrics(self) -> list[str]:
        return [
            name for name, member in inspect.getmembers(self, predicate=inspect.ismethod)
            if not name.startswith("_")
            and name not in vars(MetricsCalculatorBase)  # exclude base class non-private methods
        ]

    def mse(self, y: np.ndarray, yhat: np.ndarray) -> float:
        """simple mse"""
        return float(np.mean((y - yhat) ** 2))

    def rmse(self, y: np.ndarray, yhat: np.ndarray) -> float:
        """simple mse"""        
        return float(np.sqrt(self.mse(y, yhat)))

    def mae(self, y: np.ndarray, yhat: np.ndarray) -> float:
        """simple mae"""        
        return float(np.mean(np.abs(y - yhat)))

    def smape(self, y: np.ndarray, yhat: np.ndarray, epsilon: float=1e-6) -> float | None:
        """simple smape. Returns None when target includes only zeroes"""
        mask = ~((y == 0) & (yhat == 0))

        y, yhat = y[mask], yhat[mask]
        
        if len(y) == 0:
            return None
        
        y    = np.where(y == 0, epsilon, y)
        yhat = np.where(yhat == 0, epsilon, yhat)
        denominator = np.maximum((np.abs(y) + np.abs(yhat)) / 2, epsilon)
        return float(np.mean(np.abs(y - yhat) / denominator) * 100)

    def mape(self, y: np.ndarray, yhat: np.ndarray, epsilon: float=1e-6) -> float | None:
        """simple mape. Returns None when target includes only zeroes"""        
        mask = y != 0
        y, yhat = y[mask], yhat[mask]
        
        if len(y) == 0:
            return None
        
        denominator = np.maximum(np.abs(y), epsilon)
        return float(np.mean(np.abs(y - yhat) / denominator) * 100)

    def r2(self, y: np.ndarray, yhat: np.ndarray) -> float | None:
        """
        Coefficient of determination: the fraction of the data's variance explained by model
        When zero variance in target: returns None
        """
        ss_res = np.sum((y - yhat) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        
        if ss_tot == 0:
            return None
        
        return float(1 - ss_res / ss_tot)

    def pearson(self, y: np.ndarray, yhat: np.ndarray) -> float | None:
        """
        Pearson correlation
        When zero variance in target or zero variance in predictions, 
        returns None
        """
        if np.all(y == y[0]) or np.all(yhat == yhat[0]):
            return None 
        
        corr = cast(float, pearsonr(y, yhat).statistic)     # type: ignore
        return corr

    def spearman(self, y: np.ndarray, yhat: np.ndarray) -> float | None:
        """
        Spearman correlation
        When zero variance in target or zero variance in predictions, 
        returns None
        """        
        if np.all(y == y[0]) or np.all(yhat == yhat[0]):
            return None 
        
        corr = cast(float, spearmanr(y, yhat, nan_policy = 'omit').statistic)     # type: ignore
        return corr        

    def mbe(self, y: np.ndarray, yhat: np.ndarray) -> float:
        """part of ccc: mean bias error"""
        mean_y, mean_yhat = y.mean(), yhat.mean()
        return mean_yhat - mean_y
    
    def vr(self, y: np.ndarray, yhat: np.ndarray) -> float | None:
        """part of ccc: variance ratio. when variation in target or in predictions is 0, None is returned"""
        var_y, var_yhat = y.var(ddof = 1), yhat.var(ddof = 1)
        
        if var_y == 0 or var_yhat == 0:
            return None
        
        sd_y, sd_yhat = np.sqrt(var_y), np.sqrt(var_yhat)
        return sd_yhat / sd_y

    def bcf(self, y: np.ndarray, yhat: np.ndarray) -> float | None:
        """
        Bias correction factor (part of CCC).
        Returns None when variation in target or predictions is 0.
        """
        vr = self.vr(y, yhat)
        if vr is None:
            return None

        mbe   = self.mbe(y, yhat)
        sd_y  = float(np.sqrt(y.var(ddof=1)))
        delta = mbe / sd_y

        return float((2 * vr) / (1 + vr**2 + delta**2))

    def ccc(self, y: np.ndarray, yhat: np.ndarray) -> float | None:
        """
        part of cross concordance coefficient: a mix of pearson and a matching coefficienct 
        when variation in target or in predictions is 0, None is returned
        """            
        mean_y, mean_yhat = y.mean(), yhat.mean()
        var_y = y.var(ddof=1)
        var_yhat = yhat.var(ddof=1)
        
        if var_y == 0 or var_yhat == 0:
            return None
        
        cov = np.sum((y - mean_y) * (yhat - mean_yhat)) / (len(y) - 1)
        numerator = 2 * cov
        denominator = var_y + var_yhat + (mean_y - mean_yhat) ** 2
        
        if denominator == 0:
            return None
        
        return float(numerator / denominator)
    
    def mda(self, y: np.ndarray, yhat: np.ndarray) -> float | None:
        """
        Mean Directional Accuracy.
        Fraction of timesteps where predicted direction of change 
        matches observed direction of change.
        Returns None if fewer than 2 observations.
        """
        if len(y) < 2:
            return None

        actual_dir    = np.sign(np.diff(y))
        predicted_dir = np.sign(np.diff(yhat))

        # exclude timesteps where actual direction is flat (no change)
        mask = actual_dir != 0
        if mask.sum() == 0:
            return None

        return float(np.mean(actual_dir[mask] == predicted_dir[mask]))

    @property
    def pred_col(self) -> str:
        
        return self.pred_cols[0]

    def __repr__(self) -> str:
        representation = f"<{self.__class__.__name__}(supported_metrics: {self.supported_metrics})>"
        return representation
    