"""Concrete read-only Windows window capture backend.

Uses only Win32 window capture APIs. It does not read or modify the target
process memory and does not send keyboard/mouse input.
"""
from __future__ import annotations

import ctypes
from ctypes import wintypes


_USER32 = ctypes.WinDLL("user32", use_last_error=True)
_GDI32 = ctypes.WinDLL("gdi32", use_last_error=True)

_SRCCOPY = 0x00CC0020
_BI_RGB = 0
_DIB_RGB_COLORS = 0


class _BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class _BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", _BITMAPINFOHEADER),
        ("bmiColors", wintypes.DWORD * 3),
    ]


class Win32WindowCaptureBackend:
    """Capture a window into packed BGRA bytes using Win32/GDI."""

    def capture(self, window_handle: int) -> tuple[int, int, bytes]:
        hwnd = wintypes.HWND(window_handle)
        if not _USER32.IsWindow(hwnd):
            raise ValueError("window handle is not valid")

        rect = wintypes.RECT()
        if not _USER32.GetClientRect(hwnd, ctypes.byref(rect)):
            raise OSError(ctypes.get_last_error(), "GetClientRect failed")
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        if width <= 0 or height <= 0:
            raise ValueError("target client area has no pixels")

        window_dc = _USER32.GetDC(hwnd)
        if not window_dc:
            raise OSError(ctypes.get_last_error(), "GetDC failed")
        mem_dc = None
        bitmap = None
        old_bitmap = None
        try:
            mem_dc = _GDI32.CreateCompatibleDC(window_dc)
            bitmap = _GDI32.CreateCompatibleBitmap(window_dc, width, height)
            if not mem_dc or not bitmap:
                raise OSError(ctypes.get_last_error(), "GDI bitmap allocation failed")
            old_bitmap = _GDI32.SelectObject(mem_dc, bitmap)
            if not old_bitmap:
                raise OSError(ctypes.get_last_error(), "SelectObject failed")
            if not _USER32.PrintWindow(hwnd, mem_dc, 0):
                if not _GDI32.BitBlt(mem_dc, 0, 0, width, height, window_dc, 0, 0, _SRCCOPY):
                    raise OSError(ctypes.get_last_error(), "window capture failed")

            info = _BITMAPINFO()
            info.bmiHeader.biSize = ctypes.sizeof(_BITMAPINFOHEADER)
            info.bmiHeader.biWidth = width
            info.bmiHeader.biHeight = -height
            info.bmiHeader.biPlanes = 1
            info.bmiHeader.biBitCount = 32
            info.bmiHeader.biCompression = _BI_RGB
            size = width * height * 4
            buffer = ctypes.create_string_buffer(size)
            copied = _GDI32.GetDIBits(
                mem_dc, bitmap, 0, height, buffer,
                ctypes.byref(info), _DIB_RGB_COLORS,
            )
            if copied != height:
                raise OSError(ctypes.get_last_error(), "GetDIBits failed")
            return width, height, buffer.raw
        finally:
            if old_bitmap and mem_dc:
                _GDI32.SelectObject(mem_dc, old_bitmap)
            if bitmap:
                _GDI32.DeleteObject(bitmap)
            if mem_dc:
                _GDI32.DeleteDC(mem_dc)
            _USER32.ReleaseDC(hwnd, window_dc)
