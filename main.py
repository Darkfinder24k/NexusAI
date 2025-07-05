import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
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

/* Animation for generated content */
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}

.generated-content {
    animation: float 4s ease-in-out infinite;
    border: 2px solid var(--primary);
    border-radius: 10px;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
    transition: all 0.3s ease;
}

.generated-content:hover {
    transform: scale(1.02);
    box-shadow: 0 0 30px rgba(0, 240, 255, 0.8);
}

/* Progress bar styling */
.stProgress>div>div>div {
    background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%) !important;
}

/* Sidebar styling */
.css-1d391kg {
    background-color: rgba(10, 10, 26, 0.9) !important;
    border-right: 1px solid var(--primary) !important;
}

/* Tab styling */
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

/* Video container styling */
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
if "last_error" not in st.session_state:
    st.session_state.last_error = None

# Kling AI Video generation functions
def generate_video(prompt, duration=5, resolution="1080p", style="cinematic"):
    """Generate video using Kling AI API"""
    endpoint = KLING_API_URL  # Using base URL directly
    
    payload = {
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "style": style,
        "timestamp": int(time.time())
    }
    
    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        # Debug raw response
        print("Raw API Response:", response.text)
        
        if not response.content:
            return {
                "status": "error",
                "message": "Empty response from API server",
                "debug": response.text
            }
            
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": "Invalid JSON response",
                "debug": response.text
            }
        
        if response.status_code == 200:
            if "task_id" in response_json:
                return {
                    "status": "processing",
                    "task_id": response_json["task_id"],
                    "message": response_json.get("message", "")
                }
            return {
                "status": "error",
                "message": response_json.get("error", "Missing task_id in response"),
                "debug": response.text
            }
            
        return {
            "status": "error",
            "message": f"API Error {response.status_code}",
            "debug": response.text
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}",
            "debug": str(e)
        }

def check_video_status(task_id):
    """Check status of a video generation task"""
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
            return {
                "status": "error",
                "message": data.get("error", "Invalid response format")
            }
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": f"Invalid JSON: {response.text[:200]}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Status check failed: {str(e)}"
        }

def display_video(video_url):
    """Display generated video in Streamlit"""
    try:
        st.video(video_url)
        st.session_state.generated_video = video_url
        
        try:
            video_bytes = requests.get(video_url, stream=True, timeout=30).content
            st.download_button(
                label="📥 Download Video",
                data=video_bytes,
                file_name="nexusai_video.mp4",
                mime="video/mp4"
            )
        except Exception as e:
            st.warning(f"Video download unavailable: {str(e)}")
    
    except Exception as e:
        st.error(f"Failed to display video: {str(e)}")

def display_error_details(error_data):
    """Show detailed error information"""
    with st.expander("🚨 Error Details", expanded=False):
        st.error(error_data.get("message", "Unknown error"))
        st.code(f"Debug Info:\n{error_data.get('debug', 'No debug info available')}")
        st.markdown("**Troubleshooting Tips:**")
        st.markdown("""
        - Check your internet connection
        - Verify your API keys are correct
        - Try a simpler prompt
        - Wait a few minutes and try again
        """)

