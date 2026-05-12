# ROI (Region of Interest) Functionality

## Overview

The ROI module provides comprehensive local image analysis and processing within user-selected rectangular regions. Instead of processing the entire image, users can now select specific areas and apply targeted operations.

## Features

### 1. **ROI Selection**
- **User Action**: Click the ROI button in the toolbar, then drag a rectangle on the image
- **Result**: Selected region is highlighted with a dashed cyan border
- **Coordinates**: Saved in original image pixel coordinates (handles scaling/panning)

### 2. **Comprehensive Statistics**
When a region is selected, the ROI dialog displays:

#### Pixel Intensity Statistics
- **Mean**: Average pixel intensity
- **Std Dev**: Standard deviation (measure of contrast/variation)
- **Min**: Minimum intensity value (0-255)
- **Max**: Maximum intensity value (0-255)
- **Median**: Middle value of intensity distribution
- **Entropy**: Shannon entropy (measure of disorder/detail level)
- **Pixels**: Total number of pixels in ROI

#### Visual Display
- **ROI Preview**: Scaled preview of the extracted region
- **Histogram**: 256-bin histogram showing intensity distribution
- Color-coded statistics for easy reading

### 3. **Local Operations**

#### A. Local Histogram Equalization
```
Operation: Equalize ROI
Effect: Improves contrast within the ROI region only
Use Case: Enhance detail in dark or bright regions
Block Size: Auto-calculated based on ROI size
Result: Better visibility of features within ROI
```

#### B. Median Filtering
```
Operation: Median ROI
Effect: Noise reduction using 3x3 median kernel
Use Case: Remove salt-and-pepper noise from specific regions
Kernel: 3×3 neighborhood
Result: Smoothed region while preserving edges
```

#### C. ROI Extraction
```
Operation: Extract ROI
Effect: Isolates the ROI region as a standalone image
Use Case: Further analysis or comparison of extracted region
Result: Current working image becomes the extracted ROI
```

## Implementation Details

### Statistics Computation (`app/DIP/roi_stats.py`)

```python
def compute_roi_stats(img: np.ndarray, x1: int, y1: int, x2: int, y2: int) -> dict
```

**Returns Dictionary with:**
- `roi_array`: Extracted ROI as uint8 2D grayscale array
- `hist`: 256-bin histogram
- `mean`: Mean pixel intensity
- `std`: Standard deviation
- `min`: Minimum pixel value
- `max`: Maximum pixel value
- `median`: Median pixel value
- `entropy`: Shannon entropy in bits
- `area`: Number of pixels

**Key Features:**
- Automatic color-to-grayscale conversion (Rec. 601 coefficients)
- Handles edge cases (empty ROI, single pixel)
- All computations from scratch (no library dependencies)

### ROI Dialog (`app/gui/roi_dialog.py`)

**Class: ROIStatsDialog**
- Displays statistics grid with formatted values
- Renders scaled ROI preview
- Shows 256-bin histogram visualization
- Provides operation buttons for local processing
- Supports custom callback for operation handling

### Signal Handling (`app/gui/signal_handlers.py`)

**Methods:**
- `on_roi_selected(x1, y1, x2, y2)`: Entry point when ROI is drawn
- `_on_roi_operation(op_id, stats)`: Dispatch handler for operations

**Workflow:**
1. User draws ROI on canvas
2. `on_roi_selected()` is triggered by ROIImageCanvas signal
3. Statistics are computed
4. ROIStatsDialog is displayed with stats and operation buttons
5. User clicks an operation button
6. `_on_roi_operation()` processes the image
7. Result is committed to history (undo/redo available)

## User Workflow

### Step 1: Select ROI Mode
- Click the ROI button in the toolbar (left panel)
- Button toggles ROI selection mode on/off

### Step 2: Draw ROI
- Drag a rectangle on the image
- See live dashed border showing selection
- Release mouse to finalize

### Step 3: Review Statistics
- ROI Statistics dialog opens automatically
- View:
  - Extracted region preview
  - Intensity statistics
  - Histogram visualization

