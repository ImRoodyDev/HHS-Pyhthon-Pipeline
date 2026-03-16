import time

def timer(func):
    def fn_wrapper(*args, **keyargs):
        start_tock = time.time()
        result = func(*args, **keyargs)
        end_tock = time.time()
        print(f"Function {func.__name__} took {end_tock - start_tock:.4f} seconds to execute.")
        return result
    return fn_wrapper
