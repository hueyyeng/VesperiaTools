import logging
import sys

from vesperiatools.vesperiatools_qt.application import Application

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main():
    app = Application([])
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
