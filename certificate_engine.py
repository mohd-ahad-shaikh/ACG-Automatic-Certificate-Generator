"""
Universal Certificate Platform
Professional ReportLab certificate renderer.
Compatible with the existing app.py create_certificate(data, design, output_path).
"""

import os
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.colors import HexColor, white
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader


def color(value, fallback="#111827"):
    try:
        if isinstance(value, str) and value.strip():
            return HexColor(value.strip())
    except Exception:
        pass
    return HexColor(fallback)


def page_size(design):
    page = design.get("page", {}) or {}
    base = A4 if str(page.get("size", "A4")).upper() == "A4" else A4
    if str(page.get("orientation", "landscape")).lower() == "portrait":
        return portrait(base)
    return landscape(base)


def font_name(settings, default="Helvetica"):
    value = settings.get("font", default) if isinstance(settings, dict) else default
    return value if value else default


def font_size(settings, default=12):
    if not isinstance(settings, dict):
        return default
    for key in ("font_size", "size", "value_size"):
        try:
            return max(5, float(settings.get(key, default)))
        except Exception:
            pass
    return default


def draw_center(pdf, text, x, y, font, size, fill):
    pdf.setFont(font, size)
    pdf.setFillColor(color(fill))
    pdf.drawCentredString(x, y, str(text))


def wrap_lines(text, font, size, max_width):
    text = str(text or "").strip()
    if not text:
        return []
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = word if not current else current + " " + word
        if stringWidth(candidate, font, size) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped_center(pdf, text, x, y, max_width, font, size, fill, leading=None, max_lines=4):
    leading = leading or size * 1.35
    lines = wrap_lines(text, font, size, max_width)[:max_lines]
    pdf.setFont(font, size)
    pdf.setFillColor(color(fill))
    for i, line in enumerate(lines):
        pdf.drawCentredString(x, y - i * leading, line)
    return y - len(lines) * leading


def draw_image(pdf, path, x, y, width, height, preserve=True):
    if not path or not os.path.exists(path):
        return False
    try:
        pdf.drawImage(path, x, y, width=width, height=height,
                      preserveAspectRatio=preserve, anchor='c', mask="auto")
        return True
    except Exception:
        return False


def draw_background(pdf, w, h, design):
    bg = design.get("background", {}) or {}
    colors = design.get("colors", {}) or {}
    path = bg.get("path", "") if bg.get("image_enabled", False) or bg.get("enabled", False) else ""
    if path and os.path.exists(path):
        if draw_image(pdf, path, 0, 0, w, h, preserve=False):
            return
    pdf.setFillColor(color(bg.get("color", colors.get("background", "#FFFFFF")), "#FFFFFF"))
    pdf.rect(0, 0, w, h, fill=1, stroke=0)


def draw_premium_background(pdf, w, h, design):
    colors = design.get("colors", {}) or {}
    primary = color(colors.get("title", colors.get("primary", "#173B63")), "#173B63")
    secondary = color(colors.get("border", colors.get("secondary", "#C9A227")), "#C9A227")

    # Very light decorative panels; kept subtle so text remains readable.
    pdf.saveState()
    pdf.setFillColor(primary)
    pdf.setFillAlpha(0.035)
    pdf.circle(w * 0.08, h * 0.88, 110, fill=1, stroke=0)
    pdf.circle(w * 0.92, h * 0.12, 135, fill=1, stroke=0)
    pdf.restoreState()

    # Elegant top/bottom accent rules.
    pdf.setStrokeColor(secondary)
    pdf.setLineWidth(1.4)
    pdf.line(w * 0.23, h - 96, w * 0.77, h - 96)
    pdf.line(w * 0.23, 86, w * 0.77, 86)


def draw_border(pdf, w, h, design):
    border = design.get("border", {}) or {}
    colors = design.get("colors", {}) or {}
    if not border.get("enabled", True):
        return
    c = color(border.get("color", colors.get("border", "#C9A227")), "#C9A227")
    try:
        margin = float(border.get("margin", border.get("padding", 18)))
    except Exception:
        margin = 18
    try:
        width = float(border.get("width", 2.2))
    except Exception:
        width = 2.2
    margin = max(8, min(margin, 35))

    pdf.setStrokeColor(c)
    pdf.setLineWidth(width)
    pdf.roundRect(margin, margin, w - 2 * margin, h - 2 * margin, 7, fill=0, stroke=1)
    pdf.setLineWidth(max(0.6, width * 0.38))
    inner = margin + 7
    pdf.roundRect(inner, inner, w - 2 * inner, h - 2 * inner, 5, fill=0, stroke=1)

    # Small corner ornaments.
    pdf.setLineWidth(2)
    length = 24
    for x, y, sx, sy in [
        (margin + 2, h - margin - 2, 1, -1),
        (w - margin - 2, h - margin - 2, -1, -1),
        (margin + 2, margin + 2, 1, 1),
        (w - margin - 2, margin + 2, -1, 1),
    ]:
        pdf.line(x, y, x + sx * length, y)
        pdf.line(x, y, x, y + sy * length)


