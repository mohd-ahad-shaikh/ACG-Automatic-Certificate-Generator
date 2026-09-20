"""
Universal Certificate Platform
STEP 13A - Validation Manager

Handles:
- Empty data validation
- Required field validation
- Certificate ID validation
- Duplicate ID detection
- CSV row validation
- Filename safety
- Text length validation
"""

import re


# ============================================================
# BASIC TEXT VALIDATION
# ============================================================

def clean_text(value):
    """Convert any value into clean text."""
    if value is None:
        return ""

    return str(value).strip()


def is_empty(value):
    """Return True when a value is empty."""
    return clean_text(value) == ""


# ============================================================
# REQUIRED FIELD VALIDATION
# ============================================================

def validate_required_fields(data, required_fields=None):
    """
    Validate required fields.

    data:
        Dictionary containing certificate information.

    required_fields:
        List of field names which must contain a value.
    """

    if required_fields is None:
        required_fields = []

    errors = []

    for field in required_fields:
        value = data.get(field, "")

        if is_empty(value):
            errors.append(
                f"Required field is empty: {field}"
            )

    return errors


# ============================================================
# CERTIFICATE DATA VALIDATION
# ============================================================

def validate_certificate_data(data):
    """
    Validate general certificate data.

    Returns:
        {
            "valid": True/False,
            "errors": [...]
        }
    """

    errors = []

    if not isinstance(data, dict):
        return {
            "valid": False,
            "errors": ["Certificate data must be a dictionary."]
        }

    # --------------------------------------------------------
    # Certificate title
    # --------------------------------------------------------

    title = clean_text(data.get("title", ""))

    if not title:
        errors.append("Certificate title is required.")

    elif len(title) > 200:
        errors.append(
            "Certificate title is too long. Maximum 200 characters."
        )

    # --------------------------------------------------------
    # Recipient
    # --------------------------------------------------------

    recipient = clean_text(
        data.get("recipient", "")
        or data.get("name", "")
    )

    if not recipient:
        errors.append("Recipient name is required.")

    elif len(recipient) > 200:
        errors.append(
            "Recipient name is too long. Maximum 200 characters."
        )

    # --------------------------------------------------------
    # Description
    # --------------------------------------------------------

    description = clean_text(
        data.get("description", "")
    )

    if len(description) > 3000:
        errors.append(
            "Description is too long. Maximum 3000 characters."
        )

    # --------------------------------------------------------
    # Organization
    # --------------------------------------------------------

    organization = clean_text(
        data.get("organization", "")
    )

    if len(organization) > 300:
        errors.append(
            "Organization name is too long. Maximum 300 characters."
        )

    # --------------------------------------------------------
    # Certificate ID
    # --------------------------------------------------------

    certificate_id = clean_text(
        data.get("certificate_id", "")
    )

    if certificate_id:
        id_errors = validate_certificate_id(certificate_id)
        errors.extend(id_errors)

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


# ============================================================
# CERTIFICATE ID VALIDATION
# ============================================================

def validate_certificate_id(certificate_id):
    """
    Validate certificate ID.

    Allows:
        CERT-2026-001
        CERT-ABC-123
        MY-CERT-001

    Blocks dangerous filesystem characters.
    """

    errors = []

    certificate_id = clean_text(certificate_id)

    if not certificate_id:
        return errors

    if len(certificate_id) > 100:
        errors.append(
            "Certificate ID is too long. Maximum 100 characters."
        )
        return errors

    # Characters that are unsafe/problematic in filenames
    dangerous_characters = [
        "/",
        "\\",
        ":",
        "*",
        "?",
        "\"",
        "<",
        ">",
        "|"
    ]

    for char in dangerous_characters:
        if char in certificate_id:
            errors.append(
                f"Certificate ID contains invalid character: {char}"
            )

    # Remove control characters
    if any(ord(char) < 32 for char in certificate_id):
        errors.append(
            "Certificate ID contains invalid control characters."
        )

    return errors


# ============================================================
# DUPLICATE CERTIFICATE ID CHECK
# ============================================================

def find_duplicate_ids(ids):
    """
    Find duplicate certificate IDs.

    Example:
        ["CERT-001", "CERT-002", "CERT-001"]

    Returns:
        ["CERT-001"]
    """

    seen = set()
    duplicates = set()

    for value in ids:

        value = clean_text(value)

        if not value:
            continue

        normalized = value.lower()

        if normalized in seen:
            duplicates.add(value)
        else:
            seen.add(normalized)

    return sorted(list(duplicates))


def validate_unique_ids(ids):
    """
    Validate that all IDs are unique.

    Returns:
        {
            "valid": True/False,
            "duplicates": [...]
        }
    """

    duplicates = find_duplicate_ids(ids)

    return {
        "valid": len(duplicates) == 0,
        "duplicates": duplicates
    }


