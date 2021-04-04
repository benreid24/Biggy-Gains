import logging

logger = logging.getLogger(__name__)


"""
Base class for persistant data stores that may be hooked up to environments.
Datastores are simply key value string pairs that may be used by any module
or bot to persist data across restarts. Persisted data may be cleared for a
fresh start, but generally may be used to make bots resilient to crashes and
restarts
"""
class Datastore:
    def initialize(self) -> bool:
        """
        Initialize the datastore
        """
        logger.warning(f'initialize() is not implemented in {type(self).__name__}')
        return False

    def clear(self) -> bool:
        """
        Clears all persisted data
        """
        logger.warning(f'clear() is not implemented in {type(self).__name__}')
        return False

    def store_data(self, key: str, value: str) -> bool:
        """
        Stores the given key value pair
        """
        logger.warning(f'store_data() is not implemented in {type(self).__name__}')
        return False

    def retrieve_data(self, key: str) -> str:
        """
        Fetches the stored data for the given key. Returns None on error
        """
        logger.warning(f'retrieve_data() is not implemented in {type(self).__name__}')
        return None
