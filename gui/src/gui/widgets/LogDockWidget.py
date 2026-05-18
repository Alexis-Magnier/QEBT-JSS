from datetime import datetime
from PyQt5.QtWidgets import QDockWidget, QTextEdit
from PyQt5.QtGui import QTextCursor
import logging
from PyQt5.QtCore import QObject, pyqtSignal


class LogHandler(QObject, logging.Handler):
    # Custom signal that sends (LogLevelString, FormattedMessage)
    new_log_signal = pyqtSignal(str, str)

    def __init__(self):
        QObject.__init__(self)
        logging.Handler.__init__(self)
        
        # Optional: Set a default format for the message body
        self.setFormatter(logging.Formatter('%(name)s - %(message)s'))

    def emit(self, record):
        """Triggered automatically by the logging module when a log occurs."""
        try:
            # Format the message body using the standard logging formatter
            msg = self.format(record)
            level = record.levelname  # e.g., "INFO", "WARNING", "ERROR"
            
            # Emit the signal safely to the main GUI thread
            self.new_log_signal.emit(level, msg)
        except Exception:
            self.handleError(record)



class LogRenderSystem(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("System Log Console", parent)
        
        # Configure layout features (Cannot be closed)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        
        # Initialize the text edit console
        self.console_widget = QTextEdit()
        self.console_widget.setReadOnly(True)
        
        # Base style: dark background, default light gray text
        self.console_widget.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e; 
                color: #dcdcdc; 
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11pt;
            }
        """)
        self.setWidget(self.console_widget)
        
        # Color mapping for different log levels
        self.LOG_COLORS = {
            "DEBUG": "#808080",    # Gray
            "INFO": "#00ff00",     # Neon Green
            "WARNING": "#ffaa00",  # Amber/Orange
            "ERROR": "#ff3333",    # Red
            "SUCCESS": "#00aaff"   # Cyan Blue
        }

        # Print initial safety logs
        self.log("INFO", "Reactive event loop initialized safely.")
        self.log("INFO", "Layout boundaries computed.")

    def log(self, level: str, message: str):
        """Appends a timestamped, color-coded log message to the console."""
        level = level.upper()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        color = self.LOG_COLORS.get(level, "#ffffff") # Default to white if level unknown
        
        # Construct the HTML formatted log entry
        log_entry = (
            f'<span style="color: #6a9955;">[{timestamp}]</span> '
            f'<span style="color: {color}; font-weight: bold;">[{level}]</span> '
            f'<span style="color: #ffffff;">{message}</span>'
        )
        
        # Append and auto-scroll to the bottom
        self.console_widget.append(log_entry)
        self.console_widget.moveCursor(QTextCursor.MoveOperation.End)

    def clear_logs(self):
        """Clears the console screen."""
        self.console_widget.clear()