# App header
st.title("🚀 NexusAI Complete Studio")
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h3>The ultimate AI content creation platform</h3>
    <p>Generate stunning videos and images with the power of advanced AI</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Control Panel")
    st.markdown("---")
    
    # Initialize generation_mode in session state
    if "generation_mode" not in st.session_state:
        st.session_state.generation_mode = "🎥 Video Generation"
    
    # Mode selection
    st.session_state.generation_mode = st.selectbox(
        "Generation Mode",
        ["🎥 Video Generation", "✨ Image Generation", "🖌️ Image Editing"],
        index=0
    )
    
    st.markdown("---")
    
    if st.session_state.generation_mode == "🎥 Video Generation":
        st.subheader("Video Settings")
        duration = st.slider("Duration (seconds)", 2, 60, 5)
        resolution = st.selectbox("Resolution", ["720p", "1080p", "4K"], index=1)
        video_style = st.selectbox("Video Style", [
            "cinematic", 
            "realistic", 
            "anime", 
            "3d-animation", 
            "watercolor", 
            "cyberpunk"
        ], index=0)
    
    elif st.session_state.generation_mode in ["✨ Image Generation", "🖌️ Image Editing"]:
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
if st.session_state.generation_mode == "🎥 Video Generation":
    st.header("🎬 Video Generation Studio")
    
    with st.form("video_generation_form"):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            video_prompt = st.text_area(
                "Describe your video...",
                height=200,
                placeholder="A futuristic cityscape at night with flying cars and neon lights, cinematic camera movement..."
            )
            
            with st.expander("⚙️ Advanced Settings"):
                col_res, col_style = st.columns(2)
                
                with col_res:
                    resolution = st.selectbox(
                        "Resolution",
                        ["480p", "720p", "1080p", "2K", "4K", "8K", "12K"],
                        index=2
                    )
                
                with col_style:
                    video_style = st.selectbox(
                        "Video Style",
                        [
                            "3D Rendered", "Cyberpunk", "Sci-Fi", 
                            "Futuristic", "Neon", "Holographic",
                            "Realistic", "Anime", "Watercolor",
                            "Cinematic", "Oil Painting", "Steampunk"
                        ],
                        index=6
                    )
                
                duration = st.slider(
                    "Duration (seconds)",
                    2, 60, 5,
                    help="Select video length between 2-60 seconds"
                )
            
            generate_video_button = st.form_submit_button(
                "🎥 Generate Video",
                type="primary"
            )
        
        with col2:
            st.markdown("### 💡 Video Prompt Tips")
            st.markdown("""
            - Describe camera movements
            - Include lighting and atmosphere
            - Mention specific actions or events
            - Add style descriptors
            """)
            
            st.markdown("### 🎨 Style Guide")
            st.markdown("""
            - **Realistic**: Photorealistic videos
            - **3D Rendered**: CGI-style animation
            - **Cyberpunk**: Neon-lit futuristic scenes
            - **Anime**: Japanese animation style
            """)
    
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
            
            elif result["status"] == "error":
                st.session_state.generation_status = "error"
                st.session_state.last_error = result
                st.error(result["message"])
                display_error_details(result)
    
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
                display_error_details(status)
            
            else:
                time.sleep(5)
                st.rerun()
    
    if st.session_state.generated_video and st.session_state.generation_status == "completed":
        st.markdown("### 🎬 Your Generated Video")
        with st.container():
            st.video(st.session_state.generated_video)
            
            try:
                video_bytes = requests.get(
                    st.session_state.generated_video, 
                    stream=True,
                    timeout=30
                ).content
                
                st.download_button(
                    label="⬇️ Download HD Video",
                    data=video_bytes,
                    file_name=f"nexusai_{video_style.lower()}_{resolution}.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"Video download currently unavailable: {str(e)}")
    
    with st.expander("💡 Video Example Prompts", expanded=False):
        tab1, tab2, tab3 = st.tabs(["🌆 Scenes", "🎭 Characters", "🎨 Artistic"])
        
        with tab1:
            st.markdown("""
            **Urban Landscapes:**
            - "Cyberpunk Tokyo at night with holographic advertisements and flying cars, neon reflections on wet streets"
            - "Futuristic megacity with towering skyscrapers and aerial highways, golden hour lighting"
            """)
        
        with tab2:
            st.markdown("""
            **Character Scenes:**
            - "Anime-style warrior in glowing armor battling a dragon, dynamic camera angles"
            """)
        
        with tab3:
            st.markdown("""
            **Artistic Styles:**
            - "Watercolor animation of Paris changing through four seasons"
            """)

elif st.session_state.generation_mode == "✨ Image Generation":
    st.header("🖼️ Image Generation Studio")
    
    with st.form("image_generation_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            image_prompt = st.text_area(
                "Describe your vision...",
                height=200,
                placeholder="A cybernetic owl with neon wings perched on a futuristic skyscraper with holographic advertisements..."
            )

            with st.expander("⚙️ Advanced Settings"):
                col_style, col_aspect = st.columns(2)
                
                with col_style:
                    image_style = st.selectbox(
                        "Image Style",
                        [
                            "3D Rendered", "Cyberpunk", "Sci-Fi", 
                            "Futuristic", "Neon", "Holographic",
                            "Photorealistic", "Anime", "Watercolor",
                            "Oil Painting", "Steampunk", "Low Poly"
                        ],
                        index=2
                    )
                
                with col_aspect:
                    aspect_ratio = st.selectbox(
                        "Aspect Ratio",
                        ["1:1 (Square)", "4:3 (Standard)", "16:9 (Widescreen)", "9:16 (Portrait)", "2:3 (Vertical)"],
                        index=0
                    )

            generate_image_button = st.form_submit_button(
                "✨ Generate Image",
                type="primary"
            )

        with col2:
            st.markdown("### 💡 Image Prompt Tips")
            st.markdown("""
            - Be descriptive with details
            - Mention lighting, style, mood
            - Include futuristic elements
            - Specify composition and perspective
            """)

    if generate_image_button and image_prompt:
        with st.spinner("✨ Generating your futuristic vision..."):
            progress_bar = st.progress(0)

            for percent_complete in range(0, 101, 2):
                time.sleep(0.02)
                progress_bar.progress(percent_complete)

            try:
                enhanced_prompt = f"{image_prompt}, {image_style} style, ultra HD, {aspect_ratio.split(' ')[0]} aspect ratio"

                response = client.models.generate_content(
                    model='gemini-2.0-flash-preview-image-generation',
                    contents=enhanced_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT', 'IMAGE']
                    )
                )

                if response.candidates and response.candidates[0].content.parts:
                    st.success("✨ Generation complete! Behold your creation!")

                    cols = st.columns(2)
                    for i, part in enumerate(response.candidates[0].content.parts):
                        if part.text is not None:
                            cols[0].markdown(f"### 🤖 AI Notes")
                            cols[0].write(part.text)
                        elif part.inline_data is not None:
                            image = Image.open(BytesIO((part.inline_data.data)))
                            cols[1].markdown(f"### 🖼️ Generated Image")
                            cols[1].image(image, use_container_width=True, caption=f"{image_style} style image")

                            buf = BytesIO()
                            image.save(buf, format="PNG")
                            byte_im = buf.getvalue()
                            cols[1].download_button(
                                label="📥 Download HD Image",
                                data=byte_im,
                                file_name=f"nexusai_{image_style.lower().replace(' ', '_')}.png",
                                mime="image/png",
                                use_container_width=True
                            )
                else:
                    st.error("No image was generated. Please try a different prompt.")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

