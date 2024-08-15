from .k8s import client as k8s_client
from .prom import client as prom_client
from custom_types import *
from typing import TypeVar
from dataclasses import dataclass
import pickle, logging
from timer.timer import get_timer

timer = get_timer(logging.INFO)
logging.basicConfig(level=logging.INFO)
node_ip_mapping = k8s_client.get_node_all_node_ip()
T = TypeVar("T")


class Pod:
    def __init__(self, name: str, namespace: str, node: str, type: str) -> None:
        self.name = name
        self.namespace = namespace
        self.node = node
        self.type = type


@timer("Utils:GetAllPods")
def get_pods(node: str) -> dict[PodName, Pod]:
    pods = k8s_client.get_pods(node)
    results: dict[PodName, Pod] = {}
    for pod in pods:
        pod_name = pod.metadata.name
        pod_namespace = pod.metadata.namespace
        pod_type = "ls" if pod_namespace in ["hotel-reserv", "social-network"] else "be"
        results[pod_name] = Pod(pod_name, pod_namespace, node, pod_type)
    return results


@timer("Utils:GetBEPods")
def get_be_pods(node: str) -> dict[PodName, Pod]:
    pods = get_pods(node)
    results: dict[PodName, Pod] = {}
    for pod_name in pods:
        pod = pods[pod_name]
        if pod.type == "be":
            results[pod_name] = pod
    return results


@timer("Utils:GetLSPods")
def get_ls_pods(node: str) -> dict[PodName, Pod]:
    pods = get_pods(node)
    results: dict[PodName, Pod] = {}
    for pod_name in pods:
        pod = pods[pod_name]
        if pod.type == "ls":
            results[pod_name] = pod
    return results


@timer("Utils:GetNodeCPUCapacity")
def get_node_cpu_capacity(node: str) -> CPUCores:
    return k8s_client.get_node_cpu_capacity(node)


@timer("Utils:GetNodeMemCapacity")
def get_node_mem_capacity(node: str) -> MemInMB:
    return k8s_client.get_node_mem_capacity(node)


@timer("Utils:GetNodeCPUUsage")
def get_node_cpu_usage(node: str) -> UsedCores:
    response = prom_client.fetch_node_cpu_usage([node_ip_mapping[node]])
    utilization = float(response.json()["data"]["result"][0]["value"][1])
    all_cores = get_node_cpu_capacity(node)
    return utilization * all_cores


@timer("Utils:GetNodeMemAllocated")
def get_node_mem_allocated(node: str) -> MemInMB:
    return k8s_client.get_node_mem_allocated(node)


@timer("Utils:GetAllPodCPUUsage")
def get_all_pod_cpu_usage(node: str) -> dict[str, UsedCores]:
    response = prom_client.fetch_pod_cpu_usage_by_node(node)
    return {
        x["metric"]["pod"]: float(x["value"][1])
        for x in response.json()["data"]["result"]
    }

@dataclass
class PodMemUsage:
    name: str
    namespace: str
    mem: MemInMB


def get_pod_mem_usage() -> list[PodMemUsage]:
    results: list[PodMemUsage] = []
    response = prom_client.fetch_pod_mem_usage()
    for data in response.json()["data"]["result"]:
        name = data["metric"]["pod"]
        namespace = data["metric"]["namespace"]
        mem = float(data["value"][1]) / 1024 / 1024
        results.append(PodMemUsage(name, namespace, mem))
    return results


@timer("Utils:GetMaxPodCPUUsage")
def get_max_pod_cpu_usage(node: str) -> UsedCores:
    return max([x for x in get_all_pod_cpu_usage(node).values()])


def load_obj(path: str, obj_class: T) -> T:
    with open(path, "rb") as file:
        obj: obj_class = pickle.load(file)
        return obj


def save_obj(path: str, obj) -> None:
    with open(path, "wb") as file:
        pickle.dump(obj, file)
