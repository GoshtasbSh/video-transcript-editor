# Video & Transcript Trimmer Web App

A user-friendly web app for trimming or cutting video files and synchronizing their VTT transcript files. Built with Streamlit and MoviePy.

## Features
- **Trim mode:** Keep only the video segments you specify.
- **Cut mode:** Remove the video segments you specify, keeping the rest.
- **Multiple segments:** Enter as comma-separated pairs (e.g., `0:00-0:10,0:15-0:16`).
- **Transcript sync:** The VTT transcript is updated to match the new video timing.
- **Download results:** Download the processed video and updated transcript.

## Setup

1. **Clone the repository:**
   ```bash
   git clone git@github.com:GoshtasbSh/video-transcript-editor.git
   cd video-transcript-editor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Or, if you use conda:
   ```bash
   conda install -c conda-forge moviepy streamlit webvtt-py
   ```

## Usage

1. **Run the app:**
   ```bash
   streamlit run video_trimmer_web.py
   ```
2. **Open the local URL** (usually http://localhost:8501) in your browser.
3. **Upload your video and VTT transcript files.**
4. **Select mode:**
   - **Trim:** Keep only the segments you specify.
   - **Cut:** Remove the segments you specify, keeping the rest.
5. **Enter segments:**
   - Format: `start-end` pairs, comma-separated.
   - Example: `0:00-0:10,0:15-0:16,0:30-0:35`
6. **Process and download:**
   - Click "Process Video and Transcript".
   - Download the processed video and updated transcript.

## Example

- **Trim mode:**
  - Segments: `0:00-0:10,0:20-0:30`
  - Keeps only 0–10s and 20–30s, concatenated.
- **Cut mode:**
  - Segments: `0:00-0:10,0:20-0:30`
  - Removes 0–10s and 20–30s, keeps the rest.

## Requirements
- Python 3.8+
- moviepy
- streamlit
- webvtt-py

## License
MIT 
