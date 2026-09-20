# ============================================================
# UNIVERSAL CERTIFICATE PLATFORM
# STEP 12G
# BULK CERTIFICATE GENERATION (CSV -> ZIP)
# ============================================================

import os
import json
import zipfile
import shutil
from datetime import datetime

from flask import (
    Flask,
    request,
    render_template_string,
    send_file
)

from certificate_engine import create_certificate

import template_manager
import design_engine
import csv_manager


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "output"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

TEMP_UPLOAD_DIR = os.path.join(
    BASE_DIR,
    "temp_uploads"
)

os.makedirs(
    TEMP_UPLOAD_DIR,
    exist_ok=True
)

BULK_TEMP_DIR = os.path.join(
    BASE_DIR,
    "bulk_temp"
)

os.makedirs(
    BULK_TEMP_DIR,
    exist_ok=True
)

DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DESIGNS_FILE = os.path.join(DATA_DIR, "saved_designs.json")
HISTORY_FILE = os.path.join(DATA_DIR, "certificate_history.json")

def _load_json_file(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default

def _save_json_file(path, value):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(value, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

def _add_history(record):
    history = _load_json_file(HISTORY_FILE, [])
    history.insert(0, record)
    _save_json_file(HISTORY_FILE, history[:500])

template_manager.create_directories()


# ============================================================
# ASSET UPLOAD HELPER
# ============================================================

def handle_asset_upload(field_name, asset_type):
    """
    Reads an uploaded file from request.form, validates it,
    and saves it into the correct uploads/ folder using
    template_manager. Returns the final saved path, or None
    if no valid file was uploaded.
    """

    uploaded_file = request.files.get(field_name)

    if not uploaded_file or uploaded_file.filename == "":
        return None

    original_filename = uploaded_file.filename

    extension = template_manager.get_extension(
        original_filename
    )

    allowed = template_manager.ALLOWED_EXTENSIONS.get(
        asset_type,
        []
    )

    if extension not in allowed:
        return None

    safe_name = template_manager.safe_filename(
        original_filename
    )

    temp_path = os.path.join(
        TEMP_UPLOAD_DIR,
        safe_name
    )

    uploaded_file.save(temp_path)

    try:

        final_path = template_manager.save_asset(
            temp_path,
            asset_type
        )

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)

    return final_path


# ============================================================
# BULK CSV HELPER
# ============================================================

NAME_COLUMN_ALIASES = [
    "name",
    "student_name",
    "recipient_name",
    "recipient",
    "full_name",
    "participant_name"
]


def find_name_key(record):
    """
    Looks through a normalized CSV record's keys and
    returns the key that most likely holds the
    recipient's name (case-insensitive match).
    """

    for key in record.keys():

        if key == "_row_number":
            continue

        clean_key = key.strip().lower().replace(
            " ",
            "_"
        )

        if clean_key in NAME_COLUMN_ALIASES:
            return key

    return None


# ============================================================
# THEMES AND FONTS NOW COME FROM design_engine.py
# (see design_engine.get_available_themes() /
#  design_engine.get_available_fonts())
# ============================================================


# ============================================================
# DEFAULT HTML
# ============================================================

HTML = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>
Universal Certificate Designer
</title>


<style>

* {
    box-sizing: border-box;
}


body {

    margin: 0;

    padding: 0;

    font-family:
        Arial,
        Helvetica,
        sans-serif;

    background:
        #eef2f7;

    color:
        #222;

}


.header {

    background:
        linear-gradient(
            135deg,
            #102a43,
            #1f4e79
        );

    color:
        white;

    padding:
        22px;

    text-align:
        center;

}


.header h1 {

    margin:
        0;

    font-size:
        28px;

}


.header p {

    margin:
        8px 0 0;

    opacity:
        0.85;

}


.main {

    width:
        96%;

    max-width:
        1400px;

    margin:
        20px auto;

    display:
        grid;

    grid-template-columns:
        380px 1fr;

    gap:
        20px;

}


.panel {

    background:
        white;

    border-radius:
        16px;

    padding:
        20px;

    box-shadow:
        0 8px 30px rgba(
            0,
            0,
            0,
            0.08
        );

}


.panel h2 {

    margin-top:
        0;

    color:
        #163a5f;

}


.section {

    margin-bottom:
        24px;

    padding-bottom:
        18px;

    border-bottom:
        1px solid #e4e7eb;

}


.section:last-child {

    border-bottom:
        none;

}


label {

    display:
        block;

    font-weight:
        bold;

    margin-top:
        12px;

    margin-bottom:
        6px;

}


input,
textarea,
select {

    width:
        100%;

    padding:
        11px;

    border:
        1px solid #cbd2d9;

    border-radius:
        9px;

    font-size:
        15px;

    background:
        white;

}


textarea {

    min-height:
        90px;

    resize:
        vertical;

}


input[type="color"] {

    height:
        45px;

    padding:
        4px;

}


button {

    width:
        100%;

    border:
        none;

    border-radius:
        10px;

    padding:
        13px;

    margin-top:
        10px;

    font-size:
        16px;

    font-weight:
        bold;

    cursor:
        pointer;

}


.primary {

    background:
        #163a5f;

    color:
        white;

}


.secondary {

    background:
        #e8eef5;

    color:
        #163a5f;

}


.preview-area {

    display:
        flex;

    align-items:
        center;

    justify-content:
        center;

    min-height:
        650px;

    background:
        #dfe5ec;

    border-radius:
        14px;

    padding:
        25px;

}


.certificate {

    width:
        100%;

    max-width:
        900px;

    aspect-ratio:
        1.414 / 1;

    position:
        relative;

    background:
        #ffffff;

    border:
        8px solid #c9a227;

    box-shadow:
        0 15px 40px rgba(
            0,
            0,
            0,
            0.18
        );

    padding:
        40px;

    overflow:
        hidden;

}


.certificate::before {

    content:
        "";

    position:
        absolute;

    inset:
        12px;

    border:
        2px solid #c9a227;

    pointer-events:
        none;

}


.cert-content {

    position:
        relative;

    z-index:
        2;

    height:
        100%;

    display:
        flex;

    flex-direction:
        column;

    align-items:
        center;

    text-align:
        center;

}


.org {

    margin-top:
        5px;

    font-size:
        18px;

    font-weight:
        bold;

}


.cert-title {

    margin-top:
        45px;

    font-size:
        32px;

    font-weight:
        bold;

    letter-spacing:
        1px;

}


.subtitle {

    margin-top:
        12px;

    font-size:
        14px;

    color:
        #666;

}


.recipient {

    margin-top:
        20px;

    font-family:
        Georgia,
        serif;

    font-size:
        30px;

    font-weight:
        bold;

}


.recipient-line {

    width:
        55%;

    border-bottom:
        2px solid #c9a227;

    margin-top:
        7px;

}


.description {

    max-width:
        75%;

    margin-top:
        18px;

    font-size:
        14px;

    line-height:
        1.6;

}


.fields {

    margin-top:
        12px;

    display:
        flex;

    flex-wrap:
        wrap;

    justify-content:
        center;

    gap:
        8px 25px;

    max-width:
        80%;

}


.field {

    font-size:
        12px;

}


.footer {

    margin-top:
        auto;

    width:
        100%;

    display:
        flex;

    justify-content:
        space-between;

    font-size:
        10px;

    color:
        #555;

}


.color-row {

    display:
        grid;

    grid-template-columns:
        1fr 1fr;

    gap:
        10px;

}


.custom-row {

    display:
        grid;

    grid-template-columns:
        1fr 1fr;

    gap:
        8px;

    margin-bottom:
        8px;

}


.small-button {

    padding:
        8px;

    font-size:
        13px;

    margin-top:
        4px;

}


@media (
    max-width: 900px
) {

    .main {

        grid-template-columns:
            1fr;

    }

    .preview-area {

        min-height:
            500px;

        padding:
            10px;

    }

    .certificate {

        padding:
            25px;

    }

    .cert-title {

        font-size:
            22px;

        margin-top:
            35px;

    }

    .recipient {

        font-size:
            23px;

    }

    .description {

        max-width:
            85%;

        font-size:
            11px;

    }

}


</style>

</head>


<body>


<div class="header">

    <h1>
        Universal Certificate Designer
    </h1>

    <p>
        Design • Preview • Generate Professional Certificates
    </p>

</div>


<div class="main">


<!-- ======================================================
     DESIGN PANEL
====================================================== -->

<div class="panel">

<h2>
Certificate Designer
</h2>


<!-- BASIC INFORMATION -->

<div class="section">

<h3>
1. Certificate Information
</h3>


<label>
Organization / Institute
</label>

<input
    id="organization"
    type="text"
    value="Your Organization"
    oninput="updatePreview()"
>


<label>
Certificate Type / Title
</label>

<input
    id="title"
    type="text"
    value="CERTIFICATE OF ACHIEVEMENT"
    oninput="updatePreview()"
>


<label>
Subtitle
</label>

<input
    id="subtitle"
    type="text"
    value="This certificate is proudly presented to"
    oninput="updatePreview()"
>


<label>
Recipient Name
</label>

<input
    id="name"
    type="text"
    value="Recipient Name"
    oninput="updatePreview()"
>


<label>
Purpose / Description
</label>

<textarea
    id="description"
    oninput="updatePreview()"
>This certificate is proudly presented in recognition of outstanding achievement, dedication and successful participation.</textarea>


</div>


<!-- DATE / ID -->

<div class="section">

<h3>
2. Date & Certificate ID
</h3>


<label>
Date
</label>

<input
    id="date"
    type="date"
    onchange="updatePreview()"
>


<label>
Time
</label>

<input
    id="time"
    type="time"
    onchange="updatePreview()"
>


<label>
Certificate ID
</label>

<input
    id="certificate_id"
    type="text"
    value="CERT-2026-001"
    oninput="updatePreview()"
>


<button
    class="secondary"
    onclick="generateAutoData()"
>
Generate Date, Time & ID Automatically
</button>


</div>


<!-- CUSTOM FIELDS -->

<div class="section">

<h3>
3. Custom Fields
</h3>

<p style="font-size:13px;color:#666;">
Add any information you want.
</p>


<div id="customFields">


<div class="custom-row">

<input
    class="field-label"
    placeholder="Field name"
    value="Course"
    oninput="updatePreview()"
>

<input
    class="field-value"
    placeholder="Value"
    value="Information Technology"
    oninput="updatePreview()"

>

</div>


<div class="custom-row">

<input
    class="field-label"
    placeholder="Field name"
    value="Roll Number"
    oninput="updatePreview()"
>

<input
    class="field-value"
    placeholder="Value"
    value="15"
    oninput="updatePreview()"
>

</div>


</div>


<button
    class="secondary"
    onclick="addCustomField()"
>
+ Add Custom Field
</button>


</div>


<!-- DESIGN -->

<div class="section">

<h3>
4. Design
</h3>


<label>
Professional Theme
</label>

<select
    id="theme"
    onchange="applyTheme()"
>

<option>
Royal Blue
</option>

<option>
Classic Gold
</option>

<option>
Emerald
</option>

<option>
Burgundy
</option>

<option>
Royal Purple
</option>

<option>
Minimal
</option>

</select>


<div class="color-row">

<div>

<label>
Background
</label>

<input
    id="background"
    type="color"
    value="#ffffff"
    onchange="updatePreview()"
>

</div>


<div>

<label>
Border
</label>

<input
    id="border"
    type="color"
    value="#c9a227"
    onchange="updatePreview()"
>

</div>

</div>


<label>
Title Color
</label>

<input
    id="titleColor"
    type="color"
    value="#163a5f"
    onchange="updatePreview()"
>


<label>
Main Font
</label>

<select
    id="font"
    onchange="updatePreview()"
>

<option>Helvetica</option>
<option>Helvetica-Bold</option>
<option>Helvetica-Oblique</option>
<option>Times-Roman</option>
<option>Times-Bold</option>
<option>Times-Italic</option>
<option>Courier</option>
<option>Courier-Bold</option>
<option>Courier-Oblique</option>

</select>


<label>
Title Font Size
</label>

<input
    id="titleSize"
    type="range"
    min="18"
    max="48"
    value="32"
    oninput="updatePreview()"
>

<div
    id="titleSizeValue"
    style="text-align:center;"
>
32
</div>


</div>


<!-- GENERATE -->

<div class="section">

<h3>
5. Generate
</h3>


<form
    method="POST"
    action="/generate"
    enctype="multipart/form-data"
    onsubmit="prepareForm()"
>


<label>
Background Image (optional)
</label>

<input
    type="file"
    name="background_file"
    accept=".png,.jpg,.jpeg"
    onchange="previewBackground('background_file')"
>


<label>
Logo (optional)
</label>

<input
    type="file"
    name="logo_file"
    accept=".png,.jpg,.jpeg"
    onchange="previewAsset('logo_file','previewLogo')"
>


<label>
Signature (optional)
</label>

<input
    type="file"
    name="signature_file"
    accept=".png,.jpg,.jpeg"
    onchange="previewAsset('signature_file','previewSignature')"
>


<label>
Seal / Emblem (optional)
</label>

<input
    type="file"
    name="seal_file"
    accept=".png,.jpg,.jpeg"
    onchange="previewAsset('seal_file','previewSeal')"
>


<input
    type="hidden"
    name="organization"
    id="form_organization"
>

<input
    type="hidden"
    name="title"
    id="form_title"
>

<input
    type="hidden"
    name="subtitle"
    id="form_subtitle"
>

<input
    type="hidden"
    name="name"
    id="form_name"
>

<input
    type="hidden"
    name="description"
    id="form_description"
>

<input
    type="hidden"
    name="date"
    id="form_date"
>

<input
    type="hidden"
    name="time"
    id="form_time"
>

<input
    type="hidden"
    name="certificate_id"
    id="form_certificate_id"
>

<input
    type="hidden"
    name="background"
    id="form_background"
>

<input
    type="hidden"
    name="border"
    id="form_border"
>

<input
    type="hidden"
    name="titleColor"
    id="form_titleColor"
>

<input
    type="hidden"
    name="font"
    id="form_font"

>

<input
    type="hidden"
    name="titleSize"
    id="form_titleSize"
>


<input
    type="hidden"
    name="custom_fields"
    id="form_custom_fields"
>


<button
    type="submit"
    class="primary"
>
Generate Professional PDF
</button>


</form>


</div>


<!-- BULK GENERATION -->

<div class="section">

<h3>
6. Bulk Generation (CSV)
</h3>

<p style="font-size:13px;color:#666;">
Upload a CSV file. Any column can be included &mdash;
we auto-detect the recipient name column, and every
other column becomes a custom field on each
certificate. Uses the design/theme/colors you set
above. You'll get a ZIP with one PDF per row.
</p>


<form
    method="POST"
    action="/generate_bulk"
    enctype="multipart/form-data"
    onsubmit="prepareBulkForm()"
>


<input type="hidden" name="organization" id="bulk_organization">
<input type="hidden" name="title" id="bulk_title">
<input type="hidden" name="subtitle" id="bulk_subtitle">
<input type="hidden" name="description" id="bulk_description">
<input type="hidden" name="background" id="bulk_background">
<input type="hidden" name="border" id="bulk_border">
<input type="hidden" name="titleColor" id="bulk_titleColor">
<input type="hidden" name="font" id="bulk_font">
<input type="hidden" name="titleSize" id="bulk_titleSize">

<label>Background Image (optional)</label>
<input type="file" name="bulk_background_file" accept=".png,.jpg,.jpeg">
<label>Logo (optional)</label>
<input type="file" name="bulk_logo_file" accept=".png,.jpg,.jpeg">
<label>Signature (optional)</label>
<input type="file" name="bulk_signature_file" accept=".png,.jpg,.jpeg">
<label>Seal / Emblem (optional)</label>
<input type="file" name="bulk_seal_file" accept=".png,.jpg,.jpeg">

<label>
CSV File
</label>

<input
    type="file"
    name="csv_file"
    accept=".csv"
    required
>


<button
    type="submit"
    class="secondary"
>
Generate Bulk Certificates (ZIP)
</button>


</form>


</div>


</div>


<!-- ======================================================
     LIVE PREVIEW
====================================================== -->

<div class="panel">

<h2>
Live Certificate Preview
</h2>


<div class="preview-area">


<div
    class="certificate"
    id="certificate"
>


<div
    class="cert-content"
>


<img
    id="previewLogo"
    style="max-height:55px;max-width:55px;display:none;margin-bottom:6px;"
>

<div
    class="org"
    id="previewOrganization"
>
Your Organization
</div>


<div
    class="cert-title"
    id="previewTitle"
>
CERTIFICATE OF ACHIEVEMENT
</div>


<div
    class="subtitle"
    id="previewSubtitle"
>
This certificate is proudly presented to
</div>


<div
    class="recipient"
    id="previewName"
>
Recipient Name
</div>


<div class="recipient-line"></div>


<div
    class="description"
    id="previewDescription"
>
This certificate is proudly presented in recognition of outstanding achievement, dedication and successful participation.
</div>


<div
    class="fields"
    id="previewFields"
>
</div>


<div class="footer">


<div style="text-align:center;">
<img
    id="previewSignature"
    style="max-height:40px;display:none;"
><br>
<div id="previewDate">
Date
</div>
</div>


<div style="text-align:center;">
<img
    id="previewSeal"
    style="max-height:60px;display:none;"
><br>
<div id="previewID">
Certificate ID
</div>
</div>


</div>


</div>


</div>


</div>


</div>


</div>


<script>


// ==========================================================
// GET ELEMENT
// ==========================================================

function get(id) {

    return document.getElementById(id);

}


// ==========================================================
// UPDATE PREVIEW
// ==========================================================

function updatePreview() {

    get("previewOrganization").innerText =
        get("organization").value
        || "Your Organization";


    get("previewTitle").innerText =
        get("title").value
        || "CERTIFICATE";


    get("previewSubtitle").innerText =
        get("subtitle").value
        || "";


    get("previewName").innerText =
        get("name").value
        || "Recipient Name";


    get("previewDescription").innerText =
        get("description").value
        || "";


    get("certificate").style.background =
        get("background").value;


    get("certificate").style.borderColor =
        get("border").value;


    get("certificate").style.color =
        "#333333";


    get("previewTitle").style.color =
        get("titleColor").value;


    get("previewOrganization").style.color =
        get("titleColor").value;


    get("previewTitle").style.fontFamily =
        get("font").value
        .replace("-Bold", "")
        .replace("-Oblique", "");


    let titleSize =
        get("titleSize").value;


    get("previewTitle").style.fontSize =
        titleSize + "px";


    get("titleSizeValue").innerText =
        titleSize;


    let date =
        get("date").value;


    let time =
        get("time").value;


    if (date) {

        get("previewDate").innerText =
            "Date: " + date;

    } else {

        get("previewDate").innerText =
            "Date";

    }


    if (time) {

        get("previewDate").innerText +=
            " | " + time;

    }


    get("previewID").innerText =
        get("certificate_id").value
        ? "ID: " +
          get("certificate_id").value
        : "Certificate ID";


    updateFields();

}


// ==========================================================
// CUSTOM FIELDS
// ==========================================================

function updateFields() {

    let labels =
        document.querySelectorAll(
            ".field-label"
        );


    let values =
        document.querySelectorAll(
            ".field-value"
        );


    let output = "";


    for (
        let i = 0;
        i < labels.length;
        i++
    ) {

        let label =
            labels[i].value.trim();


        let value =
            values[i].value.trim();


        if (
            label &&
            value
        ) {

            output +=
                '<div class="field">' +
                "<b>" +
                escapeHtml(label) +
                ":</b> " +
                escapeHtml(value) +
                "</div>";

        }

    }


    get("previewFields").innerHTML =
        output;

}


// ==========================================================
// HTML ESCAPE
// ==========================================================

function escapeHtml(text) {

    let div =
        document.createElement("div");

    div.innerText =
        text;

    return div.innerHTML;

}


// ==========================================================
// ADD FIELD
// ==========================================================

function addCustomField() {

    let container =
        get("customFields");


    let row =
        document.createElement("div");


    row.className =
        "custom-row";


    row.innerHTML =

        '<input ' +
        'class="field-label" ' +
        'placeholder="Field name" ' +
        'oninput="updatePreview()">' +

        '<input ' +
        'class="field-value" ' +
        'placeholder="Value" ' +
        'oninput="updatePreview()">';


    container.appendChild(row);


    updatePreview();

}


// ==========================================================
// BACKGROUND IMAGE PREVIEW
// ==========================================================

function previewBackground(inputId) {

    let input = get(inputId);
    let cert = get("certificate");

    if (input.files && input.files[0]) {

        let reader = new FileReader();

        reader.onload = function(e) {
            cert.style.backgroundImage =
                "url('" + e.target.result + "')";
            cert.style.backgroundSize = "cover";
            cert.style.backgroundPosition = "center";
        };

        reader.readAsDataURL(input.files[0]);

    } else {

        cert.style.backgroundImage = "none";

    }

}


// ==========================================================
// ASSET PREVIEW (LOGO / SIGNATURE / SEAL)
// ==========================================================

function previewAsset(inputId, imgId) {

    let input = get(inputId);
    let img = get(imgId);

    if (input.files && input.files[0]) {

        let reader = new FileReader();

        reader.onload = function(e) {
            img.src = e.target.result;
            img.style.display = "inline-block";
        };

        reader.readAsDataURL(input.files[0]);

    } else {

        img.style.display = "none";
        img.src = "";

    }

}


// ==========================================================
// AUTO DATE / TIME / ID
// ==========================================================

function generateAutoData() {

    let now =
        new Date();


    let year =
        now.getFullYear();


    let month =
        String(
            now.getMonth() + 1
        ).padStart(2, "0");


    let day =
        String(
            now.getDate()
        ).padStart(2, "0");


    let hours =
        String(
            now.getHours()
        ).padStart(2, "0");


    let minutes =
        String(
            now.getMinutes()
        ).padStart(2, "0");


    let seconds =
        String(
            now.getSeconds()
        ).padStart(2, "0");


    get("date").value =
        year +
        "-" +
        month +
        "-" +
        day;


    get("time").value =
        hours +
        ":" +
        minutes;


    get("certificate_id").value =

        "CERT-" +
        year +
        "-" +
        month +
        day +
        "-" +
        hours +
        minutes +
        seconds;


    updatePreview();

}


// ==========================================================
// THEME (loaded from design_engine.py via the server)
// ==========================================================

const themes = {{ themes_json|safe }};


function applyTheme() {

    let name =
        get("theme").value;


    let theme =
        themes[name];


    if (!theme) {
        return;
    }


    get("background").value =
        theme.background;


    get("border").value =
        theme.border;


    get("titleColor").value =
        theme.title;


    updatePreview();

}


// ==========================================================
// PREPARE FORM
// ==========================================================

function prepareBulkForm() {

    get("bulk_organization").value =
        get("organization").value;

    get("bulk_title").value =
        get("title").value;

    get("bulk_subtitle").value =
        get("subtitle").value;

    get("bulk_description").value =
        get("description").value;

    get("bulk_background").value =
        get("background").value;

    get("bulk_border").value =
        get("border").value;

    get("bulk_titleColor").value =
        get("titleColor").value;

    get("bulk_font").value =
        get("font").value;

    get("bulk_titleSize").value =
        get("titleSize").value;

}


function prepareForm() {

    get("form_organization").value =
        get("organization").value;


    get("form_title").value =
        get("title").value;


    get("form_subtitle").value =
        get("subtitle").value;


    get("form_name").value =
        get("name").value;


    get("form_description").value =
        get("description").value;


    get("form_date").value =
        get("date").value;


    get("form_time").value =
        get("time").value;


    get("form_certificate_id").value =
        get("certificate_id").value;


    get("form_background").value =
        get("background").value;


    get("form_border").value =
        get("border").value;


    get("form_titleColor").value =
        get("titleColor").value;


    get("form_font").value =
        get("font").value;


    get("form_titleSize").value =
        get("titleSize").value;


    let labels =
        document.querySelectorAll(
            ".field-label"
        );


    let values =
        document.querySelectorAll(
            ".field-value"
        );


    let fields = [];


    for (
        let i = 0;
        i < labels.length;
        i++
    ) {

        let label =
            labels[i].value.trim();


        let value =
            values[i].value.trim();


        if (
            label &&
            value
        ) {

            fields.push({

                label: label,

                value: value

            });

        }

    }


    get("form_custom_fields").value =
        JSON.stringify(fields);

}


// ==========================================================
// INITIALIZE
// ==========================================================

window.onload = function() {

    generateAutoData();

    updatePreview();

};


</script>

<div class="section" style="margin-top:24px;">
<h3>7. Platform Tools</h3>
<p style="font-size:13px;color:#666;">Save reusable designs, view certificate history, and verify Certificate IDs.</p>
<div style="display:flex;gap:8px;flex-wrap:wrap;">
<input id="designName" placeholder="Design name" style="flex:1;min-width:220px;">
<button type="button" class="primary" onclick="saveCurrentDesign()">Save Design</button>
<button type="button" class="secondary" onclick="loadDesignList()">Load Design</button>
<button type="button" class="secondary" onclick="window.open('/history','_blank')">Certificate History</button>
<button type="button" class="secondary" onclick="window.open('/verify','_blank')">Verify Certificate</button>
</div><div id="savedDesigns" style="margin-top:12px;"></div>
</div>
<script>
function currentDesignPayload(){return {organization:(document.getElementById('organization')||{}).value||'',title:(document.getElementById('title')||{}).value||'',subtitle:(document.getElementById('subtitle')||{}).value||'',name:(document.getElementById('name')||{}).value||'',description:(document.getElementById('description')||{}).value||'',date:(document.getElementById('date')||{}).value||'',time:(document.getElementById('time')||{}).value||'',certificate_id:(document.getElementById('certificate_id')||{}).value||'',background:(document.getElementById('background')||{}).value||'#FFFFFF',border:(document.getElementById('border')||{}).value||'#C9A227',titleColor:(document.getElementById('titleColor')||{}).value||'#163A5F',font:(document.getElementById('font')||{}).value||'Helvetica-Bold',titleSize:(document.getElementById('titleSize')||{}).value||'32',custom_fields:(document.getElementById('form_custom_fields')||{}).value||'[]'};}
async function saveCurrentDesign(){const name=(document.getElementById('designName').value||'').trim();if(!name){alert('Enter a design name.');return;}const r=await fetch('/save_design',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name,design:currentDesignPayload()})});const d=await r.json();alert(d.message||d.error||'Saved');loadDesignList();}
async function loadDesignList(){const r=await fetch('/designs');const d=await r.json();const b=document.getElementById('savedDesigns');if(!d.designs.length){b.innerHTML='<span style="color:#777">No saved designs.</span>';return;}b.innerHTML=d.designs.map(x=>'<div style="margin:6px 0;padding:8px;border:1px solid #ddd;border-radius:8px;"><b>'+x.name+'</b> <button type="button" onclick="useSavedDesign('+JSON.stringify(x.name)+')">LOAD</button> <button type="button" onclick="deleteSavedDesign('+JSON.stringify(x.name)+')">DELETE</button></div>').join('');}
async function useSavedDesign(name){const r=await fetch('/designs/'+encodeURIComponent(name));const d=await r.json();if(d.error){alert(d.error);return;}const x=d.design;const keys=['organization','title','subtitle','name','description','date','time','certificate_id','background','border','titleColor','font','titleSize'];keys.forEach(k=>{const e=document.getElementById(k);if(e&&x[k]!==undefined)e.value=x[k];});if(document.getElementById('form_custom_fields'))document.getElementById('form_custom_fields').value=x.custom_fields||'[]';if(typeof updatePreview==='function')updatePreview();alert('Design loaded: '+name);}
async function deleteSavedDesign(name){if(!confirm('Delete '+name+'?'))return;const r=await fetch('/designs/'+encodeURIComponent(name),{method:'DELETE'});const d=await r.json();alert(d.message||d.error||'Deleted');loadDesignList();}
</script>

