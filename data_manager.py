# ============================================================
# UNIVERSAL CERTIFICATE GENERATOR
# STEP 6 - UNIVERSAL DYNAMIC FIELDS SYSTEM
# File: data_manager.py
# ============================================================

from datetime import datetime


class DynamicField:
    """
    Represents one custom certificate field.

    Example:
        Label  = "Roll Number"
        Value  = "15"
        Required = True
    """

    def __init__(
        self,
        label,
        value="",
        field_type="text",
        required=False,
        visible=True,
        order=0
    ):
        self.label = str(label).strip()
        self.value = "" if value is None else str(value)
        self.field_type = field_type
        self.required = bool(required)
        self.visible = bool(visible)
        self.order = order

    def to_dict(self):
        """Convert field into dictionary format."""
        return {
            "label": self.label,
            "value": self.value,
            "field_type": self.field_type,
            "required": self.required,
            "visible": self.visible,
            "order": self.order
        }

    @classmethod
    def from_dict(cls, data):
        """Create a DynamicField from dictionary data."""
        return cls(
            label=data.get("label", ""),
            value=data.get("value", ""),
            field_type=data.get("field_type", "text"),
            required=data.get("required", False),
            visible=data.get("visible", True),
            order=data.get("order", 0)
        )


class DynamicFieldManager:
    """
    Manages unlimited dynamic certificate fields.
    """

    ALLOWED_TYPES = [
        "text",
        "number",
        "date",
        "time",
        "email",
        "phone",
        "textarea"
    ]

    def __init__(self):
        self.fields = []

    # --------------------------------------------------------
    # ADD FIELD
    # --------------------------------------------------------

    def add_field(
        self,
        label,
        value="",
        field_type="text",
        required=False,
        visible=True
    ):
        """
        Add a new field.

        Example:
            manager.add_field(
                "Roll Number",
                "15",
                "number",
                True
            )
        """

        label = str(label).strip()

        if not label:
            raise ValueError("Field label cannot be empty.")

        if field_type not in self.ALLOWED_TYPES:
            field_type = "text"

        # Prevent duplicate field labels
        if self.get_field(label) is not None:
            raise ValueError(
                f"A field named '{label}' already exists."
            )

        field = DynamicField(
            label=label,
            value=value,
            field_type=field_type,
            required=required,
            visible=visible,
            order=len(self.fields)
        )

        self.fields.append(field)

        return field

    # --------------------------------------------------------
    # GET FIELD
    # --------------------------------------------------------

    def get_field(self, label):
        """
        Find a field using its label.
        """

        search_label = str(label).strip().lower()

        for field in self.fields:
            if field.label.lower() == search_label:
                return field

        return None

    # --------------------------------------------------------
    # GET FIELD BY INDEX
    # --------------------------------------------------------

    def get_field_by_index(self, index):
        """
        Get field using its position.
        """

        if index < 0 or index >= len(self.fields):
            return None

        return self.fields[index]

    # --------------------------------------------------------
    # UPDATE FIELD
    # --------------------------------------------------------

    def update_field(
        self,
        old_label,
        new_label=None,
        value=None,
        field_type=None,
        required=None,
        visible=None
    ):
        """
        Update an existing field.
        """

        field = self.get_field(old_label)

        if field is None:
            return False

        # Update label
        if new_label is not None:

            new_label = str(new_label).strip()

            if not new_label:
                raise ValueError(
                    "New field label cannot be empty."
                )

            # Check duplicate name
            existing = self.get_field(new_label)

            if existing is not None and existing is not field:
                raise ValueError(
                    f"A field named '{new_label}' already exists."
                )

            field.label = new_label

        # Update value
        if value is not None:
            field.value = str(value)

        # Update type
        if field_type is not None:

            if field_type not in self.ALLOWED_TYPES:
                raise ValueError(
                    f"Invalid field type: {field_type}"
                )

            field.field_type = field_type

        # Update required
        if required is not None:
            field.required = bool(required)

        # Update visibility
        if visible is not None:
            field.visible = bool(visible)

        return True

    # --------------------------------------------------------
    # REMOVE FIELD
    # --------------------------------------------------------

    def remove_field(self, label):
        """
        Remove a field using its label.
        """

        field = self.get_field(label)

        if field is None:
            return False

        self.fields.remove(field)

        self._reorder()

        return True

    # --------------------------------------------------------
    # REMOVE FIELD BY INDEX
    # --------------------------------------------------------

    def remove_field_by_index(self, index):
        """
        Remove a field using its position.
        """

        field = self.get_field_by_index(index)

        if field is None:
            return False

        self.fields.pop(index)

        self._reorder()

        return True

    # --------------------------------------------------------
    # CLEAR ALL FIELDS
    # --------------------------------------------------------

    def clear(self):
        """
        Remove all fields.
        """

        self.fields = []

    # --------------------------------------------------------
    # REORDER
    # --------------------------------------------------------

    def _reorder(self):
        """
        Keep field order numbers correct.
        """

        for index, field in enumerate(self.fields):
            field.order = index

    # --------------------------------------------------------
    # MOVE FIELD UP
    # --------------------------------------------------------

    def move_up(self, index):
        """
        Move a field one position upward.
        """

        if index <= 0 or index >= len(self.fields):
            return False

        self.fields[index - 1], self.fields[index] = (
            self.fields[index],
            self.fields[index - 1]
        )

        self._reorder()

        return True

    # --------------------------------------------------------
    # MOVE FIELD DOWN
    # --------------------------------------------------------

    def move_down(self, index):
        """
        Move a field one position downward.
        """

        if index < 0 or index >= len(self.fields) - 1:
            return False

        self.fields[index], self.fields[index + 1] = (
            self.fields[index + 1],
            self.fields[index]
        )

        self._reorder()

        return True

    # --------------------------------------------------------
    # SET VALUE
    # --------------------------------------------------------

    def set_value(self, label, value):
        """
        Change only the value of a field.
        """

        field = self.get_field(label)

        if field is None:
            return False

        field.value = "" if value is None else str(value)

        return True

    # --------------------------------------------------------
    # GET VALUE
    # --------------------------------------------------------

    def get_value(self, label, default=""):
        """
        Get the value of a field.
        """

        field = self.get_field(label)

        if field is None:
            return default

        return field.value

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    def validate(self):
        """
        Validate required fields.

        Returns:
            {
                "valid": True/False,
                "errors": [...]
            }
        """

        errors = []

        for field in self.fields:

            if not field.label:
                errors.append(
                    "A field has an empty label."
                )

            if field.required and not field.value.strip():
                errors.append(
                    f"Required field '{field.label}' is empty."
                )

            if field.field_type not in self.ALLOWED_TYPES:
                errors.append(
                    f"Invalid type for '{field.label}'."
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    # --------------------------------------------------------
    # GET ALL FIELDS
    # --------------------------------------------------------

    def get_all_fields(self):
        """
        Return all fields in current order.
        """

        return [
            field.to_dict()
            for field in self.fields
        ]

    # --------------------------------------------------------
    # GET VISIBLE FIELDS
    # --------------------------------------------------------

    def get_visible_fields(self):
        """
        Return only fields marked as visible.
        """

        return [
            field.to_dict()
            for field in self.fields
            if field.visible
        ]

    # --------------------------------------------------------
    # CONVERT TO CERTIFICATE DATA
    # --------------------------------------------------------

    def to_certificate_data(self):
        """
        Convert dynamic fields into a structure
        that certificate_engine.py can use.
        """

        fields = {}

        for field in self.fields:

            if field.visible:
                fields[field.label] = field.value

        return fields

    # --------------------------------------------------------
    # EXPORT DATA
    # --------------------------------------------------------

    def to_dict(self):
        """
        Convert complete manager data into dictionary.
        """

        return {
            "fields": self.get_all_fields()
        }

    # --------------------------------------------------------
    # IMPORT DATA
    # --------------------------------------------------------

    @classmethod
    def from_dict(cls, data):
        """
        Create a field manager from saved dictionary data.
        """

        manager = cls()

        field_list = data.get("fields", [])

        for field_data in field_list:

            field = DynamicField.from_dict(field_data)

            manager.fields.append(field)

        manager._reorder()

        return manager

    # --------------------------------------------------------
    # COUNT
    # --------------------------------------------------------

    def count(self):
        """
        Return total number of fields.
        """

        return len(self.fields)

    # --------------------------------------------------------
    # EMPTY CHECK
    # --------------------------------------------------------

    def is_empty(self):
        """
        Check whether there are no fields.
        """

        return len(self.fields) == 0


# ============================================================
# QUICK HELPER FUNCTIONS
# ============================================================

def create_field_manager():
    """
    Create a new empty dynamic field manager.
    """

    return DynamicFieldManager()


def create_default_fields():
    """
    Create some common certificate fields.

    These are only examples.
    The final website will allow the user
    to add/remove/change them.
    """

    manager = DynamicFieldManager()

    manager.add_field(
        "Name",
        "",
        "text",
        required=True
    )

    manager.add_field(
        "Certificate ID",
        "",
        "text",
        required=True
    )

    manager.add_field(
        "Date",
        "",
        "date",
        required=True
    )

    return manager


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("UNIVERSAL DYNAMIC FIELDS SYSTEM")
    print("=" * 60)

    manager = DynamicFieldManager()

    # Add normal fields
    manager.add_field(
        "Name",
        "Mohammad Ahad",
        "text",
        required=True
    )

    manager.add_field(
        "Roll Number",
        "15",
        "number"
    )

    manager.add_field(
        "Course",
        "BSc IT"
    )

    # Add completely custom fields
    manager.add_field(
        "Specialization",
        "Data Science"
    )

    manager.add_field(
        "Institute",
        "Siddharth College"
    )

    manager.add_field(
        "Phone Number",
        "9876543210",
        "phone"
    )

    manager.add_field(
        "Achievement",
        "Python Workshop"
    )

    # Display fields
    print("\nFIELDS ADDED:")
    print("-" * 60)

    for field in manager.get_all_fields():

        print(
            f"{field['order'] + 1}. "
            f"{field['label']} = "
            f"{field['value']}"
        )

    # Validation
    print("\nVALIDATION:")
    print("-" * 60)

    result = manager.validate()

    print("Valid:", result["valid"])

    if result["errors"]:
        for error in result["errors"]:
            print("ERROR:", error)

    # Certificate data
    print("\nCERTIFICATE DATA:")
    print("-" * 60)

    certificate_data = manager.to_certificate_data()

    for key, value in certificate_data.items():
        print(f"{key}: {value}")

    # Test update
    print("\nUPDATING FIELD...")
    manager.update_field(
        "Course",
        value="BSc Information Technology"
    )

    print(
        "Course:",
        manager.get_value("Course")
    )

    # Test remove
    print("\nREMOVING FIELD...")
    manager.remove_field("Phone Number")

    print(
        "Total Fields:",
        manager.count()
    )

    print("\nFINAL FIELDS:")
    print("-" * 60)

    for field in manager.get_all_fields():

        print(
            f"{field['order'] + 1}. "
            f"{field['label']} = "
            f"{field['value']}"
        )

    print("\n" + "=" * 60)
    print("STEP 6 TEST COMPLETED SUCCESSFULLY")
    print("=" * 60)