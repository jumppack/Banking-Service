import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger
from app.core.config import settings

def setup_logging():
    logger = logging.getLogger()
    
    # Set the minimum log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)
    
    # Remove all default handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)
        
    # Create the structured JSON formatter
    log_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    log_handler.setFormatter(formatter)
    
    # Add the Stream (Console) JSON handler
    logger.addHandler(log_handler)
    
    # Add Rotating File Handler for persistence
    os.makedirs("logs", exist_ok=True)
    file_handler = RotatingFileHandler(
        "logs/banking.log",
        maxBytes=10485760, # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Override uvicorn access and error loggers
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = [log_handler, file_handler]
        uvicorn_logger.setLevel(log_level)
        uvicorn_logger.propagate = False
    
    return logger
