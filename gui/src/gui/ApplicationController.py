from .AppContext import AppContext
from .AsyncFileLoader import AsyncFileLoader
import time

class ApplicationController:
    """
    Coordinates actions based on state changes. 
    Maintains decoupled business logic.
    """
    def __init__(self, context: AppContext):
        self.ctx = context
        
        # Wire up the Reactive Pipeline
        self.ctx.mainGraph.subscribe(self.on_graph_changed)
        self.ctx.stateMap.subscribe(self.on_state_map_reloaded)

    def trigger_file_load(self, target_path):
        """Step 1: Start async file loading"""
        self.ctx.status = f"Loading raw data file: {target_path}..."
        
        self.loader = AsyncFileLoader(target_path)
        # Funnel the thread result back into the reactive app context
        self.loader.finished_loading.connect(self._inject_loaded_graph)
        self.loader.start()

    def _inject_loaded_graph(self, graph_data):
        # Mutating this property automatically triggers Step 2
        self.ctx.mainGraph.value = graph_data 

    def on_graph_changed(self, raw_graph):
        """Step 2: Handle graph modification -> regenerate map matrix"""
        self.ctx.status = "Graph updated. Deriving state map coordinates..."
        
        # Protect state map from read operations during calculations
        with self.ctx.stateMap.lock():
            # Process heavy structural layout calculations here
            computed_map = {"total_nodes": len(raw_graph["nodes"]), "processed": True}
            time.sleep(0.5) # Simulate workload
            
        # Assign values outside the context manager to trigger reactive cascading dependencies
        self.ctx.stateMap.value = computed_map

    def on_state_map_reloaded(self, computed_map):
        """Step 3: Map matrix refreshed -> update render engine viewports"""
        self.ctx.status = "State map verified. Triggering network interface redraw..."
        print(f"--> UI Redraw Event Dispatched! Details: {computed_map}")
        self.ctx.status = "System Idle."