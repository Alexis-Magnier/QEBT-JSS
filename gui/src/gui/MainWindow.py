from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt
import sys
import logging
import traceback

from .AppContext import AppContext
from .widgets.StateSpaceNetwork import StateSpaceNetworkWidget
from .AsyncFileLoader import AsyncFileLoader
from .widgets.LogDockWidget import LogRenderSystem, LogHandler
from .widgets.PolicyEditor import PolicyPropertyEditor

from core import (
    SequenceGraph, PolicyTable, ResourceRegistry
)

from PyQt5.QtWidgets import (
    QMainWindow, QDockWidget, QTextEdit, QPushButton, QLabel, QFileDialog,
    QListWidget, QWidget, QVBoxLayout, QLabel, QAction, QMessageBox
)

from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self, ctx:AppContext):
        super().__init__()
        logging.getLogger().name = "app"

        self.ctx = ctx
        self.setWindowTitle("Dynamic Docking Workspace Engine")
        self.resize(1100, 700)

        # 1. Enable advanced layout nesting and tabbing behavior
        self.setDockOptions(
            QMainWindow.AllowNestedDocks |  # Allow docks to be placed next to each other
            QMainWindow.AllowTabbedDocks |  # Allow docks to be dropped on top of each other as tabs
            QMainWindow.GroupedDragging     # Moving a tab group moves them all together
        )

        # 2. Establish a Central Widget (The core anchor that cannot be removed)
        self.central_canvas = StateSpaceNetworkWidget(self.ctx)
        self.setCentralWidget(self.central_canvas)

        # 3. Initialize dynamic dock panels
        self.init_dock_panels()
        self.create_menu_bar()

        self.setup_logging_bridge()
    
    def setup_logging_bridge(self):
        # Create the custom handler
        self.log_handler = LogHandler()
        self.log_handler.new_log_signal.connect(self.dock_console.log)
        
        self.log_handler.setLevel(logging.DEBUG)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(self.log_handler)
    
    def add_panel(self, title:str, initial_pos: Qt.DockWidgetArea) -> QDockWidget:
        d = QDockWidget(title, self)
        self.addDockWidget(initial_pos, d)
        return d

    def init_dock_panels(self):
        # --- PANEL A: Mermaid Code Editor (Initial State: Left Side) ---
        policy_editor = self.add_panel("Policy Editor", Qt.LeftDockWidgetArea)
        # Configure what user actions are allowed (Floating, Closing, Moving)
        policy_editor.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)
        policy_editor.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Add actual interactive widgets inside the dock shell
        editor_widget = PolicyPropertyEditor(self.ctx, self)
        policy_editor.setWidget(editor_widget)

        # --- PANEL B: Data Properties Inspector (Initial State: Right Side) ---
        dock_inspector = self.add_panel("Property Inspector", Qt.RightDockWidgetArea)
        dock_inspector.setFeatures(QDockWidget.AllDockWidgetFeatures) # Allows everything including closing
        
        inspector_container = QWidget()
        layout = QVBoxLayout(inspector_container)
        layout.addWidget(QLabel("<b>Node Attributes:</b>"))
        layout.addWidget(QListWidget()) # Mock attributes table list
        dock_inspector.setWidget(inspector_container)

        self.dock_console = LogRenderSystem(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock_console)

        # 4. Optional: Force specific panels to stack together as tabs out of the box
        # self.tabifyDockWidget(dock_inspector, dock_editor)
    
    def create_menu_bar(self):
        # 1. Get the built-in menu bar object
        menu_bar = self.menuBar()

        # 2. Add top-level menus (Dropdowns)
        file_menu = menu_bar.addMenu("&File")
        edit_menu = menu_bar.addMenu("&Edit")
        help_menu = menu_bar.addMenu("&Help")

        # 3. Create Actions for the File Menu
        open_action = QAction("&Open file...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open a file")
        open_action.triggered.connect(self.open_file_callback)

        import_action = QAction("&Import file...", self)
        import_action.setShortcut("Ctrl+Shift+O")
        import_action.setStatusTip("Extend current session data with imported file")
        import_action.triggered.connect(self.extend_file_callback)

        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close) # Built-in close slot

        # 4. Add Actions to the File Menu
        file_menu.addAction(open_action)
        file_menu.addAction(import_action)
        file_menu.addSeparator() # Visual dividing line
        file_menu.addAction(exit_action)

        # 5. Create and Add Actions for the Help Menu
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.about_callback)
        help_menu.addAction(about_action)
    
    def file_popup(self, title:str):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            title, 
            "/home/alexism/Documents/Stage 2026 UiA/code/App test/test/data", 
            "JSON files (*.json);;All files (*)", 
            options=options
        )
        
        return file_path
    
    def open_file_callback(self):
        path = Path(self.file_popup("Select file to open"))

        if not path:
            return
        
        loader = self.ctx.loader
        if loader:
            loader.quit()
            loader.wait()

        loader = self.ctx.loader = AsyncFileLoader(path)
        loader.finished_loading.connect(self.load_file_replace)

        logging.info("Loading file \"%s\"" % path)

        try:
            loader.start()
        except Exception as e:
            logging.error("Exception encountered while loading file \"%s\" : %s" % (path, e))
            QMessageBox.warning(
                self, "Exception encountered", 
                f"Exception encountered while loading file \"{path}\" : {e}."
            )

            return

    def extend_file_callback(self):
        self.file_popup("Select file to import")
        print("Extend !")
    
    def show_exception_dialog(self, exception: Exception, parent=None):
        if not parent:
            parent = self

        """Displays a critical QMessageBox with an expandable traceback details panel."""
        # Fetch the full stack trace as a formatted string
        traceback_str = traceback.format_exc()
        
        msg_box = QMessageBox(parent)
        msg_box.setSizeGripEnabled(True)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Execution Error")
        
        # Primary message text
        msg_box.setText("An unexpected system exception occurred.")
        
        error_summary = f"<b>{type(exception).__name__}:</b> {exception}"
        msg_box.setInformativeText(error_summary)

        msg_box.setDetailedText(traceback_str)
        
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def load_file_replace(self, data):
        try:
            self.load_file(data, replace=True)
        except Exception as e:
            logging.error("Exception encountered : %s" % e)
            self.show_exception_dialog(e)

    def load_file_extend(self, data):
        try:
            self.load_file(data, replace=False)
        except Exception as e:
            logging.exception("Exception encountered : %s" % e)
            self.show_exception_dialog(e)
    
    def load_file(self, data:dict, replace:bool):
        for node, content in data.items():
            match node:
                case "precedence-map":
                    precedence_map = self.ctx.sequenceGraph

                    logging.info("Loading sequence graph...")
                    map = SequenceGraph.From_dict(content)
                    

                    logging.info("Computing sequence graph job links...")
                    map.compute_job_links()
                    
                    if not map.is_acyclic():
                        return

                    logging.info("Grouping sequence graph...")
                    map.group()
                    map.update_probabilities()

                    if replace:
                        precedence_map.value = map
                    else:
                        precedence_map.value.extend(map)

                case "policy-base":
                    logging.info("Loading policy table...")
                    new_table = PolicyTable.From_dict(content)

                    if replace:
                        self.ctx.policyTable.value = new_table
                    else:
                        self.ctx.policyTable.value.extend(new_table)
                    

                case "resources":
                    logging.info("Loading resource registry")
                    new_resources = ResourceRegistry.From_dict(content)

                    if replace:
                        self.ctx.resourceRegistry.value = new_resources
                    else:
                        self.ctx.resourceRegistry.value.extend(new_resources)

                case _:
                    logging.warning("Unknown field \"%s\"" % node)

        logging.info("File loaded !")

    def about_callback(self):
        QMessageBox.information(self, "About", "This is a Qt Menu Bar Example.")
    
    def closing(self):
        logging.getLogger().removeHandler(self.log_handler)