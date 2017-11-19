import json
import collections
import threading


class PersistentStore(collections.MutableMapping):
    def __init__(self, file: str):
        self.file = file
        self.lock = threading.Lock()
        try:
            with open(file, 'r') as store_file:
                self.store = json.load(store_file)
        except FileNotFoundError:
            self.store = {}

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        with self.lock:
            if self.__keytransform__(key) not in self.store or self.store[self.__keytransform__(key)] != value:
                self.store[self.__keytransform__(key)] = value
                with open(self.file, 'w') as store_file:
                    json.dump(self.store, store_file, indent=4)

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key

    def get_value(self, key: str, default=None):
        return self[key] if key in self else default