elif st.session_state.generation_mode == "🖌️ Image Editing":
    st.header("🖌️ Image Editing Studio")
    
    uploaded_file = st.file_uploader("Upload an image to edit", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            original_image = Image.open(uploaded_file)
            st.image(original_image, caption="Original Image", use_container_width=True)
        
        with col2:
            edit_instructions = st.text_area(
                "Editing instructions",
                height=150,
                placeholder="Add holographic elements, make the background futuristic, enhance with neon lighting..."
            )
            
            edit_style = st.selectbox(
                "Editing Style",
                [
                    "Match Original", "Cyberpunk", "Sci-Fi", 
                    "Futuristic", "Neon", "Holographic",
                    "Realistic", "Anime", "Watercolor"
                ],
                index=0
            )
            
            edit_button = st.button(
                "🖌️ Apply Edits",
                use_container_width=True,
                type="primary"
            )
            
            if edit_button and edit_instructions:
                with st.spinner("🖌️ Transforming your image..."):
                    progress_bar = st.progress(0)
                    
                    for percent_complete in range(0, 101, 5):
                        time.sleep(0.05)
                        progress_bar.progress(percent_complete)
                    
                    try:
                        contents = [
                            f"{edit_instructions} ({edit_style} style)",
                            original_image
                        ]
                        
                        response = client.models.generate_content(
                            model="gemini-2.0-flash-preview-image-generation",
                            contents=contents,
                            config=types.GenerateContentConfig(
                                response_modalities=['TEXT', 'IMAGE']
                            )
                        )
                        
                        if response.candidates and response.candidates[0].content.parts:
                            st.success("🎨 Edit complete!")
                            
                            cols = st.columns(2)
                            for i, part in enumerate(response.candidates[0].content.parts):
                                if part.text is not None:
                                    cols[0].markdown(f"### 🤖 AI Notes")
                                    cols[0].write(part.text)
                                elif part.inline_data is not None:
                                    edited_image = Image.open(BytesIO(part.inline_data.data))
                                    cols[1].markdown(f"### 🖼️ Edited Image")
                                    cols[1].image(edited_image, 
                                                use_container_width=True, 
                                                caption=f"Your enhanced creation ({edit_style} style)")
                                    
                                    buf = BytesIO()
                                    edited_image.save(buf, format="PNG")
                                    byte_im = buf.getvalue()
                                    cols[1].download_button(
                                        label="📥 Download Edited Image",
                                        data=byte_im,
                                        file_name=f"nexusai_edited_{edit_style.lower().replace(' ', '_')}.png",
                                        mime="image/png",
                                        use_container_width=True
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
    <p>Powered by cutting-edge AI technology - Video Generation via Kling AI & Image Generation via Gemini AI</p>
</div>
""", unsafe_allow_html=True)
