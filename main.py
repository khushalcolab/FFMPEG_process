import streamlit as st
import subprocess
import os
from pathlib import Path

def process_ffmpeg_command(image_files, primary_audio, bg_music):
    output_file = "output_reel.mp4"
    
    # Construct FFmpeg command
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-i", primary_audio,
        "-i", bg_music,
    ]
    
    for img in image_files:
        ffmpeg_cmd.extend(["-loop", "1", "-t", "3", "-i", img])
    
    filter_complex = """
        [0:a][1:a]amix=inputs=2:duration=first:weights=1.5 0.5[a];
    """
    
    for i in range(len(image_files)):
        filter_complex += (
            f"[{i+2}:v]scale=1080:1920:force_original_aspect_ratio=decrease," 
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2[s{i}];"
        )
    
    filter_complex += "".join([f"[s{i}]" for i in range(len(image_files))]) + "concat=n=6:v=1:a=0[v]"
    
    ffmpeg_cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-c:a", "aac", "-shortest", output_file
    ])
    
    # Run FFmpeg
    subprocess.run(ffmpeg_cmd, check=True)
    return output_file

st.title("FFmpeg Video Generator")

# File Uploaders
uploaded_images = [st.file_uploader(f"Upload Image {i+1}", type=["png", "jpg", "jpeg"]) for i in range(6)]
primary_audio = st.file_uploader("Upload Primary Song", type=["mp3", "wav"])
bg_music = st.file_uploader("Upload Background Music", type=["mp3", "wav"])

if st.button("Generate Video"):
    if None in uploaded_images or not primary_audio or not bg_music:
        st.error("Please upload all required files.")
    else:
        # Save files temporarily
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        image_paths = []
        for idx, img in enumerate(uploaded_images):
            img_path = temp_dir / f"image_{idx+1}.png"
            with open(img_path, "wb") as f:
                f.write(img.read())
            image_paths.append(str(img_path))
        
        primary_audio_path = temp_dir / "primary_audio.mp3"
        with open(primary_audio_path, "wb") as f:
            f.write(primary_audio.read())
        
        bg_music_path = temp_dir / "bg_music.mp3"
        with open(bg_music_path, "wb") as f:
            f.write(bg_music.read())
        
        # Process video
        output_path = process_ffmpeg_command(image_paths, str(primary_audio_path), str(bg_music_path))
        
        st.success("Video Generated Successfully!")
        st.video(output_path)
