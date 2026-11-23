import sys
from loguru import logger
from ua_ue_trade_mirror_etl.config import settings

settings.log_file.parent.mkdir(parents=True, exist_ok=True)

logger.remove()

# logowanie w konsoli
logger.add(
    sys.stderr,
    level="INFO",
    format="<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> |"
    " <level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    backtrace=True,
    diagnose=True,
)

# logowanie w pliku
logger.add(
    str(settings.log_file),
    level="DEBUG",
    rotation="10 MB",
    retention="2 days",
    encoding="utf-8",
    enqueue=True,
    backtrace=True,
    diagnose=True,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)