### Step 4: Apply Operation (Optional)
- Click one of three buttons:
  - **Equalize ROI**: Improve contrast in region
  - **Median ROI**: Reduce noise in region
  - **Extract ROI**: Isolate region as new image
- Dialog closes and operation is applied
- Result is added to undo/redo history

### Step 5: Continue Editing
- ROI mode is automatically disabled after operation
- Use Undo (Ctrl+Z) to revert operation
- Select ROI again to analyze different region

## Code Architecture

### File Structure
```
app/
├── DIP/
│   └── roi_stats.py           # Statistics computation
├── gui/
│   ├── roi_dialog.py          # ROI statistics dialog UI
│   ├── signal_handlers.py     # ROI event handling
│   └── widgets.py             # ROIImageCanvas (draw ROI)
```

### Signal Flow
```
User draws ROI on canvas
         ↓
ROIImageCanvas.roi_selected(x1, y1, x2, y2) signal
         ↓
SignalHandlers.on_roi_selected()
         ↓
compute_roi_stats() → dict with stats
         ↓
ROIStatsDialog(stats_dict, on_apply_callback)
         ↓
User clicks operation button
         ↓
_on_roi_operation(op_id, stats)
         ↓
Process image, call commit_phase2_result()
         ↓
Result added to undo/redo history
```

## Statistics Computation Methods

All statistics are computed from scratch (no NumPy methods like `.mean()`, `.std()`, etc.):

### Mean
```
mean = Σ(i × hist[i]) / total_pixels
```

### Standard Deviation
```
variance = Σ((i - mean)² × hist[i]) / total_pixels
std_dev = √variance
```

### Median
```
Find intensity level where cumulative histogram ≥ 50% of pixels
```

### Entropy
```
entropy = -Σ(p[i] × log₂(p[i]))  for p[i] > 0
```

## Integration Points

### With Image Processing Pipeline
- Operations use existing filters (histogram equalization, median filtering)
- Results integrate seamlessly with undo/redo system
- Partial image updates (only ROI affected)

### With UI Canvas
- ROI selection layer (dashed cyan border)
- Pan/zoom aware (coordinates auto-scaled)
- Visual feedback during selection

### With History System
- Each ROI operation creates history entry
- Undo/Redo work correctly with ROI operations
- Original image preserved until changes committed

## Performance Notes

- ROI statistics computed immediately (< 100ms for 256×256 regions)
- Local operations faster than full-image operations
- Dialog rendering optimized with scaled previews

## Future Enhancements

Possible extensions:
- Multiple ROI regions (list of statistics)
- ROI save/load (store selected regions)
- Custom local operations (adaptive filtering, edge detection on ROI)
- ROI-based image segmentation
- Region mask export
- ROI comparison (statistics across multiple regions)

## Testing

Run tests:
```bash
python test_roi.py           # Statistics computation
python test_roi_workflow.py  # Dialog and integration
python test_roi_ops.py       # All operations
```

All tests verify:
- ✓ Statistics accuracy
- ✓ Dialog UI creation
- ✓ Operation callbacks
- ✓ Preview rendering
- ✓ Local histogram equalization
- ✓ Median filtering
- ✓ ROI extraction

## Troubleshooting

### ROI Dialog Doesn't Open
- Check that image is loaded
- Verify ROI bounds are positive integers
- Check for errors in console

### Statistics Show 0 Values
- ROI might be outside image bounds
- ROI size might be too small (< 1 pixel)
- Image might not be loaded

### Operations Don't Change Image
- Verify "changed image" in commit was true
- Check that operation is not a no-op (e.g., median on uniform region)
- Verify undo/redo history reflects change

## Summary

ROI functionality transforms the application from global image processing to **targeted local analysis and enhancement**. Users can now:
- Analyze specific regions statistically
- Apply filters selectively
- Extract and isolate areas for further work
- Maintain full undo/redo capability for all operations

The modular design makes ROI operations easy to extend with custom analyses and filters.
