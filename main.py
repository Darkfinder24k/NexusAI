import requests
import json
import streamlit as st
from PIL import Image
import io
import time
from google import genai
from google.genai import types
from io import BytesIO

# Configure page with futuristic UI
st.set_page_config(
    page_title="NexusAI Media Studio",
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
</style>
""", unsafe_allow_html=True)

# A4F API Configuration
A4F_API_KEY = "ddc-a4f-b752e3e2936149f49b1b306953e0eaab"  # Replace with your actual API key
A4F_API_URL = "https://api.a4f.co/v1/video/generations"

# Initialize Gemini client
@st.cache_resource
def init_client():
    return genai.Client(api_key='AIzaSyCZ-1xA0qHy7p3l5VdZYCrvoaQhpMZLjig')

client = init_client()

# App header
st.title("🚀 NexusAI Media Studio")
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h3>The most advanced AI media generation platform in the universe</h3>
    <p>Create stunning futuristic visuals and videos with the power of Nexus AI</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Control Panel")
    st.markdown("---")
    
    content_type = st.radio(
        "Content Type",
        ["Image", "Video"],
        index=0
    )
    
    if content_type == "Image":
        image_style = st.selectbox(
            "Image Style",
            ["3D Rendered", "Cyberpunk", "Sci-Fi", "Futuristic", "Neon", "Holographic"],
            index=2
        )
    else:
        video_duration = st.slider("Video Duration (seconds)", 2, 60, 5)
        video_resolution = st.selectbox("Resolution", ["720p", "1080p", "4K", "8K", "10K", "12K", "14K"], index=1)
        video_style = st.selectbox(
            "Video Style", 
            ["Cinematic", "Cyberpunk", "Sci-Fi", "Anime", "3D Animation", "Holographic"],
            index=0
        )
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center;">
        <p>Powered by Quantora AI</p>
        <p>v3.0.1 | Nexus Core</p>
    </div>
    """, unsafe_allow_html=True)

# Main content area with tabs
tab1, tab2 = st.tabs(["✨ Generate", "🖌️ Edit"])

