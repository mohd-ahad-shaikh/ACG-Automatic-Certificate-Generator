"""
Design Engine
Universal Automatic Certificate Generator

This module manages certificate design settings.
It does not generate the PDF directly.
"""

from copy import deepcopy


# ============================================================
# DEFAULT PROFESSIONAL CERTIFICATE DESIGN
# ============================================================

DEFAULT_DESIGN = {
    # --------------------------------------------------------
    # PAGE
    # --------------------------------------------------------
    "page": {
        "size": "A4",
        "orientation": "landscape",
        "margin": 35
    },

    # --------------------------------------------------------
    # MAIN COLORS
    # --------------------------------------------------------
    "colors": {
        "background": "#FFFFFF",
        "primary": "#1F3A5F",
        "secondary": "#C9A227",
        "text": "#222222",
        "muted_text": "#666666",
        "border": "#C9A227",
        "accent": "#1F3A5F"
    },

    # --------------------------------------------------------
    # BORDER
    # --------------------------------------------------------
    "border": {
        "enabled": True,
        "style": "double",
        "width": 2,
        "inner_width": 1,
        "padding": 14,
        "corner_radius": 0
    },

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------
    "title": {
        "text": "CERTIFICATE",
        "font": "Helvetica-Bold",
        "size": 30,
        "color": "#1F3A5F",
        "x": "center",
        "y": 500,
        "align": "center"
    },

    # --------------------------------------------------------
    # CERTIFICATE TYPE / SUBTITLE
    # --------------------------------------------------------
    "subtitle": {
        "enabled": True,
        "text": "OF ACHIEVEMENT",
        "font": "Helvetica-Bold",
        "size": 16,
        "color": "#C9A227",
        "x": "center",
        "y": 465,
        "align": "center"
    },

    # --------------------------------------------------------
    # INTRODUCTION TEXT
    # --------------------------------------------------------
    "intro": {
        "enabled": True,
        "text": "This certificate is proudly presented to",
        "font": "Helvetica",
        "size": 13,
        "color": "#666666",
        "x": "center",
        "y": 425,
        "align": "center"
    },

    # --------------------------------------------------------
    # RECIPIENT NAME
    # --------------------------------------------------------
    "recipient": {
        "font": "Helvetica-Bold",
        "size": 28,
        "color": "#1F3A5F",
        "x": "center",
        "y": 385,
        "align": "center",
        "underline": True
    },

    # --------------------------------------------------------
    # DESCRIPTION / PURPOSE
    # --------------------------------------------------------
    "description": {
        "enabled": True,
        "text": "For outstanding participation and achievement.",
        "font": "Helvetica",
        "size": 12,
        "color": "#333333",
        "x": "center",
        "y": 335,
        "align": "center",
        "max_width": 650
    },

    # --------------------------------------------------------
    # DYNAMIC FIELDS
    # --------------------------------------------------------
    "fields": {
        "enabled": True,
        "font": "Helvetica",
        "label_font": "Helvetica-Bold",
        "size": 10,
        "label_size": 10,
        "color": "#222222",
        "label_color": "#1F3A5F",
        "start_y": 285,
        "line_gap": 24,
        "alignment": "center"
    },

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------
    "date": {
        "enabled": True,
        "label": "Date",
        "font": "Helvetica",
        "size": 10,
        "color": "#333333",
        "x": 100,
        "y": 80,
        "align": "left"
    },

    # --------------------------------------------------------
    # CERTIFICATE ID
    # --------------------------------------------------------
    "certificate_id": {
        "enabled": True,
        "label": "Certificate ID",
        "font": "Helvetica",
        "size": 9,
        "color": "#555555",
        "x": 100,
        "y": 62,
        "align": "left"
    },

    # --------------------------------------------------------
    # ORGANIZATION / INSTITUTE
    # --------------------------------------------------------
    "organization": {
        "enabled": True,
        "font": "Helvetica-Bold",
        "size": 12,
        "color": "#1F3A5F",
        "x": "center",
        "y": 535,
        "align": "center"
    },

    # --------------------------------------------------------
    # LOGO
    # --------------------------------------------------------
    "logo": {
        "enabled": False,
        "path": "",
        "x": 50,
        "y": 475,
        "width": 70,
        "height": 70
    },

    # --------------------------------------------------------
    # SIGNATURE
    # --------------------------------------------------------
    "signature": {
        "enabled": True,
        "path": "",
        "x": 650,
        "y": 65,
        "width": 100,
        "height": 45,
        "label": "Authorized Signature",
        "label_size": 9
    },

    # --------------------------------------------------------
    # SEAL / EMBLEM
    # --------------------------------------------------------
    "seal": {
        "enabled": False,
        "path": "",
        "x": 365,
        "y": 55,
        "width": 70,
        "height": 70
    },

    # --------------------------------------------------------
    # DECORATIVE ELEMENTS
    # --------------------------------------------------------
    "decorations": {
        "top_line": True,
        "bottom_line": True,
        "corner_design": True,
        "center_emblem": False,
        "small_accents": True
    },

    # --------------------------------------------------------
    # BACKGROUND
    # --------------------------------------------------------
    "background": {
        "enabled": False,
        "path": "",
        "opacity": 1.0
    }
}


# ============================================================
# BUILT-IN PROFESSIONAL THEMES
# ============================================================

