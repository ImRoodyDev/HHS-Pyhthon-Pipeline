import time
import logging
from pathlib import Path

def timer(func):
    def fn_wrapper(*args, **keyargs):
        start_tock = time.time()
        result = func(*args, **keyargs)
        end_tock = time.time()
        print(f"Function {func.__name__} took {end_tock - start_tock:.4f} seconds to execute.")
        return result
    return fn_wrapper


def setup_logger(name, log_file):
    """
    Configureert een logger die naar zowel console als logbestand schrijft.
    
    Args:
        name: Naam van de logger
        log_file: Pad naar het logbestand (bijv. "logs/sdm_load.log")
    
    Returns:
        Logger object
    """
    # Maak logs directory aan als deze niet bestaat
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configureer logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Verwijder bestaande handlers om duplicaten te voorkomen
    logger.handlers = []
    
    # Format
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
