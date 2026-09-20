# ============================================================
# UNIVERSAL CERTIFICATE GENERATOR
# Date & Time Manager
# ============================================================

from datetime import datetime


# ============================================================
# CURRENT DATE & TIME
# ============================================================

def get_current_datetime():
    """
    System ki current date aur time return karta hai.
    """

    return datetime.now()


# ============================================================
# FORMAT DATE
# ============================================================

def format_date(date_value=None, date_format="DD-MM-YYYY"):
    """
    Date ko selected format mein convert karta hai.
    """

    if date_value is None:
        date_value = datetime.now()

    formats = {
        "DD-MM-YYYY": "%d-%m-%Y",
        "MM-DD-YYYY": "%m-%d-%Y",
        "YYYY-MM-DD": "%Y-%m-%d",
        "DD/MM/YYYY": "%d/%m/%Y",
        "MM/DD/YYYY": "%m/%d/%Y",
        "YYYY/MM/DD": "%Y/%m/%d",
        "DD MMM YYYY": "%d %b %Y",
        "DD Month YYYY": "%d %B %Y"
    }

    python_format = formats.get(
        date_format,
        "%d-%m-%Y"
    )

    return date_value.strftime(python_format)


# ============================================================
# FORMAT TIME
# ============================================================

def format_time(time_value=None, time_format="12-HOUR"):
    """
    Time ko 12-hour ya 24-hour format mein convert karta hai.
    """

    if time_value is None:
        time_value = datetime.now()

    if time_format == "24-HOUR":
        return time_value.strftime("%H:%M:%S")

    return time_value.strftime("%I:%M:%S %p")


# ============================================================
# GET DATE AND TIME
# ============================================================

def get_date_time(
    date_mode="automatic",
    manual_date=None,
    date_format="DD-MM-YYYY",
    time_mode="automatic",
    manual_time=None,
    time_format="12-HOUR"
):
    """
    Certificate ke liye date aur time prepare karta hai.

    date_mode:
        automatic
        manual

    time_mode:
        automatic
        manual
    """

    now = datetime.now()

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    if date_mode == "automatic":

        final_date = format_date(
            now,
            date_format
        )

    elif date_mode == "manual":

        if not manual_date:
            raise ValueError(
                "Manual date is required."
            )

        try:

            parsed_date = datetime.strptime(
                manual_date,
                "%Y-%m-%d"
            )

            final_date = format_date(
                parsed_date,
                date_format
            )

        except ValueError:

            raise ValueError(
                "Manual date must be in YYYY-MM-DD format."
            )

    else:

        raise ValueError(
            "Invalid date mode."
        )

    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    if time_mode == "automatic":

        final_time = format_time(
            now,
            time_format
        )

    elif time_mode == "manual":

        if not manual_time:
            raise ValueError(
                "Manual time is required."
            )

        try:

            parsed_time = datetime.strptime(
                manual_time,
                "%H:%M:%S"
            )

            final_time = format_time(
                parsed_time,
                time_format
            )

        except ValueError:

            raise ValueError(
                "Manual time must be in HH:MM:SS format."
            )

    else:

        raise ValueError(
            "Invalid time mode."
        )

    return {
        "date": final_date,
        "time": final_time,
        "date_mode": date_mode,
        "time_mode": time_mode,
        "date_format": date_format,
        "time_format": time_format
    }


# ============================================================
# DEMO / TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("          DATE & TIME MANAGER TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # AUTOMATIC DATE & TIME
    # --------------------------------------------------------

    print()
    print("1. AUTOMATIC DATE & TIME")
    print("-" * 60)

    automatic = get_date_time(
        date_mode="automatic",
        date_format="DD-MM-YYYY",
        time_mode="automatic",
        time_format="12-HOUR"
    )

    print("Date:", automatic["date"])
    print("Time:", automatic["time"])

    # --------------------------------------------------------
    # DIFFERENT DATE FORMAT
    # --------------------------------------------------------

    print()
    print("2. DIFFERENT DATE FORMAT")
    print("-" * 60)

    formats_to_test = [
        "DD-MM-YYYY",
        "MM-DD-YYYY",
        "YYYY-MM-DD",
        "DD/MM/YYYY",
        "MM/DD/YYYY",
        "YYYY/MM/DD",
        "DD MMM YYYY",
        "DD Month YYYY"
    ]

    for selected_format in formats_to_test:

        result = get_date_time(
            date_mode="automatic",
            date_format=selected_format,
            time_mode="automatic",
            time_format="24-HOUR"
        )

        print(
            selected_format,
            "=>",
            result["date"],
            "|",
            result["time"]
        )

    # --------------------------------------------------------
    # MANUAL DATE & TIME
    # --------------------------------------------------------

    print()
    print("3. MANUAL DATE & TIME")
    print("-" * 60)

    manual = get_date_time(
        date_mode="manual",
        manual_date="2026-09-09",
        date_format="DD-MM-YYYY",
        time_mode="manual",
        manual_time="17:30:00",
        time_format="12-HOUR"
    )

    print("Manual Date:", manual["date"])
    print("Manual Time:", manual["time"])

    print()
    print("=" * 60)
    print("STEP 2 TEST COMPLETED")
    print("=" * 60)