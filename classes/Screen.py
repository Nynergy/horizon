"""
A Screen is a collection of non-overlapping Panel objects that appear as part
of a single "tab" in horizon. For example, there is a "Playlist Screen", a
"Media Library Screen", a "Saved Playlist Screen", etc.
"""

class Screen:
    def __init__(self, screen_dimensions, title=""):
        self.setDimensions(screen_dimensions)
        self.title = title
        self.panels = []
        self.currentPanelIndex = 0

    def setDimensions(self, screen_dimensions):
        (ul, lr) = screen_dimensions
        self.x = ul.x
        self.y = ul.y
        self.width = lr.x - ul.x
        self.height = lr.y - ul.y

    def addPanel(self, panel):
        self.panels.append(panel)

    def render(self):
        for panel in self.panels:
            panel.render()

    def getCurrentPanel(self):
        return self.panels[self.currentPanelIndex]
