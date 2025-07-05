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

/* [Keep all your existing CSS styles here] */
</style>
""", unsafe_allow_html=True)

# =============================================
# Kling AI API Configuration
# =============================================
KLING_API_URL = "https://api-singapore.klingai.com"  # Base endpoint only
ACCESS_KEY = "A9GQdrBN9LndCkQy3DHfKtKF88b4QKLF"
SECRET_KEY = "hhgHaAe3Enek4fFaf8N3HHPmmAmFpJtM"

headers = {
    "AccessKey": ACCESS_KEY,
    "SecretKey": SECRET_KEY,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# =============================================
# API Verification & Helper Functions
# =============================================
def verify_dns_resolution():
    """Verify the API domain resolves"""
    try:
        domain = KLING_API_URL.split('//')[1].split('/')[0]
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False

def verify_api_connection():
    """Check if API is reachable"""
    try:
        # First verify DNS
        if not verify_dns_resolution():
            return False, "DNS resolution failed"
            
        # Try a HEAD request to avoid potential large responses
        response = requests.head(
            KLING_API_URL,
            headers=headers,
            timeout=10,
            allow_redirects=True
        )
        return response.status_code < 500, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

# =============================================
# Kling AI API Functions (Fixed)
# =============================================
def generate_video(prompt, duration=5, resolution="1080p", style="cinematic"):
    """Generate video with robust error handling"""
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
        
        # Debug raw response
        debug_msg = f"Status: {response.status_code}, Response: {response.text[:200]}"
        print(debug_msg)  # For debugging
        
        # Handle empty response
        if not response.content:
            return {
                "status": "error",
                "message": "Empty response from server",
                "debug": debug_msg
            }
            
        # Try parsing JSON
        try:
            data = response.json()
        except ValueError:
            return {
                "status": "error",
                "message": "Invalid JSON response",
                "debug": debug_msg
            }
            
        # Check for success
        if response.status_code == 200:
            if "task_id" in data:
                return {
                    "status": "processing",
                    "task_id": data["task_id"],
                    "message": data.get("message", "")
                }
            return {
                "status": "error",
                "message": data.get("error", "Missing task_id in response"),
                "debug": debug_msg
            }
            
        return {
            "status": "error",
            "message": f"API Error {response.status_code}: {data.get('message', 'Unknown error')}",
            "debug": debug_msg
        }
        
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "message": f"Request failed: {str(e)}",
            "debug": str(e)
        }

def check_video_status(task_id):
    """Check video generation status"""
    try:
        # Kling AI typically uses POST for status checks too
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
        except ValueError:
            return {
                "status": "error",
                "message": f"Invalid JSON: {response.text[:200]}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Status check failed: {str(e)}"
        }

# =============================================
# Gemini AI Configuration (Keep Existing)
# =============================================
@st.cache_resource
def init_client():
    return genai.Client(api_key='AIzaSyCZ-1xA0qHy7p3l5VdZYCrvoaQhpMZLjig')

client = init_client()

# =============================================
# Session State Initialization
# =============================================
if "generated_video" not in st.session_state:
    st.session_state.generated_video = None
if "generation_status" not in st.session_state:
    st.session_state.generation_status = "ready"
if "task_id" not in st.session_state:
    st.session_state.task_id = None
if "last_error" not in st.session_state:
    st.session_state.last_error = None

# =============================================
# Main Application UI
# =============================================
st.title("🚀 NexusAI Complete Studio")
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h3>The ultimate AI content creation platform</h3>
    <p>Generate stunning videos and images with the power of advanced AI</p>
</div>
""", unsafe_allow_html=True)

# Verify API connection at startup
if 'api_verified' not in st.session_state:
    st.session_state.api_verified, st.session_state.api_error = verify_api_connection()
    if not st.session_state.api_verified:
        st.error(f"""
        ⚠️ Kling AI API Connection Failed:
        {st.session_state.api_error}
        
        Please check:
        1. Your internet connection
        2. API keys are correct
        3. The service is available
        """)
        st.stop()

# [Rest of your existing UI code for sidebar, video generation, etc.]
# Keep all your existing Streamlit UI components exactly as they were
# Only the API interaction functions above have been modified

# =============================================
# Enhanced Error Display
# =============================================
def display_error_details(error_data):
    """Show detailed error information"""
    with st.expander("🚨 Error Details (Click to View)"):
        st.code(f"""
        Error Message: {error_data.get("message", "Unknown error")}
        Status Code: {error_data.get("status_code", "N/A")}
        Debug Info: {error_data.get("debug", "No debug info")}
        """)
        
        st.markdown("### 🛠️ Troubleshooting Tips")
        st.markdown("""
        1. Check your internet connection
        2. Verify your API keys are correct
        3. Try a simpler prompt
        4. Wait a few minutes and try again
        5. Contact support if the problem persists
        """)

