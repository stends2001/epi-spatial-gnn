import time
import json
from typing import assert_never, TYPE_CHECKING, Dict
import pandas as pd
import geopandas as gpd
from ....utils.textformatting import checkmark

from ...epiconfig import EpiConfig

from ..containers import RawEpiData

# ============= DATA IMPORTATION CLASS =============
class EpiDataReader:
    """
    """
    
    def __init__(self, epiconfig: EpiConfig):
        self.epiconfig = epiconfig

    def orchestrate(self) -> RawEpiData:
        time_start = time.time()
        
        rawdata = RawEpiData(
            disease             = self._load_disease_data(),
            population_size     = self._load_population_size_data(),
            shapedata           = self._load_shapedata(),
            region_harmonization= self._load_regional_harm(),
            tokenization_map    = self._load_tokenization_map(),
        
            # optional data
            _population_density  = self._load_population_density()               if self.epiconfig.feature_popdens          else None         
        )

        time_end = time.time()

        return rawdata
  
    # ======= MANDATORY DATA ======= #

    def _load_disease_data(self) -> pd.DataFrame:
        """
        loads disease data cleaned from survstat

        German df looks like:
        __________________________________________________________
        | 'week' | 'nuts3_key' | 'cases' | 'year ' | 'timestamp' |

        Dutch df looks like:
        _______________________________________
        | 'timestamp' | 'cases' | 'lau_key ' | 
        """        
        filepath    = self.epiconfig.path_manager.get('cases')

        match self.epiconfig.country:
            case 'germany':
                initial_key  = 'kz_kreis'
                renamed_key  = 'nuts3_key' 

            case 'hungary':
                initial_key  = 'nuts3_key'
                renamed_key  = 'nuts3_key'                
            
            case _:
                assert_never(self.epiconfig.country)

                
        df = pd.read_csv(
            filepath,
            parse_dates = ['timestamp'],
            dtype       = {initial_key:  str, 
                           'cases':      int}
        ).rename(columns={initial_key: renamed_key})
        

        
        return df
    
    def _load_population_size_data(self) -> pd.DataFrame:
        """
        loads population data

        df looks like:
        _______________________________________________
        | 'level' | 'key' | 'year' | 'population_size |       
        """         
        filepath = self.epiconfig.path_manager.get('population_size')
        
        df = pd.read_csv(
            filepath,
            dtype = {'key' : str}
        )

        
        return df

    def _load_shapedata(self) -> gpd.GeoDataFrame:
        """
        loads shapedata for the specified nuts level

        gdf looks like:
        __________________________________________
        | 'level' | 'key' | 'geometry' |

        """          
        filepath = self.epiconfig.path_manager.get('shapefile')
        
        gdf             = gpd.read_file(filepath)
        gdf['key']      = gdf['key'].astype(str)
        
        
        return gdf
      
    def _load_regional_harm(self) -> pd.DataFrame:
        """
        loads harmonization data for nuts divisions in Germany

        df looks like this for Germany:
        _________________________________________________________________________________________
        | 'nuts3_key' | 'nuts2_key' | 'nuts1_key' | 'nuts3_name' | 'nuts2_name' | 'nuts1_name' |

        """  

        filepath = self.epiconfig.path_manager.get('region_harmonization')   
        
        df = pd.read_csv(filepath, sep='\t', dtype=str)
        

        return df

    def _load_tokenization_map(self) -> Dict[str, int]:
        
        filepath = self.epiconfig.path_manager.get('tokenization_map')       

        with open(filepath, "r") as f:
            tokenization_map = json.load(f)
        

        return tokenization_map   

    # optional data
    def _load_population_density(self) -> pd.DataFrame:
        """
        loads population density data for the specified nuts level

        df looks like:
        __________________________________________________________________
        | 'level' | 'key' | 'year' | 'population_density' |

        """          
        filepath = self.epiconfig.path_manager.get('population_density')
        
        df = pd.read_csv(
            filepath,
            dtype   = {'key': str},
        )
                
        return df