def draw_logo(pdf, design, w, h):
    logo = design.get("logo", {}) or {}
    if not logo.get("enabled", False):
        return
    path = logo.get("path", "")
    width = float(logo.get("width", 58) or 58)
    height = float(logo.get("height", 58) or 58)
    x = float(logo.get("x", 42) or 42)
    y = float(logo.get("y", h - 95) or h - 95)
    draw_image(pdf, path, x, y, width, height, True)


def draw_seal(pdf, design, w, h):
    seal = design.get("seal", {}) or {}
    if not seal.get("enabled", False):
        return
    path = seal.get("path", "")
    width = float(seal.get("width", 64) or 64)
    height = float(seal.get("height", 64) or 64)
    x = float(seal.get("x", w / 2 - width / 2) or (w / 2 - width / 2))
    y = float(seal.get("y", 42) or 42)
    draw_image(pdf, path, x, y, width, height, True)


def draw_signature(pdf, design, w, h):
    """Draw a proper certificate signature block.

    The signature line is shown even when no image has been uploaded, so the
    generated certificate still has the conventional official-signature area.
    If an uploaded signature image exists, it is placed above the line.
    """
    sig = design.get("signature", {}) or {}
    width = float(sig.get("width", 135) or 135)
    height = float(sig.get("height", 42) or 42)
    x = float(sig.get("x", w - 185) or (w - 185))
    y = float(sig.get("y", 66) or 66)
    path = sig.get("path", "")

    # Uploaded signature image, when available.
    if path and os.path.exists(path):
        draw_image(pdf, path, x, y + 4, width, height, True)

    # Official signature line.
    line_color = sig.get("line_color", design.get("colors", {}).get("border", "#C9A227"))
    pdf.setStrokeColor(color(line_color))
    pdf.setLineWidth(1.0)
    pdf.line(x, y, x + width, y)

    label = str(sig.get("label", "Authorized Signature")).strip() or "Authorized Signature"
    signer = str(sig.get("signer_name", "")).strip()
    designation = str(sig.get("designation", "")).strip()

    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.setFillColor(color(sig.get("text_color", "#333333")))
    pdf.drawCentredString(x + width / 2, y - 14, label)

    if signer:
        pdf.setFont("Helvetica", 8)
        pdf.drawCentredString(x + width / 2, y - 26, signer)
        if designation:
            pdf.setFont("Helvetica", 7.2)
            pdf.setFillColor(color("#666666"))
            pdf.drawCentredString(x + width / 2, y - 37, designation)


def normalize_fields(fields):
    if not isinstance(fields, dict):
        return []
    result = []
    for label, value in fields.items():
        if value is None or str(value).strip() == "":
            continue
        result.append((str(label).strip(), str(value).strip()))
    return result


