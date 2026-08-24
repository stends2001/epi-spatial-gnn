from typing import TYPE_CHECKING, List, assert_never
import pandas as pd

from .exceptions import EpiConfigLimitationError, EpiConfigValidationError
from ...utils import ExceptionReport, PathNotFound

if TYPE_CHECKING:
    from .epiconfig import EpiConfig

import logging
logger = logging.getLogger(__name__)

class EpiConfigValidator:
    """
    This is a  Utility class of EpiConfig that deals with the validation of input.
    Simply call `.validate()`. Warngings that do not thro exceptions may be printed.
    Alternatively, an IssueReported may be returned.
    """

    def __init__(self,
                 epiconfig: 'EpiConfig'):
        
        self.epiconfig = epiconfig 

    def validate(self):
        exceptions: List[Exception] = []
        exceptions = self._datapaths(exceptions)
        exceptions = self._current_limitations(exceptions)      
        exceptions = self._input(exceptions)  
        
        self._warnings()

        if len(exceptions) > 0:
            raise ExceptionReport(exceptions, context = "EpiConfig could not be created")        

        logger.debug('EpiConfig has been validated')            

    def _datapaths(self, exceptions: List[Exception]) -> List[Exception]:

        for property in self.epiconfig.path_manager.properties:

            path_attr = self.epiconfig.path_manager.get(property)

            if not path_attr.exists():
                exceptions.append(PathNotFound(path_attr)) 

        return exceptions        
    
    def _current_limitations(self, exceptions: List[Exception]) -> List[Exception]:
        """
        Validates any issues in the initialization of an EpiConfig instance. 
        These represent CURRENT limitations, which are also things for me to develop further.
        An CurrentEpiConfigError is thrown suggesting to adjust the input.
        """

        # temporal frequency
        if self.epiconfig.temporal_frequency not in ['m','w','d']:
            exceptions.append(EpiConfigLimitationError(f'invalid valid for temporal_frequency (currently). Value must be in ["m","w","d"]'))         

        return exceptions
    
    def _input(self, exceptions: List[Exception]) -> List[Exception]:
        """
        Validates discrepancies in the initialization of an EpiConfig instance. These represent
        actual issues or errors, so an EpiConfigError is thrown suggesting to adjust the input.
        """
        # temporal-related 
        if self.epiconfig.horizon_size < 1:
            exceptions.append(EpiConfigValidationError(f"horizon_size must be >= 1, got {self.epiconfig.horizon_size}"))
        
        if self.epiconfig.horizon_leadtime < 1:
            exceptions.append(EpiConfigValidationError(f"horizon_leadtime must be >= 1, got {self.epiconfig.horizon_leadtime}"))
        
        if self.epiconfig.sequence_length < 1:
            exceptions.append(EpiConfigValidationError(f"sequence_length must be >= 1, got {self.epiconfig.sequence_length}"))
        
        if self.epiconfig.lag_num < 1:
            exceptions.append(EpiConfigValidationError(f"number of lags must be >= 1, got {self.epiconfig.lag_num}"))
        
        if self.epiconfig.time_index_d and self.epiconfig.disease != 'covid_daily':
            exceptions.append(EpiConfigValidationError(f'time_index_d is only relevant to disease covid_daily'))


        # country-related
        match (self.epiconfig.country, self.epiconfig.level):

            case ('germany', 'nuts1' | 'nuts2' | 'nuts3'):
                pass

            case ('hungary', 'nuts1' | 'nuts2' | 'nuts3'):
                pass            

            case _:
                assert_never((self.epiconfig.country, self.epiconfig.level))                
        return exceptions
        
    def _warnings(self):
        """
        Validates some combinations of inputs that are likely not meant as such, and shouldn't disrupt the pipeline any further. 
        A EpiConfigWarning is thrown, not an exception
        """
        match (self.epiconfig.country, self.epiconfig.level):

            case ('hungary', 'nuts1'):
                logger.warning('Hungary - nuts1 units are very large (n = 3). Predictions may not be particulary informative.')

            case ('hungary', 'nuts2'):
                logger.warning('Hungary - nuts2 units are very large (n = 8). Predictions may not be particulary informative.')             

            case ('germany', 'nuts1'):
                logger.warning('Germany - nuts1 units are very large (n = 16). Predictions may not be particulary informative.')   
    
    def __repr__(self) -> str:
        representation = f"<{self.__class__.__name__}>"
        return representation 