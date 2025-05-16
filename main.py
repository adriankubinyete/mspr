import logging

from lib.logutils import console_handler, file_handler
from MPSR import Application


def handle_exception(type, value, traceback):
    logger = logging.getLogger("mpsr.__main__")
    logger.critical("Unhandled exception", exc_info=(type, value, traceback))
    exit(1)


if __name__ == "__main__":
    logger = logging.getLogger("mpsr")
    logger.setLevel(logging.TEST)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    app = Application(
        title="MPSR: Masutty's Private Server Resetter",
        width=400,
        height=250,
        exceptionHandler=handle_exception,
    )
    app.root.mainloop()
