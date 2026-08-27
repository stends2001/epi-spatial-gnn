import pandas as pd 
import geopandas as gpd
from dataclasses import dataclass

from ..utils import NonExistentAttributeEpiDataContainer
from ....utils.textformatting import checkmark

@dataclass
class RawEpiData:
    """
    """

    disease:                pd.DataFrame
    population_size:        pd.DataFrame
    shapedata:              gpd.GeoDataFrame
    region_harmonization:   pd.DataFrame    
    tokenization_map:       dict[str, int]
    
    _population_density:     pd.DataFrame | None = None
    
    @property
    def population_density(self) -> pd.DataFrame:
        df = self._population_density
        if df is None: 
            raise NonExistentAttributeEpiDataContainer(self.__class__.__name__, 'population_density')
        return df          

    def __repr__(self):
        representation = (f"<{self.__class__.__name__}(disease {checkmark}, "
                f"population_size {checkmark}, "
                f"shapedata {checkmark}, "               
                f"region_harmonization {checkmark}, "
                f"tokenization_map {checkmark}"                )
        
        if self._population_density is not None:
            representation += f", population_density {checkmark}"              

        return representation +")>"