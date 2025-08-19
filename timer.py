import time
from functools import wraps
from loguru import logger
from typing import Callable, Any, Tuple


def format_timedelta(seconds: float) -> str:

    if seconds < 0:
        return "N/A"

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{int(days)}d")
    if hours > 0:
        parts.append(f"{int(hours)}h")
    if minutes > 0:
        parts.append(f"{int(minutes)}m")

    parts.append(f"{seconds:.4f}s")

    return "".join(parts)


def time_recorder(func: Callable) -> Callable:

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Tuple[Any, float]:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time

        formatted_time = format_timedelta(run_time)

        logger.info(
            f"Function '{func.__name__}' ran in {run_time:.4f} seconds ({formatted_time})."
        )

        return result, run_time

    return wrapper


@time_recorder
def example_long_task(seconds: int):

    print(f"Executing example_long_task for {seconds} seconds...")
    time.sleep(seconds)
    print("Execution complete.")
    return "Task finished"


if __name__ == "__main__":

    task_result, task_run_time = example_long_task(10)

    print(f"Task returned: {task_result}")
    print(f"Actual run time: {task_run_time:.4f} seconds")

 
