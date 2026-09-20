import csv
import os
import re


# ============================================================
# UNIVERSAL CERTIFICATE PLATFORM
# STEP 9 - CSV BULK DATA MANAGER
# ============================================================


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ------------------------------------------------------------
# CSV VALIDATION
# ------------------------------------------------------------

def validate_csv_file(csv_path):
    """Check whether the CSV file exists and is readable."""

    if not csv_path:
        raise ValueError("CSV file path cannot be empty.")

    if not os.path.isfile(csv_path):
        raise FileNotFoundError(
            "CSV file not found: " + csv_path
        )

    extension = os.path.splitext(csv_path)[1].lower()

    if extension != ".csv":
        raise ValueError(
            "Only CSV files are supported."
        )

    return True


# ------------------------------------------------------------
# CLEAN COLUMN NAME
# ------------------------------------------------------------

def clean_column_name(column_name):
    """
    Converts a CSV column name into a clean field name.
    """

    if column_name is None:
        return ""

    column_name = str(column_name).strip()

    column_name = re.sub(
        r"\s+",
        "_",
        column_name
    )

    column_name = re.sub(
        r"[^A-Za-z0-9_-]",
        "",
        column_name
    )

    return column_name


# ------------------------------------------------------------
# READ CSV HEADERS
# ------------------------------------------------------------

