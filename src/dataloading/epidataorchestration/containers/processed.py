import pandas as pd 
from dataclasses import dataclass

from ..utils import NonExistentAttributeEpiDataContainer
from ....utils.textformatting import checkmark

@dataclass
class ProcessedEpiData:
    """
    Datacontainer for processed-data
    filtered on dates, added incidence column if necessary

    Parameters:
    ----------
    epidata: pd.DataFrame
        
    # optional
    population_size: pd.DataFrame
    population_density: pd.DataFrame
    gisd: pd.DataFrame
    population_age: pd.DataFrame
    """           
    epidata:     pd.DataFrame

    _population_size:    pd.DataFrame | None = None
    _population_density: pd.DataFrame | None = None
    
    @property
    def population_size(self) -> pd.DataFrame:
        df = self._population_size
        if df is None: 
            raise NonExistentAttributeEpiDataContainer(self.__class__.__name__, 'population_size')
        return df      
    
    @property
    def population_density(self) -> pd.DataFrame:
        df = self._population_density
        if df is None: 
            raise NonExistentAttributeEpiDataContainer(self.__class__.__name__, 'population_density')
        return df      
             

    def __repr__(self):
        representation = (f"<{self.__class__.__name__}(epidata {checkmark}")

        if self._population_size is not None:
            representation += f", population_size {checkmark}"

        if self._population_density is not None:
            representation += f", population_density {checkmark}"

        representation += ")>"
        return representation