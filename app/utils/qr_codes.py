"""QR code helper utilities."""

import base64
import io

import segno


def _qr_png_bytes(payload: str, scale: int = 6) -> bytes:
    """Generate PNG bytes for the provided payload."""
    qr = segno.make(payload)
    buffer = io.BytesIO()
    qr.save(buffer, kind="png", scale=scale)
    return buffer.getvalue()


def qr_png_data_uri(payload: str, scale: int = 6) -> str:
    """
    Generate a PNG QR code for the provided payload and return a data URI.

    The payload is embedded directly in the code (no URL wrapping) so scanners
    can send the drawer ID straight back to the API or frontend.
    """
    encoded = base64.b64encode(_qr_png_bytes(payload, scale=scale)).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def qr_png_bytes(payload: str, scale: int = 6) -> bytes:
    """Expose PNG bytes for callers that need the raw binary format."""
    return _qr_png_bytes(payload, scale=scale)
