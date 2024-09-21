from functools import partial
import subprocess
import sys
from threading import Thread
from time import sleep
from typing import Callable, Union
from loguru import logger

def do_nothing(text_or_rc: Union[str, int]) -> None:
    pass
def log_error_and_skip(rc: int, text: str) -> None:
    logger.error(f"Error {rc} from {text}")


def log_error_and_raise(rc: int, text: str) -> None:
    logger.error(f"Error {rc} from {text}")
    raise Exception(f"Error {rc} from {text}")
  
@logger.catch
def run_shell_command(
    command: str,
    stdout_callback: Callable[[str], None] = do_nothing,
    on_error: Callable[[int], None] = do_nothing,
) -> int:
    popen = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        stdout_callback(stdout_line)
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        return on_error(return_code)
    return return_code
  
@logger.catch
def create_super_user() -> None:
    # Migrate database
    run_shell_command(
        "cd /backend; python -m alembic upgrade head",
        stdout_callback=logger.info,
        on_error=partial(log_error_and_skip, text="migrate"),
    )

@logger.catch
def start_uvicorn():
    thread = Thread(
        target=run_shell_command,
        args=(
            "cd /backend; python app/main.py",
            logger.info,
            partial(log_error_and_raise, text="unicorn"),
        ),
        daemon=True,
    )
    thread.start()
    return thread
  
@logger.catch
def start_threaded_nginx() -> None:
    thread = Thread(
        target=run_shell_command,
        args=(
            "nginx -g \"daemon off;\"",
            logger.info,
            partial(log_error_and_raise, text="nginx"),
        ),
        daemon=True,
    )
    thread.start()
    return thread


if __name__ == "__main__":
    create_super_user()
    thread_uvicorn = start_uvicorn()
    thread_nginx = start_threaded_nginx()
    while True:
        sleep(1)
        if not thread_uvicorn.is_alive() or not thread_nginx.is_alive():
            logger.error("One of the threads died, please check logs")
            break