from .handlers import *
from AEFM.manager import manager
from AEFM import set_config_file, set_log_level

set_config_file("experiments/profiling/profiling.yaml")
set_log_level("info")

manager.run()
