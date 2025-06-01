import streamlit as st
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
import webvtt
from datetime import timedelta
import tempfile

st.set_page_config(page_title="Video & Transcript Trimmer", layout="centered")
st.title("🎬 Video & Transcript Trimmer")

# File upload
video_file = st.file_uploader("Upload a video file", type=["mp4", "mov", "avi", "mkv"])
vtt_file = st.file_uploader("Upload a VTT transcript file", type=["vtt"])

# Helper functions

def format_time(seconds):
    td = timedelta(seconds=seconds)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((td.total_seconds() - total_seconds) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

def parse_time(timestr):
    parts = timestr.strip().split(":")
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    elif len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    else:
        raise ValueError("Invalid time format")

def parse_segments(segments_str):
    # Expects input like '0:00-0:10,0:15-0:16,0:30-0:35'
    segments = []
    for seg in segments_str.split(','):
        if '-' not in seg:
            continue
        start_str, end_str = seg.split('-')
        start = parse_time(start_str.strip())
        end = parse_time(end_str.strip())
        if end > start:
            segments.append((start, end))
    return segments

def trim_video_segments(input_path, output_path, segments):
    with VideoFileClip(input_path) as clip:
        clips = [clip.subclip(start, end) for start, end in segments]
        final = concatenate_videoclips(clips)
        final.write_videofile(output_path, codec='libx264', audio_codec='aac', verbose=False, logger=None)

def cut_video_segments(input_path, output_path, cut_segments, duration):
    # cut_segments: list of (start, end) to remove
    keep_segments = []
    last_end = 0.0
    for start, end in sorted(cut_segments):
        if start > last_end:
            keep_segments.append((last_end, start))
        last_end = max(last_end, end)
    if last_end < duration:
        keep_segments.append((last_end, duration))
    trim_video_segments(input_path, output_path, keep_segments)
    return keep_segments

def update_vtt_segments(input_vtt, output_vtt, keep_segments):
    # keep_segments: list of (start, end) to keep, in output order
    captions = list(webvtt.read(input_vtt))
    new_captions = []
    output_time = 0.0
    for seg_start, seg_end in keep_segments:
        seg_duration = seg_end - seg_start
        for caption in captions:
            start_sec = parse_time(caption.start.replace(',', '.'))
            end_sec = parse_time(caption.end.replace(',', '.'))
            # If caption is fully before or after segment, skip
            if end_sec <= seg_start or start_sec >= seg_end:
                continue
            # Clip caption to segment
            new_start = max(start_sec, seg_start) - seg_start + output_time
            new_end = min(end_sec, seg_end) - seg_start + output_time
            if new_end > new_start:
                new_caption = webvtt.Caption(
                    format_time(new_start),
                    format_time(new_end),
                    caption.text
                )
                new_captions.append(new_caption)
        output_time += seg_duration
    webvtt_out = webvtt.WebVTT()
    for cap in new_captions:
        webvtt_out.captions.append(cap)
    webvtt_out.save(output_vtt)

# Main app logic
if 'trimmed_video_bytes' not in st.session_state:
    st.session_state['trimmed_video_bytes'] = None
if 'trimmed_vtt_bytes' not in st.session_state:
    st.session_state['trimmed_vtt_bytes'] = None
if 'trimmed_video_name' not in st.session_state:
    st.session_state['trimmed_video_name'] = None
if 'trimmed_vtt_name' not in st.session_state:
    st.session_state['trimmed_vtt_name'] = None

if video_file and vtt_file:
    # Save uploaded files to temp files
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video_file.name)[1]) as temp_vid:
        temp_vid.write(video_file.read())
        video_path = temp_vid.name
    with tempfile.NamedTemporaryFile(delete=False, suffix=".vtt") as temp_vtt:
        temp_vtt.write(vtt_file.read())
        vtt_path = temp_vtt.name

    # Video preview
    st.video(video_path)
    with VideoFileClip(video_path) as clip:
        duration = clip.duration
    st.write(f"Video duration: {duration:.2f} seconds")

    # Mode selector
    mode = st.radio("Select mode", ["Trim (keep only these segments)", "Cut (remove these segments)"])
    default_seg = "0:00-0:10" if mode.startswith("Trim") else "0:00-0:10"
    segments_str = st.text_input("Segments (comma-separated, e.g. 0:00-0:10,0:15-0:16)", value=default_seg)

    if st.button("Process Video and Transcript"):
        try:
            segments = parse_segments(segments_str)
            if not segments:
                st.error("Please enter at least one valid segment.")
            else:
                with st.spinner("Processing..."):
                    trimmed_video_path = tempfile.mktemp(suffix=os.path.splitext(video_file.name)[1])
                    trimmed_vtt_path = tempfile.mktemp(suffix=".vtt")
                    if mode.startswith("Trim"):
                        trim_video_segments(video_path, trimmed_video_path, segments)
                        keep_segments = segments
                    else:
                        keep_segments = cut_video_segments(video_path, trimmed_video_path, segments, duration)
                    update_vtt_segments(vtt_path, trimmed_vtt_path, keep_segments)
                    # Read bytes and store in session_state
                    with open(trimmed_video_path, "rb") as f:
                        st.session_state['trimmed_video_bytes'] = f.read()
                        st.session_state['trimmed_video_name'] = f"processed_{video_file.name}"
                    with open(trimmed_vtt_path, "rb") as f:
                        st.session_state['trimmed_vtt_bytes'] = f.read()
                        st.session_state['trimmed_vtt_name'] = f"processed_{vtt_file.name}"
                st.success("Done!")
        except Exception as e:
            st.error(f"Error: {e}")

# Show download buttons if results are available
if st.session_state['trimmed_video_bytes']:
    st.video(st.session_state['trimmed_video_bytes'])
    st.download_button("Download Processed Video", st.session_state['trimmed_video_bytes'], file_name=st.session_state['trimmed_video_name'])
if st.session_state['trimmed_vtt_bytes']:
    st.download_button("Download Updated Transcript", st.session_state['trimmed_vtt_bytes'], file_name=st.session_state['trimmed_vtt_name']) 