import threading
from typing import TypeVar, Generic, Type, Union, Any
from PyQt5.QtCore import QObject, pyqtSignal

# Define a Type Variable for Generic support
T = TypeVar('T')

class ObservableState(QObject, Generic[T]):
    """
    Wraps a data variable with static type hinting and optional runtime type enforcement.
    """
    changed = pyqtSignal(object)

    def __init__(self, initial_value: T = None, target_type: Union[Type[T], None] = None):
        super().__init__()
        self._value = initial_value
        self._mutex = threading.RLock()
        self._frozen = False
        
        # Optional: Save the explicit type for runtime validation
        self._target_type = target_type 
        
        # Runtime check on initial value if a type was provided
        if self._target_type and initial_value is not None:
            self._validate_type(initial_value)

    def _validate_type(self, value: Any) -> None:
        if not isinstance(value, self._target_type):
            raise TypeError(f"Expected type {self._target_type.__name__}, got {type(value).__name__}")

    @property
    def value(self) -> T:
        with self._mutex:
            return self._value
        
    def set(self, new_value: T):
        with self._mutex:
            if self._frozen:
                raise RuntimeError("State mutation rejected: Object is currently locked.")
            
            # Enforce type check at runtime if target_type was passed to __init__
            if self._target_type:
                self._validate_type(new_value)
                
            self._value = new_value
        
        self.changed.emit(new_value)


    @value.setter
    def value(self, new_value: T):
        self.set(new_value)

    def subscribe(self, callback):
        self.changed.connect(callback)

    def lock(self):
        self._mutex.acquire()
        self._frozen = True

    def unlock(self):
        self._frozen = False
        self._mutex.release()

    def __enter__(self):
        self.lock()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unlock()