def draw_fields(pdf, fields, design, w, y):
    """
    Draw dynamic certificate fields in a clean, responsive two-column layout.

    Each field is rendered as:
        LABEL
        Value

    Long values are wrapped inside their own column so that one field
    can never overlap another field.
    """
    settings = design.get("fields", {}) or {}
    pairs = normalize_fields(fields)

    if not pairs:
        return y

    label_font = settings.get(
        "label_font",
        settings.get("font", "Helvetica-Bold")
    )
    value_font = settings.get(
        "value_font",
        settings.get("font", "Helvetica")
    )

    label_size = float(settings.get("label_size", 9) or 9)
    value_size = float(settings.get("value_size", 10) or 10)

    label_color = settings.get("label_color", "#173B63")
    value_color = settings.get("value_color", "#222222")

    # Keep fields comfortably inside the certificate.
    usable_width = w * 0.78
    column_width = usable_width * 0.42
    left_center = w * 0.29
    right_center = w * 0.71

    row_height = 55
    label_to_value_gap = 15
    value_leading = max(12, value_size + 3)

    # Render all supplied fields. The certificate has enough room for
    # several rows; long values are wrapped rather than allowed to collide.
    visible_pairs = pairs[:8]

    for i, (label, value) in enumerate(visible_pairs):
        row = i // 2
        col = i % 2

        center_x = (
            left_center
            if col == 0
            else right_center
        )

        field_y = y - (row * row_height)

        # Label
        label_text = str(label).strip().upper()
        pdf.setFont(label_font, label_size)
        pdf.setFillColor(color(label_color))

        # If a very long label is supplied, shrink it slightly.
        label_draw_size = label_size
        if stringWidth(label_text, label_font, label_draw_size) > column_width:
            label_draw_size = max(
                6.5,
                label_size * column_width /
                stringWidth(label_text, label_font, label_draw_size)
            )
            pdf.setFont(label_font, label_draw_size)

        pdf.drawCentredString(
            center_x,
            field_y,
            label_text
        )

        # Value
        value_text = str(value).strip()

        pdf.setFont(value_font, value_size)
        pdf.setFillColor(color(value_color))

        value_lines = wrap_lines(
            value_text,
            value_font,
            value_size,
            column_width
        )

        # Never let one value consume an unreasonable amount of space.
        value_lines = value_lines[:2]

        value_y = field_y - label_to_value_gap

        for line_index, line in enumerate(value_lines):
            pdf.drawCentredString(
                center_x,
                value_y - (line_index * value_leading),
                line
            )

    rows = (len(visible_pairs) + 1) // 2

    # Return the next safe vertical position.
    return y - (rows * row_height) + 10

