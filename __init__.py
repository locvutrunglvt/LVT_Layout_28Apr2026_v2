# -*- coding: utf-8 -*-
"""
LVT Map Layout - QGIS Plugin
Automated map layout generator using LVT print templates (EN/VN).
"""


def classFactory(iface):
    """Load the LVT Map Layout plugin.

    Args:
        iface: A QGIS interface instance (QgisInterface).

    Returns:
        LvtMapLayout: The plugin instance.
    """
    from .lvt_map_layout import LvtMapLayout
    return LvtMapLayout(iface)
