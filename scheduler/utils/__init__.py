from ..models.types import *
from typing import TypeVar
import pickle
import logging

logger = logging.getLogger("Optum")
logger.info("Greetings from Optum!")
logger.info("We will use <> to represents pods")
logger.info("We will use [] to represents nodes")

T = TypeVar("T")


def load_obj(path: str, obj_class: T) -> T:
    with open(path, "rb") as file:
        obj: obj_class = pickle.load(file)
        return obj


def save_obj(path: str, obj) -> None:
    with open(path, "wb") as file:
        pickle.dump(obj, file)


def parse_cpu_unit(k8s_cpu_str: str) -> CPUCores:
    if k8s_cpu_str.endswith("m"):
        return float(k8s_cpu_str[:-1]) / 1000
    return float(k8s_cpu_str)