THEMES = {

    "Royal Blue": {
        "background": "#FFFFFF",
        "border": "#1F4E79",
        "title": "#163A5F",
        "text": "#333333",
        "accent": "#1F4E79"
    },

    "Classic Gold": {
        "background": "#FFFDF7",
        "border": "#C9A227",
        "title": "#6E5315",
        "text": "#333333",
        "accent": "#C9A227"
    },

    "Emerald": {
        "background": "#FBFFFD",
        "border": "#16805B",
        "title": "#07563D",
        "text": "#303030",
        "accent": "#16805B"
    },

    "Burgundy": {
        "background": "#FFF9FA",
        "border": "#7B2435",
        "title": "#641B2A",
        "text": "#333333",
        "accent": "#7B2435"
    },

    "Royal Purple": {
        "background": "#FCFAFF",
        "border": "#663399",
        "title": "#4B2470",
        "text": "#333333",
        "accent": "#663399"
    },

    "Minimal": {
        "background": "#FFFFFF",
        "border": "#333333",
        "title": "#222222",
        "text": "#333333",
        "accent": "#555555"
    }
}


# ============================================================
# BUILT-IN FONTS (SUPPORTED BY REPORTLAB / CORE PDF FONTS)
# ============================================================

BUILTIN_FONTS = [
    "Helvetica",
    "Helvetica-Bold",
    "Helvetica-Oblique",
    "Times-Roman",
    "Times-Bold",
    "Times-Italic",
    "Courier",
    "Courier-Bold",
    "Courier-Oblique"
]


def get_available_themes():
    """
    Return the dictionary of built-in themes.
    """

    return deepcopy(THEMES)


def get_available_fonts():
    """
    Return the list of built-in fonts.
    """

    return list(BUILTIN_FONTS)


def apply_theme(design, theme_name):
    """
    Apply a built-in theme's colors onto an existing design
    dict. Only touches color-related fields; layout, text,
    and assets stay untouched.
    """

    theme = THEMES.get(theme_name)

    if not theme:
        return design

    if "colors" in design:
        design["colors"]["background"] = theme["background"]
        design["colors"]["border"] = theme["border"]
        design["colors"]["primary"] = theme["title"]
        design["colors"]["text"] = theme["text"]
        design["colors"]["accent"] = theme["accent"]

    if "border" in design:
        design["border"]["enabled"] = True

    if "title" in design:
        design["title"]["color"] = theme["title"]

    if "organization" in design:
        design["organization"]["color"] = theme["title"]

    if "recipient" in design:
        design["recipient"]["color"] = theme["title"]

    return design


# ============================================================
# DESIGN FUNCTIONS
# ============================================================

def get_default_design():
    """
    Return a fresh copy of the default design.
    """

    return deepcopy(DEFAULT_DESIGN)


def get_design_value(design, section, key, default=None):
    """
    Safely get one design value.
    """

    try:
        return design[section][key]
    except (KeyError, TypeError):
        return default


def set_design_value(design, section, key, value):
    """
    Set or create a design value.
    """

    if section not in design:
        design[section] = {}

    design[section][key] = value

    return design


def update_design(design, updates):
    """
    Update multiple design settings.

    Example:

        updates = {
            "colors": {
                "primary": "#000000"
            },
            "title": {
                "size": 35
            }
        }
    """

    for section, values in updates.items():

        if section not in design:
            design[section] = {}

        if isinstance(values, dict):

            for key, value in values.items():
                design[section][key] = value

        else:
            design[section] = values

    return design


def reset_design():
    """
    Create a completely fresh default design.
    """

    return get_default_design()


# ============================================================
# DESIGN VALIDATION
# ============================================================

def validate_design(design):
    """
    Check whether important design sections exist.

    Returns:
        {
            "valid": True/False,
            "errors": [...]
        }
    """

    errors = []

    required_sections = [
        "page",
        "colors",
        "border",
        "title",
        "recipient",
        "fields"
    ]

    for section in required_sections:

        if section not in design:
            errors.append(
                f"Missing design section: {section}"
            )

    # Check page orientation
    if "page" in design:

        orientation = design["page"].get(
            "orientation",
            "landscape"
        )

        if orientation not in [
            "landscape",
            "portrait"
        ]:
            errors.append(
                "Page orientation must be landscape or portrait."
            )

    # Check page size
    if "page" in design:

        size = design["page"].get("size", "A4")

        if not isinstance(size, str):
            errors.append(
                "Page size must be a string."
            )

    # Check colors
    if "colors" in design:

        colors = design["colors"]

        for color_name in [
            "background",
            "primary",
            "secondary",
            "text",
            "border"
        ]:

            if color_name not in colors:
                errors.append(
                    f"Missing color: {color_name}"
                )

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


# ============================================================
# DESIGN SUMMARY
# ============================================================

def get_design_summary(design):
    """
    Return a simple summary of the current design.
    """

    return {
        "page_size": get_design_value(
            design,
            "page",
            "size"
        ),

        "orientation": get_design_value(
            design,
            "page",
            "orientation"
        ),

        "primary_color": get_design_value(
            design,
            "colors",
            "primary"
        ),

        "secondary_color": get_design_value(
            design,
            "colors",
            "secondary"
        ),

        "border_enabled": get_design_value(
            design,
            "border",
            "enabled"
        ),

        "logo_enabled": get_design_value(
            design,
            "logo",
            "enabled"
        ),

        "signature_enabled": get_design_value(
            design,
            "signature",
            "enabled"
        ),

        "seal_enabled": get_design_value(
            design,
            "seal",
            "enabled"
        ),

        "background_enabled": get_design_value(
            design,
            "background",
            "enabled"
        )
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    design = get_default_design()

    result = validate_design(design)

    print("====================================")
    print(" DESIGN ENGINE TEST")
    print("====================================")

    if result["valid"]:
        print("Design validation: SUCCESS")
    else:
        print("Design validation: FAILED")

        for error in result["errors"]:
            print("-", error)

    print("\nDesign Summary:")

    summary = get_design_summary(design)

    for key, value in summary.items():
        print(f"{key}: {value}")

    print("\nDesign Engine is working successfully.")