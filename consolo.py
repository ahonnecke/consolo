#!/usr/bin/env python3
"""Map an AWS lambda filesystem onto a local directory."""
import logging

from argdantic import ArgParser

from reloader import LambdaReloader

logger = logging.getLogger(__name__)

logging.getLogger("boto").setLevel(logging.CRITICAL)
logging.getLogger("botocore").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

parser = ArgParser()


@parser.command()
def main(
    profile_name: str,
    function_name: str,
    path: str,
    hot_reload: bool = True,
    verbose: bool = False
) -> None:
    """Entrypoint for AWS lambda hot reloader, CLI args in signature."""
    log_level = "INFO"
    if verbose:
        log_level = "DEBUG"

    logging.basicConfig(level=log_level)

    reloader = LambdaReloader(profile_name, function_name, path)

    reloader.validate_root()

    if hot_reload:
        # If hot reload, download the code, with clobber
        reloader.clone()
        # and start the daemon
        reloader.watch()
    else:
        # If not reload, just push whatever is there now.
        reloader.update_function_code()


if __name__ == "__main__":
    parser()
