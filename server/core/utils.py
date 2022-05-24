import os
import tracemalloc

import psutil

process = psutil.Process(os.getpid())
tracemalloc.start()


def get_memory():
    return process.memory_info().rss / (1024 * 1024)
