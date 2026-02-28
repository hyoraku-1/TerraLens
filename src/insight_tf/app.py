from textual.app import App
from textual.widgets import Header, Footer


class InsightTFApp(App):
    """Main TerraLens Application"""

    def compose(self):
        yield Header()
        yield Footer()
