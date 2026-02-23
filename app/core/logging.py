import logging
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    
    # Set the minimum log level
    logger.setLevel(logging.INFO)
    
    # Remove all default handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)
        
    # Create the structured JSON formatter
    log_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    log_handler.setFormatter(formatter)
    
    # Add the JSON handler
    logger.addHandler(log_handler)
    
    return logger