# ============================================================
# CSV ROW VALIDATION
# ============================================================

def validate_csv_row(row, row_number=None):
    """
    Validate one CSV row.

    A row must be a dictionary.
    """

    errors = []

    if not isinstance(row, dict):
        message = "CSV row must be a dictionary."

        if row_number is not None:
            message = f"Row {row_number}: {message}"

        return [message]

    # Check for completely empty row
    values = list(row.values())

    if not any(not is_empty(value) for value in values):

        message = "CSV row is completely empty."

        if row_number is not None:
            message = f"Row {row_number}: {message}"

        errors.append(message)

        return errors

    # Check empty column names
    for key in row.keys():

        if is_empty(key):

            message = "CSV contains an empty column name."

            if row_number is not None:
                message = f"Row {row_number}: {message}"

            errors.append(message)

    return errors


# ============================================================
# CSV DATASET VALIDATION
# ============================================================

def validate_csv_records(records):
    """
    Validate complete CSV record list.

    Returns:
        {
            "valid": True/False,
            "errors": [...],
            "valid_rows": [...],
            "invalid_rows": [...]
        }
    """

    errors = []
    valid_rows = []
    invalid_rows = []

    if not records:
        return {
            "valid": False,
            "errors": ["CSV file contains no records."],
            "valid_rows": [],
            "invalid_rows": []
        }

    for index, row in enumerate(records, start=2):

        row_errors = validate_csv_row(
            row,
            row_number=index
        )

        if row_errors:

            errors.extend(row_errors)

            invalid_rows.append({
                "row_number": index,
                "row": row,
                "errors": row_errors
            })

        else:

            valid_rows.append({
                "row_number": index,
                "row": row
            })

    return {
        "valid": len(invalid_rows) == 0,
        "errors": errors,
        "valid_rows": valid_rows,
        "invalid_rows": invalid_rows
    }


# ============================================================
# NAME FIELD VALIDATION
# ============================================================

def validate_recipient_name(name):
    """
    Validate recipient name.
    """

    errors = []

    name = clean_text(name)

    if not name:
        errors.append("Recipient name cannot be empty.")

        return errors

    if len(name) > 200:
        errors.append(
            "Recipient name cannot exceed 200 characters."
        )

    return errors


# ============================================================
# EMAIL VALIDATION
# ============================================================

def validate_email(email):
    """
    Validate email when a custom field uses email type.
    """

    errors = []

    email = clean_text(email)

    if not email:
        return errors

    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not re.match(pattern, email):
        errors.append(
            f"Invalid email address: {email}"
        )

    return errors


# ============================================================
# PHONE VALIDATION
# ============================================================

def validate_phone(phone):
    """
    Basic phone validation.

    Allows:
        +91 9876543210
        9876543210
        022-12345678
    """

    errors = []

    phone = clean_text(phone)

    if not phone:
        return errors

    # Keep only common phone characters for checking
    allowed_pattern = r"^[0-9+\-\s().]{6,30}$"

    if not re.match(allowed_pattern, phone):

        errors.append(
            f"Invalid phone number: {phone}"
        )

    return errors


# ============================================================
# CUSTOM FIELD VALIDATION
# ============================================================

def validate_custom_fields(fields):
    """
    Validate dynamic/custom fields.

    Supports either:

        [
            {"label": "Roll Number", "value": "15"}
        ]

    OR:

        {
            "Roll Number": "15",
            "Course": "BSc IT"
        }
    """

    errors = []

    if fields is None:
        return errors

    # --------------------------------------------------------
    # Dictionary format
    # --------------------------------------------------------

    if isinstance(fields, dict):

        for label, value in fields.items():

            label = clean_text(label)
            value = clean_text(value)

            if not label:
                errors.append(
                    "Custom field label cannot be empty."
                )

            if len(label) > 150:
                errors.append(
                    f"Custom field label is too long: {label}"
                )

        return errors

    # --------------------------------------------------------
    # List format
    # --------------------------------------------------------

    if isinstance(fields, list):

        for index, field in enumerate(fields, start=1):

            if not isinstance(field, dict):

                errors.append(
                    f"Custom field #{index} is invalid."
                )

                continue

            label = clean_text(
                field.get("label", "")
            )

            value = field.get("value", "")

            if not label:

                errors.append(
                    f"Custom field #{index} has no label."
                )

            elif len(label) > 150:

                errors.append(
                    f"Custom field #{index} label is too long."
                )

            # Email type
            field_type = clean_text(
                field.get("type", "")
            ).lower()

            if field_type == "email":

                errors.extend(
                    validate_email(value)
                )

            # Phone type
            elif field_type == "phone":

                errors.extend(
                    validate_phone(value)
                )

        return errors

    errors.append(
        "Custom fields must be a dictionary or list."
    )

    return errors


