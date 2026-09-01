import numpy as np
from typing import cast
from scipy.stats import spearmanr, pearsonr
import inspect

class MetricsCalculator:
    """
    Metrics calculator for point predictions.
    Calculates 1` metrics, visible in the 'Methods' section.
    These take in predictions and ground truth, and return a float per region.
    
    Parameters
    ----------
    target_col: str
        Name of the target column. 
    pred_cols: str 
        Name of the prediction column.
    id_col: str
        Name of the geographical unit column.
    temporal_col: str
        Name of the time stamp column.

    Methods
    -------
    ``rmse``    
        Root Mean Square Error.
    ``mse``
        Mean Square Error.
    ``mae``
        Mean Absolute Error.
    ``smape``
        Symmetric Mean Absolute Percentage Error.
    ``mape``   
        Mean Absolute Percentage Error.
    ``ccc``     
        Concordance Correlation Coefficient.
    ``r2``
        Coefficient of Determination.
    ``pearson``
        Pearson correlation.
    ``nmb`` 
        Normalized Mean Bias.
    ``vr``
        Variance Ratio.
    ``bcf``
        Bias Correction Factor.
    """
    def __init__(self, 
                 target_col : str,
                 pred_cols : str,
                 id_col : str,
                 temporal_col : str,
                 ):
        
        self.target_col = target_col
        self.pred_cols = pred_cols
        self.id_col = id_col
        self.temporal_col = temporal_col

        self.supported_metrics = self._return_supported_metrics()

    def _return_supported_metrics(self) -> list[str]:
        return [
            name for name, member in inspect.getmembers(self, predicate=inspect.ismethod)
            if not name.startswith("_")
        ]

    def rmse(self, y: np.ndarray, yhat: np.ndarray) -> float:
        """simple mse"""        
        return float(np.sqrt(np.mean((y - yhat) ** 2)))

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

    def nmb(self, y: np.ndarray, yhat: np.ndarray) -> float | None:
        r"""
        Component of ccc: normalized mean bias.
        When variation in target or in predictions is 0, None is returned.

        $$ CCC = pearson * bcf $$

        Where

        $$ bcf = \frac{2}{\nu + \frac{1}{\nu} + u^2} $$

        Where

        $$ u = (\mu_{\hat{y}} - \mu_y) / \sqrt{\sigma_y\sigma_{\hat{y}}} $$ and

        $$ \nu = \sigma_{\hat{y}}/\sigma_y $$

        Here, $u$ represents the normalized mean bias nmb, and $\nu$ the standard
        deviation ratio. Positive values indicate over-prediction, negative
        values under-prediction.
        """
        mean_y, mean_yhat = y.mean(), yhat.mean()
        sd_y, sd_yhat = y.std(ddof=1), yhat.std(ddof=1)

        if sd_y == 0 or sd_yhat == 0:
            return None

        return float((mean_yhat - mean_y) / np.sqrt(sd_y * sd_yhat))

    def vr(self, y: np.ndarray, yhat: np.ndarray) -> float | None:
        r"""
        Component of ccc: variance ratio.
        When variation in target or in predictions is 0, None is returned.

        $$ CCC = pearson * bcf $$

        Where

        $$ bcf = \frac{2}{\nu + \frac{1}{\nu} + u^2} $$

        Where

        $$ u = (\mu_{\hat{y}} - \mu_y) / \sqrt{\sigma_y\sigma_{\hat{y}}} $$ and

        $$ \nu = \sigma_{\hat{y}}/\sigma_y $$

        Here, $u$ represents the normalized mean bias nmb, and $\nu$ the standard
        deviation ratio. Values below 1 indicate under-dispersed predictions
        relative to the target, values above 1 over-dispersed predictions.
        """
        var_y, var_yhat = y.var(ddof=1), yhat.var(ddof=1)

        if var_y == 0 or var_yhat == 0:
            return None

        sd_y, sd_yhat = np.sqrt(var_y), np.sqrt(var_yhat)
        return float(sd_yhat / sd_y)

    def bcf(self, y: np.ndarray, yhat: np.ndarray) -> float | None:
        r"""
        Bias correction factor (part of CCC).
        Returns None when variation in target or predictions is 0.

        $$ CCC = pearson * bcf $$

        Where

        $$ bcf = \frac{2}{\nu + \frac{1}{\nu} + u^2} $$

        with $u$ the normalized mean bias (see ``nmb``) and $\nu$ the standard
        deviation ratio (see ``vr``).
        """
        nu = self.vr(y, yhat)
        u = self.nmb(y, yhat)

        if nu is None or u is None:
            return None

        return float(2 / (nu + 1 / nu + u ** 2))

    def ccc(self, y: np.ndarray, yhat: np.ndarray) -> float | None:
        r"""
        Concordance correlation coefficient: a mix of pearson correlation and a
        bias correction factor (bcf), see Lin (1989).
        When variation in target or in predictions is 0, None is returned.

        $$ CCC = pearson * bcf $$

        Where

        $$ bcf = \frac{2}{\nu + \frac{1}{\nu} + u^2} $$

        Where

        $$ u = (\mu_{\hat{y}} - \mu_y) / \sqrt{\sigma_y\sigma_{\hat{y}}} $$ and

        $$ \nu = \sigma_{\hat{y}}/\sigma_y $$

        Computed directly from Lin's original covariance-based formula rather
        than via ``pearson() * bcf()``, to avoid compounding rounding error;
        the two are algebraically equivalent.
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

    def __repr__(self) -> str:
        representation = f"<{self.__class__.__name__}(supported_metrics: {self.supported_metrics})>"
        return representation
    