</body>

</html>
"""


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    themes_json = json.dumps(
        design_engine.get_available_themes()
    )

    return render_template_string(
        HTML,
        themes_json=themes_json
    )


# ============================================================
# GENERATE PDF
# ============================================================

# ============================================================
# BUILD DESIGN DICT (shared by single + bulk generation)
# ============================================================

def build_design(
    organization,
    title,
    background,
    border,
    title_color,
    font,
    title_size,
    background_path,
    logo_path,
    signature_path,
    seal_path
):

    return {

        "page": {
            "size": "A4",
            "orientation": "landscape"
        },

        "colors": {

            "background": background,

            "border": border,

            "title": title_color

        },

        "background": {

            "enabled": True,

            "color": background,

            "image_enabled": bool(background_path),

            "path": background_path or ""

        },

        "border": {

            "enabled": True,

            "color": border,

            "width": 3,

            "margin": 18

        },

        "decoration": {

            "enabled": True,

            "color": border

        },

        "branding": {

            "organization": organization,

            "font": "Helvetica-Bold",

            "font_size": 16,

            "color": title_color

        },

        "title": {

            "font": font,

            "font_size": title_size,

            "color": title_color

        },

        "subtitle": {

            "font": "Helvetica",

            "font_size": 12,

            "color": "#555555"

        },

        "recipient": {

            "font": "Times-BoldItalic",

            "font_size": 27,

            "color": "#111111",

            "underline_color": border

        },

        "body": {

            "font": "Helvetica",

            "font_size": 11,

            "color": "#333333"

        },

        "fields": {

            "font": "Helvetica",

            "label_size": 9,

            "value_size": 10,

            "label_color": title_color,

            "value_color": "#111111"

        },

        "metadata": {

            "font": "Helvetica",

            "font_size": 9,

            "color": "#555555"

        },

        "logo": {

            "enabled": bool(logo_path),

            "path": logo_path or ""

        },

        "signature": {

            "enabled": bool(signature_path),

            "path": signature_path or ""

        },

        "seal": {

            "enabled": bool(seal_path),

            "path": seal_path or ""

        }

    }


@app.route(
    "/generate",
    methods=["POST"]
)
def generate():

    organization = request.form.get(
        "organization",
        ""
    ).strip()


    title = request.form.get(
        "title",
        "CERTIFICATE OF ACHIEVEMENT"
    ).strip()


    subtitle = request.form.get(
        "subtitle",
        "This certificate is proudly presented to"
    ).strip()


    name = request.form.get(
        "name",
        "Recipient Name"
    ).strip()


    description = request.form.get(
        "description",
        ""
    ).strip()


    date = request.form.get(
        "date",
        ""
    ).strip()


    time = request.form.get(
        "time",
        ""
    ).strip()


    certificate_id = request.form.get(
        "certificate_id",
        ""
    ).strip()


    background = request.form.get(
        "background",
        "#FFFFFF"
    ).strip()


    border = request.form.get(
        "border",
        "#C9A227"
    ).strip()


    title_color = request.form.get(
        "titleColor",
        "#163A5F"
    ).strip()


    font = request.form.get(
        "font",
        "Helvetica-Bold"
    ).strip()


    try:

        title_size = int(
            request.form.get(
                "titleSize",
                "32"
            )
        )

    except Exception:

        title_size = 32


    # --------------------------------------------------------
    # CUSTOM FIELDS
    # --------------------------------------------------------

    fields = {}

    raw_fields = request.form.get(
        "custom_fields",
        "[]"
    )


    try:

        custom_fields = json.loads(
            raw_fields
        )


        if isinstance(
            custom_fields,
            list
        ):

            for item in custom_fields:

                label = str(
                    item.get(
                        "label",
                        ""
                    )
                ).strip()


                value = str(
                    item.get(
                        "value",
                        ""
                    )
                ).strip()


                if label and value:

                    fields[label] = value

    except Exception:

        fields = {}


    # --------------------------------------------------------
    # ASSET UPLOADS (LOGO / SIGNATURE / SEAL)
    # --------------------------------------------------------

    background_path = handle_asset_upload(
        "background_file",
        "background"
    )

    logo_path = handle_asset_upload(
        "logo_file",
        "logo"
    )

    signature_path = handle_asset_upload(
        "signature_file",
        "signature"
    )

    seal_path = handle_asset_upload(
        "seal_file",
        "seal"
    )


    # --------------------------------------------------------
    # AUTO ID FALLBACK
    # --------------------------------------------------------

    if not certificate_id:

        certificate_id = (

            "CERT-" +

            datetime.now().strftime(
                "%Y%m%d-%H%M%S%f"
            )

        )


    # --------------------------------------------------------
    # DATE FALLBACK
    # --------------------------------------------------------

    if not date:

        date = datetime.now().strftime(
            "%d-%m-%Y"
        )


    # --------------------------------------------------------
    # OUTPUT NAME
    # --------------------------------------------------------

    safe_name = "".join(

        ch if ch.isalnum()
        else "_"

        for ch in name

    ).strip("_")


    if not safe_name:

        safe_name = "certificate"


    filename = (

        safe_name +
        "_" +
        certificate_id +
        ".pdf"

    )


    output_path = os.path.join(
        OUTPUT_DIR,
        filename
    )


    # --------------------------------------------------------
    # DESIGN
    # --------------------------------------------------------

    design = build_design(
        organization,
        title,
        background,
        border,
        title_color,
        font,
        title_size,
        background_path,
        logo_path,
        signature_path,
        seal_path
    )


    # --------------------------------------------------------
    # CERTIFICATE DATA
    # --------------------------------------------------------

    data = {

        "certificate_type": title,

        "title": title,

        "subtitle": subtitle,

        "name": name,

        "recipient": name,

        "organization": organization,

        "description": description,

        "date": date,

        "time": time,

        "certificate_id":
            certificate_id,

        "fields": fields

    }


    # --------------------------------------------------------
    # CREATE PDF
    # --------------------------------------------------------

    try:

        create_certificate(

            data,

            design,

            output_path

        )

    except Exception as error:

        return (

            "<h2>Certificate generation failed</h2>"

            "<pre>" +

            str(error) +

            "</pre>"

        ), 500


    # --------------------------------------------------------
    # SAVE CERTIFICATE HISTORY
    # --------------------------------------------------------
    _add_history({
        "certificate_id": certificate_id,
        "recipient": name,
        "title": title,
        "organization": organization,
        "date": date,
        "filename": filename,
        "created_at": datetime.now().isoformat(timespec="seconds")
    })

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    return send_file(

        output_path,

        as_attachment=True,

        download_name=filename,

        mimetype="application/pdf"

    )


@app.route(
    "/generate_bulk",
    methods=["POST"]
)
def generate_bulk():

    organization = request.form.get(
        "organization", ""
    ).strip()

    title = request.form.get(
        "title", "CERTIFICATE OF ACHIEVEMENT"
    ).strip()

    subtitle = request.form.get(
        "subtitle", ""
    ).strip()

    description = request.form.get(
        "description", ""
    ).strip()

    background = request.form.get(
        "background", "#FFFFFF"
    ).strip()

    border = request.form.get(
        "border", "#C9A227"
    ).strip()

    title_color = request.form.get(
        "titleColor", "#163A5F"
    ).strip()

    font = request.form.get(
        "font", "Helvetica-Bold"
    ).strip()

    try:
        title_size = int(
            request.form.get("titleSize", "32")
        )
    except Exception:
        title_size = 32


    # --------------------------------------------------------
    # READ THE UPLOADED CSV
    # --------------------------------------------------------

    csv_file = request.files.get("csv_file")

    if not csv_file or csv_file.filename == "":
        return (
            "<h2>Bulk generation failed</h2>"
            "<pre>No CSV file was uploaded.</pre>"
        ), 400

    if not csv_file.filename.lower().endswith(".csv"):
        return (
            "<h2>Bulk generation failed</h2>"
            "<pre>Only .csv files are supported.</pre>"
        ), 400

    safe_csv_name = template_manager.safe_filename(
        csv_file.filename
    )

    temp_csv_path = os.path.join(
        TEMP_UPLOAD_DIR,
        safe_csv_name
    )

    csv_file.save(temp_csv_path)

    try:

        records = csv_manager.load_records(
            temp_csv_path
        )

    except Exception as error:

        if os.path.exists(temp_csv_path):
            os.remove(temp_csv_path)

        return (
            "<h2>Bulk generation failed</h2>"
            "<pre>" + str(error) + "</pre>"
        ), 400

    if os.path.exists(temp_csv_path):
        os.remove(temp_csv_path)

    if not records:
        return (
            "<h2>Bulk generation failed</h2>"
            "<pre>The CSV file has no data rows.</pre>"
        ), 400


    # --------------------------------------------------------
    # OPTIONAL BULK DESIGN ASSETS
    # --------------------------------------------------------
    background_path = handle_asset_upload("bulk_background_file", "background")
    logo_path = handle_asset_upload("bulk_logo_file", "logo")
    signature_path = handle_asset_upload("bulk_signature_file", "signature")
    seal_path = handle_asset_upload("bulk_seal_file", "seal")

    # --------------------------------------------------------
    # BUILD THE SHARED DESIGN (same for every certificate)
    # --------------------------------------------------------
    design = build_design(
        organization, title, background, border, title_color, font,
        title_size, background_path, logo_path, signature_path, seal_path
    )


    # --------------------------------------------------------
    # GENERATE ONE CERTIFICATE PER ROW
    # --------------------------------------------------------

    batch_id = datetime.now().strftime(
        "%Y%m%d-%H%M%S"
    )

    batch_dir = os.path.join(
        BULK_TEMP_DIR,
        "batch_" + batch_id
    )

    os.makedirs(
        batch_dir,
        exist_ok=True
    )

    today = datetime.now().strftime(
        "%d-%m-%Y"
    )

    generated_files = []

    errors = []

    for index, record in enumerate(records, start=1):

        row_number = record.get(
            "_row_number",
            index + 1
        )

        name_key = find_name_key(record)

        name_value = (
            record.get(name_key, "").strip()
            if name_key
            else ""
        )

        if not name_value:

            errors.append(
                "Row " + str(row_number) +
                ": no recipient name found "
                "(add a 'Name' column)."
            )

            continue


        # ----------------------------------------------------
        # REMAINING CSV COLUMNS BECOME CUSTOM FIELDS
        # ----------------------------------------------------

        fields = {}

        for key, value in record.items():

            if key == "_row_number":
                continue

            if key == name_key:
                continue

            value = str(value).strip()

            if value:
                fields[key] = value


        certificate_id = (
            "CERT-" + batch_id + "-" +
            str(index).zfill(3)
        )

        data = {

            "certificate_type": title,

            "title": title,

            "subtitle": subtitle,

            "name": name_value,

            "recipient": name_value,

            "organization": organization,

            "description": description,

            "date": today,

            "time": "",

            "certificate_id": certificate_id,

            "fields": fields

        }

        safe_name = "".join(
            ch if ch.isalnum() else "_"
            for ch in name_value
        ).strip("_") or "certificate"

        pdf_filename = (
            safe_name + "_" + certificate_id + ".pdf"
        )

        pdf_path = os.path.join(
            batch_dir,
            pdf_filename
        )

        try:

            create_certificate(
                data,
                design,
                pdf_path
            )

            _add_history({
                "certificate_id": certificate_id,
                "recipient": name_value,
                "title": title,
                "organization": organization,
                "date": today,
                "filename": pdf_filename,
                "created_at": datetime.now().isoformat(timespec="seconds")
            })

            generated_files.append(pdf_path)

        except Exception as error:

            errors.append(
                "Row " + str(row_number) +
                ": " + str(error)
            )


    if not generated_files:

        shutil.rmtree(
            batch_dir,
            ignore_errors=True
        )

        return (
            "<h2>Bulk generation failed</h2>"
            "<pre>No certificates could be generated.\n\n"
            + "\n".join(errors) +
            "</pre>"
        ), 400


    # --------------------------------------------------------
    # ZIP THE RESULTS
    # --------------------------------------------------------

    zip_filename = (
        "bulk_certificates_" + batch_id + ".zip"
    )

    zip_path = os.path.join(
        OUTPUT_DIR,
        zip_filename
    )

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zip_file:

        for pdf_path in generated_files:

            zip_file.write(
                pdf_path,
                arcname=os.path.basename(pdf_path)
            )

        if errors:

            zip_file.writestr(
                "errors.txt",
                "\n".join(errors)
            )


    shutil.rmtree(
        batch_dir,
        ignore_errors=True
    )


    return send_file(
        zip_path,
        as_attachment=True,
        download_name=zip_filename,
        mimetype="application/zip"
    )


# ============================================================
# SAVED DESIGNS / HISTORY / VERIFICATION
# ============================================================

@app.route("/save_design", methods=["POST"])
def save_design():
    payload = request.get_json(silent=True) or {}
    name = str(payload.get("name", "")).strip()
    design = payload.get("design", {})
    if not name or not isinstance(design, dict):
        return {"error": "Design name and design data are required."}, 400
    designs = _load_json_file(DESIGNS_FILE, {})
    designs[name] = {"name": name, "design": design, "saved_at": datetime.now().isoformat(timespec="seconds")}
    _save_json_file(DESIGNS_FILE, designs)
    return {"message": "Design saved successfully."}

@app.route("/designs")
def designs():
    designs = _load_json_file(DESIGNS_FILE, {})
    return {"designs": [{"name": k, **({"saved_at": v.get("saved_at", "")} if isinstance(v, dict) else {})} for k,v in designs.items()]}

@app.route("/designs/<path:name>", methods=["GET", "DELETE"])
def design_item(name):
    designs = _load_json_file(DESIGNS_FILE, {})
    if request.method == "DELETE":
        if name not in designs: return {"error": "Design not found."}, 404
        del designs[name]; _save_json_file(DESIGNS_FILE, designs); return {"message": "Design deleted."}
    if name not in designs: return {"error": "Design not found."}, 404
    return designs[name]

@app.route("/history")
def history_page():
    history = _load_json_file(HISTORY_FILE, [])
    rows = "".join(f"<tr><td>{r.get('certificate_id','')}</td><td>{r.get('recipient','')}</td><td>{r.get('title','')}</td><td>{r.get('date','')}</td></tr>" for r in history)
    return f"""<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Certificate History</title><style>body{{font-family:Arial;padding:20px;background:#f5f7fa}}table{{width:100%;border-collapse:collapse;background:white}}th,td{{padding:10px;border:1px solid #ddd;text-align:left}}th{{background:#173B63;color:white}}</style></head><body><h2>Certificate History</h2><p>Total records: {len(history)}</p><table><tr><th>Certificate ID</th><th>Recipient</th><th>Certificate</th><th>Date</th></tr>{rows}</table></body></html>"""

@app.route("/verify", methods=["GET", "POST"])
def verify_certificate():
    result = ""
    if request.method == "POST":
        cid = request.form.get("certificate_id", "").strip()
        history = _load_json_file(HISTORY_FILE, [])
        found = next((r for r in history if r.get("certificate_id") == cid), None)
        if found:
            result = f"<div style='padding:15px;background:#e9f7ef;border-radius:8px'><b>Certificate Found</b><br>Recipient: {found.get('recipient','')}<br>Certificate: {found.get('title','')}<br>Organization: {found.get('organization','')}<br>Date: {found.get('date','')}<br>ID: {cid}</div>"
        else:
            result = "<div style='padding:15px;background:#fdecec;border-radius:8px'><b>Certificate ID not found.</b></div>"
    return f"""<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Verify Certificate</title></head><body style='font-family:Arial;max-width:600px;margin:40px auto;padding:20px'><h2>Certificate Verification</h2><form method='post'><input name='certificate_id' placeholder='Enter Certificate ID' required style='width:100%;padding:12px;box-sizing:border-box'><button style='margin-top:10px;padding:12px 20px'>Verify</button></form><div style='margin-top:20px'>{result}</div></body></html>"""

# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("        ACG - AUTOMATIC CERTIFICATE GENERATOR")
    print("=" * 60)
    print()
    print("  Your certificate platform is running successfully!")
    print()
    print("  🌐 OPEN ACG WEBSITE:")
    print("  http://100.70.249.67:5000/")
    print()
    print("  👉 Click the link above to open ACG")
    print()
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )