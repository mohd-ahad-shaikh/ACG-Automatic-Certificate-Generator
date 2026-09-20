import json
import os


# ============================================================
# DEFAULT LAYOUT
# ============================================================

def get_default_layout():
    return {
        "page": {
            "width": 842,
            "height": 595,
            "orientation": "landscape"
        },

        "elements": {

            "organization": {
                "x": 421,
                "y": 503,
                "width": 500,
                "height": 30,
                "visible": True,
                "align": "center"
            },

            "logo": {
                "x": 60,
                "y": 475,
                "width": 55,
                "height": 55,
                "visible": True,
                "align": "center"
            },

            "title": {
                "x": 421,
                "y": 467,
                "width": 650,
                "height": 40,
                "visible": True,
                "align": "center"
            },

            "subtitle": {
                "x": 421,
                "y": 444,
                "width": 600,
                "height": 25,
                "visible": True,
                "align": "center"
            },

            "recipient": {
                "x": 421,
                "y": 390,
                "width": 650,
                "height": 45,
                "visible": True,
                "align": "center"
            },

            "intro": {
                "x": 421,
                "y": 345,
                "width": 600,
                "height": 30,
                "visible": True,
                "align": "center"
            },

            "description": {
                "x": 421,
                "y": 315,
                "width": 600,
                "height": 50,
                "visible": True,
                "align": "center"
            },

            "fields": {
                "x": 421,
                "y": 250,
                "width": 600,
                "height": 100,
                "visible": True,
                "align": "center"
            },

            "date": {
                "x": 105,
                "y": 108,
                "width": 150,
                "height": 30,
                "visible": True,
                "align": "center"
            },

            "certificate_id": {
                "x": 737,
                "y": 108,
                "width": 180,
                "height": 30,
                "visible": True,
                "align": "center"
            },

            "signature": {
                "x": 421,
                "y": 78,
                "width": 150,
                "height": 55,
                "visible": True,
                "align": "center"
            },

            "seal": {
                "x": 730,
                "y": 65,
                "width": 70,
                "height": 70,
                "visible": True,
                "align": "center"
            }
        }
    }


# ============================================================
# LAYOUT MANAGER
# ============================================================

