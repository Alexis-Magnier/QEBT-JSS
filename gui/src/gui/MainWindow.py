from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt
import sys

from .AppContext import AppContext
from .widgets.StateSpaceNetwork import StateSpaceNetworkWidget
from .AsyncFileLoader import AsyncFileLoader

from core import (
    SequenceGraph
)

from PyQt5.QtWidgets import (
    QMainWindow, QDockWidget, QTextEdit, QPushButton, QLabel, QFileDialog,
    QListWidget, QWidget, QVBoxLayout, QLabel, QAction, QMessageBox
)

import time
from pathlib import Path

# Core HTML Shell delivering dynamic Mermaid.js compilation engine offline/online
MERMAID_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({ startOnLoad: true, theme: 'dark' });
        
        function updateChart(code) {
            var container = document.getElementById('graph');
            container.innerHTML = code;
            container.removeAttribute('data-processed');
            mermaid.run({
                nodes: [container]
            });
        }
    </script>
    <style>
        body { 
            background-color: #222222; 
            margin: 0; 
            padding: 20px; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 90vh;
        }
        #graph {
            color: #ffffff;
        }
    </style>
</head>
<body>
    <div id="graph" class="mermaid">
        graph LR
        A[File Loaded] --> B[Network Visualized]
        A --> C[Mermaid Ready]
    </div>
