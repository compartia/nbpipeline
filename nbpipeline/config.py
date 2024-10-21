import logging
from logging.handlers import RotatingFileHandler
import os

from pathlib import Path
from dotenv import load_dotenv
load_dotenv()


default_work_dir = Path.cwd().parent 
if "__file__" in globals():
    default_work_dir = Path(__file__).parent.parent
    print("default_work_dir=", default_work_dir)


workspace_dir =   os.getenv('NPB_WORK_DIR', default_work_dir)


def configure_logging():
    # Create a logger
    logger = logging.getLogger()
    log_level = os.environ.get('NBP_LOG_LEVEL', 'INFO')
    file_log_level = os.environ.get('NBP_LOG_LEVEL_FILE', 'INFO')
    logger.setLevel(getattr(logging, log_level))

    # Create formatters
    _fs = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    
    console_formatter = logging.Formatter(_fs)
    file_formatter = logging.Formatter(_fs)
 
    # Create console handler and set level to info
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Create file handler and set level to info
    log_file = workspace_dir / 'logfile.log'
    file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)    
    file_handler.setLevel(getattr(logging, file_log_level))

    file_handler.setFormatter(file_formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


# Call this function to configure logging
configure_logging()


logging.info(f'{workspace_dir=}')
data_dir = workspace_dir / 'data'
exported_data_dir = data_dir / 'exported_data'
 
exported_data_dir.mkdir(parents=True, exist_ok=True)
