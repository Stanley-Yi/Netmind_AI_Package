""" 
======
logger
======
@file_name: logger.py
@author: Bin Liang
@date: 2024-3-7

"""


# python standard packages
import os
from datetime import datetime

# python third-party packages
from loguru import logger 

# import from our modules


    
def create_logger(log_folder, rotation="00:00", compression='zip'):
    """
    Create a logger object with the specified log folder, rotation time, and compression format.

    Parameters:
        log_folder (str): The path to the folder where the log files will be stored.
        rotation (str, optional): The time of day when the log file should be rotated. Defaults to "00:00".
        compression (str, optional): The compression format for the rotated log files. Defaults to 'zip'.

    Returns:
        logger: The logger object.

    Example:
        >>> logger = create_logger('/path/to/logs', rotation='12:00', compression='gzip')
    """

    # Create the log folder if it does not exist
    now = datetime.now()

    # Create the log folder if it does not exist
    log_file_path = f"{log_folder}/{now.strftime('%Y-%m-%d')}/experiment-{now.strftime('%H-%M')}.log"
    logger.remove()

    # Create the logger object
    logger.add(log_file_path, rotation=rotation, compression=compression, enqueue=True)
    
    return logger

