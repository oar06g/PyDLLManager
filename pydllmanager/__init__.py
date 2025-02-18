"""
PyDLLManager - A library for effortlessly loading DLL files in Python.

This module provides a class and decorator for loading and accessing functions
from dynamic link libraries (DLLs) using the ctypes module.

Author: Omar Mohamed
Version: 1.1.0
Github: https://github.com/oar06g/PyDLLManager
"""

import ctypes
import os
import platform
import functools
import threading
from typing import Any, Callable

__all__ = ['DLLLoader', 'DllImprt', 'ctypes_type', 'DLLManagerError']

class DLLManagerError(Exception):
    """Custom exception class for PyDLLManager errors."""
    pass

class DLLLoader:
    """
    A class to load and interact with DLL files.

    Attributes:
        dll: The loaded DLL object.
        lock: A threading lock for thread-safe operations.

    Methods:
        get_function: Retrieve a function from the DLL with specified argument
                      and return types.
    """
    def __init__(self, dll_path: str):
        """
        Initialize the DLLLoader with the path to the DLL file.

        Args:
            dll_path (str): The path to the DLL file.

        Raises:
            FileNotFoundError: If the specified DLL file does not exist.
            DLLManagerError: If loading the DLL file fails.
        """
        self.lock = threading.Lock()
        if not os.path.exists(dll_path):
            raise FileNotFoundError(f"Library not found: {dll_path}")

        # Check the system's architecture
        arch = platform.architecture()[0]
        try:
            with self.lock:
                if arch == "32bit":
                    self.dll = ctypes.cdll.LoadLibrary(dll_path)
                elif arch == "64bit":
                    self.dll = ctypes.cdll.LoadLibrary(dll_path)
                else:
                    raise DLLManagerError(f"Unsupported architecture: {arch}")
        except OSError as e:
            raise DLLManagerError(f"Failed to load library: {e}")

    def get_function(self, func_name: str, argtypes=None, restype=None):
        """
        Retrieve a function from the DLL with the specified argument and return types.

        Args:
            func_name (str): The name of the function to retrieve.
            argtypes (list, optional): A list of argument types for the function.
            restype (type, optional): The return type of the function.

        Returns:
            function: The retrieved function with specified argument and return types.

        Raises:
            AttributeError: If the function is not found in the DLL.
            DLLManagerError: If retrieving the function fails.
        """
        try:
            with self.lock:
                func = getattr(self.dll, func_name)
                if argtypes:
                    func.argtypes = argtypes
                func.restype = restype
                print(f"Successfully loaded function {func_name} from DLL")
                return func
        except AttributeError:
            raise AttributeError(f"Cannot find function {func_name} in this library")
        except Exception as e:
            raise DLLManagerError(f"Error retrieving function {func_name}: {e}")

dll_loader_cache = {}

def DllImprt(dll_path: str, logging: bool = False) -> Callable:
    """
    A decorator to load a DLL function and call it with specified arguments.

    Args:
        dll_path (str): The path to the DLL file.
        logging (bool, optional): Whether to enable logging of function calls. Defaults to False.

    Returns:
        Callable: The decorated function with the loaded DLL function call.
    """
    def decorator(func: Callable) -> Callable:
        func_name = func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            if dll_path not in dll_loader_cache:
                dll_loader_cache[dll_path] = DLLLoader(dll_path)
            loader = dll_loader_cache[dll_path]
            annotations = func.__annotations__
            argtypes = [ctypes_type(annotations.get(param, Any)) for param in annotations if param != 'return']
            restype = ctypes_type(annotations.get('return', None))

            dll_func = loader.get_function(func_name, argtypes, restype)
            if logging:
                print(f"import {func_name}, args={args}, kwargs={kwargs}")
                print(f"type data argtypes={argtypes}, restype={restype}")

            result = dll_func(*args, **kwargs)
            if restype == ctypes.c_char_p and result:
                return (result.decode("utf-8") if result is not None else None)
            return result
        return wrapper
    return decorator

def ctypes_type(py_type: type) -> Any:
    """
    Map Python types to ctypes types.

    Args:
        py_type (type): The Python type to map.

    Returns:
        type: The corresponding ctypes type.
    """
    mapping = {
        int: ctypes.c_int,
        float: ctypes.c_double,
        str: ctypes.c_char_p,
        bool: ctypes.c_bool,
        None: ctypes.c_void_p,
        Any: ctypes.c_void_p,
        str: ctypes.c_wchar_p,
    }
    return mapping.get(py_type, ctypes.c_void_p)