class LayoutManager:

    def __init__(self, layout=None):
        self.layout = layout or get_default_layout()

    # --------------------------------------------------------
    # GET ELEMENT
    # --------------------------------------------------------

    def get_element(self, name):
        return self.layout["elements"].get(name)

    # --------------------------------------------------------
    # ADD ELEMENT
    # --------------------------------------------------------

    def add_element(
        self,
        name,
        x=421,
        y=300,
        width=200,
        height=40,
        visible=True,
        align="center"
    ):

        if not name:
            raise ValueError("Element name is required")

        self.layout["elements"][name] = {
            "x": float(x),
            "y": float(y),
            "width": float(width),
            "height": float(height),
            "visible": bool(visible),
            "align": str(align)
        }

    # --------------------------------------------------------
    # UPDATE ELEMENT
    # --------------------------------------------------------

    def update_element(self, name, **values):

        element = self.get_element(name)

        if element is None:
            raise ValueError(
                "Element not found: " + str(name)
            )

        allowed = [
            "x",
            "y",
            "width",
            "height",
            "visible",
            "align"
        ]

        for key, value in values.items():

            if key in allowed:
                element[key] = value

    # --------------------------------------------------------
    # MOVE ELEMENT
    # --------------------------------------------------------

    def move(self, name, x=None, y=None):

        element = self.get_element(name)

        if element is None:
            raise ValueError(
                "Element not found: " + str(name)
            )

        if x is not None:
            element["x"] = float(x)

        if y is not None:
            element["y"] = float(y)

    # --------------------------------------------------------
    # RESIZE ELEMENT
    # --------------------------------------------------------

    def resize(self, name, width=None, height=None):

        element = self.get_element(name)

        if element is None:
            raise ValueError(
                "Element not found: " + str(name)
            )

        if width is not None:
            element["width"] = float(width)

        if height is not None:
            element["height"] = float(height)

    # --------------------------------------------------------
    # SHOW / HIDE
    # --------------------------------------------------------

    def show(self, name):

        element = self.get_element(name)

        if element:
            element["visible"] = True

    def hide(self, name):

        element = self.get_element(name)

        if element:
            element["visible"] = False

    def toggle(self, name):

        element = self.get_element(name)

        if element:
            element["visible"] = not element.get(
                "visible",
                True
            )

    # --------------------------------------------------------
    # ALIGNMENT
    # --------------------------------------------------------

    def set_alignment(self, name, alignment):

        alignment = str(alignment).lower()

        if alignment not in [
            "left",
            "center",
            "right"
        ]:
            raise ValueError(
                "Alignment must be left, center or right"
            )

        element = self.get_element(name)

        if element:
            element["align"] = alignment

    # --------------------------------------------------------
    # REMOVE ELEMENT
    # --------------------------------------------------------

    def remove_element(self, name):

        if name in self.layout["elements"]:
            del self.layout["elements"][name]

    # --------------------------------------------------------
    # LIST ELEMENTS
    # --------------------------------------------------------

    def get_elements(self):

        return self.layout["elements"]

    def get_visible_elements(self):

        return {
            name: element
            for name, element
            in self.layout["elements"].items()
            if element.get("visible", True)
        }

    # --------------------------------------------------------
    # PAGE
    # --------------------------------------------------------

    def set_page(
        self,
        width=None,
        height=None,
        orientation=None
    ):

        page = self.layout["page"]

        if width is not None:
            page["width"] = float(width)

        if height is not None:
            page["height"] = float(height)

        if orientation is not None:

            orientation = str(
                orientation
            ).lower()

            if orientation not in [
                "landscape",
                "portrait"
            ]:
                raise ValueError(
                    "Orientation must be landscape or portrait"
                )

            page["orientation"] = orientation

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    def save(self, path):

        folder = os.path.dirname(path)

        if folder:
            os.makedirs(
                folder,
                exist_ok=True
            )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.layout,
                file,
                indent=4
            )

        return path

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    @classmethod
    def load(cls, path):

        if not os.path.exists(path):
            raise FileNotFoundError(
                "Layout file not found: " + path
            )

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            layout = json.load(file)

        return cls(layout)

    # --------------------------------------------------------
    # COPY
    # --------------------------------------------------------

    def copy(self):

        new_layout = json.loads(
            json.dumps(self.layout)
        )

        return LayoutManager(new_layout)

    # --------------------------------------------------------
    # RESET
    # --------------------------------------------------------

    def reset(self):

        self.layout = get_default_layout()

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    def summary(self):

        elements = self.layout["elements"]

        visible = sum(
            1
            for e in elements.values()
            if e.get("visible", True)
        )

        return {
            "total_elements": len(elements),
            "visible_elements": visible,
            "hidden_elements":
                len(elements) - visible,
            "orientation":
                self.layout["page"]["orientation"]
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("Testing Layout Manager...")

    manager = LayoutManager()

    print()
    print("Default elements:")
    print(
        list(manager.get_elements().keys())
    )

    # Move title
    manager.move(
        "title",
        x=421,
        y=470
    )

    # Resize title
    manager.resize(
        "title",
        width=700,
        height=45
    )

    # Change alignment
    manager.set_alignment(
        "title",
        "center"
    )

    # Hide logo
    manager.hide("logo")

    # Add custom element
    manager.add_element(
        "custom_text",
        x=421,
        y=180,
        width=500,
        height=40
    )

    print()
    print("Updated elements:")
    print(
        list(manager.get_elements().keys())
    )

    print()
    print("Summary:")
    print(manager.summary())

    # Save test layout
    output = "test_layout.json"

    manager.save(output)

    print()
    print("Layout saved:")
    print(output)

    # Load test
    loaded = LayoutManager.load(output)

    print()
    print("Loaded successfully:")
    print(loaded.summary())

    print()
    print("===================================")
    print("STEP 12A TEST COMPLETED SUCCESSFULLY")
    print("===================================")