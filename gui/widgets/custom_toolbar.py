from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

class CustomNavigationToolbar(NavigationToolbar2QT):
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        self.keep_only_buttons(['Home', 'Zoom'])

    def keep_only_buttons(self, keep_labels):
        for action in self.actions():
            text = action.text()
            if not any(label in text for label in keep_labels):
                self.removeAction(action)
