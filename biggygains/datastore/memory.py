from .interface import Datastore


"""
Simple in memory datastore with no persistence. Useful for testing
"""
class InMemoryDatastore(Datastore):
    def __init__(self):
        self.data = {}

    def initialize(self):
        return True

    def clear(self):
        self.data = {}
        return True

    def store_data(self, key, value):
        self.data[key] = value
        return True

    def retrieve_data(self, key):
        return self.data.get(key, None)
