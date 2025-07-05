import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import time
import requests
import json
import socket

# Configure page
st.set_page_config(
    page_title="NexusAI Complete Studio",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for futuristic UI
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&display=swap');

:root {
    --primary: #00f0ff;
    --secondary: #ff00f0;
    --dark: #0a0a1a;
    --light: #f0f0ff;
}

* {
    font-family: 'Orbitron', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, var(--dark) 0%, #1a1a2e 100%);
    color: var(--light);
}

h1, h2, h3, h4, h5, h6 {
    color: var(--primary) !important;
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
}

.stTextInput>div>div>input, .stTextArea>div>div>textarea {
    background-color: rgba(10, 10, 26, 0.8) !important;
    color: var(--light) !important;
    border: 1px solid var(--primary) !important;
    border-radius: 5px !important;
}

.stButton>button {
    background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%) !important;
    color: var(--dark) !important;
    border: none !important;
    border-radius: 25px !important;
    padding: 10px 25px !important;
    font-weight: bold !important;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.7);
    transition: all 0.3s ease !important;
}

.stButton>button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.9);
}

.stProgress>div>div>div {
    background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%) !important;
}

.css-1d391kg {
    background-color: rgba(10, 10, 26, 0.9) !important;
    border-right: 1px solid var(--primary) !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    padding: 0 20px;
    background-color: rgba(10, 10, 26, 0.5);
    border-radius: 10px 10px 0 0 !important;
    border: 1px solid var(--primary) !important;
    color: var(--light) !important;
}

.stTabs [aria-selected="true"] {
    background-color: rgba(0, 240, 255, 0.2) !important;
    color: var(--primary) !important;
    font-weight: bold;
    box-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
}

.video-container {
    border: 2px solid var(--primary);
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
}
</style>
""", unsafe_allow_html=True)

# Kling AI API Configuration
KLING_API_URL = "https://api-singapore.klingai.com"
ACCESS_KEY = "A9GQdrBN9LndCkQy3DHfKtKF88b4QKLF"
SECRET_KEY = "hhgHaAe3Enek4fFaf8N3HHPmmAmFpJtM"

headers = {
    "AccessKey": ACCESS_KEY,
    "SecretKey": SECRET_KEY,
    "Content-Type": "application/json"
}

# Initialize Gemini client
@st.cache_resource
def init_client():
    return genai.Client(api_key='AIzaSyCZ-1xA0qHy7p3l5VdZYCrvoaQhpMZLjig')

client = init_client()

# Session state initialization
if "generated_video" not in st.session_state:
    st.session_state.generated_video = None
if "generation_status" not in st.session_state:
    st.session_state.generation_status = "ready"
if "task_id" not in st.session_state:
    st.session_state.task_id = None

def verify_api_connection():
    try:
        response = requests.head(KLING_API_URL, headers=headers, timeout=5)
        return response.status_code < 500
    except:
        return False

def generate_video(prompt, duration=5, resolution="1080p", style="cinematic"):
    payload = {
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "style": style,
        "timestamp": int(time.time())
    }
    
    try:
        response = requests.post(
            KLING_API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if not response.content:
            return {"status": "error", "message": "Empty response from server"}
            
        try:
            data = response.json()
        except ValueError:
            return {"status": "error", "message": f"Invalid response: {response.text[:100]}"}
            
        if response.status_code == 200:
            if "task_id" in data:
                return {
                    "status": "processing",
                    "task_id": data["task_id"],
                    "message": data.get("message", "")
                }
            return {"status": "error", "message": data.get("error", "Missing task_id")}
            
        return {"status": "error", "message": f"API Error {response.status_code}"}
        
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Request failed: {str(e)}"}

def check_video_status(task_id):
    try:
        response = requests.post(
            KLING_API_URL,
            headers=headers,
            json={"task_id": task_id},
            timeout=30
        )
        
        if not response.content:
            return {"status": "error", "message": "Empty response"}
            
        try:
            data = response.json()
            if "status" in data:
                return data
            return {"status": "error", "message": "Invalid response format"}
        except ValueError:
            return {"status": "error", "message": f"Invalid JSON: {response.text[:100]}"}
            
    except Exception as e:
        return {"status": "error", "message": f"Status check failed: {str(e)}"}

def display_video(video_url):
    try:
        st.video(video_url)
        st.session_state.generated_video = video_url
        
        try:
            video_bytes = requests.get(video_url, timeout=30).content
            st.download_button(
                label="📥 Download Video",
                data=video_bytes,
                file_name="nexusai_video.mp4",
                mime="video/mp4"
            )
        except:
            st.warning("Video download unavailable")
    except Exception as e:
        st.error(f"Failed to display video: {str(e)}")

# App header
st.title("🚀 NexusAI Complete Studio")
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h3>The ultimate AI content creation platform</h3>
    <p>Generate stunning videos and images with the power of advanced AI</p>
</div>
""", unsafe_allow_html=True)

