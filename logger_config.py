import sys
from pathlib import Path
from loguru import logger

Path("logs").mkdir(exist_ok=True)

logger.remove()

#logowanie w konsoli
logger.add(
    sys.stderr,
    level="INFO",
    format="<blue>{time:YYYY-MM-DD HH:mm:ss}</blue> |"
    " <level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

#logowanie w pliku
logger.add(
    "logs/pytest.log",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
)
