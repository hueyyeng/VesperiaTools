import os
import logging

from exceptions.files import (
    InvalidFileException,
    InvalidFourCCException,
)

logger = logging.getLogger(__name__)


def check_fourcc(fourcc, file_path):
    """Check FOURCC code of a file

    Parameters
    ----------
    fourcc : str
        The expected FOURCC value
    file_path : str
        Path to file

    Returns
    -------
    None

    """
    if not isinstance(file_path, str) or not os.path.isfile(file_path):
        raise InvalidFileException(file_path)
    file_header = open(file_path, "rb").read(32)
    file_fourcc = file_header[:4]
    # Check file's FOURCC with expected FOURCC in bytes representation
    if file_fourcc != fourcc.encode('utf-8'):
        logger.warning({
            "msg": f"Not an {fourcc} file!",
            "fourcc": str(file_fourcc),
            "file_header": str(file_header),
        })
        raise InvalidFourCCException(fourcc, file_fourcc)
