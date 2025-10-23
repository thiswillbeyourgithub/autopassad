# AutoPassAd

A (hopefully) cross-platform Python script that automatically detects "continue" text on screen and simulates mouse clicks.

*This project was developed with assistance from [aider.chat](https://github.com/Aider-AI/aider/).*

## Features

- Takes screenshots around mouse cursor at configurable intervals
- Dual OCR engine support:
  - EasyOCR (primary, more accurate, GPU-accelerated when available)
  - Tesseract OCR (fallback, always available)
- Fuzzy text matching to detect "continue" text
- Automatic mouse clicking when text is found
- Cross-platform support (tested on Linux and macOS, not on Windows)
- Configurable parameters via command line
- Performance optimizations for low CPU usage

## Requirements

- Python 3.13+ (probably works on older versions but more recent python versions are faster)
- Tesseract OCR engine (required)
- EasyOCR (optional but recommended for better accuracy and GPU acceleration)

## Installation

**Note:** The installation instructions below are LLM-generated and have not been fully tested across all platforms. Please report any issues you encounter.

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Tesseract OCR engine

### Step 1: Verify Python Installation

Check that Python 3.7+ is installed:

```bash
python --version
# or
python3 --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/)

### Step 2: Install Tesseract OCR

Tesseract is a critical dependency and must be properly installed and configured.

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

Verify installation:
```bash
tesseract --version
```

#### macOS

Using Homebrew (recommended):
```bash
brew install tesseract
```

Verify installation:
```bash
tesseract --version
```

**Note:** On Apple Silicon (M1/M2/M3) Macs, Homebrew installs to `/opt/homebrew/bin/` by default, which should already be in your PATH.

#### Windows

1. **Download Tesseract:**
   - Go to https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest installer (e.g., `tesseract-ocr-w64-setup-5.3.X.XXXXXXXX.exe`)
   - Run the installer

2. **Important: Note the installation path** (default is usually `C:\Program Files\Tesseract-OCR`)

3. **Add Tesseract to PATH:**

   **Option A - During Installation (Recommended):**
   - When installing, check the box "Add to PATH" if available

   **Option B - Manual PATH Configuration:**
   - Open "Environment Variables":
     - Press `Win + X` and select "System"
     - Click "Advanced system settings"
     - Click "Environment Variables"
   - Under "System variables", find and select "Path", then click "Edit"
   - Click "New" and add the Tesseract installation path:
     ```
     C:\Program Files\Tesseract-OCR
     ```
   - Click "OK" on all dialogs
   - **Restart your command prompt/terminal** for changes to take effect

4. **Verify installation:**

   Open a **new** command prompt and run:
   ```cmd
   tesseract --version
   ```

   If you get an error like `'tesseract' is not recognized`, the PATH is not configured correctly. Double-check steps above.

### Step 3: Set Up Python Virtual Environment (Recommended)

Using a virtual environment prevents dependency conflicts:

**Linux/macOS:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

**Windows:**
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

You should see `(venv)` in your command prompt when activated.

### Step 4: Install AutoPassAd

With your virtual environment activated, you have several installation options depending on which OCR backend you want to use:

**Option 1: Install with both OCR backends (Recommended)**
```bash
pip install -e .[all]
```

**Option 2: Install with pytesseract only (lighter weight)**
```bash
pip install -e .[pytesseract]
```

**Option 3: Install with easyocr only (more accurate, GPU-accelerated)**
```bash
pip install -e .[easyocr]
```

**About OCR backends:**
- **pytesseract**: Faster, lighter weight, requires tesseract binary (installed in Step 2)
- **easyocr**: More accurate, GPU-accelerated when available, but heavier dependencies
- **all**: Installs both backends (recommended) - tool will prefer easyocr but fall back to pytesseract

**Note:** EasyOCR will download language models on first run (~100MB for English). If EasyOCR is not installed or fails to load, the tool will automatically fall back to using Tesseract OCR.

**GPU Support:**
- EasyOCR can use GPU acceleration if you have CUDA-compatible hardware and drivers installed
- Without GPU, EasyOCR will still work but will be slower than Tesseract
- The tool will automatically detect and use GPU if available

### Step 5: Verify Installation

After installation, you can use the `autopassad` command directly:

```bash
autopassad --help
```

You should see the help message without any errors.

**Check OCR Engine:**
When you run the tool, it will print a message indicating which OCR engine is being used:
- If EasyOCR is installed: It will use EasyOCR by default
- If EasyOCR is not available: You'll see "Warning: easyocr not available, will use pytesseract only"

### Installation Troubleshooting

#### "tesseract is not installed or it's not in your PATH"

**Linux/macOS:**
- Verify Tesseract is installed: `which tesseract`
- If not found, reinstall Tesseract
- Try running with full path: `/usr/bin/tesseract --version`
- On macos use homebrew to install tesseract: `brew install tesseract`

**Windows:**
- Ensure Tesseract is added to PATH (see Step 2.3 above)
- Restart your terminal/command prompt after modifying PATH
- Verify with: `where tesseract` (should show the installation path)
- If still not working, you can set the path directly in your environment:
  ```cmd
  set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
  ```

#### "No module named 'PIL'" or similar import errors

- Ensure your virtual environment is activated
- Reinstall the package: `pip install -e .[all]`
- If still failing, try upgrading pip: `pip install --upgrade pip`

#### Permission errors on macOS

The tool requires accessibility permissions to control the mouse:
1. Go to System Preferences → Security & Privacy → Privacy
2. Select "Accessibility" from the left panel
3. Click the lock icon and authenticate
4. Add Terminal (or your IDE) to the list
5. Restart your terminal/IDE

#### Virtual environment issues

If `python3 -m venv venv` fails:
- **Ubuntu/Debian:** Install venv: `sudo apt-get install python3-venv`
- **Other systems:** Ensure Python was installed with pip and venv support

### Deactivating Virtual Environment

When you're done using the tool:

```bash
deactivate
```

## Usage

After installation via setup.py, you can use the `autopassad` command directly from anywhere in your terminal.

### Basic Usage
```bash
autopassad
```

### With Custom Parameters
```bash
# Custom interval (2 seconds between screenshots)
autopassad --interval 2.0

# Custom rectangle size (100px vertical x 250px horizontal around cursor)
autopassad --rect-size 100x250

# Custom similarity threshold (90% match required)
autopassad --threshold 90

# Custom target word
autopassad --target-word "next"

# Enable verbose output with timing information
autopassad --verbose

# All parameters combined
autopassad --interval 0.5 --rect-size 50x200 --threshold 85 --target-word "continue" --verbose
```

**Alternative:** If you haven't installed via setup.py, you can still run directly:
```bash
python autopassad.py --help
```

### Command Line Options

- `--interval, -i`: Time between screenshots in seconds (default: 1.0)
- `--rect-size, -r`: Size of rectangle around cursor in VERTICALxHORIZONTAL format (default: 70x170)
- `--threshold, -t`: Minimum similarity threshold for text matching (default: 80)
- `--target-word, -w`: Target word to search for in OCR text (default: "continue")
- `--verbose, -v`: Enable verbose output with timing information
- `--help, -h`: Show help message

## How It Works

1. Captures a screenshot of a rectangle around the mouse cursor
2. Applies performance optimizations:
   - Skips blank images (low pixel variance)
   - Detects and skips duplicate screenshots using perceptual hashing
   - Converts to grayscale and applies binary threshold for faster OCR
3. Performs OCR to extract text from the screenshot:
   - **Primary engine**: EasyOCR (more accurate, GPU-accelerated when available)
   - **Fallback engine**: Tesseract OCR (with legacy engine optimization when available)
   - Automatically falls back to Tesseract if EasyOCR is not installed or fails
4. Uses rapidfuzz to check if any word matches the target word with the specified similarity threshold
5. Simulates a mouse click if a match is found
6. Repeats at the specified interval

### Performance Optimizations

The tool includes several optimizations to minimize CPU usage and improve responsiveness:
- **Blank image detection**: Skips OCR on mostly uniform images
- **Duplicate detection**: Uses perceptual hashing to avoid processing the same image multiple times
- **Image preprocessing**: Converts to grayscale and applies binary threshold to simplify OCR
- **Dual OCR engine support**: Uses EasyOCR for accuracy, falls back to Tesseract for reliability
- **OCR engine optimization**: Uses legacy Tesseract engine (--oem 0) when available for faster processing
- **Character whitelisting**: Limits recognition to alphabetic characters only (Tesseract)
- **GPU acceleration**: Leverages GPU when available with EasyOCR

## Troubleshooting

### Tesseract Not Found
If you get a "tesseract not found" error:
- Make sure Tesseract is installed and in your PATH
- On Windows, you may need to add the Tesseract installation directory to your PATH

### Permission Issues (macOS)
On macOS, you may need to grant accessibility permissions:
1. Go to System Preferences > Security & Privacy > Privacy
2. Select "Accessibility" from the left panel
3. Add Terminal or your Python executable to the list

### Low Detection Accuracy
If the tool isn't detecting text properly:
- Install EasyOCR for better accuracy: `pip install easyocr`
- Increase the rectangle size with `--rect-size` (e.g., `--rect-size 100x300` for a taller/wider area)
- Lower the similarity threshold with `--threshold`
- Ensure the text is clear and readable in the screenshot area
- Try enabling `--verbose` to see timing information and detected text

### EasyOCR Issues
If you encounter issues with EasyOCR:
- The tool will automatically fall back to Tesseract
- Check GPU drivers if you want to use GPU acceleration
- EasyOCR requires ~100MB download for language models on first run
- You can uninstall EasyOCR if needed: `pip uninstall easyocr`

## License

This project is open source and available under the MIT License.
