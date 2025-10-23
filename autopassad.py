#!/usr/bin/env python3
"""
AutoPassAd
Takes screenshots around mouse cursor, performs OCR, and clicks when "continue" text is found.
"""

import time
import argparse
import sys
from PIL import Image, ImageGrab
from pynput import mouse
import pytesseract
import easyocr
from rapidfuzz import fuzz
import imagehash
from collections import deque


class AutoPassAd:
    def __init__(
        self,
        interval=1.0,
        rect_size=(70, 170),
        similarity_threshold=80,
        target_word="continue",
        verbose=False,
    ):
        """
        Initialize autopassad.

        Args:
            interval (float): Time between screenshots in seconds
            rect_size (tuple): Size of rectangle around cursor (vertical, horizontal) in pixels
            similarity_threshold (int): Minimum similarity score for text matching
            target_word (str): The word to search for in OCR text
            verbose (bool): Enable verbose output with timing information
        """
        self.interval = interval
        self.rect_size = rect_size  # (vertical, horizontal)
        self.similarity_threshold = similarity_threshold
        self.target_word = target_word.lower()
        self.mouse_controller = mouse.Controller()
        self.verbose = verbose
        # Track which OCR engine to use (try easyocr first, fall back to tesseract if needed)
        self.use_easyocr = True
        self.easyocr_reader = None  # Lazy initialization on first use
        # Store last 3 image hashes for duplicate detection (deque provides O(1) operations)
        self.recent_image_hashes = deque(maxlen=3)

    def get_cursor_position(self):
        """Get current mouse cursor position."""
        return self.mouse_controller.position

    def capture_screenshot_around_cursor(self):
        """Capture screenshot in rectangle around mouse cursor."""
        x, y = self.get_cursor_position()

        # Calculate rectangle bounds using separate vertical and horizontal sizes
        vertical_size, horizontal_size = self.rect_size
        half_vertical = vertical_size // 2
        half_horizontal = horizontal_size // 2

        left = max(0, x - half_horizontal)
        top = max(0, y - half_vertical)
        right = x + half_horizontal
        bottom = y + half_vertical

        # Capture screenshot of the region
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        return screenshot

    def extract_text_from_image(self, image):
        """
        Extract text from image using OCR with performance optimizations.

        OCR engine selection:
        - Try EasyOCR first (more accurate, GPU-accelerated if available)
        - Fall back to Tesseract if EasyOCR fails or is unavailable

        Optimizations applied:
        - Skip blank images (low pixel variance)
        - Skip duplicate images using perceptual hashing
        - Convert to grayscale to reduce processing complexity
        - Apply binary threshold to simplify the image
        - For Tesseract: Use legacy OCR engine (--oem 0) for faster processing, with fallback to default
        - For Tesseract: Use single line PSM mode (--psm 7) since we're looking for a single word
        - For Tesseract: Whitelist only alphabetic characters to reduce recognition complexity
        """
        try:
            # Start timing preprocessing
            preprocess_start = time.time()

            # Quick check: skip if image is mostly blank (performance optimization)
            # Calculate standard deviation of pixel values using low-memory method
            # Low std dev indicates uniform image (likely blank)
            import numpy as np

            pixels = np.array(image)
            if pixels.std() < 10:  # Very low variance = likely blank
                return "", None

            # Convert to grayscale to reduce processing time (3x less data)
            image = image.convert("L")

            # Quick duplicate detection using perceptual hash (very fast)
            # Perceptual hash is robust to minor changes but detects true duplicates
            current_hash = imagehash.phash(image, hash_size=8)

            # Check if current image is same as any of the last 3 images
            # Hash difference of 0 means identical or near-identical images
            for recent_hash in self.recent_image_hashes:
                if (
                    current_hash - recent_hash <= 1
                ):  # Allow 1 bit difference for minor variations
                    return "", None  # Skip OCR on duplicate image

            # Apply binary threshold to make text clearer and faster to process
            # Adjust threshold value (128) if needed based on your use case
            threshold = 128
            image = image.point(lambda p: p > threshold and 255)

            preprocess_time = time.time() - preprocess_start
            if self.verbose:
                print(f"  Preprocessing time: {preprocess_time * 1000:.2f}ms")

            # Start timing OCR
            ocr_start = time.time()

            # Try EasyOCR first (more accurate, GPU-accelerated if available)
            if self.use_easyocr:
                try:
                    # Lazy initialization of EasyOCR reader on first use
                    # This initialization is done once and reused for all subsequent calls
                    if self.easyocr_reader is None:
                        # Initialize with English language, GPU if available
                        # verbose=False to suppress initialization messages
                        self.easyocr_reader = easyocr.Reader(
                            ["en"], gpu=True, verbose=False
                        )

                    # Convert PIL image to numpy array for EasyOCR
                    img_array = np.array(image)

                    # EasyOCR returns list of (bbox, text, confidence) tuples
                    # We only care about the text parts
                    results = self.easyocr_reader.readtext(img_array, detail=0)

                    # Combine all detected text into a single string
                    text = " ".join(results)

                    ocr_time = time.time() - ocr_start
                    if self.verbose:
                        print(f"  OCR time (EasyOCR): {ocr_time * 1000:.2f}ms")
                    return text.strip(), current_hash

                except Exception as easyocr_error:
                    # If EasyOCR fails (not installed, GPU issues, etc.), fall back to Tesseract
                    print(
                        f"EasyOCR failed ({easyocr_error}), falling back to Tesseract..."
                    )
                    # Permanently switch to Tesseract for all future calls
                    self.use_easyocr = False
                    # Continue to Tesseract below

            # Use Tesseract (either as fallback or if EasyOCR was disabled)
            # Try optimized config first (legacy engine is faster)
            # --psm 7: Single line of text (faster than block analysis)
            # --oem 0: Legacy engine (significantly faster than LSTM)
            # -c tessedit_char_whitelist: Only recognize alphabetic characters
            config = "--psm 7 --oem 0 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

            try:
                text = pytesseract.image_to_string(image, config=config)
                ocr_time = time.time() - ocr_start
                if self.verbose:
                    print(f"  OCR time (Tesseract): {ocr_time * 1000:.2f}ms")
                return text.strip(), current_hash
            except Exception as legacy_error:
                # If legacy engine fails (not installed), fall back to default Tesseract engine
                if (
                    "legacy" in str(legacy_error).lower()
                    or "oem" in str(legacy_error).lower()
                ):
                    print(
                        "Tesseract legacy engine not available, using default engine..."
                    )
                    # Fallback config without --oem 0 (uses default engine)
                    fallback_config = "--psm 7 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                    text = pytesseract.image_to_string(image, config=fallback_config)
                    ocr_time = time.time() - ocr_start
                    if self.verbose:
                        print(f"  OCR time (Tesseract): {ocr_time * 1000:.2f}ms")
                    return text.strip(), current_hash
                else:
                    # Re-raise if it's a different error
                    raise
        except Exception as e:
            print(f"Error extracting text: {e}")
            return "", None

    def check_for_continue_text(self, text):
        """Check if text contains the target word using fuzzy matching."""
        if not text:
            return False

        # Split text into words and check each word
        words = text.lower().split()

        for word in words:
            # Clean word of punctuation
            clean_word = "".join(c for c in word if c.isalnum())
            if clean_word:
                similarity = fuzz.ratio(clean_word, self.target_word)
                if similarity >= self.similarity_threshold:
                    print(
                        f"\t\tFound match: '{clean_word}' (similarity: {similarity}%)"
                    )
                    return True

        return False

    def simulate_click(self):
        """Simulate mouse click at current cursor position."""
        try:
            x, y = self.get_cursor_position()
            self.mouse_controller.click(mouse.Button.left, 1)
            print(f"Clicked at position: ({x}, {y})")
        except Exception as e:
            print(f"Error simulating click: {e}")


