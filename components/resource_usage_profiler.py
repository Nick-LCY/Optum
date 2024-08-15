from utils import get_all_pod_cpu_usage, timer
from utils.k8s import client as k8s_client
from models.profiler import EROTable
import os


class ResourceUsageProfiler:
    def __init__(self, data_path: str) -> None:
        self.ero_table = EROTable()
        self.data_path = data_path
        if not os.path.exists(data_path):
            return
        with open(data_path, "r") as file:
            for line in file.readlines():
                key = line.split(":")[0].split(",")
                value = line.split(":")[1]
                self.ero_table[key] = float(value)

    @timer("GetAllPodCPUQuota")
    def _get_all_pod_cpu_quota(self, node: str):
        return k8s_client.get_all_pod_cpu_quota(node)

    @timer("GetNodeERO")
    def get_node_ero(self, node: str) -> EROTable:
        pods_usage = get_all_pod_cpu_usage(node)
        pods_quota = self._get_all_pod_cpu_quota(node)
        pods_usage: dict[str, dict[str, float | str]] = {
            x: {"app": pods_quota[x]["app"], "cpu_usage": pods_usage[x]}
            for x in pods_usage
            if x in pods_quota
        }

        pod_names = list(pods_usage.keys())
        ero = EROTable()
        for i, pod_name_a in enumerate(pod_names):
            app_a = pods_usage[pod_name_a]["app"]
            for j in range(i, len(pod_names)):
                pod_name_b = pod_names[j]
                app_b = pods_usage[pod_name_b]["app"]
                if app_a == app_b:
                    continue
                ro = (
                    pods_usage[pod_name_a]["cpu_usage"]
                    + pods_usage[pod_name_b]["cpu_usage"]
                ) / (
                    pods_quota[pod_name_a]["cpu_quota"]
                    + pods_quota[pod_name_b]["cpu_quota"]
                )
                key = [app_a, app_b]
                ero[key] = max(ero.get(key, 0), ro)
        return ero

    @timer("UpdateERO")
    def update_ero(self, nodes: list[str]) -> EROTable:
        for node in nodes:
            ero = self.get_node_ero(node)
            for key in ero:
                self.ero_table[key] = max(self.ero_table.get(key, 0), ero[key])
        self.save_ero()
        return self.ero_table

    def save_ero(self):
        with open(self.data_path, "w") as file:
            lines = []
            for key in self.ero_table:
                lines.append(f"{','.join(key)}:{self.ero_table[key]}\n")
            file.writelines(lines)

    def get_ero(self) -> EROTable:
        return self.ero_table
