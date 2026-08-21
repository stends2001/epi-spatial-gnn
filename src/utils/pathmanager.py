from pathlib import Path

class PathManager:
    """ 
    Manages paths in this projects

    Attributes
    ----------
    - `project_root`
    - `data`
    - `src`
    - `exp_out`
    - `results`
    """
    def __init__(self):
        self.project_root   = Path(__file__).resolve().parent.parent.parent 
        self.data           = self.project_root / 'data'
        self.src            = self.project_root / 'src'
        self.exp_out        = self.project_root / 'outcomes'
        self.results        = self.project_root / 'results'
        self.figures        = self.project_root / 'results' / 'figures'