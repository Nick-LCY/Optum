from .base import BaselineScheduler
from random import choice
import pandas as pd
from ..models.types import *
from ..models import Cluster, Node, Pod
from logging import getLogger

logger = getLogger("NSigma")

SCHEDULER_NAME = "n-sigma-scheduler"


class NSigmaScheduler(BaselineScheduler):
    def __init__(
        self, cluster: Cluster, historical_node_data_path: str, n: int = 5
    ) -> None:
        super().__init__(cluster)
        self.node_data = pd.read_csv(historical_node_data_path)
        self.n = n

    def get_mean(self, node: Node) -> float:
        data = self.node_data.loc[self.node_data["node"] == node.name]
        return data["node_cpu"].mean()

    def get_std(self, node: Node) -> float:
        data = self.node_data.loc[self.node_data["node"] == node.name]
        return data["node_cpu"].std()

    def get_n_sigma(self, node) -> float:
        return self.n * self.get_std(node) + self.get_mean(node)

    def select(self, pod: Pod) -> Node:
        available_nodes: list[Node] = []
        self.cluster_lock.acquire()
        for node in self.cluster.nodes.values():
            if not self.check_mem_availability(node, pod):
                logger.info(f"NsigmaScheduler.select: [{node.name}] failed due to memory availability")
                continue
            # Check node CPU availability
            pod_cpu_util = self.cluster.get_app(pod.app_name).get_p95_pod_cpu_util()
            node_cpu_usage = self.get_n_sigma(node)
            if node_cpu_usage + pod_cpu_util > node.cpu_cap:
                logger.info(f"NsigmaScheduler.select: [{node.name}] failed due to CPU availability")
                continue
            available_nodes.append(node)
        logger.info(f"NsigmaScheduler.select: Available nodes [{'],['.join([x.name for x in available_nodes])}]")
        selected_node = choice(available_nodes)
        self.cluster.assign_pod_to_node(pod, selected_node)
        self.cluster_lock.release()
        logger.info(f"Final selection of <{pod.name}> is [{selected_node.name}]")
        return selected_node

    def run(self):
        super()._run(SCHEDULER_NAME)
