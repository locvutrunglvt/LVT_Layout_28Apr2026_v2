# -*- coding: utf-8 -*-
"""LVT Map Layout - Dialog UI built programmatically with PyQt5."""

import os
import math
from datetime import date

from qgis.PyQt.QtCore import Qt, QSize
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QComboBox, QSpinBox,
    QCheckBox, QRadioButton, QButtonGroup, QGroupBox,
    QTextEdit, QPushButton, QProgressBar,
    QMessageBox, QGridLayout, QScrollArea
)
from qgis.core import QgsProject, QgsMapLayerProxyModel, QgsVectorLayer
from qgis.gui import QgsMapLayerComboBox

from .lvt_engine import LvtEngine


# Paper sizes in mm (width x height for landscape)
PAPER_SIZES = {
    # A-series (ISO 216)
    "A5 (210 × 148 mm)": (210, 148),
    "A4 (297 × 210 mm)": (297, 210),
    "A3 (420 × 297 mm)": (420, 297),
    "A2 (594 × 420 mm)": (594, 420),
    "A1 (841 × 594 mm)": (841, 594),
    "A0 (1189 × 841 mm)": (1189, 841),
    # B-series (ISO 216)
    "B5 (250 × 176 mm)": (250, 176),
    "B4 (353 × 250 mm)": (353, 250),
    "B3 (500 × 353 mm)": (500, 353),
    "B2 (707 × 500 mm)": (707, 500),
    "B1 (1000 × 707 mm)": (1000, 707),
    "B0 (1414 × 1000 mm)": (1414, 1000),
}

# Layout modes
MODE_SLIDE = "slide"
MODE_PRINT = "print"

# Standard scales for suggestion
STANDARD_SCALES = [
    500, 1000, 2000, 2500, 5000, 10000, 15000,
    20000, 25000, 50000, 100000, 250000, 500000, 1000000,
]


