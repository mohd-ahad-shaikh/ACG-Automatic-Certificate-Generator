# universal_data.py
# STEP 10
# Universal Data + Certificate Engine Integration

from datetime import datetime


class UniversalCertificateData:
    """
    Universal certificate data manager.

    This class connects:
    Dynamic fields -> Certificate data -> Certificate engine
    """

    def __init__(self):
        self.data = {}

        self.fields = {}

        self.certificate_type = "Certificate"

        self.design_name = "Classic Gold"

    # ---------------------------------------------------------
    # CERTIFICATE TYPE
    # ---------------------------------------------------------

    def set_certificate_type(self, certificate_type):
        certificate_type = str(certificate_type).strip()

        if certificate_type:
            self.certificate_type = certificate_type

    def get_certificate_type(self):
        return self.certificate_type

    # ---------------------------------------------------------
    # BASIC DATA
    # ---------------------------------------------------------

    def set_data(self, key, value):
        """
        Add or update any data.

        Example:
        set_data("name", "Mohammad Ahad")
        set_data("roll_no", "15")
        set_data("phone", "9876543210")
        """

        key = str(key).strip()

        if not key:
            raise ValueError("Data key cannot be empty.")

        self.data[key] = value

    def get_data(self, key, default=None):
        return self.data.get(key, default)

    def remove_data(self, key):
        if key in self.data:
            del self.data[key]
            return True

        return False

    def get_all_data(self):
        return dict(self.data)

    # ---------------------------------------------------------
    # MULTIPLE DATA
    # ---------------------------------------------------------

    def set_multiple_data(self, data):
        """
        Add multiple values at once.
        """

        if not isinstance(data, dict):
            raise TypeError("Data must be a dictionary.")

        for key, value in data.items():
            self.set_data(key, value)

    # ---------------------------------------------------------
    # DYNAMIC FIELDS
    # ---------------------------------------------------------

    def add_field(
        self,
        field_name,
        value="",
        field_type="text",
        required=False,
        visible=True
    ):
        """
        Add a completely custom field.

        Example:
        add_field(
            "Specialization",
            "Artificial Intelligence",
            "text"
        )
        """

        field_name = str(field_name).strip()

        if not field_name:
            raise ValueError("Field name cannot be empty.")

        self.fields[field_name] = {
            "value": value,
            "type": field_type,
            "required": required,
            "visible": visible
        }

    def update_field(self, field_name, value):
        if field_name not in self.fields:
            raise KeyError(
                f"Field '{field_name}' does not exist."
            )

        self.fields[field_name]["value"] = value

    def remove_field(self, field_name):
        if field_name in self.fields:
            del self.fields[field_name]
            return True

        return False

    def get_field(self, field_name):
        return self.fields.get(field_name)

    def get_all_fields(self):
        return dict(self.fields)

    # ---------------------------------------------------------
    # DATE & TIME
    # ---------------------------------------------------------

    def set_current_datetime(self):
        """
        Automatically use current date and time.
        """

        now = datetime.now()

        self.data["date"] = now.strftime("%d-%m-%Y")
        self.data["time"] = now.strftime("%I:%M %p")

    def set_date(self, date_value):
        self.data["date"] = str(date_value)

    def set_time(self, time_value):
        self.data["time"] = str(time_value)

    # ---------------------------------------------------------
    # CERTIFICATE ID
    # ---------------------------------------------------------

    def set_certificate_id(self, certificate_id):
        self.data["certificate_id"] = str(certificate_id)

    def get_certificate_id(self):
        return self.data.get("certificate_id", "")

    # ---------------------------------------------------------
    # DESIGN
    # ---------------------------------------------------------

    def set_design_name(self, design_name):
        self.design_name = str(design_name)

    def get_design_name(self):
        return self.design_name

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------

    def validate(self):
        """
        Validate required fields.
        """

        errors = []

        for field_name, field_info in self.fields.items():

            if not field_info.get("required", False):
                continue

            value = field_info.get("value", "")

            if value is None or str(value).strip() == "":
                errors.append(
                    f"Required field is empty: {field_name}"
                )

        return errors

    # ---------------------------------------------------------
    # CONVERT TO CERTIFICATE ENGINE FORMAT
    # ---------------------------------------------------------

    def to_certificate_data(self):
        """
        Convert universal data into the format expected
        by certificate_engine.py
        """

        certificate_data = {}

        # Copy normal data
        for key, value in self.data.items():
            certificate_data[key] = value

        # Certificate type
        certificate_data["certificate_type"] = (
            self.certificate_type
        )

        # Design
        certificate_data["design_name"] = self.design_name

        # Dynamic fields
        dynamic_fields = {}

        for field_name, field_info in self.fields.items():

            if not field_info.get("visible", True):
                continue

            dynamic_fields[field_name] = field_info.get(
                "value",
                ""
            )

        certificate_data["fields"] = dynamic_fields

        return certificate_data

    # ---------------------------------------------------------
    # RESET
    # ---------------------------------------------------------

    def clear(self):
        self.data.clear()
        self.fields.clear()

        self.certificate_type = "Certificate"
        self.design_name = "Classic Gold"

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    def summary(self):
        return {
            "certificate_type": self.certificate_type,
            "design": self.design_name,
            "data_count": len(self.data),
            "field_count": len(self.fields),
            "data": self.get_all_data(),
            "fields": self.get_all_fields()
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("STEP 10 - UNIVERSAL DATA SYSTEM TEST")
    print("=" * 60)

    certificate = UniversalCertificateData()

    # Certificate purpose/type
    certificate.set_certificate_type(
        "Certificate of Achievement"
    )

    # Normal data
    certificate.set_data(
        "name",
        "Mohammad Ahad"
    )

    certificate.set_data(
        "roll_no",
        "15"
    )

    certificate.set_data(
        "course",
        "BSc IT"
    )

    certificate.set_data(
        "organization",
        "Siddharth College"
    )

    # Automatic date and time
    certificate.set_current_datetime()

    # Certificate ID
    certificate.set_certificate_id(
        "CERT-2026-0001"
    )

    # Completely custom fields
    certificate.add_field(
        "Specialization",
        "Artificial Intelligence",
        "text"
    )

    certificate.add_field(
        "Phone Number",
        "9876543210",
        "phone"
    )

    certificate.add_field(
        "Grade",
        "A+",
        "text"
    )

    certificate.add_field(
        "Achievement",
        "Successfully completed the program.",
        "textarea"
    )

    # Display data
    print("\nCERTIFICATE DATA:")
    print("-" * 60)

    for key, value in certificate.get_all_data().items():
        print(f"{key}: {value}")

    print("\nCUSTOM FIELDS:")
    print("-" * 60)

    for key, value in certificate.get_all_fields().items():
        print(f"{key}: {value['value']}")

    # Validation
    print("\nVALIDATION:")
    print("-" * 60)

    errors = certificate.validate()

    if errors:
        for error in errors:
            print("ERROR:", error)
    else:
        print("All required fields are valid.")

    # Final certificate-engine data
    print("\nFINAL CERTIFICATE DATA:")
    print("-" * 60)

    final_data = certificate.to_certificate_data()

    for key, value in final_data.items():
        print(f"{key}: {value}")

    # Summary
    print("\nSUMMARY:")
    print("-" * 60)

    print(certificate.summary())

    print("\n" + "=" * 60)
    print("STEP 10 TEST COMPLETED SUCCESSFULLY")
    print("=" * 60)