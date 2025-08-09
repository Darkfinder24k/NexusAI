import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import time
import requests
import json

# Configure page
st.set_page_config(
    page_title="NexusAI Creative Studio",
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

@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}

.generated-image {
    animation: float 4s ease-in-out infinite;
    border: 2px solid var(--primary);
    border-radius: 10px;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
    transition: all 0.3s ease;
}

.generated-image:hover {
    transform: scale(1.02);
    box-shadow: 0 0 30px rgba(0, 240, 255, 0.8);
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

video {
    border: 2px solid var(--primary);
    border-radius: 10px;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.5);
    width: 100%;
    margin-bottom: 20px;
}

.generated-video {
    animation: float 6s ease-in-out infinite;
}
</style>
""", unsafe_allow_html=True)

# API Configuration - URL is fixed exactly as specified
A4F_API_KEY = "ddc-a4f-b752e3e2936149f49b1b306953e0eaab"
A4F_BASE_URL = "https://api.a4f.co/v1"  # This exact URL remains unchanged
IMAGE_MODEL = "provider-4/imagen-4"
VIDEO_MODEL = "provider-6/wan-2.1"

# Initialize Gemini client for image editing
@st.cache_resource
def init_client():
    return genai.Client(api_key='AIzaSyCZ-1xA0qHy7p3l5VdZYCrvoaQhpMZLjig')

client = init_client()

# App header
st.title("🚀 NexusAI Creative Studio")
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h3>The ultimate AI image and video generation platform</h3>
    <p>Create stunning futuristic content with cutting-edge AI</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Control Panel")
    st.markdown("---")
    
    image_style = st.selectbox(
        "Image Style",
        ["3D Rendered", "Cyberpunk", "Sci-Fi", "Futuristic", "Neon", "Holographic"],
        index=2
    )
    
    video_style = st.selectbox(
        "Video Style",
        ["Cinematic", "Anime", "Realistic", "Cyberpunk", "Sci-Fi", "Futuristic"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center;">
        <p>Powered by Quantora AI</p>
        <p>v3.0.0 | Nexus Core</p>
    </div>
    """, unsafe_allow_html=True)

