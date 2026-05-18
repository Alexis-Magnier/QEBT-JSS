import json
from PyQt5.QtCore import QThread, pyqtSignal

class AsyncFileLoader(QThread):
    """
    Safely opens, reads, and parses a file on a secondary thread,
    then emits the structured data to the main thread.
    """
    # Define the signal to carry the parsed data structure (e.g., a dict)
    finished_loading = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                # Do the heavy I/O and parsing HERE on the background thread
                raw_data = file.read()
                
                # Assuming it's a JSON file for your graph layout:
                parsed_dict = json.loads(raw_data)
                
            # Safely emit the plain Python dictionary across the thread boundary
            self.finished_loading.emit(parsed_dict)
            
        except Exception as e:
            # Broadcast errors safely back to the UI thread if something breaks
            self.error_occurred.emit(str(e))