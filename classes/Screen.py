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

    def setCurrentPanel(self, newIndex):
        self.getCurrentPanel().unfocus()
        newIndex = self.wrapIndex(newIndex)
        self.currentPanelIndex = newIndex
        self.getCurrentPanel().focus()

    def incrementCurrentPanel(self):
        if self.currentPanelIndex >= len(self.panels) - 1:
            return

        newIndex = self.currentPanelIndex + 1
        self.setCurrentPanel(newIndex)

    def decrementCurrentPanel(self):
        if self.currentPanelIndex <= 0:
            return

        newIndex = self.currentPanelIndex - 1
        self.setCurrentPanel(newIndex)

    def wrapIndex(self, index):
        if(index > len(self.panels) - 1):
            return 0
        if(index < 0):
            return len(self.panels) - 1

        return index
