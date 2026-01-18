from sys import exit, stdout

from loguru import logger

from ..config import config


def logger_init() -> None:
    level = config.log.level.upper()
    if level not in ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]:
        logger.error(f"Invalid log level: {level}")
        level = "INFO"
    debug_mode = level in ["TRACE", "DEBUG"]
    log_format = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</> <light-red>|</> "
                  "<yellow>{thread:<5}</> <light-red>|</> "
                  "<magenta>{elapsed}</> <light-red>|</> "
                  "<level>{level:8}</> <light-red>|</> "
                  "<cyan>{name}<light-red>:</>{function}<light-red>:</>{line}</> "
                  "<light-red>-</> <level>{message}</>")
    logger.debug(f"Change logger level to {level}")
    logger.remove()
    if debug_mode:
        logger.add(stdout, format=log_format, level=level)
    logger.add(config.log.path, format=log_format, level=level, rotation=config.log.rotation,
               retention=config.log.retention, compression=config.log.compression)
    logger.add(lambda _: exit(-1), level="CRITICAL")