def generate_image(prompt, style):
    """Generate image using A4F API with fixed URL"""
    headers = {
        "Authorization": f"Bearer {A4F_API_KEY}",
        "Content-Type": "application/json"
    }
    
    enhanced_prompt = f"{prompt}, {style} style, ultra HD, photorealistic, cinematic lighting"
    
    payload = {
        "model": IMAGE_MODEL,
        "prompt": enhanced_prompt,
        "num_images": 1,
        "width": 1024,
        "height": 1024,
        "steps": 50,
        "guidance_scale": 7.5
    }
    
    try:
        response = requests.post(
            f"{A4F_BASE_URL}/v1/images/generations",  # Using the exact fixed URL
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and len(result['data']) > 0:
                image_url = result['data'][0]['url']
                image_response = requests.get(image_url, timeout=30)
                if image_response.status_code == 200:
                    return Image.open(BytesIO(image_response.content))
        return None
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

def generate_video(prompt, style):
    """Generate video using A4F API with fixed URL"""
    headers = {
        "Authorization": f"Bearer {A4F_API_KEY}",
        "Content-Type": "application/json"
    }
    
    enhanced_prompt = f"{prompt}, {style} style, cinematic, high quality, 4K resolution"
    
    payload = {
        "model": VIDEO_MODEL,
        "prompt": enhanced_prompt,
        "num_videos": 1,
        "width": 1024,
        "height": 576,
        "duration": 4,
        "fps": 24
    }
    
    try:
        response = requests.post(
            f"{A4F_BASE_URL}/v1/video/generations",  # Using the exact fixed URL
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and len(result['data']) > 0:
                return result['data'][0]['url']
        return None
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

# Main content area with tabs
tab1, tab2, tab3 = st.tabs(["🖼️ Generate Image", "🎥 Generate Video", "🖌️ Edit Image"])

with tab1:
    with st.form("image_generation_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            prompt = st.text_area(
                "Describe your image...",
                height=200,
                placeholder="A cybernetic owl with neon wings perched on a futuristic skyscraper..."
            )

            generate_button = st.form_submit_button(
                "Generate Image",
                type="primary"
            )

        with col2:
            st.markdown("### 💡 Prompt Tips")
            st.markdown("""
            - Be descriptive with details
            - Mention lighting and style
            - Include futuristic elements
            - Example: "A floating city at sunset with neon lights"
            """)

    if generate_button and prompt:
        with st.spinner("Generating your vision..."):
            progress_bar = st.progress(0)
            
            for percent_complete in range(100):
                time.sleep(0.02)
                progress_bar.progress(percent_complete + 1)
            
            try:
                generated_image = generate_image(prompt, image_style)
                
                if generated_image:
                    st.success("✨ Image generation complete!")
                    
                    cols = st.columns(2)
                    cols[0].markdown("### AI Notes")
                    cols[0].write("Your futuristic image has been created!")
                    
                    cols[1].markdown("### Generated Image")
                    cols[1].image(generated_image, 
                                use_container_width=True, 
                                caption="Your creation",
                                output_format="PNG")

                    buf = BytesIO()
                    generated_image.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    cols[1].download_button(
                        label="Download Image",
                        data=byte_im,
                        file_name="nexusai_image.png",
                        mime="image/png"
                    )
                else:
                    st.error("Image generation failed. Please try again.")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")

with tab2:
    with st.form("video_generation_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            video_prompt = st.text_area(
                "Describe your video...",
                height=200,
                placeholder="Flying cars zooming between neon-lit skyscrapers at night..."
            )

            generate_video_button = st.form_submit_button(
                "Generate Video",
                type="primary"
            )

        with col2:
            st.markdown("### 💡 Video Tips")
            st.markdown("""
            - Describe movement and action
            - Specify camera angles
            - Example: "A spaceship landing on an alien planet"
            """)

    if generate_video_button and video_prompt:
        with st.spinner("Creating your video..."):
            progress_bar = st.progress(0)
            
            for percent_complete in range(100):
                time.sleep(0.05)
                progress_bar.progress(percent_complete + 1)
            
            try:
                video_url = generate_video(video_prompt, video_style)
                
                if video_url:
                    st.success("🎬 Video generation complete!")
                    st.markdown("### Your Generated Video")
                    
                    # Display video with animation
                    st.markdown('<div class="generated-video">', unsafe_allow_html=True)
                    st.video(video_url)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Download button
                    video_data = requests.get(video_url).content
                    st.download_button(
                        label="Download Video",
                        data=video_data,
                        file_name="nexusai_video.mp4",
                        mime="video/mp4"
                    )
                else:
                    st.error("Video generation failed. Please try again.")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")

with tab3:
    st.markdown("## 🖌️ Image Editing Studio")
    
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
                placeholder="Make the background futuristic, add holographic elements..."
            )
            
            edit_button = st.button(
                "Apply Edits",
                use_container_width=True,
                key="edit_button"
            )
            
            if edit_button and edit_instructions:
                with st.spinner("Editing your image..."):
                    progress_bar = st.progress(0)
                    
                    for percent_complete in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(percent_complete + 1)
                    
                    try:
                        contents = [
                            edit_instructions,
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
                                    cols[0].markdown(f"### AI Notes")
                                    cols[0].write(part.text)
                                elif part.inline_data is not None:
                                    edited_image = Image.open(BytesIO(part.inline_data.data))
                                    cols[1].markdown(f"### Edited Image")
                                    cols[1].image(edited_image, 
                                                use_container_width=True, 
                                                caption="Enhanced creation", 
                                                output_format="PNG")
                                    
                                    buf = BytesIO()
                                    edited_image.save(buf, format="PNG")
                                    byte_im = buf.getvalue()
                                    cols[1].download_button(
                                        label="Download Edited Image",
                                        data=byte_im,
                                        file_name="nexusai_edited.png",
                                        mime="image/png"
                                    )
                        else:
                            st.error("Editing failed. Please try different instructions.")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid var(--primary);">
    <p>© 2025 NexusAI Studios | All Rights Reserved</p>
    <p>Using fixed API URL: https://api.a4f.co/v1</p>
</div>
""", unsafe_allow_html=True)
