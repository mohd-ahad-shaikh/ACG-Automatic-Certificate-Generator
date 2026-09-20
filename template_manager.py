import os
import shutil
import re


# ============================================================
# UNIVERSAL CERTIFICATE PLATFORM
# STEP 8 - TEMPLATE & ASSET MANAGER
# ============================================================


# ------------------------------------------------------------
# BASE DIRECTORIES
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

BACKGROUNDS_DIR = os.path.join(UPLOADS_DIR, "backgrounds")
LOGOS_DIR = os.path.join(UPLOADS_DIR, "logos")
SIGNATURES_DIR = os.path.join(UPLOADS_DIR, "signatures")
SEALS_DIR = os.path.join(UPLOADS_DIR, "seals")
FONTS_DIR = os.path.join(UPLOADS_DIR, "fonts")
TEMPLATES_DIR = os.path.join(UPLOADS_DIR, "templates")


# ------------------------------------------------------------
# ALLOWED FILE TYPES
# ------------------------------------------------------------

ALLOWED_EXTENSIONS = {

    "background": [
        ".png",
        ".jpg",
        ".jpeg"
    ],

    "logo": [
        ".png",
        ".jpg",
        ".jpeg"
    ],

    "signature": [
        ".png",
        ".jpg",
        ".jpeg"
    ],

    "seal": [
        ".png",
        ".jpg",
        ".jpeg"
    ],

    "font": [
        ".ttf",
        ".otf"
    ],

    "template": [
        ".json"
    ]
}


# ------------------------------------------------------------
# DIRECTORY SETUP
# ------------------------------------------------------------

def create_directories():
    """
    Creates all required upload folders.
    """

    directories = [
        UPLOADS_DIR,
        BACKGROUNDS_DIR,
        LOGOS_DIR,
        SIGNATURES_DIR,
        SEALS_DIR,
        FONTS_DIR,
        TEMPLATES_DIR
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# ------------------------------------------------------------
# SAFE FILE NAME
# ------------------------------------------------------------

def safe_filename(filename):
    """
    Converts a filename into a safe filename.
    """

    if not filename:
        raise ValueError("Filename cannot be empty.")

    filename = os.path.basename(filename)

    filename = re.sub(
        r"[^A-Za-z0-9._-]",
        "_",
        filename
    )

    return filename


# ------------------------------------------------------------
# GET FILE EXTENSION
# ------------------------------------------------------------

def get_extension(filename):
    """
    Returns file extension in lowercase.
    """

    return os.path.splitext(filename)[1].lower()


# ------------------------------------------------------------
# VALIDATE ASSET TYPE
# ------------------------------------------------------------

def validate_asset(filename, asset_type):
    """
    Checks whether a file is allowed for the selected asset type.
    """

    asset_type = asset_type.lower().strip()

    if asset_type not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Invalid asset type: " + asset_type
        )

    extension = get_extension(filename)

    allowed = ALLOWED_EXTENSIONS[asset_type]

    if extension not in allowed:
        raise ValueError(
            "File type " + extension +
            " is not allowed for " +
            asset_type
        )

    return True


# ------------------------------------------------------------
# GET DIRECTORY FOR ASSET
# ------------------------------------------------------------

def get_asset_directory(asset_type):
    """
    Returns the correct folder for an asset.
    """

    folders = {

        "background": BACKGROUNDS_DIR,

        "logo": LOGOS_DIR,

        "signature": SIGNATURES_DIR,

        "seal": SEALS_DIR,

        "font": FONTS_DIR,

        "template": TEMPLATES_DIR
    }

    asset_type = asset_type.lower().strip()

    if asset_type not in folders:
        raise ValueError(
            "Unknown asset type: " + asset_type
        )

    return folders[asset_type]


# ------------------------------------------------------------
# MAKE UNIQUE FILE NAME
# ------------------------------------------------------------

def make_unique_filename(directory, filename):
    """
    Prevents accidental file replacement.
    """

    filename = safe_filename(filename)

    name, extension = os.path.splitext(filename)

    candidate = filename

    counter = 1

    while os.path.exists(
        os.path.join(directory, candidate)
    ):

        candidate = (
            name +
            "_" +
            str(counter) +
            extension
        )

        counter += 1

    return candidate


# ------------------------------------------------------------
# SAVE ASSET
# ------------------------------------------------------------

def save_asset(source_path, asset_type, new_filename=None):
    """
    Copies an asset into the correct upload folder.

    Example:

    save_asset(
        "mylogo.png",
        "logo"
    )
    """

    create_directories()

    if not os.path.isfile(source_path):
        raise FileNotFoundError(
            "Source file not found: " +
            source_path
        )

    asset_type = asset_type.lower().strip()

    validate_asset(
        source_path,
        asset_type
    )

    directory = get_asset_directory(
        asset_type
    )

    original_filename = os.path.basename(
        source_path
    )

    if new_filename:

        filename = safe_filename(
            new_filename
        )

        # Keep original extension if
        # user did not provide one.

        if not os.path.splitext(filename)[1]:

            filename += get_extension(
                original_filename
            )

    else:

        filename = safe_filename(
            original_filename
        )

    filename = make_unique_filename(
        directory,
        filename
    )

    destination = os.path.join(
        directory,
        filename
    )

    shutil.copy2(
        source_path,
        destination
    )

    return destination