class LvtDialog(QDialog):
    """Main dialog for LVT Map Layout plugin."""

    def __init__(self, iface, plugin_dir, parent=None):
        super().__init__(parent or iface.mainWindow())
        self.iface = iface
        self.plugin_dir = plugin_dir
        self.engine = LvtEngine(iface, plugin_dir)
        self.setWindowTitle("LVT Map Layout")
        self.setMinimumSize(QSize(560, 500))
        self._build_ui()

    # ── UI Construction ──────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        tabs = QTabWidget()
        tabs.addTab(self._tab_general(), "General")
        tabs.addTab(self._tab_map(), "Map Settings")
        tabs.addTab(self._tab_content(), "Content")
        root.addWidget(tabs)

        # Buttons
        btn_row = QHBoxLayout()

        btn_help = QPushButton("❓ Help")
        btn_help.setStyleSheet(
            "QPushButton{background:#ff8f00;color:#fff;font-weight:bold;"
            "padding:6px 14px;border-radius:4px}"
            "QPushButton:hover{background:#ffa000}"
        )
        btn_help.clicked.connect(self._show_help)

        self.btn_create = QPushButton("Create Layout / Tạo khung")
        self.btn_create.setStyleSheet(
            "QPushButton{background:#2e7d32;color:#fff;font-weight:bold;"
            "padding:6px 20px;border-radius:4px}"
            "QPushButton:hover{background:#388e3c}"
        )
        self.btn_create.clicked.connect(self._on_create)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.close)

        btn_row.addWidget(btn_help)

        btn_crs = QPushButton("🌐 CRS")
        btn_crs.setStyleSheet(
            "QPushButton{background:#1565c0;color:#fff;font-weight:bold;"
            "padding:6px 14px;border-radius:4px}"
            "QPushButton:hover{background:#1976d2}"
        )
        btn_crs.clicked.connect(self._show_crs)
        btn_row.addWidget(btn_crs)

        btn_row.addStretch()
        btn_row.addWidget(btn_close)
        btn_row.addWidget(self.btn_create)
        root.addLayout(btn_row)

    # ── Tab: General ─────────────────────────────────────────────

    def _tab_general(self):
        w = QWidget()
        g = QGridLayout(w)
        row = 0

        # Layout mode selector
        g.addWidget(QLabel("Layout Mode / Chế độ:"), row, 0)
        mode_box = QHBoxLayout()
        self.rad_slide = QRadioButton("Slide (simple)")
        self.rad_print = QRadioButton("Print (full frame)")
        self.rad_slide.setChecked(True)
        bg_mode = QButtonGroup(w)
        bg_mode.addButton(self.rad_slide)
        bg_mode.addButton(self.rad_print)
        self.rad_slide.toggled.connect(self._toggle_mode_fields)
        mode_box.addWidget(self.rad_slide)
        mode_box.addWidget(self.rad_print)
        g.addLayout(mode_box, row, 1)
        row += 1

        # Language selector
        g.addWidget(QLabel("Language / Ngôn ngữ:"), row, 0)
        self.cmb_lang = QComboBox()
        self.cmb_lang.addItems(["English (EN)", "Tiếng Việt (VN)"])
        self.cmb_lang.setCurrentIndex(1)  # VN default
        g.addWidget(self.cmb_lang, row, 1)
        row += 1

        # ── Print-only fields ─────────────────────────────────────
        self.lbl_title = QLabel("Map Title / Tên bản đồ:")
        g.addWidget(self.lbl_title, row, 0)
        self.txt_title = QLineEdit()
        self.txt_title.setPlaceholderText("e.g. Land Use Map 2026")
        g.addWidget(self.txt_title, row, 1)
        row += 1

        self.lbl_org = QLabel("Organization / Đơn vị:")
        g.addWidget(self.lbl_org, row, 0)
        self.txt_org = QLineEdit()
        self.txt_org.setPlaceholderText("e.g. Tan Cao Nguyên JSC")
        g.addWidget(self.txt_org, row, 1)
        row += 1

        self.lbl_study = QLabel("Study Area / Khu vực:")
        g.addWidget(self.lbl_study, row, 0)
        self.txt_study = QLineEdit()
        self.txt_study.setPlaceholderText("e.g. Gia Lai Province")
        g.addWidget(self.txt_study, row, 1)
        row += 1

        self.lbl_refs = QLabel("References / Viện dẫn:")
        g.addWidget(self.lbl_refs, row, 0)
        self.txt_refs = QLineEdit()
        self.txt_refs.setPlaceholderText("e.g. TCVN 8211:2009")
        g.addWidget(self.txt_refs, row, 1)
        row += 1

        # Store print-only widgets for toggle
        self._print_widgets = [
            self.lbl_title, self.txt_title,
            self.lbl_org, self.txt_org,
            self.lbl_study, self.txt_study,
            self.lbl_refs, self.txt_refs,
        ]
        for wgt in self._print_widgets:
            wgt.setVisible(False)  # hidden by default (Slide mode)

        # ── Common fields ─────────────────────────────────────────
        g.addWidget(QLabel("Author / Người lập:"), row, 0)
        self.txt_author = QLineEdit()
        self.txt_author.setPlaceholderText("e.g. Lộc Vũ Trung")
        g.addWidget(self.txt_author, row, 1)
        row += 1

        g.addWidget(QLabel("Date / Ngày:"), row, 0)
        self.txt_date = QLineEdit(date.today().strftime("%d/%m/%Y"))
        g.addWidget(self.txt_date, row, 1)
        row += 1

        g.setRowStretch(row, 1)
        return w

    def _toggle_mode_fields(self, checked):
        """Show/hide print-only fields based on mode selection."""
        is_print = self.rad_print.isChecked()
        for wgt in self._print_widgets:
            wgt.setVisible(is_print)

    # ── Tab: Map Settings ────────────────────────────────────────

    def _tab_map(self):
        w = QWidget()
        g = QGridLayout(w)
        row = 0

        g.addWidget(QLabel("Paper Size / Khổ giấy:"), row, 0)
        self.cmb_paper = QComboBox()
        self.cmb_paper.addItems(list(PAPER_SIZES.keys()) + ["Custom / Tự chọn"])
        self.cmb_paper.setCurrentIndex(1)  # A4 default
        self.cmb_paper.currentIndexChanged.connect(self._toggle_custom_size)
        g.addWidget(self.cmb_paper, row, 1)
        row += 1

        g.addWidget(QLabel("Custom Size (mm) / Kích thước tự chọn:"), row, 0)
        custom_box = QHBoxLayout()
        self.spn_custom_w = QSpinBox()
        self.spn_custom_w.setRange(50, 3000)
        self.spn_custom_w.setValue(297)
        self.spn_custom_w.setSuffix(" mm")
        self.spn_custom_w.setPrefix("W: ")
        self.spn_custom_w.setEnabled(False)
        self.spn_custom_h = QSpinBox()
        self.spn_custom_h.setRange(50, 3000)
        self.spn_custom_h.setValue(210)
        self.spn_custom_h.setSuffix(" mm")
        self.spn_custom_h.setPrefix("H: ")
        self.spn_custom_h.setEnabled(False)
        custom_box.addWidget(self.spn_custom_w)
        custom_box.addWidget(QLabel("×"))
        custom_box.addWidget(self.spn_custom_h)
        g.addLayout(custom_box, row, 1)
        row += 1

        # Draw Extent button (only enabled in Custom mode)
        self.btn_draw = QPushButton("🖊 Draw Extent / Vẽ phạm vi → tự tính kích thước")
        self.btn_draw.setStyleSheet(
            "QPushButton{background:#1565c0;color:#fff;font-weight:bold;"
            "padding:8px 16px;border-radius:4px;font-size:13px}"
            "QPushButton:hover{background:#1976d2}"
            "QPushButton:disabled{background:#bbb;color:#666}"
        )
        self.btn_draw.setEnabled(False)
        self.btn_draw.clicked.connect(self._on_draw_extent)
        g.addWidget(self.btn_draw, row, 0, 1, 2)
        row += 1

        # Drawn extent + scale suggestion display
        self.lbl_drawn = QLabel("")
        self.lbl_drawn.setStyleSheet("color:#888;font-style:italic")
        self.lbl_drawn.setWordWrap(True)
        g.addWidget(self.lbl_drawn, row, 0, 1, 2)
        row += 1

        # Orientation (hidden when Custom + Draw is used)
        self.lbl_orient = QLabel("Orientation / Hướng:")
        g.addWidget(self.lbl_orient, row, 0)
        orient_box = QHBoxLayout()
        self.rad_landscape = QRadioButton("Landscape / Ngang")
        self.rad_portrait = QRadioButton("Portrait / Dọc")
        self.rad_landscape.setChecked(True)
        bg = QButtonGroup(w)
        bg.addButton(self.rad_landscape)
        bg.addButton(self.rad_portrait)
        orient_box.addWidget(self.rad_landscape)
        orient_box.addWidget(self.rad_portrait)
        self.orient_widget = QWidget()
        self.orient_widget.setLayout(orient_box)
        g.addWidget(self.orient_widget, row, 1)
        row += 1

        # Scale
        g.addWidget(QLabel("Scale / Tỷ lệ:"), row, 0)
        scale_box = QHBoxLayout()
        self.chk_auto_scale = QCheckBox("Auto fit / Tự động")
        self.chk_auto_scale.setChecked(True)
        self.chk_auto_scale.stateChanged.connect(self._toggle_scale)
        self.spn_scale = QSpinBox()
        self.spn_scale.setRange(100, 10000000)
        self.spn_scale.setValue(10000)
        self.spn_scale.setPrefix("1 : ")
        self.spn_scale.setEnabled(False)
        self.spn_scale.valueChanged.connect(self._on_scale_changed)
        scale_box.addWidget(self.chk_auto_scale)
        scale_box.addWidget(self.spn_scale)
        g.addLayout(scale_box, row, 1)
        row += 1

        # Scale suggestion label
        self.lbl_scale_hint = QLabel("")
        self.lbl_scale_hint.setWordWrap(True)
        self.lbl_scale_hint.setStyleSheet(
            "color:#1565c0;font-style:italic;padding:2px 0"
        )
        g.addWidget(self.lbl_scale_hint, row, 0, 1, 2)
        row += 1

        g.setRowStretch(row, 1)
        return w

    # ── Tab: Content ─────────────────────────────────────────────

    def _tab_content(self):
        w = QWidget()
        g = QGridLayout(w)
        row = 0

        g.addWidget(QLabel("Map Data Sources / Nguồn dữ liệu:"), row, 0, 1, 2)
        row += 1
        self.txt_sources = QTextEdit()
        self.txt_sources.setPlaceholderText(
            "e.g. National land-use map 2020, Sentinel-2 imagery..."
        )
        self.txt_sources.setMaximumHeight(80)
        g.addWidget(self.txt_sources, row, 0, 1, 2)
        row += 1

        grp = QGroupBox("Elements to show / Các thành phần hiển thị")
        grp_lay = QVBoxLayout(grp)
        self.chk_legend = QCheckBox("Legend / Chú giải")
        self.chk_legend.setChecked(True)
        self.chk_north = QCheckBox("North Arrow / Mũi tên Bắc")
        self.chk_north.setChecked(True)
        self.chk_scalebar = QCheckBox("Scale Bar / Thước tỷ lệ")
        self.chk_scalebar.setChecked(True)
        for c in [self.chk_legend, self.chk_north, self.chk_scalebar]:
            grp_lay.addWidget(c)
        g.addWidget(grp, row, 0, 1, 2)
        row += 1

        g.setRowStretch(row, 1)
        return w

    # ── Slots ────────────────────────────────────────────────────


    def _toggle_custom_size(self, idx):
        is_custom = self.cmb_paper.currentText() == "Custom / Tự chọn"
        self.spn_custom_w.setEnabled(is_custom)
        self.spn_custom_h.setEnabled(is_custom)
        self.btn_draw.setEnabled(is_custom)
        # Show/hide orientation: hide when Custom (draw determines it)
        has_drawn = hasattr(self, "drawn_extent") and self.drawn_extent
        show_orient = not (is_custom and has_drawn)
        self.lbl_orient.setVisible(show_orient)
        self.orient_widget.setVisible(show_orient)
        if not is_custom:
            self.lbl_drawn.setText("")
            self.lbl_scale_hint.setText("")

    def _toggle_scale(self, state):
        self.spn_scale.setEnabled(state == Qt.Unchecked)
        if state == Qt.Unchecked and hasattr(self, 'drawn_extent') and self.drawn_extent:
            self._on_scale_changed(self.spn_scale.value())

    def refresh_layers(self):
        pass  # QgsMapLayerComboBox auto-refreshes

    # ── Draw Extent on Map ───────────────────────────────────────

    def _on_draw_extent(self):
        """Activate rectangle drawing tool on the map canvas."""
        from .lvt_extent_tool import LvtExtentTool
        canvas = self.iface.mapCanvas()
        self.extent_tool = LvtExtentTool(canvas, self._on_extent_drawn)
        canvas.setMapTool(self.extent_tool)
        self.iface.messageBar().pushInfo(
            "LVT", "Draw a rectangle on the map to define extent & page size."
        )
        self.hide()  # Hide dialog while drawing

    def _on_extent_drawn(self, rect):
        """Callback: store drawn extent and calculate initial page size.

        Workflow: draw extent → suggest scales → user picks scale → page auto-sizes.
        """
        self.drawn_extent = rect

        # Store extent in real-world meters
        crs = self.iface.mapCanvas().mapSettings().destinationCrs()
        ext_w = rect.width()
        ext_h = rect.height()
        if crs.isGeographic():
            ext_w *= 111320
            ext_h *= 111320
        self._extent_w_m = ext_w
        self._extent_h_m = ext_h

        # Calculate natural scale from current canvas view
        canvas = self.iface.mapCanvas()
        mu_per_mm = canvas.mapUnitsPerPixel() * (canvas.logicalDpiX() / 25.4)
        view_map_w = rect.width() / mu_per_mm
        view_map_h = rect.height() / mu_per_mm
        natural_scale = max(
            ext_w / view_map_w * 1000 if view_map_w > 0 else 10000,
            ext_h / view_map_h * 1000 if view_map_h > 0 else 10000
        )

        # Suggest scales
        suggestions = [s for s in STANDARD_SCALES
                       if s >= natural_scale * 0.5 and s <= natural_scale * 3]
        if not suggestions:
            diffs = sorted([(abs(s - natural_scale), s) for s in STANDARD_SCALES])
            suggestions = [d[1] for d in diffs[:3]]
        suggestions.sort()
        suggestion_str = ", ".join([f"1:{s:,}" for s in suggestions])
        self.lbl_scale_hint.setText(
            f"💡 Suggested / Đề xuất: {suggestion_str}\n"
            f"   (Natural / Tự nhiên ≈ 1:{int(natural_scale):,})"
        )

        # Set best scale → triggers _on_scale_changed → sets page size
        best = min(STANDARD_SCALES, key=lambda s: abs(s - natural_scale))
        self.spn_scale.setValue(best)

        # Also calculate page for current scale right away
        self._recalc_page_from_scale(best)

        self.lbl_orient.setVisible(False)
        self.orient_widget.setVisible(False)

        self.show()
        self.raise_()

    def _on_scale_changed(self, scale_val):
        """When user changes scale, recalculate page size from drawn extent."""
        if not hasattr(self, '_extent_w_m') or not self._extent_w_m:
            return
        if self.chk_auto_scale.isChecked():
            return
        self._recalc_page_from_scale(scale_val)

    def _recalc_page_from_scale(self, scale_val):
        """Calculate page size from extent and scale.

        Uses size-dependent margins matching template design:
          A5/A4: left=19.15  top=32.65  bottom=30.9
          A3:    left=21.85  top=34.85  bottom=30.9
          A2:    left=25.85  top=59.85  bottom=30.9
          A1:    left=25.85  top=81.85  bottom=30.9
          A0:    left=35.85  top=99.85  bottom=30.9
        """
        if scale_val <= 0:
            return

        map_w_mm = self._extent_w_m / scale_val * 1000
        map_h_mm = self._extent_h_m / scale_val * 1000

        # Slide margins: 5mm all sides
        page_w = int(round(map_w_mm + 10))
        page_h = int(round(map_h_mm + 10))

        page_w = max(50, min(3000, page_w))
        page_h = max(50, min(3000, page_h))

        if page_w > 3000 or page_h > 3000:
            self.lbl_drawn.setStyleSheet("color:#c62828;font-weight:bold")
            self.lbl_drawn.setText(
                f"⚠️ Page too large! / Trang quá lớn! ({page_w}×{page_h} mm)\n"
                f"   Max 3000mm. Try a smaller scale / Thử tỷ lệ nhỏ hơn."
            )
            return

        self.spn_custom_w.setValue(page_w)
        self.spn_custom_h.setValue(page_h)

        if page_w >= page_h:
            self.rad_landscape.setChecked(True)
        else:
            self.rad_portrait.setChecked(True)

        self.lbl_drawn.setText(
            f"✅ Extent: {self.drawn_extent.xMinimum():.1f}, "
            f"{self.drawn_extent.yMinimum():.1f} → "
            f"{self.drawn_extent.xMaximum():.1f}, "
            f"{self.drawn_extent.yMaximum():.1f}\n"
            f"   Scale 1:{scale_val:,}  →  "
            f"Page: {page_w} × {page_h} mm  |  "
            f"Map: {int(map_w_mm)} × {int(map_h_mm)} mm"
        )
        self.lbl_drawn.setStyleSheet("color:#2e7d32;font-weight:bold")

    # ── Help ─────────────────────────────────────────────────────

    def _show_help(self):
        """Show help dialog with language toggle."""
        dlg = QDialog(self)
        dlg.setWindowTitle("📖 LVT Map Layout — Help / Trợ giúp")
        dlg.setMinimumSize(620, 500)
        lay = QVBoxLayout(dlg)

        # Language toggle
        btn_row = QHBoxLayout()
        btn_en = QPushButton("🇬🇧 English")
        btn_vn = QPushButton("🇻🇳 Tiếng Việt")
        for b in [btn_en, btn_vn]:
            b.setCheckable(True)
            b.setStyleSheet(
                "QPushButton{padding:6px 16px;border-radius:4px;"
                "font-weight:bold;border:2px solid #ccc}"
                "QPushButton:checked{background:#1565c0;color:#fff;border-color:#1565c0}"
            )
        btn_vn.setChecked(True)
        btn_row.addStretch()
        btn_row.addWidget(btn_en)
        btn_row.addWidget(btn_vn)
        btn_row.addStretch()
        lay.addLayout(btn_row)

        # Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QLabel()
        content.setWordWrap(True)
        content.setTextFormat(Qt.RichText)
        content.setOpenExternalLinks(True)
        content.setMargin(12)
        scroll.setWidget(content)
        lay.addWidget(scroll)

        help_en = self._help_text_en()
        help_vn = self._help_text_vn()
        content.setText(help_vn)

        def switch_en():
            btn_en.setChecked(True); btn_vn.setChecked(False)
            content.setText(help_en)
        def switch_vn():
            btn_vn.setChecked(True); btn_en.setChecked(False)
            content.setText(help_vn)

        btn_en.clicked.connect(switch_en)
        btn_vn.clicked.connect(switch_vn)

        btn_close = QPushButton("OK")
        btn_close.clicked.connect(dlg.accept)
        lay.addWidget(btn_close)
        dlg.exec_()

    # ── CRS Library Dialog ───────────────────────────────────────

    def _show_crs(self):
        """Show CRS Library dialog with language toggle."""
        dlg = QDialog(self)
        dlg.setWindowTitle("🌐 CRS Library / Thư viện Hệ tọa độ")
        dlg.setMinimumSize(680, 520)
        lay = QVBoxLayout(dlg)

        # Current project CRS info bar
        from qgis.core import QgsProject
        current_crs = QgsProject.instance().crs()
        crs_info = QLabel(
            f"📍 Current Project CRS / CRS dự án hiện tại: "
            f"<b>{current_crs.authid()}</b> — {current_crs.description()}"
        )
        crs_info.setStyleSheet(
            "background:#e8f5e9;padding:8px;border-radius:4px;"
            "font-size:12px;border:1px solid #a5d6a7"
        )
        crs_info.setWordWrap(True)
        lay.addWidget(crs_info)

        # Language toggle
        btn_row = QHBoxLayout()
        btn_en = QPushButton("🇬🇧 English")
        btn_vn = QPushButton("🇻🇳 Tiếng Việt")
        for b in [btn_en, btn_vn]:
            b.setCheckable(True)
            b.setStyleSheet(
                "QPushButton{padding:6px 16px;border-radius:4px;"
                "font-weight:bold;border:2px solid #ccc}"
                "QPushButton:checked{background:#1565c0;color:#fff;border-color:#1565c0}"
            )
        btn_vn.setChecked(True)
        btn_row.addStretch()
        btn_row.addWidget(btn_en)
        btn_row.addWidget(btn_vn)
        btn_row.addStretch()
        lay.addLayout(btn_row)

        # CRS content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QLabel()
        content.setWordWrap(True)
        content.setTextFormat(Qt.RichText)
        content.setOpenExternalLinks(True)
        content.setMargin(12)
        scroll.setWidget(content)
        lay.addWidget(scroll)

        crs_en = self._crs_text_en()
        crs_vn = self._crs_text_vn()
        content.setText(crs_vn)

        def switch_en():
            btn_en.setChecked(True); btn_vn.setChecked(False)
            content.setText(crs_en)
        def switch_vn():
            btn_vn.setChecked(True); btn_en.setChecked(False)
            content.setText(crs_vn)

        btn_en.clicked.connect(switch_en)
        btn_vn.clicked.connect(switch_vn)

        btn_close = QPushButton("OK")
        btn_close.clicked.connect(dlg.accept)
        lay.addWidget(btn_close)
        dlg.exec_()

    def _help_text_en(self):
        return """
<h2>🗺️ LVT Map Layout v2.0 — User Guide</h2>

<h3>🔷 LAYOUT MODES</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;margin-bottom:8px">
<tr style="background:#e3f2fd"><td><b>🖼️ Slide</b></td>
<td>Simple, borderless layout — ideal for presentations, reports, quick exports.</td></tr>
<tr style="background:#e8f5e9"><td><b>🖨️ Print</b></td>
<td>Full cartographic layout — multi-line frame, coordinate grids, scalebars,
title block, references. Professional map output (A5→A0).</td></tr>
</table>

<h3>📌 Step 1 — General Settings</h3>
<ul>
<li>🔘 <b>Layout Mode:</b> Choose <b>Slide</b> or <b>Print</b>.</li>
<li>🌐 <b>Language:</b> EN (English) or VN (Tiếng Việt) — controls all template labels.</li>
</ul>
<p><b>🖨️ Print mode — additional fields:</b></p>
<ul>
<li>📝 <b>Map Title:</b> Main title displayed in the title block.</li>
<li>🏢 <b>Organization:</b> Company / organization name.</li>
<li>📍 <b>Study Area:</b> Geographic area name (province, district, etc.).</li>
<li>📚 <b>References:</b> Technical standards, e.g. <i>TCVN 8211:2009</i>.</li>
</ul>
<p><b>👤 Common fields (both modes):</b></p>
<ul>
<li>✍️ <b>Author:</b> Map creator name.</li>
<li>📅 <b>Date:</b> Creation date (auto-filled today).</li>
</ul>

<h3>📌 Step 2 — Map Settings</h3>
<p><b>📐 Option A — Standard Paper:</b></p>
<ul>
<li>📄 Select paper size: <b>A5, A4, A3, A2, A1, A0</b>.</li>
<li>🔄 Choose orientation: <b>Landscape</b> (horizontal) or <b>Portrait</b> (vertical).</li>
<li>Map extent = current QGIS canvas view.</li>
</ul>
<p><b>🖊️ Option B — Draw Extent (Custom):</b></p>
<ol>
<li>Select <b>"Custom / Tự chọn"</b> in Paper Size dropdown.</li>
<li>Click <b>"🖊 Draw Extent"</b> button → draw a rectangle on the map canvas.</li>
<li>The drawn rectangle defines the exact map content area.</li>
<li>Plugin auto-calculates page dimensions and suggests standard scales.</li>
<li>💡 Scale suggestions appear below (e.g. 1:5,000 / 1:10,000 / 1:25,000).</li>
</ol>
<p><b>🔍 Scale options:</b></p>
<ul>
<li>☑ <b>Auto fit:</b> Scale adjusts automatically to fill the page.</li>
<li>☐ <b>Manual:</b> Uncheck "Auto fit" → enter a specific scale (e.g. 1:10,000).</li>
</ul>

<h3>📌 Step 3 — Content</h3>
<ul>
<li>📋 <b>Data Sources:</b> List your map data sources (satellite imagery, survey data, etc.).</li>
<li>🧭 <b>North Arrow:</b> Toggle on/off.</li>
<li>📏 <b>Scale Bar:</b> Toggle on/off (meter + degree/minute bars in Print mode).</li>
<li>🗂️ <b>Legend:</b> Toggle on/off.</li>
</ul>

<h3>📌 Step 4 — Create &amp; Export</h3>
<ol>
<li>✅ Click <b>"Create Layout / Tạo khung"</b>.</li>
<li>🖥️ Layout opens in <b>QGIS Layout Designer</b>.</li>
<li>👀 Review all elements — adjust if needed.</li>
<li>💾 <b>File → Export as PDF</b> or <b>Export as Image</b> (PNG/TIFF).</li>
</ol>

<h3>📄 Paper Size Reference (ISO 216)</h3>
<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;font-size:11px">
<tr style="background:#f5f5f5"><th>Size</th><th>Dimensions (mm)</th><th>Best for</th></tr>
<tr style="background:#e3f2fd"><td colspan="3"><b>A-series</b></td></tr>
<tr><td>A5</td><td>210 × 148</td><td>Field pocket maps</td></tr>
<tr><td>A4</td><td>297 × 210</td><td>Reports, desk reference</td></tr>
<tr><td>A3</td><td>420 × 297</td><td>Field operations, presentations</td></tr>
<tr><td>A2</td><td>594 × 420</td><td>Wall display, planning</td></tr>
<tr><td>A1</td><td>841 × 594</td><td>Large wall maps</td></tr>
<tr><td>A0</td><td>1189 × 841</td><td>Exhibition, official submissions</td></tr>
<tr style="background:#e8f5e9"><td colspan="3"><b>B-series</b> (larger than A at same number)</td></tr>
<tr><td>B5</td><td>250 × 176</td><td>Books, envelopes</td></tr>
<tr><td>B4</td><td>353 × 250</td><td>Newspapers, atlases</td></tr>
<tr><td>B3</td><td>500 × 353</td><td>Posters, large charts</td></tr>
<tr><td>B2</td><td>707 × 500</td><td>Large posters, wall maps</td></tr>
<tr><td>B1</td><td>1000 × 707</td><td>Very large wall displays</td></tr>
<tr><td>B0</td><td>1414 × 1000</td><td>Exhibition, architectural plans</td></tr>
</table>

<hr>
<table cellpadding="6" cellspacing="0" style="margin-top:8px">
<tr><td colspan="2"><b>👨‍💻 Author: Lộc Vũ Trung</b></td></tr>
<tr><td>📱 Zalo:</td><td>0913 191 178</td></tr>
<tr><td>🌐 Web:</td><td><a href="http://locvutrung.lvtcenter.it.com">locvutrung.lvtcenter.it.com</a></td></tr>
<tr><td>🎯 Expertise:</td><td><b>FSC/CoC</b> • <b>EUDR</b> • <b>QGIS</b> • <b>DATA</b> • <b>Webapp</b> • <b>Appsheet</b> • <b>Silviculture</b></td></tr>
</table>
<p style="color:#888;font-size:10px;margin-top:6px"><i>LVT Map Layout v2.0 — Designed for forestry &amp; environmental mapping.</i></p>"""

    def _help_text_vn(self):
        return """
<h2>🗺️ LVT Map Layout v2.0 — Hướng dẫn sử dụng</h2>

<h3>🔷 CHẾ ĐỘ KHUNG BẢN ĐỒ</h3>
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;margin-bottom:8px">
<tr style="background:#e3f2fd"><td><b>🖼️ Slide</b></td>
<td>Khung đơn giản, không viền — phù hợp trình chiếu, báo cáo, xuất nhanh.</td></tr>
<tr style="background:#e8f5e9"><td><b>🖨️ Print</b></td>
<td>Khung bản đồ chuyên nghiệp — khung viền nhiều lớp, lưới tọa độ,
thước tỷ lệ, khối tiêu đề, viện dẫn. Xuất bản đồ chuẩn (A5→A0).</td></tr>
</table>

<h3>📌 Bước 1 — Thiết lập chung (Tab General)</h3>
<ul>
<li>🔘 <b>Chế độ:</b> Chọn <b>Slide</b> hoặc <b>Print</b>.</li>
<li>🌐 <b>Ngôn ngữ:</b> EN (Tiếng Anh) hoặc VN (Tiếng Việt) — thay đổi toàn bộ nhãn trong khung.</li>
</ul>
<p><b>🖨️ Chế độ Print — các trường bổ sung:</b></p>
<ul>
<li>📝 <b>Tên bản đồ:</b> Tiêu đề chính hiển thị trong khối tiêu đề.</li>
<li>🏢 <b>Đơn vị:</b> Tên công ty / tổ chức xây dựng bản đồ.</li>
<li>📍 <b>Khu vực:</b> Tên khu vực nghiên cứu (tỉnh, huyện, xã, v.v.).</li>
<li>📚 <b>Viện dẫn:</b> Tiêu chuẩn kỹ thuật, vd: <i>TCVN 8211:2009</i>.</li>
</ul>
<p><b>👤 Trường chung (cả hai chế độ):</b></p>
<ul>
<li>✍️ <b>Người lập:</b> Tên người tạo bản đồ.</li>
<li>📅 <b>Ngày:</b> Ngày lập (tự điền ngày hôm nay).</li>
</ul>

<h3>📌 Bước 2 — Thiết lập bản đồ (Tab Map Settings)</h3>
<p><b>📐 Cách 1 — Khổ giấy chuẩn:</b></p>
<ul>
<li>📄 Chọn khổ giấy: <b>A5, A4, A3, A2, A1, A0</b>.</li>
<li>🔄 Chọn hướng: <b>Ngang</b> (Landscape) hoặc <b>Dọc</b> (Portrait).</li>
<li>Phạm vi bản đồ = toàn bộ canvas QGIS hiện tại.</li>
</ul>
<p><b>🖊️ Cách 2 — Vẽ phạm vi (Custom):</b></p>
<ol>
<li>Chọn <b>"Custom / Tự chọn"</b> ở dropdown Khổ giấy.</li>
<li>Bấm nút <b>"🖊 Draw Extent"</b> → vẽ hình chữ nhật trên bản đồ.</li>
<li>Hình chữ nhật vẽ = vùng nội dung bản đồ chính xác.</li>
<li>Plugin tự tính kích thước trang và đề xuất tỷ lệ chuẩn.</li>
<li>💡 Các tỷ lệ đề xuất hiện bên dưới (vd: 1:5.000 / 1:10.000 / 1:25.000).</li>
</ol>
<p><b>🔍 Tùy chọn tỷ lệ:</b></p>
<ul>
<li>☑ <b>Auto fit:</b> Tỷ lệ tự động điều chỉnh vừa trang.</li>
<li>☐ <b>Tự chọn:</b> Bỏ dấu "Auto fit" → nhập tỷ lệ cụ thể (vd: 1:10.000).</li>
</ul>

<h3>📌 Bước 3 — Nội dung (Tab Content)</h3>
<ul>
<li>📋 <b>Nguồn dữ liệu:</b> Liệt kê các nguồn dữ liệu bản đồ (ảnh vệ tinh, khảo sát, v.v.).</li>
<li>🧭 <b>Mũi tên Bắc:</b> Bật/tắt.</li>
<li>📏 <b>Thước tỷ lệ:</b> Bật/tắt (thước mét + thước độ/phút ở chế độ Print).</li>
<li>🗂️ <b>Chú giải:</b> Bật/tắt.</li>
</ul>

<h3>📌 Bước 4 — Tạo &amp; Xuất bản đồ</h3>
<ol>
<li>✅ Bấm <b>"Create Layout / Tạo khung"</b>.</li>
<li>🖥️ Khung bản đồ mở trong <b>QGIS Layout Designer</b>.</li>
<li>👀 Kiểm tra các thành phần — chỉnh sửa nếu cần.</li>
<li>💾 <b>File → Export as PDF</b> hoặc <b>Export as Image</b> (PNG/TIFF).</li>
</ol>

<h3>📄 Bảng khổ giấy tham khảo (ISO 216)</h3>
<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;font-size:11px">
<tr style="background:#f5f5f5"><th>Khổ</th><th>Kích thước (mm)</th><th>Phù hợp cho</th></tr>
<tr style="background:#e3f2fd"><td colspan="3"><b>Dòng A</b></td></tr>
<tr><td>A5</td><td>210 × 148</td><td>Bản đồ bỏ túi, thực địa</td></tr>
<tr><td>A4</td><td>297 × 210</td><td>Báo cáo, tài liệu tham khảo</td></tr>
<tr><td>A3</td><td>420 × 297</td><td>Thực địa, trình bày</td></tr>
<tr><td>A2</td><td>594 × 420</td><td>Treo tường, quy hoạch</td></tr>
<tr><td>A1</td><td>841 × 594</td><td>Bản đồ treo tường lớn</td></tr>
<tr><td>A0</td><td>1189 × 841</td><td>Triển lãm, nộp hồ sơ chính thức</td></tr>
<tr style="background:#e8f5e9"><td colspan="3"><b>Dòng B</b> (lớn hơn A cùng số)</td></tr>
<tr><td>B5</td><td>250 × 176</td><td>Sách, bìa thư</td></tr>
<tr><td>B4</td><td>353 × 250</td><td>Báo, tập bản đồ</td></tr>
<tr><td>B3</td><td>500 × 353</td><td>Poster, biểu đồ lớn</td></tr>
<tr><td>B2</td><td>707 × 500</td><td>Poster lớn, bản đồ treo tường</td></tr>
<tr><td>B1</td><td>1000 × 707</td><td>Trưng bày cỡ rất lớn</td></tr>
<tr><td>B0</td><td>1414 × 1000</td><td>Triển lãm, bản vẽ kiến trúc</td></tr>
</table>

<hr>
<table cellpadding="6" cellspacing="0" style="margin-top:8px">
<tr><td colspan="2"><b>👨‍💻 Tác giả: Lộc Vũ Trung</b></td></tr>
<tr><td>📱 Zalo:</td><td>0913 191 178</td></tr>
<tr><td>🌐 Web:</td><td><a href="http://locvutrung.lvtcenter.it.com">locvutrung.lvtcenter.it.com</a></td></tr>
<tr><td>🎯 Phạm vi:</td><td><b>FSC/CoC</b> • <b>EUDR</b> • <b>QGIS</b> • <b>DATA</b> • <b>Webapp</b> • <b>Appsheet</b> • <b>Silviculture</b></td></tr>
</table>
<p style="color:#888;font-size:10px;margin-top:6px"><i>LVT Map Layout v2.0 — Thiết kế cho bản đồ lâm nghiệp &amp; môi trường.</i></p>"""


    # ── CRS Library Text ─────────────────────────────────────────

    def _crs_text_en(self):
        return """
<h2>🌐 CRS Library — Coordinate Reference Systems for Vietnam</h2>
<p>Quick reference for EPSG codes commonly used in forestry & environmental mapping in Vietnam.</p>

<h3>🔵 Global / WGS 84</h3>
<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;font-size:11px;width:100%">
<tr style="background:#e3f2fd"><th>EPSG</th><th>Name</th><th>Type</th><th>Description</th></tr>
<tr><td><b>4326</b></td><td>WGS 84</td><td>Geographic</td><td>Global standard (GPS). Lat/Lon in degrees. Used by Google Earth, OpenStreetMap.</td></tr>
<tr><td><b>32648</b></td><td>WGS 84 / UTM zone 48N</td><td>Projected</td><td>Western Vietnam (west of 108°E). Meters. Good for area calculations.</td></tr>
<tr><td><b>32649</b></td><td>WGS 84 / UTM zone 49N</td><td>Projected</td><td>Eastern Vietnam (east of 108°E). Meters.</td></tr>
</table>

<h3>🟢 VN-2000 — National 6° Zones (Toàn quốc)</h3>
<p>Used for national-scale mapping. Based on WGS 84 ellipsoid, Transverse Mercator projection.</p>
<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;font-size:11px;width:100%">
<tr style="background:#e8f5e9"><th>EPSG</th><th>Name</th><th>Central Meridian</th><th>Coverage</th></tr>
<tr><td><b>3405</b></td><td>VN-2000 / UTM zone 48N</td><td>105°E</td><td>Western Vietnam (west of 108°E)</td></tr>
<tr><td><b>3406</b></td><td>VN-2000 / UTM zone 49N</td><td>111°E</td><td>Eastern Vietnam (east of 108°E)</td></tr>
</table>

<h3>🟡 VN-2000 — Provincial 3° Zones (Tỉnh)</h3>
<p>Used for large-scale cadastral & engineering mapping. Each province is assigned a specific central meridian.</p>
<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;font-size:11px;width:100%">
<tr style="background:#fff9c4"><th>EPSG</th><th>Central Meridian</th><th>Provinces / Areas</th></tr>
<tr><td><b>9205</b></td><td>103°00'</td><td>Điện Biên, Lai Châu</td></tr>
<tr><td><b>9206</b></td><td>104°00'</td><td>Sơn La, Hà Giang (partial)</td></tr>
<tr><td><b>9207</b></td><td>104°30'</td><td>Lào Cai, Yên Bái</td></tr>
<tr><td><b>9208</b></td><td>104°45'</td><td>Tuyên Quang, Phú Thọ, Hòa Bình</td></tr>
<tr><td><b>5896</b></td><td>105°00'</td><td>Hà Nội, Bắc Giang, Thái Nguyên, Lạng Sơn</td></tr>
<tr><td><b>9209</b></td><td>105°30'</td><td>Bắc Ninh, Hải Dương, Hưng Yên, Nam Định, Thái Bình, Hà Tĩnh, Sóc Trăng, Tây Ninh, Trà Vinh, Vĩnh Long</td></tr>
<tr><td><b>9210</b></td><td>105°45'</td><td>Hải Phòng, TP.HCM, Bình Dương, Cao Bằng, Long An, Tiền Giang, Bến Tre</td></tr>
<tr><td><b>9211</b></td><td>106°00'</td><td>Quảng Ninh, Ninh Bình, Thanh Hóa</td></tr>
<tr><td><b>9212</b></td><td>106°15'</td><td>Nghệ An (partial)</td></tr>
<tr><td><b>9213</b></td><td>106°30'</td><td>Quảng Bình, Quảng Trị</td></tr>
<tr><td><b>5899</b></td><td>107°45'</td><td>Đà Nẵng, Thừa Thiên Huế, Quảng Nam</td></tr>
<tr><td><b>9214</b></td><td>107°00'</td><td>Kon Tum, Gia Lai (partial)</td></tr>
<tr><td><b>9216</b></td><td>107°30'</td><td>Đắk Lắk, Đắk Nông, Lâm Đồng</td></tr>
<tr><td><b>9217</b></td><td>108°15'</td><td>Quảng Ngãi, Bình Định, Phú Yên</td></tr>
<tr><td><b>9218</b></td><td>108°30'</td><td>Khánh Hòa, Ninh Thuận, Bình Thuận</td></tr>
</table>

<h3>💡 How to Choose?</h3>
<ul>
<li>📍 <b>GPS / web mapping:</b> EPSG:4326 (WGS 84)</li>
<li>📐 <b>Area/distance calculations:</b> EPSG:32648 or 32649 (UTM)</li>
<li>🗺️ <b>National maps:</b> EPSG:3405 or 3406 (VN-2000 / 6°)</li>
<li>📏 <b>Cadastral / provincial:</b> Use the 3° zone matching your province</li>
</ul>
<p style="color:#888;font-size:10px"><i>Source: EPSG Registry (epsg.io) — MONRE Vietnam</i></p>"""

    def _crs_text_vn(self):
        return """
<h2>🌐 Thư viện Hệ tọa độ — CRS cho Việt Nam</h2>
<p>Tra cứu nhanh mã EPSG thường dùng trong lâm nghiệp & môi trường tại Việt Nam.</p>

<h3>🔵 Toàn cầu / WGS 84</h3>
<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;font-size:11px;width:100%">
<tr style="background:#e3f2fd"><th>EPSG</th><th>Tên</th><th>Loại</th><th>Mô tả</th></tr>
<tr><td><b>4326</b></td><td>WGS 84</td><td>Địa lý</td><td>Tiêu chuẩn toàn cầu (GPS). Tọa độ Lat/Lon tính bằng độ. Google Earth, OpenStreetMap.</td></tr>
<tr><td><b>32648</b></td><td>WGS 84 / UTM zone 48N</td><td>Phép chiếu</td><td>Tây Việt Nam (phía tây 108°E). Đơn vị: mét.</td></tr>
<tr><td><b>32649</b></td><td>WGS 84 / UTM zone 49N</td><td>Phép chiếu</td><td>Đông Việt Nam (phía đông 108°E). Đơn vị: mét.</td></tr>
</table>

<h3>🟢 VN-2000 — Múi 6° (Toàn quốc)</h3>
<p>Dùng cho bản đồ quy mô quốc gia. Dựa trên ellipsoid WGS 84, phép chiếu Transverse Mercator.</p>
<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;font-size:11px;width:100%">
<tr style="background:#e8f5e9"><th>EPSG</th><th>Tên</th><th>Kinh tuyến trục</th><th>Phạm vi</th></tr>
<tr><td><b>3405</b></td><td>VN-2000 / UTM zone 48N</td><td>105°E</td><td>Tây Việt Nam (phía tây 108°E)</td></tr>
<tr><td><b>3406</b></td><td>VN-2000 / UTM zone 49N</td><td>111°E</td><td>Đông Việt Nam (phía đông 108°E)</td></tr>
</table>

<h3>🟡 VN-2000 — Múi 3° (Tỉnh)</h3>
<p>Dùng cho bản đồ địa chính & kỹ thuật tỷ lệ lớn. Mỗi tỉnh được gán một kinh tuyến trục riêng.</p>
<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;font-size:11px;width:100%">
<tr style="background:#fff9c4"><th>EPSG</th><th>Kinh tuyến trục</th><th>Tỉnh / Khu vực</th></tr>
<tr><td><b>9205</b></td><td>103°00'</td><td>Điện Biên, Lai Châu</td></tr>
<tr><td><b>9206</b></td><td>104°00'</td><td>Sơn La, Hà Giang (một phần)</td></tr>
<tr><td><b>9207</b></td><td>104°30'</td><td>Lào Cai, Yên Bái</td></tr>
<tr><td><b>9208</b></td><td>104°45'</td><td>Tuyên Quang, Phú Thọ, Hòa Bình</td></tr>
<tr><td><b>5896</b></td><td>105°00'</td><td>Hà Nội, Bắc Giang, Thái Nguyên, Lạng Sơn</td></tr>
<tr><td><b>9209</b></td><td>105°30'</td><td>Bắc Ninh, Hải Dương, Hưng Yên, Nam Định, Thái Bình, Hà Tĩnh, Sóc Trăng, Tây Ninh, Trà Vinh, Vĩnh Long</td></tr>
<tr><td><b>9210</b></td><td>105°45'</td><td>Hải Phòng, TP.HCM, Bình Dương, Cao Bằng, Long An, Tiền Giang, Bến Tre</td></tr>
<tr><td><b>9211</b></td><td>106°00'</td><td>Quảng Ninh, Ninh Bình, Thanh Hóa</td></tr>
<tr><td><b>9212</b></td><td>106°15'</td><td>Nghệ An (một phần)</td></tr>
<tr><td><b>9213</b></td><td>106°30'</td><td>Quảng Bình, Quảng Trị</td></tr>
<tr><td><b>5899</b></td><td>107°45'</td><td>Đà Nẵng, Thừa Thiên Huế, Quảng Nam</td></tr>
<tr><td><b>9214</b></td><td>107°00'</td><td>Kon Tum, Gia Lai (một phần)</td></tr>
<tr><td><b>9216</b></td><td>107°30'</td><td>Đắk Lắk, Đắk Nông, Lâm Đồng</td></tr>
<tr><td><b>9217</b></td><td>108°15'</td><td>Quảng Ngãi, Bình Định, Phú Yên</td></tr>
<tr><td><b>9218</b></td><td>108°30'</td><td>Khánh Hòa, Ninh Thuận, Bình Thuận</td></tr>
</table>

<h3>💡 Chọn hệ tọa độ nào?</h3>
<ul>
<li>📍 <b>GPS / bản đồ web:</b> EPSG:4326 (WGS 84)</li>
<li>📐 <b>Tính diện tích / khoảng cách:</b> EPSG:32648 hoặc 32649 (UTM)</li>
<li>🗺️ <b>Bản đồ toàn quốc:</b> EPSG:3405 hoặc 3406 (VN-2000 / 6°)</li>
<li>📏 <b>Địa chính / cấp tỉnh:</b> Tra múi 3° theo tỉnh ở bảng trên</li>
</ul>
<p style="color:#888;font-size:10px"><i>Nguồn: EPSG Registry (epsg.io) — Bộ TN&MT Việt Nam</i></p>"""

    # ── Collect Parameters ───────────────────────────────────────

    def _collect_params(self):
        """Gather all UI values into a dict for the engine."""
        mode = MODE_PRINT if self.rad_print.isChecked() else MODE_SLIDE
        lang = "EN" if self.cmb_lang.currentIndex() == 0 else "VN"

        paper_key = self.cmb_paper.currentText()
        is_custom = paper_key == "Custom / Tự chọn"
        drawn_extent = getattr(self, "drawn_extent", None)

        if is_custom:
            pw = self.spn_custom_w.value()
            ph = self.spn_custom_h.value()
        else:
            pw, ph = PAPER_SIZES[paper_key]
            # Only apply orientation swap for standard paper sizes
            if self.rad_portrait.isChecked():
                pw, ph = ph, pw

        return {
            "mode": mode,
            "lang": lang,
            "title": self.txt_title.text().strip(),
            "org_name": self.txt_org.text().strip(),
            "study_area": self.txt_study.text().strip(),
            "references": self.txt_refs.text().strip(),
            "author": self.txt_author.text().strip(),
            "date": self.txt_date.text().strip(),
            "page_width": pw,
            "page_height": ph,
            "auto_scale": self.chk_auto_scale.isChecked(),
            "scale": self.spn_scale.value(),
            "extent_mode": "drawn" if (is_custom and drawn_extent) else "canvas",
            "drawn_extent": drawn_extent,
            "data_sources": self.txt_sources.toPlainText().strip(),
            "show_legend": self.chk_legend.isChecked(),
            "show_north": self.chk_north.isChecked(),
            "show_scalebar": self.chk_scalebar.isChecked(),
        }

    # ── Actions ──────────────────────────────────────────────────

    def _on_create(self):
        """Generate layout and open in QGIS layout designer."""
        params = self._collect_params()

        # Validation
        if params["extent_mode"] == "drawn" and not params["drawn_extent"]:
            QMessageBox.warning(
                self, "LVT",
                "Please draw an extent first using the 'Draw Extent' button."
            )
            return

        # Disable button + show wait cursor (no modal dialog to avoid freeze)
        self.btn_create.setEnabled(False)
        self.btn_create.setText("⏳ Creating... / Đang tạo...")
        from qgis.PyQt.QtWidgets import QApplication
        QApplication.setOverrideCursor(Qt.WaitCursor)
        QApplication.processEvents()

        try:
            layout = self.engine.create_layout(params)
            designer = self.iface.openLayoutDesigner(layout)
            try:
                designer.view().zoomFull()
            except Exception:
                pass
            self.iface.messageBar().pushSuccess(
                "LVT", "✅ Layout created! / Đã tạo khung!"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            QApplication.restoreOverrideCursor()
            self.btn_create.setEnabled(True)
            self.btn_create.setText("Create Layout / Tạo khung")
