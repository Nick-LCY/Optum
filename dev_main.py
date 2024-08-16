from components.scheduler import Scheduler
from components.interference_predictor import InterferencePredictor
from components.resource_usage_predictor import ResourceUsagePredictor
from models import Pod, Cluster

# inf_pred = InterferencePredictor({}, {})
# res_pred = ResourceUsagePredictor("data/ero_table", "data/mem_table")

# cluster = Cluster(["slave9"], [])
# scheduler = Scheduler(cluster, inf_pred, res_pred)
# print(scheduler.schedule([Pod("test", "test", cpu_requests=1, mem_requests=1024)], 100))

from components.interference_profiler import InterferenceProfiler

# InterferenceProfiler.train_ls(
#     "data/understanding_11/hardware_data.csv",
#     "data/understanding_11/node_data.csv",
#     "data/models",
# )

InterferenceProfiler.train_be(
    "data/understanding_11/hardware_data.csv",
    "data/understanding_11/node_data.csv",
    "data/understanding_11/jct_data.csv",
    "data/models",
)