def get_csv_headers(csv_path):
    """
    Returns all column names from a CSV file.
    """

    validate_csv_file(csv_path)

    with open(
        csv_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.reader(file)

        try:
            headers = next(reader)
        except StopIteration:
            raise ValueError(
                "CSV file is empty."
            )

    headers = [
        str(header).strip()
        for header in headers
    ]

    if not any(headers):
        raise ValueError(
            "CSV file does not contain valid headers."
        )

    return headers


# ------------------------------------------------------------
# READ CSV RECORDS
# ------------------------------------------------------------

def read_csv(csv_path):
    """
    Reads the complete CSV and returns
    a list of dictionaries.
    """

    validate_csv_file(csv_path)

    with open(
        csv_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError(
                "CSV file does not contain headers."
            )

        headers = [
            str(header).strip()
            for header in reader.fieldnames
        ]

        records = []

        for row_number, row in enumerate(
            reader,
            start=2
        ):

            record = {}

            for header in headers:

                value = row.get(header, "")

                if value is None:
                    value = ""

                record[header] = str(
                    value
                ).strip()

            record["_row_number"] = row_number

            records.append(record)

    return records


# ------------------------------------------------------------
# NORMALIZE RECORD
# ------------------------------------------------------------

def normalize_record(record):
    """
    Cleans the keys and values of one CSV record.
    """

    normalized = {}

    for key, value in record.items():

        if key == "_row_number":
            normalized[key] = value
            continue

        clean_key = clean_column_name(
            key
        )

        if isinstance(value, str):
            clean_value = value.strip()
        else:
            clean_value = value

        normalized[clean_key] = clean_value

    return normalized


# ------------------------------------------------------------
# READ AND NORMALIZE CSV
# ------------------------------------------------------------

def load_records(csv_path):
    """
    Reads CSV and returns clean records.
    """

    records = read_csv(csv_path)

    normalized_records = []

    for record in records:

        normalized = normalize_record(
            record
        )

        normalized_records.append(
            normalized
        )

    return normalized_records


# ------------------------------------------------------------
# GET COLUMN MAPPING
# ------------------------------------------------------------

def create_column_mapping(
    csv_headers,
    dynamic_fields
):
    """
    Creates an initial mapping between
    CSV columns and certificate fields.

    Example:

    Name -> Name
    Roll_No -> Roll_No
    Course -> Course
    """

    mapping = {}

    clean_headers = {}

    for header in csv_headers:

        clean_headers[
            clean_column_name(header).lower()
        ] = header

    for field in dynamic_fields:

        field_name = field

        clean_field = clean_column_name(
            field_name
        ).lower()

        if clean_field in clean_headers:

            mapping[field_name] = (
                clean_headers[clean_field]
            )

    return mapping


# ------------------------------------------------------------
# APPLY COLUMN MAPPING
# ------------------------------------------------------------

def apply_mapping(
    record,
    mapping
):
    """
    Converts CSV data into certificate data
    according to the selected mapping.

    mapping format:

    {
        "name": "Student_Name",
        "course": "Course_Name"
    }
    """

    result = {}

    for certificate_field, csv_column in mapping.items():

        if csv_column in record:

            result[certificate_field] = (
                record[csv_column]
            )

        else:

            result[certificate_field] = ""

    return result


# ------------------------------------------------------------
# AUTO-DETECT COMMON FIELDS
# ------------------------------------------------------------

def auto_detect_mapping(headers):
    """
    Automatically detects common certificate fields.
    """

    aliases = {

        "name": [
            "name",
            "student_name",
            "recipient_name",
            "full_name",
            "participant_name"
        ],

        "roll_no": [
            "roll_no",
            "roll_number",
            "roll",
            "student_id"
        ],

        "id_number": [
            "id",
            "id_number",
            "identity_number"
        ],

        "phone": [
            "phone",
            "phone_number",
            "mobile",
            "mobile_number",
            "contact"
        ],

        "email": [
            "email",
            "email_address"
        ],

        "course": [
            "course",
            "course_name"
        ],

        "specialization": [
            "specialization",
            "specialisation",
            "branch",
            "stream"
        ],

        "organization": [
            "organization",
            "organisation",
            "institute",
            "institution",
            "college",
            "school",
            "company"
        ],

        "event": [
            "event",
            "event_name",
            "program",
            "programme"
        ],

        "date": [
            "date",
            "certificate_date",
            "issue_date"
        ]
    }

    mapping = {}

    cleaned_headers = {}

    for header in headers:

        cleaned = clean_column_name(
            header
        ).lower()

        cleaned_headers[cleaned] = header

    for field, possible_names in aliases.items():

        for name in possible_names:

            if name in cleaned_headers:

                mapping[field] = (
                    cleaned_headers[name]
                )

                break

    return mapping


# ------------------------------------------------------------
# VALIDATE RECORD
# ------------------------------------------------------------

def validate_record(
    record,
    required_fields
):
    """
    Validates required fields for one record.

    Returns:

    {
        "valid": True/False,
        "missing": [...]
    }
    """

    missing = []

    for field in required_fields:

        value = record.get(
            field,
            ""
        )

        if value is None or str(value).strip() == "":

            missing.append(field)

    return {

        "valid": len(missing) == 0,

        "missing": missing
    }


# ------------------------------------------------------------
# VALIDATE ALL RECORDS
# ------------------------------------------------------------

def validate_records(
    records,
    required_fields
):
    """
    Validates all CSV records.
    """

    results = []

    for index, record in enumerate(
        records,
        start=1
    ):

        validation = validate_record(
            record,
            required_fields
        )

        results.append({

            "record_number": index,

            "row_number": record.get(
                "_row_number",
                index + 1
            ),

            "valid": validation["valid"],

            "missing": validation["missing"]
        })

    return results


# ------------------------------------------------------------
# GET VALID RECORDS
# ------------------------------------------------------------

def get_valid_records(
    records,
    required_fields
):
    """
    Returns only records that contain
    all required fields.
    """

    valid_records = []

    for record in records:

        validation = validate_record(
            record,
            required_fields
        )

        if validation["valid"]:

            valid_records.append(record)

    return valid_records


# ------------------------------------------------------------
# GET INVALID RECORDS
# ------------------------------------------------------------

def get_invalid_records(
    records,
    required_fields
):
    """
    Returns records that have missing
    required information.
    """

    invalid_records = []

    for record in records:

        validation = validate_record(
            record,
            required_fields
        )

        if not validation["valid"]:

            invalid_records.append({

                "record": record,

                "missing": validation["missing"]
            })

    return invalid_records


# ------------------------------------------------------------
# CSV SUMMARY
# ------------------------------------------------------------

def get_csv_summary(csv_path):
    """
    Returns useful information about
    a CSV file.
    """

    headers = get_csv_headers(
        csv_path
    )

    records = read_csv(
        csv_path
    )

    return {

        "filename": os.path.basename(
            csv_path
        ),

        "path": csv_path,

        "columns": headers,

        "column_count": len(headers),

        "record_count": len(records)
    }


# ------------------------------------------------------------
# CREATE SAMPLE CSV
# ------------------------------------------------------------

def create_sample_csv(
    output_path
):
    """
    Creates a sample CSV for testing.
    """

    headers = [

        "Name",

        "Roll_No",

        "Course",

        "Specialization",

        "Institute",

        "Event",

        "Phone",

        "Email"
    ]

    rows = [

        [
            "Mohammad Ahad",
            "15",
            "BSc IT",
            "Information Technology",
            "Siddharth College",
            "Python Workshop",
            "9876543210",
            "ahad@example.com"
        ],

        [
            "Yaseer",
            "1",
            "BSc IT",
            "Information Technology",
            "Python Workshop",
            "9876543211",
            "yaseer@example.com"
        ],

        [
            "Kunal",
            "2",
            "BSc IT",
            "Information Technology",
            "Python Workshop",
            "9876543212",
            "kunal@example.com"
        ]
    ]

    directory = os.path.dirname(
        os.path.abspath(output_path)
    )

    if directory:
        os.makedirs(
            directory,
            exist_ok=True
        )

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        writer = csv.writer(file)

        writer.writerow(headers)

        writer.writerows(rows)

    return output_path


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "STEP 9 - CSV BULK DATA MANAGER TEST"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # Create sample CSV
    # --------------------------------------------------------

    sample_csv = os.path.join(
        BASE_DIR,
        "sample_bulk_data.csv"
    )

    create_sample_csv(
        sample_csv
    )

    print(
        "\nSample CSV created:"
    )

    print(sample_csv)


    # --------------------------------------------------------
    # CSV SUMMARY
    # --------------------------------------------------------

    summary = get_csv_summary(
        sample_csv
    )

    print(
        "\nCSV Summary:"
    )

    print(
        "Filename:",
        summary["filename"]
    )

    print(
        "Columns:",
        summary["columns"]
    )

    print(
        "Column Count:",
        summary["column_count"]
    )

    print(
        "Record Count:",
        summary["record_count"]
    )


    # --------------------------------------------------------
    # READ RECORDS
    # --------------------------------------------------------

    records = load_records(
        sample_csv
    )

    print(
        "\nRecords loaded:",
        len(records)
    )

    for record in records:

        print(record)


    # --------------------------------------------------------
    # AUTO MAPPING
    # --------------------------------------------------------

    mapping = auto_detect_mapping(
        summary["columns"]
    )

    print(
        "\nAutomatically detected mapping:"
    )

    for key, value in mapping.items():

        print(
            key,
            "<--",
            value
        )


    # --------------------------------------------------------
    # APPLY MAPPING
    # --------------------------------------------------------

    if records:

        certificate_data = apply_mapping(
            records[0],
            mapping
        )

        print(
            "\nFirst record converted into"
            " certificate data:"
        )

        print(
            certificate_data
        )


    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    required_fields = [
        "Name"
    ]

    validation_results = validate_records(
        records,
        required_fields
    )

    print(
        "\nValidation results:"
    )

    for result in validation_results:

        print(result)


    # --------------------------------------------------------
    # VALID / INVALID COUNT
    # --------------------------------------------------------

    valid_records = get_valid_records(
        records,
        required_fields
    )

    invalid_records = get_invalid_records(
        records,
        required_fields
    )

    print(
        "\nValid records:",
        len(valid_records)
    )

    print(
        "Invalid records:",
        len(invalid_records)
    )


    # --------------------------------------------------------
    # FINAL MESSAGE
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    print(
        "STEP 9 TEST COMPLETED SUCCESSFULLY"
    )

    print("=" * 60)