# Verify API connection
if not verify_api_connection():
    st.error("Could not connect to Kling AI API. Please check your connection and API keys.")
    st.stop()

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Control Panel")
    st.markdown("---")
    
    generation_mode = st.selectbox(
        "Generation Mode",
        ["🎥 Video Generation", "✨ Image Generation", "🖌️ Image Editing"],
        index=0
    )
    
    st.markdown("---")
    
    if generation_mode == "🎥 Video Generation":
        st.subheader("Video Settings")
        duration = st.slider("Duration (seconds)", 2, 60, 5)
        resolution = st.selectbox("Resolution", ["720p", "1080p", "4K"], index=1)
        video_style = st.selectbox("Video Style", [
            "cinematic", "realistic", "anime", 
            "3d-animation", "watercolor", "cyberpunk"
        ], index=0)
    
    elif generation_mode in ["✨ Image Generation", "🖌️ Image Editing"]:
        st.subheader("Image Settings")
        image_style = st.selectbox(
            "Image Style",
            ["3D Rendered", "Cyberpunk", "Sci-Fi", "Futuristic", "Neon", "Holographic"],
            index=2
        )
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center;">
        <p>Powered by NexusAI</p>
        <p>v3.0.0 | Complete Studio</p>
    </div>
    """, unsafe_allow_html=True)

# Main content area
if generation_mode == "🎥 Video Generation":
    st.header("🎬 Video Generation Studio")
    
    with st.form("video_generation_form"):
        video_prompt = st.text_area(
            "Describe your video...",
            height=200,
            placeholder="A futuristic cityscape at night with flying cars and neon lights..."
        )
        
        generate_video_button = st.form_submit_button(
            "🎥 Generate Video",
            type="primary"
        )
    
    if generate_video_button and video_prompt:
        st.session_state.generation_status = "generating"
        with st.spinner("🎥 Creating your video masterpiece..."):
            progress_bar = st.progress(0)
            
            for percent_complete in range(0, 101, 2):
                time.sleep(0.05)
                progress_bar.progress(percent_complete)
            
            result = generate_video(
                prompt=video_prompt,
                duration=duration,
                resolution=resolution.replace("p", "").lower(),
                style=video_style.lower()
            )
            
            if result["status"] == "processing":
                st.session_state.task_id = result["task_id"]
                st.session_state.generation_status = "processing"
                st.info("⏳ Video is being generated. Please wait...")
            else:
                st.session_state.generation_status = "error"
                st.error(result["message"])
    
    if st.session_state.generation_status == "processing" and st.session_state.task_id:
        with st.spinner("🔄 Checking video generation status..."):
            status = check_video_status(st.session_state.task_id)
            
            if status.get("status") == "completed":
                st.session_state.generation_status = "completed"
                if "video_url" in status:
                    st.success("✅ Video generated successfully!")
                    display_video(status["video_url"])
                    st.rerun()
                else:
                    st.error("Video generated but URL missing in response")
            elif status.get("status") == "error":
                st.session_state.generation_status = "error"
                st.error(status["message"])
            else:
                time.sleep(5)
                st.rerun()
    
    if st.session_state.generated_video and st.session_state.generation_status == "completed":
        st.markdown("### 🎬 Your Generated Video")
        st.video(st.session_state.generated_video)

elif generation_mode == "✨ Image Generation":
    st.header("🖼️ Image Generation Studio")
    
    with st.form("image_generation_form"):
        image_prompt = st.text_area(
            "Describe your vision...",
            height=200,
            placeholder="A cybernetic owl with neon wings perched on a futuristic skyscraper..."
        )

        generate_image_button = st.form_submit_button(
            "✨ Generate Image",
            type="primary"
        )

    if generate_image_button and image_prompt:
        with st.spinner("✨ Generating your futuristic vision..."):
            progress_bar = st.progress(0)

            for percent_complete in range(0, 101, 2):
                time.sleep(0.02)
                progress_bar.progress(percent_complete)

            try:
                response = client.models.generate_content(
                    model='gemini-2.0-flash-preview-image-generation',
                    contents=image_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT', 'IMAGE']
                    )
                )

                if response.candidates and response.candidates[0].content.parts:
                    st.success("✨ Generation complete!")
                    for part in response.candidates[0].content.parts:
                        if part.inline_data is not None:
                            image = Image.open(BytesIO((part.inline_data.data)))
                            st.image(image, use_container_width=True)
                            buf = BytesIO()
                            image.save(buf, format="PNG")
                            st.download_button(
                                label="📥 Download Image",
                                data=buf.getvalue(),
                                file_name="nexusai_image.png",
                                mime="image/png"
                            )
                else:
                    st.error("No image was generated. Please try a different prompt.")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

elif generation_mode == "🖌️ Image Editing":
    st.header("🖌️ Image Editing Studio")
    
    uploaded_file = st.file_uploader("Upload an image to edit", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        original_image = Image.open(uploaded_file)
        st.image(original_image, caption="Original Image", use_container_width=True)
        
        edit_instructions = st.text_area(
            "Editing instructions",
            height=150,
            placeholder="Add holographic elements, make the background futuristic..."
        )
        
        edit_button = st.button(
            "🖌️ Apply Edits",
            type="primary"
        )
        
        if edit_button and edit_instructions:
            with st.spinner("🖌️ Transforming your image..."):
                progress_bar = st.progress(0)
                
                for percent_complete in range(0, 101, 5):
                    time.sleep(0.05)
                    progress_bar.progress(percent_complete)
                
                try:
                    response = client.models.generate_content(
                        model="gemini-2.0-flash-preview-image-generation",
                        contents=[edit_instructions, original_image],
                        config=types.GenerateContentConfig(
                            response_modalities=['TEXT', 'IMAGE']
                        )
                    )
                    
                    if response.candidates and response.candidates[0].content.parts:
                        st.success("🎨 Edit complete!")
                        for part in response.candidates[0].content.parts:
                            if part.inline_data is not None:
                                edited_image = Image.open(BytesIO(part.inline_data.data))
                                st.image(edited_image, use_container_width=True)
                                buf = BytesIO()
                                edited_image.save(buf, format="PNG")
                                st.download_button(
                                    label="📥 Download Edited Image",
                                    data=buf.getvalue(),
                                    file_name="nexusai_edited.png",
                                    mime="image/png"
                                )
                    else:
                        st.error("The image could not be edited. Please try different instructions.")
                
                except Exception as e:
                    st.error(f"An error occurred during editing: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid var(--primary);">
    <p>© 2025 NexusAI Complete Studio | All Rights Reserved</p>
    <p>Powered by cutting-edge AI technology</p>
</div>
""", unsafe_allow_html=True)
