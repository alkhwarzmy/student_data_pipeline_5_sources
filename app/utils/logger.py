import logging
from pathlib import Path

def get_logger(log_path="logs/pipeline.log"):
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("student_data_pipeline")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    return logger
