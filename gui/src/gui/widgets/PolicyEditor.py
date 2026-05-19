import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QListWidget, QListWidgetItem,
    QWidget, QFormLayout, QLineEdit, QSpinBox, QComboBox, QGroupBox,
    QDockWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget,
    QAbstractItemView, QInputDialog, QMessageBox, QTabWidget, QLabel,
    QTableWidget, QHeaderView, QTableWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal

from ..AppContext import AppContext
from core import ResourceRegistry, Resource, Policy, PolicyTable

class DomainSetWidget(QWidget):
    """Handles choosing existing items or adding new strings to a Python set."""
    def __init__(self, existing_domains: set[str], parent=None):
        super().__init__(parent)

        self.existing_domains = existing_domains
        
        # Setup UI layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Input row
        input_layout = QHBoxLayout()
        self.combo = QComboBox()
        self.combo.setEditable(True)
        self.combo.addItems(self.existing_domains)
        
        self.add_btn = QPushButton("Add")
        input_layout.addWidget(self.combo, stretch=4)
        input_layout.addWidget(self.add_btn, stretch=1)
        main_layout.addLayout(input_layout)
        
        # Display list of active selections
        self.list_widget = QListWidget()
        main_layout.addWidget(self.list_widget)
        
        # Actions
        self.add_btn.clicked.connect(self._add_domain)
        self.list_widget.itemDoubleClicked.connect(self._remove_domain)
    
    def updateDomains(self):
        self.combo.clear()
        self.combo.addItems(self.existing_domains)

    def _add_domain(self):
        text = self.combo.currentText().strip()
        if not text:
            return
            
        # Add to global unique known domains pool if it's new
        if text not in self.existing_domains:
            self.existing_domains.add(text)
            self.combo.addItem(text)
            
        # Add to active visual selection list if not already there
        existing_items = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        if text not in existing_items:
            self.list_widget.addItem(text)
            
        self.combo.setCurrentText("")

    def _remove_domain(self, item):
        self.list_widget.takeItem(self.list_widget.row(item))

    def get_domains(self) -> set[str]:
        return {self.list_widget.item(i).text() for i in range(self.list_widget.count())}

    def set_domains(self, domains: set[str]):
        self.list_widget.clear()
        for dom in domains:
            self.list_widget.addItem(dom)


