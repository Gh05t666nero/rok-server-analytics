# styles/__init__.py
"""
Modul gaya untuk aplikasi analisis server Rise of Kingdoms.
Berisi fungsi-fungsi untuk menerapkan gaya CSS kustom.
"""

from styles.custom_styles import apply_custom_styles, apply_light_mode_styles, apply_print_friendly_styles

__all__ = [
    'apply_custom_styles',
    'apply_light_mode_styles',
    'apply_print_friendly_styles'
]