</body>
</html>
"""

class MainWindow(QMainWindow):
    def __init__(self, ctx:AppContext):
        super().__init__()

        self.ctx = ctx
        self.setWindowTitle("Dynamic Docking Workspace Engine")
        self.resize(1100, 700)

        self.status_bar = self.statusBar()
        self.ctx.status_changed.connect(self.status_bar.showMessage)
        self.status_bar.showMessage(self.ctx.status)

        # 1. Enable advanced layout nesting and tabbing behavior
        self.setDockOptions(
            QMainWindow.AllowNestedDocks |  # Allow docks to be placed next to each other
            QMainWindow.AllowTabbedDocks |  # Allow docks to be dropped on top of each other as tabs
            QMainWindow.GroupedDragging     # Moving a tab group moves them all together
        )

        # 2. Establish a Central Widget (The core anchor that cannot be removed)
        self.central_canvas = QTextEdit()
        self.central_canvas.setPlaceholderText("Central Workspace (e.g., Your Main Network Graph Visualizer)")
        self.setCentralWidget(self.central_canvas)

        # 3. Initialize dynamic dock panels
        self.init_dock_panels()
        self.create_menu_bar()
    
    def add_panel(self, title:str, initial_pos: Qt.DockWidgetArea) -> QDockWidget:
        d = QDockWidget(title, self)
        self.addDockWidget(initial_pos, d)
        return d

    def init_dock_panels(self):
        # --- PANEL A: Mermaid Code Editor (Initial State: Left Side) ---
        dock_editor = self.add_panel("Mermaid Code Deck", Qt.LeftDockWidgetArea)
        # Configure what user actions are allowed (Floating, Closing, Moving)
        dock_editor.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetClosable)
        dock_editor.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        # Add actual interactive widgets inside the dock shell
        editor_widget = QTextEdit()
        editor_widget.setPlainText("graph TD\n    A --> B")
        dock_editor.setWidget(editor_widget)

        # --- PANEL B: Data Properties Inspector (Initial State: Right Side) ---
        dock_inspector = self.add_panel("Property Inspector", Qt.RightDockWidgetArea)
        dock_inspector.setFeatures(QDockWidget.AllDockWidgetFeatures) # Allows everything including closing
        
        inspector_container = QWidget()
        layout = QVBoxLayout(inspector_container)
        layout.addWidget(QLabel("<b>Node Attributes:</b>"))
        layout.addWidget(QListWidget()) # Mock attributes table list
        dock_inspector.setWidget(inspector_container)

        # --- PANEL C: System Output Console (Initial State: Bottom Side) ---
        dock_console = QDockWidget("System Log Console", self)
        dock_console.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable) # Cannot be closed
        
        console_widget = QTextEdit()
        console_widget.setReadOnly(True)
        console_widget.setText("[INFO] Reactive event loop initialized safely.\n[INFO] Layout boundaries computed.")
        console_widget.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Consolas;")
        dock_console.setWidget(console_widget)
        
        self.addDockWidget(Qt.BottomDockWidgetArea, dock_console)

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
        print("Open action triggered!")

        if not path:
            return
        
        loader = self.ctx.loader
        if loader:
            loader.quit()
            loader.wait()

        loader = self.ctx.loader = AsyncFileLoader(path)
        loader.finished_loading.connect(self.load_file_replace)

        self.ctx.status = f"Loading file \"{path}\"..."

        try:
            loader.start()
        except Exception as e:
            QMessageBox.warning(
                self, "Exception encountered", 
                f"Exception encountered while loading file \"{path}\" : {e}."
            )

            self.ctx.status = f"Failed to load file \"{path}\" with exception {type(e)}"
            return

    def extend_file_callback(self):
        self.file_popup("Select file to import")
        print("Extend !")

    def load_file_replace(self, data):
        self.load_file(data, replace=True)

    def load_file_extend(self, data):
        self.load_file(data, replace=False)
    
    def load_file(self, data:dict, replace:bool):
        
        for node, content in data.items():
            match node:
                case "precedence-map":
                    precedence_map = self.ctx.sequenceGraph

                    self.ctx.status = f"Loading sequence graph..."
                    map = SequenceGraph.From_dict(content)
                    

                    self.ctx.status = f"Computing sequence graph job links..."
                    map.compute_job_links()
                    
                    if not map.is_acyclic():
                        return

                    self.ctx.status = f"Grouping sequence graph"
                    map.group()
                    map.update_probabilities()

                    precedence_map.value = map

                case "policy-base":
                    print("loading policy table")

                case "resources":
                    print("loading resources")

                case _:
                    print("unknown")

        self.ctx.status = f"File loaded with success !"

    def about_callback(self):
        QMessageBox.information(self, "About", "This is a Qt Menu Bar Example.")

class MainWndow(QMainWindow):
    def __init__(self, ctx: AppContext):
        super().__init__()
        self.ctx = ctx
        self.setWindowTitle("Qt High-Scale Network & Mermaid Workspace")
        
        self.init_ui()
        
        # Enforce execution barrier: Requires file immediately upon initialization
        # QTimer.singleShot(0, self.require_file_on_startup)

    def init_ui(self):
        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)

        # Left panel allocations -> High Density Graph Setup
        self.network_widget = StateSpaceNetworkWidget()
        main_splitter.addWidget(self.network_widget)

        # Right panel allocations -> Mermaid Playground Configurations
        mermaid_container = QWidget()
        mermaid_layout = QVBoxLayout(mermaid_container)
        mermaid_layout.setContentsMargins(10, 10, 10, 10)

        mermaid_layout.addWidget(QLabel("<b>Mermaid Markup Editor:</b>"))
        self.code_editor = QTextEdit()
        self.code_editor.setPlaceholderText("Write raw structural Mermaid configurations...")
        self.code_editor.setPlainText("graph TD\n    A[Data File Read] --> B(Generate Graph Canvas)\n    B --> C{10,000 Points Verified}\n    C -->|Render| D[Smooth Realtime Zoom]")
        self.code_editor.setMaximumHeight(160)
        mermaid_layout.addWidget(self.code_editor)

        self.render_btn = QPushButton("Compile Diagram")
        self.render_btn.setStyleSheet("background-color: #00adb5; color: white; font-weight: bold; padding: 8px;")
        self.render_btn.clicked.connect(self.compile_mermaid_diagram)
        mermaid_layout.addWidget(self.render_btn)

        self.web_view = QWebEngineView()
        self.web_view.setHtml(MERMAID_HTML)
        mermaid_layout.addWidget(self.web_view)

        main_splitter.addWidget(mermaid_container)
        main_splitter.setSizes([750, 550])

    def require_file_on_startup(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Required Execution Target: Select File to Open", 
            "", 
            "All Files (*);;Text Documents (*.txt);;Data Files (*.json *.csv)", 
            options=options
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as selected_file:
                    _ = selected_file.read() # Target data parsed/opened successfully
                
                QMessageBox.information(
                    self, "Initialization Success", 
                    f"Successfully mounted file:\n{file_path}\n\nLoading 10,000 structural node matrix view."
                )
            except Exception as error:
                QMessageBox.critical(self, "Read Failure", f"Fatal execution interruption reading file:\n{str(error)}")
                sys.exit(1)
        else:
            # Enforce mandatory file execution clause: close application if bypassed
            QMessageBox.warning(self, "Bypass Prevented", "This application requires a file instantiation context to run.")
            sys.exit(0)

    def compile_mermaid_diagram(self):
        raw_text = self.code_editor.toPlainText()
        # Normalize text characters safely avoiding string injection boundary issues inside JS Engine
        sanatized_js_string = raw_text.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
        
        execution_pipeline = f"updateChart('{sanatized_js_string}');"
        self.web_view.page().runJavaScript(execution_pipeline)
