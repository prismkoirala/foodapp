"""
Utility functions for orders app.
"""
import qrcode
from io import BytesIO
from django.core.files import File
from datetime import datetime
import secrets


def generate_qr_code_image(qr_code_string, base_url='https://foodapp.com'):
    """
    Generate a QR code image for a given code string.

    Args:
        qr_code_string: The unique QR code identifier
        base_url: Base URL for the QR code redirect

    Returns:
        File object containing the QR code image
    """
    # Create QR code URL
    qr_url = f"{base_url}/qr/{qr_code_string}"

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    # Return as File object
    return File(buffer, name=f'qr_{qr_code_string}.png')


def generate_order_number():
    """
    Generate a unique order number.

    Format: ORD-YYYYMMDD-XXXX
    Example: ORD-20240125-A3F9
    """
    today = datetime.now().strftime('%Y%m%d')
    random_part = secrets.token_hex(4).upper()
    return f"ORD-{today}-{random_part}"


def calculate_order_total(order_items):
    """
    Calculate the total amount for an order based on its items.

    Args:
        order_items: List of dictionaries with 'quantity' and 'unit_price' keys

    Returns:
        Decimal: Total amount
    """
    from decimal import Decimal
    total = Decimal('0.00')
    for item in order_items:
        quantity = item.get('quantity', 0)
        unit_price = Decimal(str(item.get('unit_price', 0)))
        total += quantity * unit_price
    return total
