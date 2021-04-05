from environment.interface import Environment


"""
A live environment. Makes real (or paper) trades and gets data from the real
world. Runs in realtime. Components can still be changed via the Environment
"""
class AlpacaEnvironment(Environment):
    def __init__(self):
        # TODO - create API. Use env vars for config or pass in
        # TODO - Create and set components

    def _initialize(self):
        # Custom setup?
        return True
