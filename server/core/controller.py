import os
import tracemalloc
import uuid

import psutil
from flask import current_app

process = psutil.Process(os.getpid())
tracemalloc.start()


def get_file_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def get_memory():
    return process.memory_info().rss / (1024 * 1024)


def upload(file):
    filename = f"{uuid.uuid4()}.{get_file_extension(file.filename)}"
    file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
    return filename
