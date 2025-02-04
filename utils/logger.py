import logging

def get_logger(name, level=logging.INFO):
    """
    Vraća logger sa zadatim imenom i nivoom logovanja.
    Ako logger još nema handler-e, kreira se StreamHandler sa unapred definisanim formatter-om.
    
    :param name: Ime logger-a
    :param level: Nivo logovanja (podrazumevano INFO)
    :return: Konfigurisani logger
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Kreiramo handler samo ako već nije postavljen
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
