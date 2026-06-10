"""
Description: Logging utility class
Author: Pengcheng_Hu hpc0813@outlook.com
Date: 2022-07-03 09:04:34
LastEditor: DeepSeek
LastEditTime: 2024-01-12
"""

import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from typing import Dict

import pytz


class CSTFormatter(logging.Formatter):
    """Formatter to convert log time to UTC+8 timezone"""

    def __init__(self, fmt=None, datefmt=None):
        super().__init__(fmt, datefmt)
        self.cst_tz = pytz.timezone("Asia/Shanghai")
        self.utc_tz = pytz.UTC

    def formatTime(self, record, datefmt=None):
        """Override formatTime method to use UTC+8 timezone"""
        # Convert timestamp to aware UTC time
        utc_dt = datetime.utcfromtimestamp(record.created).replace(tzinfo=self.utc_tz)
        # Convert to UTC+8 timezone
        cst_dt = utc_dt.astimezone(self.cst_tz)

        if datefmt:
            return cst_dt.strftime(datefmt)
        else:
            # Format as: 2024-01-12 15:30:45 CST
            return cst_dt.strftime("%Y-%m-%d %H:%M:%S") + " CST"


class Logger:
    """Logger utility class - stable version"""

    LOG_LEVELS: Dict[str, int] = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    fmt: str = (
        r"%(asctime)s  %(filename)s:%(lineno)d [%(process)d] [%(levelname)s] %(message)s"
    )

    def __init__(
        self,
        log_dir: str = "./logs/",
        when: str = "midnight",
        interval: int = 1,
        backupCount: int = 7,
        logger_name: str = "global_logger",
        use_utc_for_rotation: bool = True,
    ):
        """
        Initialize logger utility class

        Args:
            log_dir: Log directory path
            when: Log rotation time unit ('S', 'M', 'H', 'D', 'midnight', 'W0'-'W6')
            interval: Rotation interval
            backupCount: Number of backup files to keep
            logger_name: Logger name
            use_utc_for_rotation: Whether to use UTC time for log rotation
        """
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)

        # Configuration parameters
        self.when: str = when
        self.interval: int = interval
        self.backupCount: int = backupCount
        self.logger_name: str = logger_name
        self.use_utc_for_rotation: bool = use_utc_for_rotation
        self.logger: logging.Logger = None  # type: ignore
        self._setup()

    def _create_level_filter(self, target_level: int):
        """Create level filter"""

        class LevelFilter(logging.Filter):

            def filter(self, record):
                return record.levelno >= target_level

        return LevelFilter()

    def _create_exact_filter(self, target_level: int):
        """Only allow logs of exact level to pass"""

        class ExactFilter(logging.Filter):

            def filter(self, record):
                return record.levelno == target_level

        return ExactFilter()

    def _setup(self) -> None:
        """Initialize logging configuration"""
        self.logger = logging.getLogger(self.logger_name)

        # Prevent duplicate handler addition
        if self.logger.handlers:
            return

        self.logger.setLevel(logging.DEBUG)

        # 1. debug.log: Record all levels (DEBUG and above)
        debug_file = os.path.join(self.log_dir, "debug.log")  # type: ignore
        debug_handler = TimedRotatingFileHandler(
            filename=debug_file,
            when=self.when,
            interval=self.interval,
            backupCount=self.backupCount,
            encoding="utf-8",
            utc=self.use_utc_for_rotation,
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(CSTFormatter(self.fmt))
        debug_handler.addFilter(self._create_level_filter(logging.DEBUG))
        self.logger.addHandler(debug_handler)

        # # 2. info.log: Record INFO and above
        # info_file = os.path.join(self.log_dir, "info.log")
        # info_handler = TimedRotatingFileHandler(
        #     filename=info_file, when=self.when, interval=self.interval,
        #     backupCount=self.backupCount, encoding="utf-8", utc=self.use_utc_for_rotation
        # )
        # info_handler.setLevel(logging.INFO)
        # info_handler.setFormatter(CSTFormatter(self.fmt))
        # info_handler.addFilter(self._create_level_filter(logging.INFO))
        # self.logger.addHandler(info_handler)

        # # 3. error.log: Record ERROR and above only (serious errors)
        # error_file = os.path.join(self.log_dir, "error.log")
        # error_handler = TimedRotatingFileHandler(
        #     filename=error_file, when=self.when, interval=self.interval,
        #     backupCount=self.backupCount, encoding="utf-8", utc=self.use_utc_for_rotation
        # )
        # error_handler.setLevel(logging.ERROR)
        # error_handler.setFormatter(CSTFormatter(self.fmt))
        # error_handler.addFilter(self._create_level_filter(logging.ERROR))
        # self.logger.addHandler(error_handler)

        # Console output
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(CSTFormatter(self.fmt))
        self.logger.addHandler(console_handler)

    # Logging method wrappers
    def debug(self, msg: str, *args, **kwargs) -> None:
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log exception information (including stack trace)"""
        self.logger.exception(msg, *args, **kwargs)

    def get_logger(self) -> logging.Logger:
        """Get the raw logging.Logger object"""
        return self.logger

    def set_level(self, level: str) -> None:
        """Set logging level

        Args:
            level: One of 'debug', 'info', 'warning', 'error', 'critical'
        """
        if level.lower() in self.LOG_LEVELS:
            self.logger.setLevel(self.LOG_LEVELS[level.lower()])
            for handler in self.logger.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.setLevel(self.LOG_LEVELS[level.lower()])
        else:
            self.warning(f"Unknown log level: {level}, using default level INFO")
            self.logger.setLevel(logging.INFO)


# Create global logger instance
logger = Logger()
