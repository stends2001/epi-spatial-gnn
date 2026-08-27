import pandas as pd 
import geopandas as gpd
from dataclasses import dataclass

from ..utils import EpiDataTemporalSummary
from ....utils import Country, AdminLevel
from ....utils.textformatting import checkmark


@dataclass 
class ContextEpiData:
    """

    """    
    country : Country
    level : AdminLevel
    global_shapedata : gpd.GeoDataFrame   
    local_shapedata : gpd.GeoDataFrame     
    population_size : pd.DataFrame
    nodenames : pd.DataFrame
    region_harmonization : pd.DataFrame
    tokenization_map : dict[str, int]
    temporal_summary : 'EpiDataTemporalSummary'

    @property
    def num_nodes(self) -> int:
        return len(self.local_shapedata)

    def __repr__(self):
        representation = (f"<{self.__class__.__name__}(country = {self.country}, "
                f"level = {self.level}, "
                f"global_shapedata {checkmark}, "             
                f"local_shapedata {checkmark}, "                  
                f"population_size {checkmark}, "                   
                f"region_harmonization {checkmark}, "                                                                      
                f"nodenames {checkmark}, "
                f"tokenization_map {checkmark}, "
                f"temporal_summary {checkmark}"            
                )
        representation += ")>"
        return representation