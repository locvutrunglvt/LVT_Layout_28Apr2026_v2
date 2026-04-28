# LVT Map Layout — QGIS Plugin

## Overview
Automated map layout generator using professional LVT print templates.  
Supports **English** and **Vietnamese**, paper sizes **A5→A0**, and batch export via **Atlas**.

## Features
- **Preserves 100% template design** — colors, line styles, fonts, data-defined positions
- **Responsive layout** — scalebars, labels, coordinates auto-adjust per paper size
- **5-tab dialog**: General, Map Settings, Content, Export, Batch/Atlas
- **Export formats**: PDF, PNG, SVG at 150/300/600 DPI
- **Atlas batch**: One map per polygon feature → bulk export

## Installation

### Option 1: Symlink (recommended for development)
```powershell
# Run PowerShell as Administrator
cd "C:\Users\User\OneDrive - Slow Forest\Apps\2026\GIS\Layout_LVT"
.\install.ps1
```

### Option 2: Manual copy
Copy the entire `Layout_LVT` folder to:
```
%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\
```

Then in QGIS: **Plugins → Manage and Install Plugins → Enable "LVT Map Layout"**

## Usage

1. Click **LVT Map Layout** button in toolbar (or Plugins menu)
2. Fill in the tabs:
   - **General**: Language, Title, Study Area, Organization, Author, Date
   - **Map Settings**: Paper size, orientation, scale, extent
   - **Content**: Data sources, toggle legend/north/scalebar/grid/coordinates
   - **Export**: Format (PDF/PNG/SVG), DPI, output directory
   - **Batch/Atlas**: Enable atlas, select coverage layer + name field
3. Click **Preview Layout** to review in QGIS Designer
4. Click **Export** to generate files

## Template Element IDs

| Element | EN ID | VN ID |
|---------|-------|-------|
| Map | `Map` | `Map` |
| Title | `Map title` | `Tên bản đồ` |
| Study Area | `Study area` | `Khu vực bản đồ` |
| Organization | `Map org name` | `Tên dv xd bản đồ` |
| Scale Bar | `Scale meter` | `Scale mét` |
| References | `References` | `Viện dẫn` |
| Map Data | `Map data` | `Dữ liệu bản đồ` |
| Main Frame | `Main frame` | `Khung tổng` |

## Compatibility
- QGIS 3.28 LTR and above
- Windows, macOS, Linux
