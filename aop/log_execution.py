import functools

from aop.timer import timer


# The "Aspect" / "Advice"
def log_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[Before] Calling {func.__name__}...") # Before Advice
        timer.start(func.__name__)
        result = func(*args, **kwargs)
        print(f"[After] {func.__name__} executed successfully.") # After Advice
        timer.stop(func.__name__)
        return result
    return wrapper


def print_timers(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        for name, time in timer.timers.items():
            print_time(name, time)
        print_time("Total", sum(timer.timers.values()))
        return result
    return wrapper


def print_time(name, time):
    space = " " * (20 - len(name))
    print(f"{name}:{space}{time} seconds")
