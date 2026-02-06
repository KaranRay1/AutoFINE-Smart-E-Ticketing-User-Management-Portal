"""
ALPR Module for AutoFINE System
"""

from .license_plate_recognition import recognize_license_plate, batch_process_images

__all__ = ['recognize_license_plate', 'batch_process_images']
