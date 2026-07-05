import sys
import json
from datetime import datetime
from loguru import logger
from quantum_os.core.config import settings, Environment

class JSONFormatter:
    """Custom JSON formatter for structured logging"""
    
    @staticmethod
    def format(record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record["level"].name,
            "module": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
            "environment": settings.ENVIRONMENT,
        }
        
        # Add extra fields if present
        if record.get("extra"):
            log_entry["extra"] = record["extra"]
        
        return json.dumps(log_entry) + "\n"

def setup_logging():
    """Configure logging for the application"""
    
    # Remove default handler
    logger.remove()
    
    # Console handler with colors (for development)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
        filter=lambda record: settings.ENVIRONMENT != Environment.PRODUCTION
    )
    
    # Console handler with JSON (for production)
    logger.add(
        sys.stdout,
        format=JSONFormatter.format,
        level=settings.LOG_LEVEL,
        filter=lambda record: settings.ENVIRONMENT == Environment.PRODUCTION
    )
    
    # File handler - all logs
    logger.add(
        settings.LOG_FILE,
        rotation="00:00",
        retention="30 days",
        compression="gz",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
    )
    
    # File handler - errors only
    logger.add(
        "logs/errors_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        compression="gz",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
    )
    
    return logger

# Create logger instance
log = setup_logging()