class DescriptorDictWidget(QWidget):
    """Dynamic table editing key-value configurations (float -> str mapping)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Descriptor", "Value"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("+ Add Row")
        self.remove_btn = QPushButton("- Remove Selected")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        layout.addLayout(btn_layout)
        
        self.add_btn.clicked.connect(self.add_row)
        self.remove_btn.clicked.connect(self.remove_selected)

    def add_row(self, str_val="", flt_val=1.0):
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Numeric cell config
        num_item = QTableWidgetItem(str(float(flt_val)))
        num_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.table.setItem(row, 0, QTableWidgetItem(str_val))
        self.table.setItem(row, 1, num_item)

    def remove_selected(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def get_dict(self) -> dict[float, str]:
        result = {}
        for row in range(self.table.rowCount()):
            val_item = self.table.item(row, 0)
            key_item = self.table.item(row, 1)
            if key_item and val_item:
                try:
                    v = float(key_item.text().strip())
                    k = val_item.text().strip()
                    result[k] = v
                except ValueError:
                    continue  # Safely ignore un-parsable float input strings
        return result

    def set_dict(self, data_dict: dict[str, float]):
        self.table.setRowCount(0)
        for k, v in data_dict.items():
            self.add_row(k, v)

class PolicyEditor(QWidget):
    """Editor specific to Policies: Needs Target and Effect."""
    def __init__(self, existing_domains):
        super().__init__()
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.id_edit = 0
        self.name_edit = QLineEdit()

        self.domains_edit = DomainSetWidget(existing_domains)
        self.descriptors_edit = DescriptorDictWidget()
        
        self.impl_edit = QLineEdit()
        self.impl_edit.setText("N/A")
        self.impl_edit.setEnabled(False)
        
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Domains:", self.domains_edit)
        layout.addRow("Descriptors:", self.descriptors_edit)
        layout.addRow("Implementation:", self.impl_edit)
    
    def updateDomains(self):
        self.domains_edit.updateDomains()

    def load_data(self, data:Policy):
        self.id_edit = data.id
        self.name_edit.setText(data.name)
        
        self.domains_edit.set_domains(sorted(list(data.domains)))
        self.descriptors_edit.set_dict(data.descriptors)

    def get_data(self):
        return Policy(
            id=self.id_edit,
            name=self.name_edit.text(),
            descriptors=self.descriptors_edit.get_dict(),
            domains=self.domains_edit.get_domains(),
            implementation=None,
            parameters=[]
        )

class ResourceEditor(QWidget):
    """Editor specific to Components: Needs Version and Language."""
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.version_edit = QLineEdit()
        self.lang_edit = QLineEdit()
        
        layout.addRow("Version:", self.version_edit)
        layout.addRow("Language/Tech:", self.lang_edit)

    def load_data(self, data):
        self.version_edit.setText(data.get("version", ""))
        self.lang_edit.setText(data.get("language", ""))

    def get_data(self):
        return {"version": self.version_edit.text(), "language": self.lang_edit.text()}



class SelectionPanel(QWidget):
    # Signals to communicate with the main window
    item_selected = pyqtSignal(str, str)
    item_cleared = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Tab Widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.lists = {} # Maps registry_type -> QListWidget

        # Add / Remove Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("+ Add")
        self.remove_btn = QPushButton("- Remove")
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        layout.addLayout(btn_layout)

        # Connect button actions
        self.add_btn.clicked.connect(self.add_item)
        self.remove_btn.clicked.connect(self.remove_item)

    def load_data(self, registry_data):
        """Dynamically generates tabs based on the provided dictionary."""
        self.tabs.clear()
        self.lists.clear()

        for reg_type, items in registry_data.items():
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            # Search bar
            search_bar = QLineEdit()
            search_bar.setPlaceholderText(f"Search {reg_type}...")
            tab_layout.addWidget(search_bar)

            # List widget
            list_widget = QListWidget()
            list_widget.addItems(items)
            tab_layout.addWidget(list_widget)

            # Connections
            search_bar.textChanged.connect(
                lambda text, lw=list_widget: self.filter_list(text, lw)
            )
            list_widget.currentItemChanged.connect(
                lambda current, previous, rt=reg_type: self.on_item_selected(current, rt)
            )

            self.lists[reg_type] = list_widget
            self.tabs.addTab(tab, reg_type)

    def filter_list(self, text, list_widget):
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def on_item_selected(self, current_item, reg_type):
        if current_item:
            self.item_selected.emit(reg_type, current_item.text())
        else:
            self.item_cleared.emit()

    def add_item(self):
        """Prompts the user and adds a new item to the active tab."""
        current_index = self.tabs.currentIndex()
        if current_index == -1: return # No tabs exist
        
        reg_type = self.tabs.tabText(current_index)
        
        # Open a simple input dialog
        new_name, ok = QInputDialog.getText(self, f"Add {reg_type}", "Component Name:")
        
        if ok and new_name.strip():
            list_widget = self.lists[reg_type]
            list_widget.addItem(new_name.strip())
            
            # Automatically select the newly created item
            new_item = list_widget.item(list_widget.count() - 1)
            list_widget.setCurrentItem(new_item)

    def remove_item(self):
        """Removes the currently selected item from the active tab."""
        current_index = self.tabs.currentIndex()
        if current_index == -1: return
        
        reg_type = self.tabs.tabText(current_index)
        list_widget = self.lists[reg_type]
        
        current_row = list_widget.currentRow()
        if current_row >= 0:
            # Confirm deletion
            reply = QMessageBox.question(self, 'Confirm', 'Are you sure you want to delete this item?',
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                list_widget.takeItem(current_row)
                self.item_cleared.emit() # Tell the editor to clear itself


# ---------------------------------------------------------
# 2. Editor Panel (Right Side)
# ---------------------------------------------------------
class EditorPanel(QWidget):
    data_saved = pyqtSignal(str, int, object)

    def __init__(self, existing_domains):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.group_box = QGroupBox("Editor")
        layout.addWidget(self.group_box)
        layout.addStretch()

        form_layout = QFormLayout(self.group_box)

        # Global Properties (Shared by all)
        self.type_label = QLabel("N/A")
        self.id_label = QLabel("N/A")
        form_layout.addRow("Registry Type:", self.type_label)
        form_layout.addRow("Item ID:", self.id_label)

        # The Stacked Widget holds our specific sub-editors
        self.stacked_widget = QStackedWidget()
        form_layout.addRow(self.stacked_widget)

        # Instantiate and index sub-editors
        self.sub_editors = {
            "Policies": PolicyEditor(existing_domains),
            #"Resources": ResourceEditor()
        }
        
        # Add them to the stack
        for widget in self.sub_editors.values():
            self.stacked_widget.addWidget(widget)

        # Save Button
        self.save_btn = QPushButton("Save Changes")
        self.save_btn.clicked.connect(self.on_save_clicked)
        form_layout.addRow("", self.save_btn)

        self.current_type = None
        self.current_id = None
        self.clear_editor()

        self.clear_editor() # Start in a disabled state
    
    def updateDomains(self):
        self.sub_editors["Policies"].updateDomains()

    def load_item(self, reg_type, item_id, item_data):
        """Switches the visible editor sub-panel and loads specific data."""
        self.current_type = reg_type
        self.current_id = item_id
        
        self.group_box.setTitle(f"Editing: {item_id}")
        self.type_label.setText(reg_type)
        self.id_label.setText(str(item_id))

        # Switch to the correct form stack page if we have a custom sub-editor for it
        if reg_type in self.sub_editors:
            sub_w = self.sub_editors[reg_type]
            self.stacked_widget.setCurrentWidget(sub_w)
            sub_w.load_data(item_data)
            self.stacked_widget.setVisible(True)
        else:
            # Fallback for types without special properties
            self.stacked_widget.setVisible(False)

        self.save_btn.setEnabled(True)

    def on_save_clicked(self):
        """Collects data from the active sub-editor and fires a save signal."""
        if self.current_type in self.sub_editors:
            updated_properties = self.sub_editors[self.current_type].get_data()
            self.data_saved.emit(self.current_type, self.current_id, updated_properties)

    def clear_editor(self):
        self.group_box.setTitle("Editor - No Item Selected")
        self.type_label.setText("N/A")
        self.id_label.setText("N/A")
        self.current_type = None
        self.current_id = None
        self.save_btn.setEnabled(False)
        self.stacked_widget.setVisible(False)

class SelectionPanel(QWidget):
    item_selected = pyqtSignal(str, int, object)
    item_cleared = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.lists = {} 
    
    def update_single_type(self, reg_type, items_list):
        if reg_type in self.lists:
            list_widget = self.lists[reg_type]
            list_widget.blockSignals(True)
            list_widget.clear()
            
            for item_data in items_list:
                # Create the list item
                item = QListWidgetItem(item_data.name)
                
                # Store the ID and the full data dictionary inside the item itself!
                item.setData(Qt.ItemDataRole.UserRole, item_data.id)
                # Optional: store the whole dict for easy access later
                item.setData(Qt.ItemDataRole.UserRole + 1, item_data) 
                
                list_widget.addItem(item)
                
            list_widget.blockSignals(False)
        else:
            # First time creating this type layout dynamically
            tab = QWidget()
            tab_layout = QVBoxLayout(tab)
            
            search_bar = QLineEdit()
            search_bar.setPlaceholderText(f"Search {reg_type}...")
            tab_layout.addWidget(search_bar)

            list_widget = QListWidget()
            list_widget.addItems(items_list)
            tab_layout.addWidget(list_widget)

            search_bar.textChanged.connect(lambda text, lw=list_widget: self.filter_list(text, lw))
            list_widget.currentItemChanged.connect(lambda cur, prev, rt=reg_type: self.on_item_selected(cur, rt))

            self.lists[reg_type] = list_widget
            self.tabs.addTab(tab, reg_type)

    def filter_list(self, text, list_widget):
        search_query = text.lower().strip()
        
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            
            # 1. Get the visible name
            item_name = item.text().lower()
            
            # 2. Get the hidden ID (fallback to empty string if missing)
            item_id = str(item.data(Qt.ItemDataRole.UserRole)).lower()
            
            # Match condition: True if query is found in name OR in ID
            matches_name = search_query in item_name
            matches_id = search_query in item_id
            
            # Hide the item if it doesn't match either property
            item.setHidden(not (matches_name or matches_id))

    def on_item_selected(self, current_item, reg_type):
        if current_item:
            # Retrieve the hidden complete dictionary we stored at slot (UserRole + 1)
            item_data = current_item.data(Qt.ItemDataRole.UserRole + 1)
            
            # Pass the rich data straight to your editor panel
            self.item_selected.emit(reg_type, item_data.id, item_data)
        else:
            self.item_cleared.emit()

class PolicyPropertyEditor(QWidget):
    resource_changed = pyqtSignal()

    def __init__(self, ctx:AppContext, parent=None):
        super().__init__()

        self.current = None
        self.ctx = ctx

        self.types = {
            "Policies": {
                "content": {},
                "ctx-value": self.ctx.policyTable,
                "attribute": "policies",
                "callback": lambda data: self.on_policies_changed(data)
            },
        }

        self.existing_domains = set()

        self.setup_callbacks()
        self.setup_ui()
    
    def on_policies_changed(self, data: PolicyTable):
        self.existing_domains.clear()

        
        for p in data.policies.values():
            self.existing_domains |= p.domains
        
        self.editor_panel.updateDomains()
        
    
    def setup_callbacks(self):
        for type, info in self.types.items():
            info["ctx-value"].changed.connect(
                lambda arg: self.callback(arg, type, info)
            )
            
        
    def callback(self, data, type, info):
        self.types[type]["content"] = getattr(data, info["attribute"])
        self.reload_type_from_db(type)

        if not (clbk := info.get("callback")) is None:
            clbk(data)


    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Splitter to allow resizing the left/right panels
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)

        self.selection_panel = SelectionPanel()
        self.editor_panel = EditorPanel(self.existing_domains)

        splitter.addWidget(self.selection_panel)
        splitter.addWidget(self.editor_panel)
        splitter.setSizes([300, 600])

        # Routes
        self.selection_panel.item_selected.connect(self.handle_item_selection)
        self.selection_panel.item_cleared.connect(self.editor_panel.clear_editor)
        self.editor_panel.data_saved.connect(self.handle_data_save)

        # Initial isolated loads
        self.reload_type_from_db("Policies")

    def reload_type_from_db(self, reg_type):
        """Fetches items for ONLY one type and tells the selection panel to update."""
        items_list = list(self.types.get(reg_type, {}).get("content", {}).values())
        self.selection_panel.update_single_type(reg_type, items_list)

    def handle_item_selection(self, reg_type, item_id):
        """Extracts the underlying dictionary for an item and forwards it to the editor."""
        item_data = self.types.get(reg_type, {}).get("content", {}).get(item_id, {})

        self.editor_panel.load_item(reg_type, item_id, item_data)

    def handle_data_save(self, reg_type, item_id, updated_properties):
        """Saves editor changes into state without touching other data categories."""

        
        if reg_type in self.types and item_id in self.types[reg_type]["content"]:
            type = self.types[reg_type]

            local = type["content"]
            local[item_id] = updated_properties

            ctx_value = type["ctx-value"]

            with ctx_value:
                value = ctx_value.value
                setattr(value, type["attribute"], local)

            ctx_value.changed.emit(ctx_value._value)

            logging.debug("Saved changed to item %d" % item_id)
    
    def setups_ui(self):
        main_layout = QVBoxLayout(self)

        # Splitter to allow resizing the left/right panels
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter)

        self.selection_panel = SelectionPanel()
        self.editor_panel = EditorPanel()

        splitter.addWidget(self.selection_panel)
        splitter.addWidget(self.editor_panel)
        splitter.setSizes([280, 570])

        # Signal Routing
        self.selection_panel.item_selected.connect(self.editor_panel.load_item)
        self.selection_panel.item_cleared.connect(self.editor_panel.clear_editor)

        # Simulate fetching data dynamically (e.g., from an API or database)
        self.fetch_and_load_data()