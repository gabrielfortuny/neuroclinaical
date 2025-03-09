import json
import typing
import threading


class DatabaseCredentials:
    """
    Description:
    Provides database access and stores credentials from env for fast access

    Invariants:

    """
    _instance = None  # ✅ Shared instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)  # ✅ Creates the instance only once
        return cls._instance

    def initialize(self, value):
        """
        Manually initializes the singleton instance.
        Should be called only once after creation.
        """
        if hasattr(self, "_initialized"):  # Prevent re-initialization
            raise RuntimeError("Singleton instance has already been initialized")

        self.value = value
        self._initialized = True



def database_controller(query: str) -> json:
    """
    Description:

    Requires:
    Query is a string for the
    Modifies:
    Effects:

    @param query: String to be used for query, presumably a SQL query
    """

    return ""
