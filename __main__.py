import logging
from lib.logutils import file_handler, console_handler
from MSPR import Application


def handle_exception(type, value, traceback):
    l = logging.getLogger("mspr.__main__")
    l.critical("Unhandled exception", exc_info=(type, value, traceback))
    exit(1)


if __name__ == "__main__":
    l = logging.getLogger("mspr")
    l.setLevel(logging.TEST)
    l.addHandler(file_handler)
    l.addHandler(console_handler)
    app = Application(
        title="MSPR: Masutty's Private Server Resetter",
        width=400,
        height=250,
        exceptionHandler=handle_exception,
    )
    app.root.mainloop()