def create_certificate(data, design, output_path):
    if not isinstance(data, dict):
        raise ValueError("Certificate data must be a dictionary.")
    if not isinstance(design, dict):
        raise ValueError("Design must be a dictionary.")

    w, h = page_size(design)
    folder = os.path.dirname(output_path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    pdf = canvas.Canvas(output_path, pagesize=(w, h))
    pdf.setTitle(str(data.get("title", "Certificate")))
    pdf.setAuthor(str(data.get("organization", "Universal Certificate Platform")))

    draw_background(pdf, w, h, design)
    draw_premium_background(pdf, w, h, design)
    draw_border(pdf, w, h, design)
    draw_logo(pdf, design, w, h)

    colors = design.get("colors", {}) or {}
    primary = colors.get("title", colors.get("primary", "#173B63"))
    secondary = colors.get("border", colors.get("secondary", "#C9A227"))

    # Organization / institute
    brand = design.get("branding", {}) or design.get("organization", {}) or {}
    org = str(data.get("organization", brand.get("organization", ""))).strip()
    if org:
        org_font = font_name(brand, "Helvetica-Bold")
        org_size = font_size(brand, 16)
        org_color = brand.get("color", primary)
        draw_center(pdf, org, w / 2, h - 63, org_font, org_size, org_color)

    # Main title
    title_cfg = design.get("title", {}) or {}
    title = str(data.get("title", "CERTIFICATE OF ACHIEVEMENT")).strip()
    title_font = font_name(title_cfg, "Helvetica-Bold")
    title_size = font_size(title_cfg, 29)
    title_color = title_cfg.get("color", primary)
    draw_center(pdf, title.upper(), w / 2, h - 128, title_font, title_size, title_color)

    # Gold divider
    pdf.setStrokeColor(color(secondary))
    pdf.setLineWidth(1.2)
    pdf.line(w * 0.37, h - 151, w * 0.63, h - 151)

    subtitle_cfg = design.get("subtitle", {}) or {}
    subtitle = str(data.get("subtitle", "This certificate is proudly presented to")).strip()
    if subtitle:
        draw_center(pdf, subtitle, w / 2, h - 182,
                    font_name(subtitle_cfg, "Helvetica"),
                    font_size(subtitle_cfg, 12.5),
                    subtitle_cfg.get("color", "#555555"))

    # Recipient
    recipient_cfg = design.get("recipient", {}) or {}
    recipient = str(data.get("recipient", data.get("name", "Recipient Name"))).strip()
    recipient_font = font_name(recipient_cfg, "Helvetica-Bold")
    recipient_size = font_size(recipient_cfg, 28)
    recipient_color = recipient_cfg.get("color", "#111111")
    recipient_y = h - 235
    # Shrink only when the name is unusually long.
    if stringWidth(recipient, recipient_font, recipient_size) > w * 0.72:
        recipient_size = max(18, recipient_size * (w * 0.72) / stringWidth(recipient, recipient_font, recipient_size))
    draw_center(pdf, recipient, w / 2, recipient_y, recipient_font, recipient_size, recipient_color)

    # Recipient accent line
    line_width = min(w * 0.34, max(180, stringWidth(recipient, recipient_font, recipient_size) * 0.72))
    pdf.setStrokeColor(color(recipient_cfg.get("underline_color", secondary)))
    pdf.setLineWidth(1.2)
    pdf.line((w - line_width) / 2, recipient_y - 10, (w + line_width) / 2, recipient_y - 10)

    # Description / purpose
    body_cfg = design.get("body", {}) or {}
    description = str(data.get("description", "")).strip()
    current_y = recipient_y - 42
    if description:
        current_y = draw_wrapped_center(
            pdf, description, w / 2, current_y, w * 0.72,
            font_name(body_cfg, "Helvetica"), font_size(body_cfg, 11.5),
            body_cfg.get("color", "#333333"), leading=16, max_lines=3
        ) - 5

    # Dynamic fields
    current_y = draw_fields(pdf, data.get("fields", {}), design, w, current_y - 5)

    # Footer metadata: NEVER expose filesystem paths.
    metadata = design.get("metadata", {}) or {}
    meta_font = font_name(metadata, "Helvetica")
    meta_size = font_size(metadata, 8.5)
    meta_color = metadata.get("color", "#555555")

    date_value = str(data.get("date", "")).strip()
    time_value = str(data.get("time", "")).strip()
    cert_id = str(data.get("certificate_id", "")).strip()

    footer_y = 45
    if date_value:
        draw_center(pdf, "Date: " + date_value, w * 0.22, footer_y, meta_font, meta_size, meta_color)
    if time_value:
        draw_center(pdf, "Time: " + time_value, w * 0.50, footer_y, meta_font, meta_size, meta_color)
    if cert_id:
        # Keep long IDs inside the page and separate from date.
        id_text = "Certificate ID: " + cert_id
        if stringWidth(id_text, meta_font, meta_size) > w * 0.34:
            meta_size_id = 7.2
        else:
            meta_size_id = meta_size
        draw_center(pdf, id_text, w * 0.78, footer_y, meta_font, meta_size_id, meta_color)

    draw_signature(pdf, design, w, h)
    draw_seal(pdf, design, w, h)

    # Small platform mark, unobtrusive and not a file path.
    pdf.setFont("Helvetica", 6.5)
    pdf.setFillColor(color("#888888"))
    pdf.drawCentredString(w / 2, 28, "Generated by Universal Certificate Platform")

    pdf.showPage()
    pdf.save()
    return output_path


if __name__ == "__main__":
    demo_design = {
        "page": {"size": "A4", "orientation": "landscape"},
        "colors": {"background": "#FFFFFF", "border": "#C9A227", "title": "#173B63"},
        "background": {"enabled": True, "color": "#FFFFFF"},
        "border": {"enabled": True, "color": "#C9A227", "width": 2.4, "margin": 18},
        "branding": {"font": "Helvetica-Bold", "font_size": 16, "color": "#173B63"},
        "title": {"font": "Helvetica-Bold", "font_size": 29, "color": "#173B63"},
        "subtitle": {"font": "Helvetica", "font_size": 12, "color": "#555555"},
        "recipient": {"font": "Helvetica-Bold", "font_size": 28, "color": "#111111", "underline_color": "#C9A227"},
        "body": {"font": "Helvetica", "font_size": 11, "color": "#333333"},
        "fields": {"font": "Helvetica", "label_size": 9, "value_size": 10, "label_color": "#173B63", "value_color": "#111111"},
        "metadata": {"font": "Helvetica", "font_size": 8.5, "color": "#555555"},
        "logo": {"enabled": False}, "signature": {"enabled": True, "label": "Authorized Signature", "signer_name": "Program Coordinator", "designation": "Authorized Signatory"}, "seal": {"enabled": False}
    }
    demo_data = {
        "organization": "Siddharth College of Commerce and Economics",
        "title": "CERTIFICATE OF PARTICIPATION",
        "subtitle": "This certificate is proudly presented to",
        "name": "Mohammad Ahad Shaikh",
        "recipient": "Mohammad Ahad Shaikh",
        "description": "For participating in the Python Workshop and demonstrating active involvement in the program.",
        "date": "16-09-2026",
        "time": "",
        "certificate_id": "CERT-2026-001",
        "fields": {"Course": "BSc IT", "Role": "Participant"}
    }
    create_certificate(demo_data, demo_design, "output/certificate_engine_demo.pdf")
    print("CERTIFICATE ENGINE TEST COMPLETED")
