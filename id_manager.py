# ============================================================
# UNIVERSAL CERTIFICATE GENERATOR
# Certificate ID Manager
# ============================================================

from datetime import datetime
import re


# ============================================================
# AUTOMATIC ID GENERATOR
# ============================================================

def generate_certificate_id(
    prefix="CERT",
    year=None,
    number=1,
    digits=6
):
    """
    Automatic certificate ID generate karta hai.

    Example:
    CERT-2026-000001
    """

    if year is None:
        year = datetime.now().year

    prefix = str(prefix).strip().upper()

    if not prefix:
        prefix = "CERT"

    if not isinstance(number, int):
        raise ValueError("Certificate number must be an integer.")

    if number < 1:
        raise ValueError("Certificate number must be greater than 0.")

    if not isinstance(digits, int) or digits < 1:
        raise ValueError("Digits must be a positive integer.")

    formatted_number = str(number).zfill(digits)

    return f"{prefix}-{year}-{formatted_number}"


# ============================================================
# CUSTOM ID GENERATOR
# ============================================================

def generate_custom_id(
    prefix,
    number,
    separator="-",
    digits=6
):
    """
    Custom certificate ID banata hai.

    Example:

    prefix = BSCIT
    number = 15

    Result:
    BSCIT-000015
    """

    prefix = str(prefix).strip().upper()

    if not prefix:
        raise ValueError("Prefix cannot be empty.")

    if not isinstance(number, int):
        raise ValueError("Number must be an integer.")

    if number < 1:
        raise ValueError("Number must be greater than 0.")

    formatted_number = str(number).zfill(digits)

    return (
        f"{prefix}"
        f"{separator}"
        f"{formatted_number}"
    )


# ============================================================
# MANUAL ID VALIDATION
# ============================================================

def validate_manual_id(certificate_id):
    """
    User ke manually entered Certificate ID ko validate karta hai.
    """

    if certificate_id is None:
        return False, "Certificate ID is required."

    certificate_id = str(
        certificate_id
    ).strip()

    if not certificate_id:
        return False, "Certificate ID cannot be empty."

    # Certificate ID mein dangerous characters allow nahi honge.
    if not re.match(
        r"^[A-Za-z0-9._-]+$",
        certificate_id
    ):
        return (
            False,
            "Certificate ID can contain only letters, "
            "numbers, hyphen and underscore."
        )

    if len(certificate_id) > 100:
        return False, "Certificate ID is too long."

    return True, "Certificate ID is valid."


# ============================================================
# CHECK DUPLICATE ID
# ============================================================

def is_duplicate_id(
    certificate_id,
    existing_ids
):
    """
    Check karta hai ki ID pehle se exist karti hai ya nahi.
    """

    if existing_ids is None:
        existing_ids = []

    target = str(
        certificate_id
    ).strip().lower()

    for existing_id in existing_ids:

        if str(existing_id).strip().lower() == target:
            return True

    return False


# ============================================================
# GET UNIQUE AUTOMATIC ID
# ============================================================

def generate_unique_id(
    existing_ids,
    prefix="CERT",
    year=None,
    start_number=1,
    digits=6
):
    """
    Existing IDs ko check karke unique automatic ID banata hai.
    """

    number = start_number

    while True:

        certificate_id = generate_certificate_id(
            prefix=prefix,
            year=year,
            number=number,
            digits=digits
        )

        if not is_duplicate_id(
            certificate_id,
            existing_ids
        ):
            return certificate_id

        number += 1


# ============================================================
# PREPARE CERTIFICATE ID
# ============================================================

def prepare_certificate_id(
    mode="automatic",
    manual_id=None,
    existing_ids=None,
    prefix="CERT",
    year=None,
    start_number=1,
    digits=6
):
    """
    Certificate ID ka final decision karta hai.

    mode:
        automatic
        manual
    """

    if existing_ids is None:
        existing_ids = []

    # --------------------------------------------------------
    # MANUAL MODE
    # --------------------------------------------------------

    if mode == "manual":

        valid, message = validate_manual_id(
            manual_id
        )

        if not valid:
            raise ValueError(message)

        if is_duplicate_id(
            manual_id,
            existing_ids
        ):
            raise ValueError(
                "This Certificate ID already exists."
            )

        return str(manual_id).strip()

    # --------------------------------------------------------
    # AUTOMATIC MODE
    # --------------------------------------------------------

    if mode == "automatic":

        return generate_unique_id(
            existing_ids=existing_ids,
            prefix=prefix,
            year=year,
            start_number=start_number,
            digits=digits
        )

    raise ValueError(
        "Invalid ID mode. Use automatic or manual."
    )


# ============================================================
# DEMO / TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("             CERTIFICATE ID MANAGER")
    print("=" * 60)

    # --------------------------------------------------------
    # EXISTING IDS
    # --------------------------------------------------------

    existing_ids = [
        "CERT-2026-000001",
        "CERT-2026-000002",
        "CERT-2026-000003"
    ]

    print()
    print("EXISTING IDS:")
    print("-" * 60)

    for certificate_id in existing_ids:
        print(certificate_id)

    # --------------------------------------------------------
    # AUTOMATIC UNIQUE ID
    # --------------------------------------------------------

    print()
    print("1. AUTOMATIC UNIQUE ID")
    print("-" * 60)

    automatic_id = prepare_certificate_id(
        mode="automatic",
        existing_ids=existing_ids,
        prefix="CERT",
        year=2026,
        start_number=1,
        digits=6
    )

    print(
        "Generated ID:",
        automatic_id
    )

    # --------------------------------------------------------
    # CUSTOM ID
    # --------------------------------------------------------

    print()
    print("2. CUSTOM ID")
    print("-" * 60)

    custom_id = generate_custom_id(
        prefix="BSCIT",
        number=15,
        separator="-",
        digits=6
    )

    print(
        "Custom ID:",
        custom_id
    )

    # --------------------------------------------------------
    # MANUAL ID
    # --------------------------------------------------------

    print()
    print("3. MANUAL ID")
    print("-" * 60)

    manual_id = prepare_certificate_id(
        mode="manual",
        manual_id="AHAD-CERT-001",
        existing_ids=existing_ids
    )

    print(
        "Manual ID:",
        manual_id
    )

    # --------------------------------------------------------
    # DUPLICATE TEST
    # --------------------------------------------------------

    print()
    print("4. DUPLICATE ID TEST")
    print("-" * 60)

    duplicate = is_duplicate_id(
        "CERT-2026-000002",
        existing_ids
    )

    print(
        "Is duplicate?",
        duplicate
    )

    # --------------------------------------------------------
    # VALIDATION TEST
    # --------------------------------------------------------

    print()
    print("5. MANUAL ID VALIDATION")
    print("-" * 60)

    valid, message = validate_manual_id(
        "CERT-AHAD-001"
    )

    print("Valid:", valid)
    print("Message:", message)

    print()
    print("=" * 60)
    print("STEP 3 TEST COMPLETED")
    print("=" * 60)