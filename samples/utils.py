"""
Common utilities
"""

import os


def get_env_var_or_fail(env_var_name: str) -> str:
    """
    Get an environment variable or raise an exception if not found.

    :param env_var_name: The environment variable name.
    :return: The environment variable value.
    """
    env_var = os.getenv(env_var_name)
    if env_var is None:
        raise Exception(f"{env_var_name} environment variable is not set.")
    return env_var
