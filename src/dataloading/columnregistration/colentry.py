from dataclasses import dataclass

from .transformation_params import TransformationParams
from .exceptions import InvalidColEntry, ColEntryMissingAttribute
from ...utils.types import ColumnType

@dataclass
class ColEntry:
    """
    Entry for a single column in the ``ColumnRegistry``. ``ColEntry`` Instances should
    only be created and accessed through ``ColumnRegistry``.

    Parameters
    ----------
    column_name : str
        Name of column as it appears in the final df of the ``EpiDataOrchestrator``.
    column_type : ColumnType
        Type of the column.
    transformation : bool
        Whether or not the column requires a transformation.
    _transformation_group : str | None
        Specifies what directs the transformation of this column. There are three 
        options:
        
        - ``'self'`` : individual transformation based on parameters from the column 
        itself.
        - ``{column_name}`` : the name of another ``ColEntry``.
        - ``None`` : no transformation group needed. This is only possible when 
        ``transformation`` == ``False``.

    _transformation_params : TransformationParams | None = None
        Dataclass that holds information on all transformations that have been done
        on the column.

    See Also
    --------
    ``ColumnRegistry`` 
        A collection of ``ColEntry`` instances, that interacts with entries.
    ``TransformationParams`` 
        A collection of parameters that guide the transformation of the column.

    Downstream
    ----------
    ``EpiDataOrchestrator`` Stores information on columns in ``ColEntry`` instances,
    which are stored in ``ColumnRegistry``.

    Examples
    --------
    >>> column_registration = ColumnRegistry()
    >>> column_registration.add_column(
    ...     'timestep',
    ...     'context'
    ...     )    
    >>> column_registration.add_column(
    ...     'target', 
    ...     'target',
    ...     transformation = True,
    ...     transformation_group = 'self'
    ...     )              
    """
    column_name : str
    column_type : ColumnType
    transformation : bool 
    _transformation_group :  str | None                   = None
    _transformation_params : TransformationParams | None  = None    
    
    def __post_init__(self):

        # lower case input
        self.column_name = self.column_name.lower()
        self._validate_input()

        # ensure lower case in transformation group
        if self._transformation_group:
            self._transformation_group = self._transformation_group.lower()

    def _validate_input(self) -> None:
        """validate against invalid states"""
        if not self.transformation:
            if self._transformation_group is not None:
                raise InvalidColEntry(
                    f"transformation is False, but _transformation_group is given for {self.column_name}."
                    )
            if self._transformation_params is not None:
                raise InvalidColEntry(
                    f"transformation is False, but _transformation_params is given for {self.column_name}."
                    )                

    @property
    def transformation_group(self) -> str:
        if self._transformation_group:
            return self._transformation_group
        else:
            raise ColEntryMissingAttribute(
                self.column_name, "transformation_group"
                )

    @property
    def transformation_params(self) -> TransformationParams:
        if self._transformation_params:
            return self._transformation_params
        else:
            raise ColEntryMissingAttribute(
                self.column_name, "transformation_params"
                )     
    
    def __repr__(self) -> str:
        representation = (
            f"<{self.__class__.__name__}("+
            f"column_name = {self.column_name}, " +
            f"column_type = {self.column_type}"
        )
        
        if self.transformation:
            representation += f", transformation = {self.transformation}"
            representation += f", transformation_group = {self._transformation_group}"            
            representation += f", transformation_params = {self._transformation_params}"                 
        
        representation += ")>"
        return representation
