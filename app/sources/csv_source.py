import pandas as pd

def extract_csv(path, logger):
    logger.info("CSV extraction started")
    df = pd.read_csv(path, dtype=str)
    logger.info("CSV records: %s", len(df))
    return df
