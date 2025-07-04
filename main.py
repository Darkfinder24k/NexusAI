import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64
import time

# Configure page
st.set_page_config(
    page_title="NexusAI Image Studio",
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

/* Animation for generated images */
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

# Initialize Gemini client
@st.cache_resource
def init_client():
    return genai.Client(api_key='AIzaSyCZ-1xA0qHy7p3l5VdZYCrvoaQhpMZLjig')

client = init_client()

# App header
st.title("🚀 NexusAI Image Studio")
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h3>The most advanced AI image generation platform in the universe</h3>
    <p>Create stunning futuristic visuals with the power of Nexus AI</p>
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
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center;">
        <p>Powered by Quantora AI</p>
        <p>v2.3.7 | Nexus Core</p>
    </div>
    """, unsafe_allow_html=True)

# Main content area with tabs
tab1, tab2 = st.tabs(["✨ Generate", "🖌️ Edit"])

with tab1:
    with st.form("image_generation_form"):
        col1, col2 = st.columns([2, 1])

        with col1:
            prompt = st.text_area(
                "Describe your vision...",
                height=200,
                placeholder="A cybernetic owl with neon wings perched on a futuristic skyscraper with holographic advertisements in the background..."
            )

            generate_button = st.form_submit_button(
                "Generate Image",
                type="primary"
            )

        with col2:
            st.markdown("### 💡 Prompt Tips")
            st.markdown("""
            - Be descriptive with details
            - Mention lighting, style, mood
            - Include futuristic elements
            - Example: "A floating city at sunset with neon lights reflecting on the water, in cyberpunk style"
            """)

    if generate_button and prompt:
        with st.spinner("Generating your futuristic vision..."):
            progress_bar = st.progress(0)

            for percent_complete in range(100):
                time.sleep(0.02)
                progress_bar.progress(percent_complete + 1)

            try:
                # Enhanced prompt with style
                enhanced_prompt = f"{prompt}, {image_style} style, ultra HD, photorealistic, cinematic lighting"

                response = client.models.generate_content(
                    model='imagen-4.0-ultra-generate-preview-06-06',
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
                            cols[1].image(image, use_container_width=True, caption="Your futuristic creation",
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

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

with tab2:
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
                placeholder="Add a llama next to me, make the background futuristic, add holographic elements..."
            )
            
            edit_button = st.button(
                "Apply Edits",
                use_container_width=True,
                key="edit_button"
            )
            
            if edit_button and edit_instructions:
                with st.spinner("Transforming your image..."):
                    progress_bar = st.progress(0)
                    
                    for percent_complete in range(100):
                        time.sleep(0.02)
                        progress_bar.progress(percent_complete + 1)
                    
                    try:
                        # Create the content parts
                        contents = [
                            edit_instructions,
                            original_image
                        ]
                        
                        response = client.models.generate_content(
                            model="imagen-4.0-ultra-generate-preview-06-06",
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
                                                caption="Your enhanced creation", 
                                                output_format="PNG")
                                    
                                    # Save option
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
                            st.error("The image could not be edited. Please try different instructions.")
                    
                    except Exception as e:
                        st.error(f"An error occurred during editing: {str(e)}")

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 50px; padding: 20px; border-top: 1px solid var(--primary);">
    <p>© 2025 NexusAI Studios | All Rights Reserved</p>
    <p>Powered by the cutting-edge Quantora AI technology</p>
</div>
""", unsafe_allow_html=True)
