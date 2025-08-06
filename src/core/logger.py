from src.config import app_settings
import colorlog

formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)s%(reset)s:\t\t%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

logger = colorlog.getLogger(__name__)

logger.setLevel(app_settings.log_level.value)
console_handler = colorlog.StreamHandler()
console_handler.setLevel(app_settings.log_level.value)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