# ============================================================
# FILE NAME VALIDATION
# ============================================================

def safe_filename(filename, default="certificate"):
    """
    Create a safe filename.

    This does NOT create a file.
    """

    filename = clean_text(filename)

    if not filename:
        filename = default

    # Remove extension first
    filename = re.sub(
        r"\.[A-Za-z0-9]{1,10}$",
        "",
        filename
    )

    # Replace unsafe characters
    filename = re.sub(
        r"[^A-Za-z0-9._ -]",
        "_",
        filename
    )

    # Remove repeated spaces
    filename = re.sub(
        r"\s+",
        " ",
        filename
    )

    # Prevent problematic filenames
    filename = filename.strip(" .")

    if not filename:
        filename = default

    # Limit filename length
    filename = filename[:150]

    return filename


# ============================================================
# BULK RECORD VALIDATION
# ============================================================

def validate_bulk_record(
    record,
    row_number=None,
    name_key=None
):
    """
    Validate one bulk-generation record.

    Name/recipient is required when name_key is supplied.
    """

    errors = []

    if not isinstance(record, dict):

        errors.append(
            "Record must be a dictionary."
        )

        return errors

    # --------------------------------------------------------
    # Name validation
    # --------------------------------------------------------

    if name_key:

        name = record.get(name_key, "")

        name_errors = validate_recipient_name(name)

        for error in name_errors:

            if row_number is not None:

                errors.append(
                    f"Row {row_number}: {error}"
                )

            else:

                errors.append(error)

    # --------------------------------------------------------
    # All values
    # --------------------------------------------------------

    for key, value in record.items():

        key_text = clean_text(key)

        if not key_text:

            errors.append(
                f"Row {row_number}: Empty column name."
                if row_number is not None
                else "Empty column name."
            )

    return errors


# ============================================================
# BULK VALIDATION SUMMARY
# ============================================================

def validate_bulk_records(
    records,
    name_key=None
):
    """
    Validate all bulk records.

    Returns:
        {
            "total": number,
            "valid": number,
            "invalid": number,
            "errors": [...],
            "valid_records": [...],
            "invalid_records": [...]
        }
    """

    result = {
        "total": 0,
        "valid": 0,
        "invalid": 0,
        "errors": [],
        "valid_records": [],
        "invalid_records": []
    }

    if not records:
        result["errors"].append(
            "No records were provided."
        )

        return result

    result["total"] = len(records)

    for index, record in enumerate(records, start=2):

        row_errors = validate_bulk_record(
            record,
            row_number=index,
            name_key=name_key
        )

        if row_errors:

            result["invalid"] += 1

            result["errors"].extend(row_errors)

            result["invalid_records"].append({
                "row_number": index,
                "record": record,
                "errors": row_errors
            })

        else:

            result["valid"] += 1

            result["valid_records"].append({
                "row_number": index,
                "record": record
            })

    return result


# ============================================================
# GENERAL VALIDATION
# ============================================================

def validate_all(
    certificate_data=None,
    custom_fields=None
):
    """
    Run complete validation.
    """

    errors = []

    if certificate_data is not None:

        result = validate_certificate_data(
            certificate_data
        )

        errors.extend(
            result["errors"]
        )

    if custom_fields is not None:

        errors.extend(
            validate_custom_fields(
                custom_fields
            )
        )

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


# ============================================================
# ERROR FORMATTER
# ============================================================

def format_errors(errors):
    """
    Convert errors into a clean text message.
    """

    if not errors:
        return ""

    cleaned = []

    for error in errors:

        text = clean_text(error)

        if text:
            cleaned.append(
                f"• {text}"
            )

    return "\n".join(cleaned)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("STEP 13A - VALIDATION MANAGER TEST")
    print("=" * 60)

    data = {
        "title": "Certificate of Achievement",
        "recipient": "Rahul Sharma",
        "organization": "Siddharth College",
        "description": "Successfully completed the workshop.",
        "certificate_id": "CERT-2026-001"
    }

    result = validate_certificate_data(data)

    print("\nCertificate Validation:")
    print("Valid:", result["valid"])

    if result["errors"]:
        print(format_errors(result["errors"]))
    else:
        print("No errors found.")

    ids = [
        "CERT-001",
        "CERT-002",
        "CERT-001",
        "CERT-003"
    ]

    duplicate_result = validate_unique_ids(ids)

    print("\nDuplicate ID Test:")
    print("Valid:", duplicate_result["valid"])
    print("Duplicates:", duplicate_result["duplicates"])

    filename = safe_filename(
        "Rahul Sharma / Certificate: 2026"
    )

    print("\nSafe Filename:")
    print(filename)

    print("\n" + "=" * 60)
    print("STEP 13A TEST COMPLETED")
    print("=" * 60)