# ------------------------------------------------------------
# LIST ASSETS
# ------------------------------------------------------------

def list_assets(asset_type=None):
    """
    Returns available assets.

    If asset_type is None,
    all asset categories are returned.
    """

    create_directories()

    folders = {

        "background": BACKGROUNDS_DIR,

        "logo": LOGOS_DIR,

        "signature": SIGNATURES_DIR,

        "seal": SEALS_DIR,

        "font": FONTS_DIR,

        "template": TEMPLATES_DIR
    }

    result = {}

    if asset_type:

        asset_type = asset_type.lower().strip()

        if asset_type not in folders:
            raise ValueError(
                "Unknown asset type: " +
                asset_type
            )

        folders = {
            asset_type: folders[asset_type]
        }

    for category, directory in folders.items():

        files = []

        if os.path.exists(directory):

            for filename in os.listdir(directory):

                full_path = os.path.join(
                    directory,
                    filename
                )

                if os.path.isfile(full_path):

                    files.append(filename)

        files.sort()

        result[category] = files

    return result


# ------------------------------------------------------------
# GET ASSET PATH
# ------------------------------------------------------------

def get_asset_path(asset_type, filename):
    """
    Returns full path of an asset.
    """

    create_directories()

    asset_type = asset_type.lower().strip()

    directory = get_asset_directory(
        asset_type
    )

    filename = safe_filename(
        filename
    )

    path = os.path.join(
        directory,
        filename
    )

    if not os.path.isfile(path):
        raise FileNotFoundError(
            "Asset not found: " +
            filename
        )

    return path


# ------------------------------------------------------------
# DELETE ASSET
# ------------------------------------------------------------

def delete_asset(asset_type, filename):
    """
    Deletes an asset from the platform.
    """

    path = get_asset_path(
        asset_type,
        filename
    )

    os.remove(path)

    return True


# ------------------------------------------------------------
# CHECK ASSET EXISTS
# ------------------------------------------------------------

def asset_exists(asset_type, filename):
    """
    Checks whether an asset exists.
    """

    try:

        path = get_asset_path(
            asset_type,
            filename
        )

        return os.path.isfile(path)

    except FileNotFoundError:

        return False


# ------------------------------------------------------------
# GET ASSET INFORMATION
# ------------------------------------------------------------

def get_asset_info(asset_type, filename):
    """
    Returns useful information about an asset.
    """

    path = get_asset_path(
        asset_type,
        filename
    )

    return {

        "type": asset_type,

        "filename": os.path.basename(path),

        "path": path,

        "extension": get_extension(path),

        "size_bytes": os.path.getsize(path)
    }


# ------------------------------------------------------------
# CLEAR EMPTY DIRECTORIES
# ------------------------------------------------------------

def ensure_structure():
    """
    Makes sure the complete folder structure exists.
    """

    create_directories()

    return {

        "uploads": UPLOADS_DIR,

        "backgrounds": BACKGROUNDS_DIR,

        "logos": LOGOS_DIR,

        "signatures": SIGNATURES_DIR,

        "seals": SEALS_DIR,

        "fonts": FONTS_DIR,

        "templates": TEMPLATES_DIR
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 55)

    print(
        "STEP 8 - TEMPLATE & ASSET MANAGER TEST"
    )

    print("=" * 55)

    # Create complete folder structure

    folders = ensure_structure()

    print("\nFolders created successfully:")

    for name, path in folders.items():

        print(
            name,
            "->",
            path
        )

    print("\nAllowed asset types:")

    for asset_type, extensions in ALLOWED_EXTENSIONS.items():

        print(
            asset_type,
            "->",
            ", ".join(extensions)
        )

    print("\nCurrent assets:")

    assets = list_assets()

    for category, files in assets.items():

        print(
            category,
            "->",
            files
        )

    print("\nTesting filename security:")

    test_name = safe_filename(
        "My Certificate Logo @2026!.png"
    )

    print(
        "Original: My Certificate Logo @2026!.png"
    )

    print(
        "Safe:    ",
        test_name
    )

    print("\nTesting extension validation:")

    try:

        validate_asset(
            "college_logo.png",
            "logo"
        )

        print(
            "Logo validation: PASSED"
        )

    except Exception as e:

        print(
            "Logo validation FAILED:",
            e
        )

    try:

        validate_asset(
            "certificate.ttf",
            "font"
        )

        print(
            "Font validation: PASSED"
        )

    except Exception as e:

        print(
            "Font validation FAILED:",
            e
        )

    print("\nTesting invalid file type:")

    try:

        validate_asset(
            "virus.exe",
            "logo"
        )

        print(
            "ERROR: Invalid file was accepted."
        )

    except ValueError:

        print(
            "Invalid file correctly rejected."
        )

    print("\n" + "=" * 55)

    print(
        "STEP 8 TEST COMPLETED SUCCESSFULLY"
    )

    print("=" * 55)