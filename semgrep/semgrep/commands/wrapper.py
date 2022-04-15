import sys
from functools import wraps
from typing import Any
from typing import Callable

from semgrep import __VERSION__
from semgrep.error import FATAL_EXIT_CODE
from semgrep.error import OK_EXIT_CODE
from semgrep.error import SemgrepError
from semgrep.metric_manager import metric_manager
from semgrep.verbose_logging import getLogger


def command_wrapper(func: Callable) -> Callable:
    """
    Adds the following functionaity to our subcommands:
    - Enforces that exit code 1 is only for findings
    - Sets global logging level
    - Handles metric sending before exit

    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        # When running semgrep as a command line tool
        # silence root level logger otherwise logs higher
        # than warning are handled twice
        logger = getLogger("semgrep")
        logger.propagate = False
        metric_manager.set_version(__VERSION__)

        try:
            func(*args, **kwargs)
        # Catch custom exception, output the right message and exit
        except SemgrepError as e:
            metric_manager.set_return_code(e.code)
            sys.exit(e.code)
        except Exception as e:
            logger.exception(e)
            sys.exit(FATAL_EXIT_CODE)
        else:
            metric_manager.set_return_code(OK_EXIT_CODE)
            sys.exit(OK_EXIT_CODE)
        finally:
            metric_manager.send()

    return wrapper
