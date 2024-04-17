def format_float(val, n=2):
    """
    Return a given value with n decimal places.
    - inputs:
        - val: The value to be formatted.
        - n: Number of decimal places (int; default is 2).
    - output:
        - val: Formatted float as a string with n decimal places if val is a float.
            Or the original value if val is not a float.
    """
    if isinstance(val, float):
        # Create format string dynamically
        format_str = "{:." + str(n) + "f}"
        return format_str.format(val)
    else:
        return val
