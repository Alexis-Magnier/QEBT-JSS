from PyQt5.QtCore import QObject, pyqtSignal
from .ObservableState import ObservableState
from .AsyncFileLoader import AsyncFileLoader

from core import (
    SequenceGraph, StateSpaceGraph,
    PolicyTable, ResourceRegistry
)

import threading


class AppContext(QObject):
    """
    Single source of truth for the application state.
    Manages global status updates and system variables.
    """
    status_changed = pyqtSignal(str) # Async background job updates

    def __init__(self):
        super().__init__()
        # Main Reactive State Targets

        self.loader: AsyncFileLoader = None
        self.sequenceGraph = ObservableState[SequenceGraph](initial_value=None)
        self.stateSpaceGraph = ObservableState[StateSpaceGraph](initial_value=None)
        self.policyTable = ObservableState[PolicyTable](initial_value=None)
        self.resourceRegistry = ObservableState[ResourceRegistry](initial_value=None)
        
        self._status = "Idle"
        self._status_mutex = threading.Lock()
    
    @property
    def status(self) -> str:
        """Thread-safe getter for the current status."""
        with self._status_mutex:
            return self._status

    @status.setter
    def status(self, new_status: str):
        """
        Thread-safe setter. Updates the internal string and automatically
        broadcasts it to any listening UI component (like the status bar).
        """
        with self._status_mutex:
            if self._status == new_status:
                return # Skip redundant updates
            self._status = new_status
        
        # Emit outside the lock to prevent deadlocks in UI event loops
        self.status_changed.emit(new_status)