def main():
    """Main function with command-line argument parsing."""
    parser = argparse.ArgumentParser(
        description="AutoPassAd - Automatically click when 'continue' text is detected"
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=float,
        default=1.0,
        help="Time between screenshots in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--rect-size",
        "-r",
        type=str,
        default="70x170",
        help="Size of rectangle around cursor in VERTICALxHORIZONTAL format (default: 70x170)",
    )
    parser.add_argument(
        "--threshold",
        "-t",
        type=int,
        default=80,
        help="Minimum similarity threshold for text matching (default: 80)",
    )
    parser.add_argument(
        "--target-word",
        "-w",
        type=str,
        default="continue",
        help="Target word to search for in OCR text (default: continue)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output with timing information",
    )

    args = parser.parse_args()

    # Parse rect_size from "VxH" format
    try:
        parts = args.rect_size.split("x")
        if len(parts) != 2:
            raise ValueError("Invalid format")
        vertical, horizontal = int(parts[0]), int(parts[1])
        if vertical <= 0 or horizontal <= 0:
            raise ValueError("Sizes must be positive")
        rect_size = (vertical, horizontal)
    except ValueError as e:
        print(
            f"Error: Invalid rect-size format. Use VERTICALxHORIZONTAL (e.g., 20x200)"
        )
        sys.exit(1)

    # Validate arguments
    if args.interval <= 0:
        print("Error: Interval must be positive")
        sys.exit(1)
    if not (0 <= args.threshold <= 100):
        print("Error: Threshold must be between 0 and 100")
        sys.exit(1)

    # Create tool with configured parameters
    tool = AutoPassAd(
        interval=args.interval,
        rect_size=rect_size,
        similarity_threshold=args.threshold,
        target_word=args.target_word,
        verbose=args.verbose,
    )

    print(f"Auto-Click OCR Tool started with:")
    print(f"  Interval: {args.interval}s")
    print(f"  Rectangle size: {rect_size[0]}x{rect_size[1]}px (vertical x horizontal)")
    print(f"  Similarity threshold: {args.threshold}%")
    print(f"  Target word: '{args.target_word}'")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            iteration_start = time.time()
            screenshot = tool.capture_screenshot_around_cursor()
            text, image_hash = tool.extract_text_from_image(screenshot)

            if text.strip():
                if tool.check_for_continue_text(text):
                    print(f"\t\tFound '{tool.target_word}' text! Clicking...")
                    tool.simulate_click()
                    # Don't add to skip queue - we want to detect this image again if it reappears
                else:
                    # Only print detected text in verbose mode when not matched
                    if tool.verbose:
                        print(f"Detected text: '{text}'")
                    print(f"\tNo '{tool.target_word}' text found")
                    # Add to skip queue since this image didn't match
                    if image_hash is not None:
                        tool.recent_image_hashes.append(image_hash)
            else:
                # No text detected, add to skip queue if we have a hash
                if image_hash is not None:
                    tool.recent_image_hashes.append(image_hash)

            if tool.verbose:
                iteration_time = time.time() - iteration_start
                print(f"  Total iteration time: {iteration_time * 1000:.2f}ms")

            time.sleep(tool.interval)
    except KeyboardInterrupt:
        print("\nStopping Auto-Click OCR Tool.")


if __name__ == "__main__":
    main()
