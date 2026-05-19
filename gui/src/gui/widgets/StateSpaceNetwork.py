from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QFont
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QVBoxLayout
from PyQt5.QtGui import QPainter

import pyqtgraph as pg
import numpy as np

from core import StateSpaceGraph, SequenceGraph
from PyQt5.QtOpenGL import QGLWidget

from ..AppContext import AppContext

import random
import math

class StateSpaceNetworkWidget(QWidget):
    def __init__(self, ctx:AppContext, parent=None):
        super().__init__(parent)
        self.nodes = []        # List of QPointF positions
        self.node_labels = [] # List of strings
        self.edges = []       # List of tuples: (source_idx, target_idx, edge_label)

        self.ctx = ctx

        ctx.stateSpaceGraph.subscribe(self.callback)
        ctx.sequenceGraph.subscribe(self.sequenceGraphChanged)
        
        self.zoom = 0.2       # Start zoomed out to see the hierarchy
        self.pan_x = 0
        self.pan_y = -200
        self.is_panning = False
        self.mouse_start = QPointF()
        self.selected_node_idx = None
        
        # Performance Thresholds
        self.LABEL_ZOOM_THRESHOLD = 0.6  # Only draw labels if zoom is greater than this
        self.NODE_RADIUS = 20
        self.NDOE_RADIUS_SELECTED = 25 
        self.CLICK_RADIUS = 15

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        pg.setConfigOption('antialias', False)  # Disables antialiasing globally for raw speed
        # pg.setConfigOption('useOpenGL', True) # Alternative global OpenGL switch

        # ... inside your class init or method ...

        # 2. Initialize the view
        view = pg.GraphicsLayoutWidget()
        view.setViewport(QGLWidget())
        view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        layout.addWidget(view)

        plot = view.addPlot()

        # 10,000 nodes with random (x, y) positions
        N = 10000
        pos = np.random.normal(size=(N, 2))

        # Define edges
        adj = np.vstack([np.arange(N-1), np.arange(1, N)]).T

        # Create and add the graph item
        g = pg.GraphItem()
        g.setData(pos=pos, adj=adj, symbolBrush='b', symbolSize=5, pen='w')
        plot.addItem(g)

        plot.autoRange()
    
    def sequenceGraphChanged(self, data:SequenceGraph):
        print(type(data))
        g = StateSpaceGraph.From_SequenceGraph(data)
        
        self.ctx.stateSpaceGraph.value = g
    
    def callback(self, graph:StateSpaceGraph):
        print("a")
        
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#121212"))
        
        # Global Transform Layer
        painter.save()
        mid_x = self.width() / 2 + self.pan_x
        mid_y = self.height() / 2 + self.pan_y
        painter.translate(mid_x, mid_y)
        painter.scale(self.zoom, self.zoom)

        # View Frustum Culling Bounds: Determine what is visible on screen
        visible_rect = QRectF(
            (-self.width() / 2 - self.pan_x) / self.zoom,
            (-self.height() / 2 - self.pan_y) / self.zoom,
            self.width() / self.zoom,
            self.height() / self.zoom
        )

        show_labels = self.zoom >= self.LABEL_ZOOM_THRESHOLD

        # Configure Fonts
        font = QFont("Arial", 10)
        painter.setFont(font)

        # 1. Draw Edges
        pen_edge = QPen(QColor("#2d2d2d"), 1)
        pen_edge_label = QPen(QColor("#888888"), 1)
        
        for p1_idx, p2_idx, label in self.edges:
            pt1 = self.nodes[p1_idx]
            pt2 = self.nodes[p2_idx]
            
            # Culling Check for Edges (If both endpoints are out, skip drawing)
            if not (visible_rect.contains(pt1) or visible_rect.contains(pt2)):
                continue
                
            painter.setPen(pen_edge)
            painter.drawLine(pt1, pt2)
            
            # Optional: Simple Downward Arrowhead Hint
            if show_labels:
                painter.setPen(pen_edge_label)
                mid_point = (pt1 + pt2) / 2
                painter.drawText(mid_point, label)

        # 2. Draw Nodes
        pen_selected = QPen(QColor("#ff007f"), self.NDOE_RADIUS_SELECTED)
        pen_normal = QPen(QColor("#00adb5"), self.NODE_RADIUS)
        pen_text = QPen(QColor("#ffffff"))

        for idx, pt in enumerate(self.nodes):
            if not visible_rect.contains(pt):
                continue
            
            if idx == self.selected_node_idx:
                painter.setPen(pen_selected)
            else:
                painter.setPen(pen_normal)
                
            painter.drawPoint(pt)

            if show_labels:
                painter.setPen(pen_text)
                # Offset text labels cleanly to the right of node points
                painter.drawText(int(pt.x()) + 8, int(pt.y()) + 4, self.node_labels[idx])
        
        painter.restore()

    # Coordinates Mapping Systems
    def screen_to_world(self, pos):
        world_x = (pos.x() - self.width() / 2 - self.pan_x) / self.zoom
        world_y = (pos.y() - self.height() / 2 - self.pan_y) / self.zoom
        return QPointF(world_x, world_y)

    # Mouse & Interactive Pipeline Events
    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        factor = 1.15 if angle > 0 else 0.85
        
        # Clamp zoom limits
        new_zoom = self.zoom * factor
        if 0.02 < new_zoom < 5.0:
            self.zoom = new_zoom
            self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            world_pos = self.screen_to_world(event.pos())
            
            # Linear proximity detection scan for user click selection
            clicked_node = None
            min_dist = self.CLICK_RADIUS
            
            for idx, pt in enumerate(self.nodes):
                dist = math.hypot(world_pos.x() - pt.x(), world_pos.y() - pt.y())
                if dist < min_dist:
                    min_dist = dist
                    clicked_node = idx
            
            if clicked_node is not None:
                self.selected_node_idx = clicked_node
                # Broadcast selection data to parent container window status bar
                window = self.window()
                if hasattr(window, 'status_bar'):
                    window.status_bar.showMessage(f"Selected: {self.node_labels[clicked_node]} (Global Vector Index: {clicked_node})")
            else:
                # If clicked empty space, activate Pan-and-Scan mode
                self.is_panning = True
                self.mouse_start = event.pos()
            
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_panning:
            delta = event.pos() - self.mouse_start
            self.pan_x += delta.x()
            self.pan_y += delta.y()
            self.mouse_start = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_panning = False