with tab1:
    with st.form("generation_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            prompt = st.text_area(
                "Describe your vision...",
                height=200,
                placeholder="A cybernetic owl with neon wings soaring through a futuristic cityscape with holographic advertisements..." 
                if content_type == "Image" else 
                "A futuristic cityscape at night with flying cars and neon lights, cinematic style"
            )

            generate_button = st.form_submit_button(
                f"Generate {content_type}",
                type="primary"
            )

        with col2:
            st.markdown("### 💡 Prompt Tips")
            if content_type == "Image":
                st.markdown("""
                - Be descriptive with details
                - Mention lighting, style, mood
                - Include futuristic elements
                - Example: "A floating city at sunset with neon lights reflecting on the water, in cyberpunk style"
                """)
            else:
                st.markdown("""
                - Describe the scene, action, and style
                - Include camera movements if desired
                - Example: "A drone shot flying through a neon-lit cyberpunk city at night, cinematic style"
                """)

    if generate_button and prompt:
        with st.spinner(f"Generating your futuristic {content_type.lower()}..."):
            progress_bar = st.progress(0)

            for percent_complete in range(100):
                time.sleep(0.02)
                progress_bar.progress(percent_complete + 1)

            try:
                if content_type == "Image":
                    # Enhanced prompt with style
                    enhanced_prompt = f"{prompt}, {image_style} style, ultra HD, photorealistic, cinematic lighting"

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
                                cols[0].markdown(f"### AI Notes")
                                cols[0].write(part.text)
                            elif part.inline_data is not None:
                                image = Image.open(BytesIO((part.inline_data.data)))
                                cols[1].markdown(f"### Generated Image")
                                cols[1].image(image, use_container_width=True, 
                                            caption="Your futuristic creation",
                                            output_format="PNG")

                                # Save option
                                buf = BytesIO()
                                image.save(buf, format="PNG")
                                byte_im = buf.getvalue()
                                cols[1].download_button(
                                    label="Download Image",
                                    data=byte_im,
                                    file_name="nexusai_generation.png",
                                    mime="image/png"
                                )
                    else:
                        st.error("No image was generated. Please try a different prompt.")

                else:  # Video generation
                    headers = {
                        "Authorization": f"Bearer {A4F_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    
                    data = {
                        "model": "provider-6/wan-2.1",
                        "prompt": f"{prompt}, {video_style} style",
                        "duration": video_duration,
                        "resolution": video_resolution,
                        "style": video_style.lower().replace(" ", "-"),
                        "parameters": {
                            "temperature": 0.7,
                            "seed": int(time.time()),
                            "steps": 30,
                            "cfg_scale": 7.5
                        }
                    }
                    
                    response = requests.post(
                        A4F_API_URL,
                        headers=headers,
                        json=data,
                        timeout=60
                    )
                    response.raise_for_status()
                    
                    if response.status_code == 202:
                        job_id = response.json().get("job_id")
                        st.session_state.video_job_id = job_id
                        st.session_state.generation_status = "processing"
                        st.info("⏳ Video is being generated. Please wait...")
                    else:
                        video_url = response.json().get("video_url")
                        if video_url:
                            st.success("🎥 Video generation complete!")
                            st.video(video_url)
                            
                            # Download button
                            video_bytes = requests.get(video_url).content
                            st.download_button(
                                label="📥 Download Video",
                                data=video_bytes,
                                file_name="generated_video.mp4",
                                mime="video/mp4"
                            )
                        else:
                            st.error("Video generation failed. Please try again.")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Polling for async video jobs
if hasattr(st.session_state, 'generation_status') and st.session_state.generation_status == "processing":
    with st.spinner("🔄 Checking video generation status..."):
        try:
            headers = {
                "Authorization": f"Bearer {A4F_API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{A4F_API_URL}/status/{st.session_state.video_job_id}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            status = response.json()
            
            if status.get("status") == "completed":
                st.session_state.generation_status = "completed"
                video_url = status.get("video_url")
                
                st.success("🎥 Video generation complete!")
                st.video(video_url)
                
                # Download button
                video_bytes = requests.get(video_url).content
                st.download_button(
                    label="📥 Download Video",
                    data=video_bytes,
                    file_name="generated_video.mp4",
                    mime="video/mp4"
                )
                
                st.rerun()
            elif status.get("status") == "error":
                st.session_state.generation_status = "error"
                st.error(status.get("message", "Video generation failed"))
            else:
                time.sleep(5)
                st.rerun()
                
        except Exception as e:
            st.error(f"Error checking video status: {str(e)}")

with tab2:
    st.markdown(f"## 🖌️ {content_type} Editing Studio")
    
    uploaded_file = st.file_uploader(
        f"Upload a {content_type.lower()} to edit", 
        type=["png", "jpg", "jpeg"] if content_type == "Image" else ["mp4", "mov"]
    )
    
    if uploaded_file is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            if content_type == "Image":
                original_content = Image.open(uploaded_file)
                st.image(original_content, caption="Original Image", use_container_width=True)
            else:
                st.video(uploaded_file)
                original_content = uploaded_file.read()
                st.caption("Original Video")
        
        with col2:
            edit_instructions = st.text_area(
                "Editing instructions",
                height=150,
                placeholder="Add a futuristic cityscape in the background, make it cyberpunk style..." 
                if content_type == "Image" else
                "Add flying cars, make the scene at night with neon lights, cyberpunk style..."
            )
            
            edit_button = st.button(
                "Apply Edits",
                use_container_width=True,
                key="edit_button"
            )
            
            if edit_button and edit_instructions:
                with st.spinner("Transforming your content..."):
                    progress_bar = st.progress(0)
                    
                    for percent_complete in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(percent_complete + 1)
                    
                    try:
                        if content_type == "Image":
                            # Create the content parts
                            contents = [
                                edit_instructions,
                                original_content
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
                                        edited_content = Image.open(BytesIO(part.inline_data.data))
                                        cols[1].markdown(f"### Edited Image")
                                        cols[1].image(edited_content, 
                                                    use_container_width=True, 
                                                    caption="Your enhanced creation", 
                                                    output_format="PNG")
                                        
                                        # Save option
                                        buf = BytesIO()
                                        edited_content.save(buf, format="PNG")
                                        byte_im = buf.getvalue()
                                        cols[1].download_button(
                                            label="Download Edited Image",
                                            data=byte_im,
                                            file_name="nexusai_edited.png",
                                            mime="image/png"
                                        )
                            else:
                                st.error("The image could not be edited. Please try different instructions.")
                        
                        else:  # Video editing
                            st.warning("Video editing is currently in beta. Please check back soon!")
                            # Placeholder for future video editing implementation
                            # Would use similar A4F API call with the original video and edit instructions
                    
                    except Exception as e:
                        st.error(f"An error occurred during editing: {str(e)}")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid var(--primary);">
    <p>© 2025 NexusAI Studios | All Rights Reserved</p>
    <p>Powered by the cutting-edge Quantora AI technology</p>
</div>
""", unsafe_allow_html=True)
