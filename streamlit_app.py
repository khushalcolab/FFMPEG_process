import streamlit as st
from moviepy.editor import *
import tempfile
import os

def create_reel(images, voiceover, background_music):
    # Create temporary directory to store processed files
    temp_dir = tempfile.mkdtemp()
    
    # Load the voiceover audio to get its duration
    voice_clip = AudioFileClip(voiceover)
    total_duration = voice_clip.duration
    
    # Calculate duration for each image
    image_duration = total_duration / 6
    
    # Create image clips
    image_clips = []
    for img in images:
        # Read the image
        clip = ImageClip(img)
        # Resize to Instagram reel size (1080x1920)
        clip = clip.resize(width=1080, height=1920)
        # Set the duration for this image
        clip = clip.set_duration(image_duration)
        image_clips.append(clip)
    
    # Concatenate all image clips
    final_clip = concatenate_videoclips(image_clips, method="compose")
    
    # Load and adjust background music
    bg_music = AudioFileClip(background_music)
    # Loop the background music if it's shorter than the video
    if bg_music.duration < total_duration:
        bg_music = vfx.loop(bg_music, duration=total_duration)
    # Trim if longer than video
    bg_music = bg_music.subclip(0, total_duration)
    # Lower the volume of background music
    bg_music = bg_music.volumex(0.3)
    
    # Combine voiceover and background music
    final_audio = CompositeAudioClip([voice_clip, bg_music])
    
    # Set the final audio to the video
    final_clip = final_clip.set_audio(final_audio)
    
    # Export path
    output_path = os.path.join(temp_dir, "instagram_reel.mp4")
    
    # Write the final video
    final_clip.write_videofile(
        output_path,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile=os.path.join(temp_dir, 'temp-audio.m4a'),
        remove_temp=True
    )
    
    return output_path

def main():
    st.title("Instagram Reel Generator")
    
    st.header("Upload Images")
    uploaded_images = []
    for i in range(6):
        image = st.file_uploader(f"Upload Image {i+1}", type=['jpg', 'jpeg', 'png'], key=f"image_{i}")
        if image:
            uploaded_images.append(image)
    
    st.header("Upload Audio")
    voiceover = st.file_uploader("Upload Voiceover", type=['mp3', 'wav', 'm4a'], key="voiceover")
    background_music = st.file_uploader("Upload Background Music", type=['mp3', 'wav', 'm4a'], key="background_music")
    
    # Using a single button with conditional logic
    if st.button("Generate Reel", key="generate_button"):
        if len(uploaded_images) == 6 and voiceover and background_music:
            try:
                with st.spinner("Generating your reel..."):
                    # Save uploaded files temporarily
                    temp_dir = tempfile.mkdtemp()
                    
                    # Save images
                    image_paths = []
                    for i, img in enumerate(uploaded_images):
                        img_path = os.path.join(temp_dir, f"image_{i}.png")
                        with open(img_path, "wb") as f:
                            f.write(img.getbuffer())
                        image_paths.append(img_path)
                    
                    # Save audio files
                    voiceover_path = os.path.join(temp_dir, "voiceover.mp3")
                    with open(voiceover_path, "wb") as f:
                        f.write(voiceover.getbuffer())
                    
                    bg_music_path = os.path.join(temp_dir, "background.mp3")
                    with open(bg_music_path, "wb") as f:
                        f.write(background_music.getbuffer())
                    
                    # Generate reel
                    output_path = create_reel(image_paths, voiceover_path, bg_music_path)
                    
                    # Provide download button
                    with open(output_path, "rb") as f:
                        st.download_button(
                            label="Download Reel",
                            data=f,
                            file_name="instagram_reel.mp4",
                            mime="video/mp4",
                            key="download_button"
                        )
                    
                    # Cleanup
                    import shutil
                    shutil.rmtree(temp_dir)
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please upload all required files (6 images, voiceover, and background music)")

if __name__ == "__main__":
    main()