# =============================================
# Updated Video Generation Section
# =============================================
if generation_mode == "🎥 Video Generation":
    # [Keep your existing UI code]
    
    if generate_video_button and video_prompt:
        st.session_state.generation_status = "generating"
        with st.spinner("🎥 Creating your video masterpiece..."):
            progress_bar = st.progress(0)
            
            # Simulate progress
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
                st.session_state.last_error = result
                st.error(result["message"])
                display_error_details(result)

# [Keep all other existing code for image generation, editing, etc.]
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
                    st.error("Generated video but missing URL in response")
                    display_error_details(status)
            
            elif status.get("status") == "error":
                st.session_state.generation_status = "error"
                st.error(status["message"])
                display_error_details(status)
            
            else:
                time.sleep(5)  # Wait before checking again
                st.rerun()
    
    # Display previous result if available
    if st.session_state.generated_video and st.session_state.generation_status == "completed":
        st.markdown("### 🎬 Your Generated Video")
        with st.container():
            st.video(st.session_state.generated_video)
            
            # Enhanced download button with error handling
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
    
    # Enhanced example prompts section
    with st.expander("💡 Video Example Prompts", expanded=False):
        tab1, tab2, tab3 = st.tabs(["🌆 Scenes", "🎭 Characters", "🎨 Artistic"])
        
        with tab1:
            st.markdown("""
            **Urban Landscapes:**
            - "Cyberpunk Tokyo at night with holographic advertisements and flying cars, neon reflections on wet streets"
            - "Futuristic megacity with towering skyscrapers and aerial highways, golden hour lighting"
            
            **Nature:**
            - "Serene mountain lake at dawn with mist rising, cinematic drone flyover"
            """)
        
        with tab2:
            st.markdown("""
            **Character Scenes:**
            - "Anime-style warrior in glowing armor battling a dragon, dynamic camera angles"
            - "Robotic bartender in a neon-lit speakeasy, close-up of mixing drinks"
            """)
        
        with tab3:
            st.markdown("""
            **Artistic Styles:**
            - "Watercolor animation of Paris changing through four seasons"
            - "Oil painting style portrait of a steampunk inventor in workshop"
            """)

elif generation_mode == "✨ Image Generation":
    st.header("🖼️ Image Generation Studio")
    
    with st.form("image_generation_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            image_prompt = st.text_area(
                "Describe your vision...",
                height=200,
                placeholder="A cybernetic owl with neon wings perched on a futuristic skyscraper with holographic advertisements..."
            )

            # Advanced image settings
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
            - Example: *"A cybernetic samurai standing on a neon-lit rooftop at dusk, intricate armor glowing with circuit patterns"*
            """)
            
            st.markdown("### 🎨 Style Guide")
            st.markdown("""
            - **Photorealistic**: Camera-like quality
            - **3D Rendered**: CGI game asset style
            - **Cyberpunk**: Neon-noir aesthetic
            - **Watercolor**: Painterly artistic look
            """)

    if generate_image_button and image_prompt:
        with st.spinner("✨ Generating your futuristic vision..."):
            progress_bar = st.progress(0)

            # Smooth progress animation
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

                            # Enhanced download options
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
                st.session_state.last_error = {
                    "message": str(e),
                    "type": "image_generation"
                }

elif generation_mode == "🖌️ Image Editing":
    st.header("🖌️ Image Editing Studio")
    
    uploaded_file = st.file_uploader(
        "Upload an image to edit", 
        type=["png", "jpg", "jpeg"], 
        accept_multiple_files=False
    )
    
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
            
            # Editing style options
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
                                    
                                    # Enhanced download options
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
                        st.session_state.last_error = {
                            "message": str(e),
                            "type": "image_editing"
                        }

# Display detailed error if one exists
if st.session_state.get('last_error'):
    with st.expander("⚠️ Last Error Details", expanded=False):
        st.error(st.session_state.last_error["message"])
        st.json(st.session_state.last_error)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid var(--primary);">
    <p>© 2025 NexusAI Complete Studio | All Rights Reserved</p>
    <p>Powered by cutting-edge AI technology - Video Generation via Kling AI & Image Generation via Gemini AI</p>
</div>
""", unsafe_allow_html=True)
