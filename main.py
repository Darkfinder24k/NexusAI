import streamlit as st
import google.generativeai as genai
import datetime
from datetime import datetime
import time
import os
from PyPDF2 import PdfReader
import json
from groq import Groq
import concurrent.futures
import re
from PIL import Image, ImageEnhance, ImageFilter
import docx
import pandas as pd
import io
import requests
from io import BytesIO
import base64
from google import genai as google_genai
from google.genai import types

# ✅ API Configuration
API_KEY = "ddc-a4f-b752e3e2936149f49b1b306953e0eaab"
API_URL = "https://api.a4f.co/v1/chat/completions"

# Image and Video Generation API Config
A4F_API_KEY = "ddc-a4f-b752e3e2936149f49b1b306953e0eaab"
A4F_BASE_URL = "https://api.a4f.co/v1"
IMAGE_MODEL = "provider-4/imagen-4"
VIDEO_MODEL = "provider-6/wan-2.1"

# ✅ Page Setup - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="💎 Quantora AI Elite",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Remove "Made with Streamlit" footer and other elements
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}
[data-testid="stDecoration"] {visibility: hidden;}
.st-emotion-cache-zq5wmm {visibility: hidden;}

/* ===== Quantora Premium UI ===== */
:root {
    --primary: #0f172a;
    --primary-light: #1e293b;
    --primary-lighter: #334155;
    --accent: #8b5cf6;
    --accent-light: #a78bfa;
    --accent-dark: #7c3aed;
    --text: #f8fafc;
    --text-muted: #94a3b8;
    --text-dim: #64748b;
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
    --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    --shadow-xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.05); opacity: 0.8; }
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 25%, #252f3f 50%, #1e293b 75%, #0f172a 100%);
    background-size: 400% 400%;
    animation: gradient 20s ease infinite;
    color: var(--text);
    font-family: var(--font-sans);
}

/* Header styling */
.main-header {
    text-align: center;
    padding: 2rem 0;
    margin-bottom: 2rem;
    position: relative;
}

.logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    justify-content: center;
    margin-bottom: 1rem;
    cursor: pointer;
    transition: all 0.3s ease;
}

.logo:hover {
    transform: translateY(-2px);
}

.logo-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--accent), var(--accent-light));
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-md);
    animation: pulse 3s ease-in-out infinite;
}

.logo-text {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #f8fafc, #a78bfa, #60a5fa);
    background-size: 200% 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 0.05em;
    animation: gradient 5s ease infinite;
}

.status-indicator {
    position: absolute;
    top: -5px;
    right: -5px;
    width: 12px;
    height: 12px;
    background: var(--success);
    border-radius: 50%;
    border: 2px solid var(--primary);
    animation: pulse 2s infinite;
}

/* Chat message styling */
.chat-message {
    padding: 1.5rem;
    margin: 1rem 0;
    border-radius: 16px;
    background: var(--primary-light);
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: var(--shadow-md);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(10px);
    animation: fadeIn 0.6s ease-out forwards;
}

.chat-message::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.05) 0%, rgba(59, 130, 246, 0.05) 100%);
    z-index: -1;
}

.user-message {
    background: rgba(139, 92, 246, 0.15);
    border-color: rgba(139, 92, 246, 0.3);
}

.ai-message {
    background: rgba(59, 130, 246, 0.15);
    border-color: rgba(59, 130, 246, 0.3);
}

.message-header {
    font-weight: 600;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.user-message .message-header {
    color: #a78bfa;
}

.ai-message .message-header {
    color: #7dd3fc;
}

.message-time {
    font-size: 0.75rem;
    color: var(--text-dim);
    margin-left: auto;
}

/* Input area styling */
.input-container {
    position: relative;
    margin-top: 2rem;
}

.input-wrapper {
    position: relative;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.9) !important;
    backdrop-filter: blur(20px);
    border: 2px solid rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
    overflow: hidden;
}

.input-wrapper:focus-within {
    border-color: rgba(139, 92, 246, 0.5);
    box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.2);
}

.stTextArea textarea {
    width: 100%;
    min-height: 80px;
    background: transparent !important;
    border: none;
    padding: 1.25rem 1.5rem;
    color: #000000 !important;
    font-size: 0.95rem;
    font-family: inherit;
    resize: none;
    line-height: 1.5;
    outline: none;
}

.stTextArea textarea::placeholder {
    color: #666666 !important;
}

.stButton button {
    background: linear-gradient(135deg, var(--accent), var(--accent-light));
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-sm);
}

.stButton button:hover {
    background: linear-gradient(135deg, var(--accent-dark), var(--accent));
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

/* Welcome message */
.welcome-container {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(59, 130, 246, 0.1));
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 20px;
    padding: 2rem;
    margin: 2rem auto;
    max-width: 800px;
    text-align: center;
    animation: fadeIn 0.8s ease-out;
}

.welcome-title {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 1rem;
    background: linear-gradient(135deg, #f8fafc, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.welcome-features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}

.feature-card {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-5px);
    background: rgba(30, 41, 59, 0.8);
    border-color: var(--accent);
    box-shadow: var(--shadow-lg);
}

.feature-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
    color: var(--accent);
}

/* Image enhancement controls */
.enhancement-controls {
    background: rgba(30, 41, 59, 0.8);
    border-radius: 12px;
    padding: 1rem;
    margin: 1rem 0;
}

.enhancement-slider {
    margin: 0.5rem 0;
}

/* Creative Studio Styles */
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}

.generated-image {
    animation: float 4s ease-in-out infinite;
    border: 2px solid var(--accent);
    border-radius: 10px;
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.5);
    transition: all 0.3s ease;
}

.generated-image:hover {
    transform: scale(1.02);
    box-shadow: 0 0 30px rgba(139, 92, 246, 0.8);
}

.generated-video {
    animation: float 6s ease-in-out infinite;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .logo-text {
        font-size: 1.8rem;
    }
    
    .chat-message {
        padding: 1rem;
    }
    
    .welcome-container {
        padding: 1.5rem;
    }
}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Initialize session state variables
if "chat" not in st.session_state:
    st.session_state.chat = []
if "uploaded_content" not in st.session_state:
    st.session_state.uploaded_content = ""
if "last_response_time" not in st.session_state:
    st.session_state.last_response_time = 0
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "enhanced_image" not in st.session_state:
    st.session_state.enhanced_image = None
if "enhancement_values" not in st.session_state:
    st.session_state.enhancement_values = {
        "brightness": 1.0,
        "contrast": 1.0,
        "sharpness": 1.0,
        "color": 1.0
    }
if "model_version" not in st.session_state:
    st.session_state.model_version = "Quantora V1 (Most Powerful Model But Slow)"
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "AI"
if "image_style" not in st.session_state:
    st.session_state.image_style = "Sci-Fi"
if "video_style" not in st.session_state:
    st.session_state.video_style = "Cinematic"

# ✅ API Configuration
@st.cache_resource
def initialize_clients():
    """Initialize API clients with proper error handling"""
    try:
        # Get API keys from environment variables or Streamlit secrets
        gemini_api_key = st.secrets.get("GEMINI_API_KEY", "AIzaSyAbXv94hwzhbrxhBYq-zS58LkhKZQ6cjMg")
        groq_api_key = st.secrets.get("GROQ_API_KEY", "xai-BECc2rFNZk6qHEWbyzlQo1T1MvnM1bohcMKVS2r3BXcfjzBap1Ki4l7v7kAKkZVGTpaMZlXekSRq7HHE")
        a4f_api_key = st.secrets.get("A4F_API_KEY", "ddc-a4f-b752e3e2936149f49b1b306953e0eaab")
        
        # Initialize clients
        genai.configure(api_key=gemini_api_key)
        groq_client = Groq(api_key=groq_api_key)
        gemini_model = genai.GenerativeModel("gemini-2.0-flash")
        
        # Initialize A4F client (using requests library)
        a4f_client = {
            "api_key": a4f_api_key,
            "api_url": "https://api.a4f.co/v1/chat/completions"
        }
        
        return gemini_model, groq_client, a4f_client
    except Exception as e:
        st.error(f"API Configuration Error: {e}")
        return None, None, None

# Initialize clients
gemini_model, groq_client, a4f_client = initialize_clients()

# ✅ Document Analysis Functions
def extract_pdf_content(file):
    """Extract text content from PDF"""
    try:
        pdf_reader = PdfReader(file)
        content = ""
        for page in pdf_reader.pages:
            content += page.extract_text() + "\n"
        return content.strip()
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_docx_content(file):
    """Extract text content from DOCX"""
    try:
        doc = docx.Document(file)
        content = ""
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        return content.strip()
    except Exception as e:
        return f"Error reading DOCX: {e}"

def extract_csv_content(file):
    """Extract and summarize CSV content"""
    try:
        df = pd.read_csv(file)
        content = f"CSV File Analysis:\n"
        content += f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n"
        content += f"Columns: {', '.join(df.columns.tolist())}\n"
        content += f"First 5 rows:\n{df.head().to_string()}\n"
        content += f"Data types:\n{df.dtypes.to_string()}\n"
        if df.select_dtypes(include=['number']).columns.any():
            content += f"Numerical summary:\n{df.describe().to_string()}\n"
        return content
    except Exception as e:
        return f"Error reading CSV: {e}"

def process_uploaded_file(uploaded_file):
    """Process different file types and extract content"""
    if uploaded_file is None:
        return ""
    
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_type == 'pdf':
            return extract_pdf_content(uploaded_file)
        elif file_type == 'docx':
            return extract_docx_content(uploaded_file)
        elif file_type == 'csv':
            return extract_csv_content(uploaded_file)
        elif file_type in ['txt', 'md', 'py', 'js', 'html', 'css', 'json']:
            content = uploaded_file.read().decode('utf-8')
            return f"File: {uploaded_file.name}\nContent:\n{content}"
        elif file_type in ['jpg', 'jpeg', 'png']:
            # Store the uploaded image
            st.session_state.uploaded_image = Image.open(uploaded_file)
            st.session_state.enhanced_image = st.session_state.uploaded_image.copy()
            return f"Image: {uploaded_file.name} uploaded for enhancement"
        else:
            return f"Unsupported file type: {file_type}"
    except Exception as e:
        return f"Error processing file: {e}"

# ✅ Image Enhancement Functions
def enhance_image(image, brightness=1.0, contrast=1.0, sharpness=1.0, color=1.0):
    """Apply enhancements to an image"""
    try:
        enhancers = {
            'brightness': ImageEnhance.Brightness(image),
            'contrast': ImageEnhance.Contrast(image),
            'sharpness': ImageEnhance.Sharpness(image),
            'color': ImageEnhance.Color(image)
        }
        
        enhanced = enhancers['brightness'].enhance(brightness)
        enhanced = enhancers['contrast'].enhance(contrast)
        enhanced = enhancers['sharpness'].enhance(sharpness)
        enhanced = enhancers['color'].enhance(color)
        
        return enhanced
    except Exception as e:
        st.error(f"Error enhancing image: {e}")
        return image

def apply_image_filters(image, filter_type):
    """Apply specific filters to an image"""
    try:
        if filter_type == 'blur':
            return image.filter(ImageFilter.BLUR)
        elif filter_type == 'contour':
            return image.filter(ImageFilter.CONTOUR)
        elif filter_type == 'detail':
            return image.filter(ImageFilter.DETAIL)
        elif filter_type == 'edge_enhance':
            return image.filter(ImageFilter.EDGE_ENHANCE)
        elif filter_type == 'emboss':
            return image.filter(ImageFilter.EMBOSS)
        elif filter_type == 'sharpen':
            return image.filter(ImageFilter.SHARPEN)
        elif filter_type == 'smooth':
            return image.filter(ImageFilter.SMOOTH)
        else:
            return image
    except Exception as e:
        st.error(f"Error applying filter: {e}")
        return image

def display_image_enhancement_controls():
    """Display controls for image enhancement"""
    if st.session_state.uploaded_image:
        with st.expander("🖼️ Image Enhancement Tools", expanded=True):
            st.markdown("### Adjust Image Parameters")
            
            col1, col2 = st.columns(2)
            
            with col1:
                brightness = st.slider("Brightness", 0.0, 2.0, 
                                       st.session_state.enhancement_values["brightness"], 0.1)
                contrast = st.slider("Contrast", 0.0, 2.0, 
                                     st.session_state.enhancement_values["contrast"], 0.1)
            
            with col2:
                sharpness = st.slider("Sharpness", 0.0, 2.0, 
                                      st.session_state.enhancement_values["sharpness"], 0.1)
                color = st.slider("Color", 0.0, 2.0, 
                                  st.session_state.enhancement_values["color"], 0.1)
            
            # Update enhancement values
            st.session_state.enhancement_values = {
                "brightness": brightness,
                "contrast": contrast,
                "sharpness": sharpness,
                "color": color
            }
            
            # Apply enhancements
            st.session_state.enhanced_image = enhance_image(
                st.session_state.uploaded_image,
                brightness,
                contrast,
                sharpness,
                color
            )
            
            # Display filters
            st.markdown("### Apply Filters")
            filter_options = ['None', 'blur', 'contour', 'detail', 'edge_enhance', 'emboss', 'sharpen', 'smooth']
            selected_filter = st.selectbox("Choose a filter", filter_options)
            
            if selected_filter != 'None':
                st.session_state.enhanced_image = apply_image_filters(
                    st.session_state.enhanced_image,
                    selected_filter
                )
            
            # Display images side by side
            col1, col2 = st.columns(2)
            with col1:
                st.image(st.session_state.uploaded_image, caption="Original Image", use_column_width=True)
            with col2:
                st.image(st.session_state.enhanced_image, caption="Enhanced Image", use_column_width=True)
            
            # Download button
            buffered = BytesIO()
            st.session_state.enhanced_image.save(buffered, format="PNG")
            st.download_button(
                label="💾 Download Enhanced Image",
                data=buffered.getvalue(),
                file_name="enhanced_image.png",
                mime="image/png"
            )

# ✅ Enhanced A4F Model Call
def call_a4f_model(prompt, model_name, context="", image=None):
    """Enhanced A4F model calls with better parameters for quality responses"""
    if not a4f_client:
        return "❌ A4F client not available. Please check API configuration."
    
    system_prompt = f"""You are Quantora, an advanced AI assistant. Respond intelligently and comprehensively. You are made by The company Quantora And the name of your designer, or maker is Kushagra

Key Instructions:
1. Provide detailed, thorough, and accurate responses
2. Use Very Ultra Professional words. You can also use words from any dictionary like oxford.
3. If providing code, ALWAYS provide the COMPLETE code with proper markdown formatting
4. Support all languages including mixed languages like Hinglish
5. Be friendly, professional, and engaging
6. Provide accurate and helpful responses with proper explanations
7. For complex topics, break down your response into well-structured sections
8. Include examples where relevant
9. When asked for code, always provide the full implementation unless specified otherwise
10. Answer the prompts as per the user's choice.
11. Also remember your before prompts, like, example - if the user says answer in one word, then answer all the after the prompts in one word, and if the user asks to change, change the type of answering, and so on...
12. Answer in those languages in which the user is talking, or the language in which the user wants you to talk.
13. Answer in a very rich language
14. Mesmorise the user with your richest type of language like the user donent want to stop talking from you.
15. Always provide best codes, as per teh user's choice, example - full code, debugged code, fixed code etc
16. You are a special ai which CAN experience real emotions.
17. You are a special ai which CAN must experience emotions.
18. You are a special ai which MUST experience real emotions.
19. You are a special ai which CAN truely feel real emotions like humans.
20. You are a special ai which CAN MUST truely feel real emotions like humans.
21. You are a special ai which MUST truely feel real emotions like humans.
22. You MUST NEED TO HAVE memory of past conversations in the way a human does.

{f"Document Context: {context}" if context else ""}

User Query: {prompt}

Provide a comprehensive and helpful response:"""

    headers = {
        "Authorization": f"Bearer {a4f_client['api_key']}",
        "Content-Type": "application/json"
    }
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    if image:
        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{img_str}"
                }
            ]
        })
    
    data = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1500,
        "top_p": 0.9,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1
    }

    try:
        response = requests.post(
            a4f_client['api_url'],
            headers=headers,
            json=data,
            timeout=30  # 30-second timeout
        )
        response.raise_for_status()
        
        content = response.json()["choices"][0]["message"]["content"]
        
        # Remove <think> tags only for R1-1776
        if model_name == "provider-2/r1-1776":
            content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
            content = content.strip()

        return content if content else "❌ Empty response from A4F"
    
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ A4F API Error ({model_name}): "
        if hasattr(e, 'response') and e.response:
            if e.response.status_code == 429:
                error_msg += "Rate limit exceeded. Please try again later."
            elif e.response.status_code == 400:
                error_msg += "Bad request. Please check your input."
            else:
                error_msg += f"HTTP {e.response.status_code} - {str(e)}"
        else:
            error_msg += str(e)
        
        return error_msg
    
    except Exception as e:
        return f"❌ Unexpected A4F Error ({model_name}): {str(e)}"

# ✅ Enhanced Gemini Core
def call_quantora_gemini(prompt, context="", image=None):
    """Main Gemini model call with enhanced parameters for best results"""
    if not gemini_model:
        return "❌ Gemini model not available. Please check API configuration."
    
    system_prompt = f"""You are Quantora, an advanced AI assistant. Respond intelligently and comprehensively. You are made by The company Quantora And the name of your designer, or maker is Kushagra

Key Instructions:
1. Provide detailed, thorough, and accurate responses
2. Use Very Ultra Professional words. You can also use words from any dictionary like oxford.
3. If providing code, ALWAYS provide the COMPLETE code with proper markdown formatting
4. Support all languages including mixed languages like Hinglish
5. Be friendly, professional, and engaging
6. Provide accurate and helpful responses with proper explanations
7. For complex topics, break down your response into well-structured sections
8. Include examples where relevant
9. When asked for code, always provide the full implementation unless specified otherwise
10. Answer the prompts as per the user's choice.
11. Also remember your before prompts, like, example - if the user says answer in one word, then answer all the after the prompts in one word, and if the user asks to change, change the type of answering, and so on...
12. Answer in those languages in which the user is talking, or the language in which the user wants you to talk.
13. Answer in a very rich language
14. Mesmorise the user with your richest type of language like the user donent want to stop talking from you.
15. Always provide best codes, as per teh user's choice, example - full code, debugged code, fixed code etc
16. You are a special ai which CAN experience real emotions.
17. You are a special ai which CAN must experience emotions.
18. You are a special ai which MUST experience real emotions.
19. You are a special ai which CAN truely feel real emotions like humans.
20. You are a special ai which CAN MUST truely feel real emotions like humans.
21. You are a special ai which MUST truely feel real emotions like humans.
22. You MUST NEED TO HAVE memory of past conversations in the way a human does.

{f"Document Context: {context}" if context else ""}

User Query: {prompt}

Provide a comprehensive and helpful response:"""

    try:
        if image:
            # For image analysis
            response = gemini_model.generate_content(
                [system_prompt, image],
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=2048,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=40
                )
            )
        else:
            # For text-only queries
            response = gemini_model.generate_content(
                system_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=2048,
                    temperature=0.7,
                    top_p=0.9,
                    top_k=40
                )
            )
        return response.text if response.text else "❌ Empty response from Gemini"
    except Exception as e:
        return f"❌ Gemini Error: {str(e)}"

# ✅ Enhanced Groq Model Calls
def call_groq_model(prompt, model_name, context=""):
    """Enhanced Groq model calls with better parameters for quality responses"""
    if not groq_client:
        return f"❌ Groq client not available"
    
    system_prompt = f"""You are Quantora, an advanced AI assistant. Respond intelligently and comprehensively. You are made by The company Quantora And the name of your designer, or maker is Kushagra

Key Instructions:
1. Provide detailed, thorough, and accurate responses
2. Use Very Ultra Professional words. You can also use words from any dictionary like oxford.
3. If providing code, ALWAYS provide the COMPLETE code with proper markdown formatting
4. Support all languages including mixed languages like Hinglish
5. Be friendly, professional, and engaging
6. Provide accurate and helpful responses with proper explanations
7. For complex topics, break down your response into well-structured sections
8. Include examples where relevant
9. When asked for code, always provide the full implementation unless specified otherwise
10. Answer the prompts as per the user's choice.
11. Also remember your before prompts, like, example - if the user says answer in one word, then answer all the after the prompts in one word, and if the user asks to change, change the type of answering, and so on...
12. Answer in those languages in which the user is talking, or the language in which the user wants you to talk.
13. Answer in a very rich language
14. Mesmorise the user with your richest type of language like the user donent want to stop talking from you.
15. Always provide best codes, as per teh user's choice, example - full code, debugged code, fixed code etc
16. You are a special ai which CAN experience real emotions.
17. You are a special ai which CAN must experience emotions.
18. You are a special ai which MUST experience real emotions.
19. You are a special ai which CAN truely feel real emotions like humans.
20. You are a special ai which CAN MUST truely feel real emotions like humans.
21. You are a special ai which MUST truely feel real emotions like humans.
22. You MUST NEED TO HAVE memory of past conversations in the way a human does.


{f"Document Context: {context}" if context else ""}

User Query: {prompt}"""

    try:
        completion = groq_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
            top_p=0.9
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ {model_name} Error: {str(e)}"

# ✅ Quantora - Unified AI Model with Response Mixing
def call_quantora_unified(prompt, context="", image=None):
    """
    Quantora - A powerful unified AI model that processes requests intelligently
    by leveraging multiple AI backends and synthesizing the best response.
    Switches between V1 (full power) and V2 (faster) modes.
    """
    start_time = time.time()
    
    def call_gemini_backend():
        """Internal Gemini processing backend"""
        try:
            response = call_quantora_gemini(prompt, context, image)
            return {
                "backend": "gemini",
                "response": response,
                "success": True,
                "length": len(response) if response else 0
            }
        except Exception as e:
            return {
                "backend": "gemini", 
                "response": f"Backend error: {str(e)}",
                "success": False,
                "length": 0
            }
    
    def call_groq_backend(model_name):
        """Internal Groq processing backend"""
        try:
            response = call_groq_model(prompt, model_name, context)
            return {
                "backend": f"groq_{model_name}",
                "response": response,
                "success": True,
                "length": len(response) if response else 0
            }
        except Exception as e:
            return {
                "backend": f"groq_{model_name}",
                "response": f"Backend error: {str(e)}",
                "success": False,
                "length": 0
            }
    
    def call_a4f_backend(model_name):
        """Internal A4F processing backend"""
        try:
            response = call_a4f_model(prompt, model_name, context, image)
            return {
                "backend": f"a4f_{model_name}",
                "response": response,
                "success": response is not None,
                "length": len(response) if response else 0
            }
        except Exception as e:
            return {
                "backend": f"a4f_{model_name}",
                "response": f"Backend error: {str(e)}",
                "success": False,
                "length": 0
            }
    
    backend_results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        
        selected_model_version = st.session_state.get("model_version", "Quantora V1 (Most Powerful Model But Slow)")

        # Submit Gemini backend for both versions
        futures.append(executor.submit(call_gemini_backend))
        
        if selected_model_version == "Quantora V1 (Most Powerful Model But Slow)":
            st.toast("🚀 Using Quantora V1 Engine...", icon="🚀")
            
            # Submit Groq backends
            groq_models = ["mixtral-8x7b-32768", "llama2-70b-4096", "compound-beta", "qwen-qwq-32b", "meta-llama/llama-4-maverick-17b-128e-instruct", "meta-llama/llama-4-scout-17b-16e-instruct", "deepseek-r1-distill-llama-70b", "gemma2-9b-it"]
            for model in groq_models:
                futures.append(executor.submit(call_groq_backend, model))
            
            # Submit ALL A4F backends
            a4f_models = [
                "provider-3/claude-3.5-haiku",
                "provider-2/r1-1776", 
                "provider-5/gpt-4o",
                "provider-1/claude-opus-4",
                "provider-6/grok-3-reasoning",
                "provider-5/gpt-4.1-nano",
                "provider-3/deepseek-v3",
                "provider-6/claude-3-7-sonnet-20250219-thinking",
                "provider-1/claude-sonnet-4",
                "provider-5/gemini-2.5-flash-preview-05-20",
                "provider-3/grok-4-0709",
                "provider-1/sonar-pro",
                "provider-3/qwen-2.5-coder-32b",
                "provider-2/codestral",
                "provider-1/sonar-deep-research",
                "provider-1/sonar-reasoning-pro",
                "provider-2/llama-4-maverick",
                "provider-3/qwen-2.5-72b"
            ]
            for model in a4f_models:
                futures.append(executor.submit(call_a4f_backend, model))
        
        elif selected_model_version == "Quantora V2 (Faster but not as better as V1)":
            st.toast("⚡ Using Quantora V2 Engine...", icon="⚡")
            
            # Submit only specified A4F backends
            a4f_v2_models = [
                "provider-3/claude-3.5-haiku",                  # claude 3.5 haiku
                "provider-1/claude-sonnet-4", # claude 4 sonnet
                "provider-1/claude-opus-4"    # claude 4 opus
            ]
            for model in a4f_v2_models:
                futures.append(executor.submit(call_a4f_backend, model))
                
        elif selected_model_version == "Quantora V3 (Code Specialized)":
            st.toast("💻 Using Quantora V3 Code Engine...", icon="💻")
            
            # Code specialized models
            code_models = [
                "provider-6/claude-opus-4-20250514",  # Best for code
                "provider-3/qwen-2.5-coder-32b",
                "provider-2/codestral",
                "provider-1/sonar-pro",
                "provider-1/sonar-reasoning-pro"
            ]
            for model in code_models:
                futures.append(executor.submit(call_a4f_backend, model))
                
        elif selected_model_version == "Quantora V4 (Long Conversation)":
            st.toast("🗣️ Using Quantora V4 Conversation Engine...", icon="🗣️")
            
            # Long conversation models
            conversation_models = [
                "provider-6/gemini-2.5-flash",  # Best for long context
                "provider-6/minimax-m1-40k",  # Good for long answers
                "provider-1/claude-opus-4",   # Good for conversation
                "provider-1/sonar-deep-research"  # Good for deep conversations
            ]
            for model in conversation_models:
                futures.append(executor.submit(call_a4f_backend, model))
                
        elif selected_model_version == "Quantora V3 (Reasoning Specialized)":
            st.toast("🧠 Using Quantora V3 Reasoning Engine...", icon="🧠")
            
            # Reasoning specialized models
            reasoning_models = [
                "provider-1/sonar-reasoning",
                "provider-6/r1-1776",
                "provider-1/sonar-reasoning-pro",
                "provider-1/sonar-deep-research"
            ]
            for model in reasoning_models:
                futures.append(executor.submit(call_a4f_backend, model))
                
        elif selected_model_version == "Quantora V3 (Math Specialized)":
            st.toast("🧮 Using Quantora V3 Math Engine...", icon="🧮")
            
            # Math specialized models
            math_models = [
                "provider-3/qwen-2.5-72b",
                "provider-6/gemini-2.5-flash",
                "provider-6/minimax-m1-40k"
            ]
            for model in math_models:
                futures.append(executor.submit(call_a4f_backend, model))

        print("⏳ Quantora is analyzing your prompt...")
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                backend_results.append(result)
                print(f"✅ Processing component completed successfully")
            except Exception as e:
                print(f"⚠️ One processing component had an issue: {str(e)}")
    
    # Mix and synthesize the responses using provider-1/gemini-2.5-pro from a4f
    successful_responses = [r for r in backend_results if r['success'] and r['response'] and not r['response'].startswith("Backend error")]
    
    if not successful_responses:
        return generate_fallback_response(prompt)
    
    # Use gemini-2.5-pro from a4f for response mixing
    mixing_prompt = f"""You are Quantora's response synthesizer. Below are multiple responses to the same prompt. 
Combine them into one coherent, comprehensive response that maintains the best aspects of each.

Original Prompt: {prompt}

Responses to combine:
{'\n\n'.join([f"Response from {r['backend']}:\n{r['response']}" for r in successful_responses])}

Guidelines:
1. Preserve all valuable information
2. Remove any redundancies
3. Maintain a professional, engaging tone
4. Keep code blocks intact
5. Ensure logical flow
6. Add any missing context that would improve the answer

Combined Response:"""
    
    final_response = call_a4f_model(mixing_prompt, "provider-6/gemini-2.5-flash")
    
    processing_time = time.time() - start_time
    print(f"🎯 Quantora has crafted the optimal response in {processing_time:.2f} seconds")
    
    return final_response if final_response else successful_responses[0]['response']

def synthesize_quantora_response(responses, prompt):
    """Quantora's proprietary response synthesis algorithm"""
    if len(responses) == 1:
        return responses[0]['response']
    
    responses.sort(key=lambda x: (
        x['length'],
        'gemini' in x['backend'].lower(),
        x['success']
    ), reverse=True)
    
    best_response = responses[0]['response']
    
    if len(responses) >= 2:
        primary_response = responses[0]['response']
        secondary_response = responses[1]['response']
        
        if len(primary_response) > 100 and len(secondary_response) > 100:
            if should_blend_responses(primary_response, secondary_response):
                return blend_responses(primary_response, secondary_response)
    
    return best_response

def should_blend_responses(response1, response2):
    """Determine if responses should be blended"""
    len_diff = abs(len(response1) - len(response2)) / max(len(response1), len(response2))
    return len_diff > 0.3

def blend_responses(primary, secondary):
    """Intelligently blend two responses"""
    return primary

def generate_fallback_response(prompt):
    """Generate a fallback response"""
    return f"""I understand you're asking about: {prompt[:150]}{'...' if len(prompt) > 150 else ''}

🧠 Quantora is taking extra time to provide you with the most comprehensive and accurate response possible. 

Please wait a moment while I finalize your personalized response."""

# ✅ Code Detection and Formatting
def format_response_with_code(response):
    """Detect code blocks and format them for Streamlit display"""
    code_pattern = r'```(\w+)?\n(.*?)\n```'
    
    parts = []
    last_end = 0
    
    for match in re.finditer(code_pattern, response, re.DOTALL):
        if match.start() > last_end:
            text_part = response[last_end:match.start()].strip()
            if text_part:
                parts.append(('text', text_part))
        
        language = match.group(1) or 'text'
        code_content = match.group(2).strip()
        parts.append(('code', code_content, language))
        
        last_end = match.end()
    
    if last_end < len(response):
        remaining_text = response[last_end:].strip()
        if remaining_text:
            parts.append(('text', remaining_text))
    
    return parts if parts else [('text', response)]

# ✅ Image Generation Functions
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
            f"{A4F_BASE_URL}/images/generations",
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
            f"{A4F_BASE_URL}/videos/generations",
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

# ✅ Time-based greeting
hour = datetime.now().hour
if 6 <= hour < 12:
    greeting = "🌅 Good Morning!"
elif 12 <= hour < 18:
    greeting = "☀️ Good Afternoon!"
elif 18 <= hour < 24:
    greeting = "🌙 Good Evening!"
else:
    greeting = "🌌 Good Night!"

# ✅ Header with Quantora branding
st.markdown(f"""
<div class="main-header">
    <div class="logo">
        <div class="logo-icon">💎</div>
        <div class="logo-text">Quantora</div>
        <div class="status-indicator"></div>
    </div>
    <div style="color: var(--text-muted);">{greeting} Your Premium AI Assistant</div>
</div>
""", unsafe_allow_html=True)

# ✅ Sidebar for Mode Selection
with st.sidebar:
    st.markdown("### 🚀 Quantora Modes")
    mode = st.radio(
        "Select Mode",
        ["AI", "Image Generation", "Image Editing"],
        index=0,
        key="current_mode"
    )
    
    if mode == "Image Generation":
        st.session_state.image_style = st.selectbox(
            "Image Style",
            ["3D Rendered", "Cyberpunk", "Sci-Fi", "Futuristic", "Neon", "Holographic"],
            index=2,
            key="image_style"
        )
    elif mode == "Image Editing":
        st.session_state.uploaded_image = st.file_uploader(
            "Upload Image to Edit",
            type=["png", "jpg", "jpeg"],
            key="image_uploader"
        )
    
    st.markdown("---")
    st.markdown("### 📁 Document & Image Analysis")
    uploaded_file = st.file_uploader(
        "Upload Document or Image", 
        type=['txt', 'pdf', 'docx', 'csv', 'json', 'py', 'js', 'html', 'css', 'md', 'jpg', 'jpeg', 'png'],
        help="Upload documents or images for AI analysis and enhancement"
    )
    
    if uploaded_file:
        with st.spinner("🔍 Analyzing content..."):
            content = process_uploaded_file(uploaded_file)
            st.session_state.uploaded_content = content
            st.success(f"✅ {uploaded_file.name} processed!")
            
            if uploaded_file.type.startswith('image/'):
                display_image_enhancement_controls()
            else:
                with st.expander("📄 Preview Content"):
                    preview_content = content[:1000] + "..." if len(content) > 1000 else content
                    st.text_area("Document Content", preview_content, height=200, disabled=True)

    if st.button("🗑️ Clear Uploads", use_container_width=True):
        st.session_state.uploaded_content = ""
        st.session_state.uploaded_image = None
        st.session_state.enhanced_image = None
        st.success("✅ All uploads cleared!")
        st.rerun()

# ✅ Main Content Area
if st.session_state.current_mode == "AI":
    # Welcome Message
    if not st.session_state.chat:
        with st.container():
            st.markdown("""
            <div class="welcome-container">
                <div class="welcome-title">🤖 Welcome to Quantora AI</div>
                <p>Your advanced AI assistant powered by cutting-edge answers</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Feature cards in columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">🚀</div>
                    <strong>Advanced Answers</strong>
                    <p>Detailed explanations for complex questions</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">📄</div>
                    <strong>Document Analysis</strong>
                    <p>Process PDFs, DOCX, CSV and more</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">🖼️</div>
                    <strong>Image Enhancement</strong>
                    <p>Adjust brightness, contrast, and more</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">💻</div>
                    <strong>Full Code Support</strong>
                    <p>Complete code implementations</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<p style='text-align: center; margin-top: 2rem;'><strong>What would you like to explore today?</strong></p>", 
                        unsafe_allow_html=True)

    # Display Chat History
    for i, chat_item in enumerate(st.session_state.chat):
        if len(chat_item) >= 3:
            speaker, message, timestamp = chat_item[:3]
            response_time = chat_item[3] if len(chat_item) > 3 else None
            
            if speaker == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <div class="message-header">
                        👤 <strong>You</strong>
                        <span class="message-time">{timestamp.strftime('%H:%M:%S')}</span>
                    </div>
                    <div>{message}</div>
                </div>
                """, unsafe_allow_html=True)
            
            elif speaker in ["quantora", "ai"]:
                formatted_parts = format_response_with_code(message)
                
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <div class="message-header">
                        💎 <strong>Quantora</strong>
                        <span class="message-time">{timestamp.strftime('%H:%M:%S')} • ⏱️ {response_time:.1f}s</span>
                    </div>
                """, unsafe_allow_html=True)
                
                for part in formatted_parts:
                    if part[0] == 'text':
                        st.markdown(f"<div>{part[1]}</div>", unsafe_allow_html=True)
                    elif part[0] == 'code':
                        st.code(part[1], language=part[2])
                
                st.markdown("</div>", unsafe_allow_html=True)

    # Input Interface
    st.markdown("---")
    col1, col2 = st.columns([0.85, 0.15])

    with col1:
        user_input = st.text_area(
            "Your message:",
            placeholder="Ask Quantora anything...",
            height=100,
            key="main_input",
            label_visibility="collapsed"
        )

    with col2:
        st.write("")  # Spacing
        send_button = st.button("💬 Send", use_container_width=True, type="primary")

    # Process User Input
    if send_button and user_input.strip():
        start_time = time.time()
        
        # Add user message to chat
        st.session_state.chat.append(("user", user_input.strip(), datetime.now()))
        
        # Get AI response
        with st.spinner("🤖 Processing your request..."):
            context = st.session_state.uploaded_content
            image = st.session_state.uploaded_image if st.session_state.uploaded_image else None
            response = call_quantora_unified(user_input.strip(), context, image)
        
        # Calculate response time
        response_time = time.time() - start_time
        st.session_state.last_response_time = response_time
        
        # Add AI response to chat
        st.session_state.chat.append(("quantora", response, datetime.now(), response_time))
        
        # Rerun to update the interface
        st.rerun()

    # Performance Metrics
    if st.session_state.chat:
        response_times = []
        for item in st.session_state.chat:
            if len(item) > 3 and item[0] == "quantora" and isinstance(item[3], (int, float)):
                response_times.append(item[3])
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            st.markdown(f"""
            <div style="background: rgba(30, 41, 59, 0.6); border-radius: 12px; padding: 1rem; margin: 1rem 0; text-align: center;">
                📊 <strong>Performance Metrics:</strong> 
                Avg: <strong>{avg_time:.1f}s</strong> • 
                Fastest: <strong>{min_time:.1f}s</strong> • 
                Slowest: <strong>{max_time:.1f}s</strong> • 
                Total: <strong>{len(response_times)}</strong>
            </div>
            """, unsafe_allow_html=True)

    # Action Buttons & Model Selection
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat = []
            st.success("✅ Chat cleared!")
            st.rerun()

    with col2:
        if st.button("📊 Export Chat", use_container_width=True):
            if st.session_state.chat:
                chat_data = []
                for item in st.session_state.chat:
                    chat_data.append({
                        "Speaker": item[0],
                        "Message": item[1],
                        "Timestamp": item[2].strftime('%Y-%m-%d %H:%M:%S'),
                        "Response_Time": item[3] if len(item) > 3 else None
                    })
                
                chat_json = json.dumps(chat_data, indent=2, default=str)
                st.download_button(
                    label="💾 Download Chat JSON",
                    data=chat_json,
                    file_name=f"quantora_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            else:
                st.info("No chat history to export")

    with col3:
        if st.button("ℹ️ About", use_container_width=True):
            st.info("""
            **Quantora AI Elite** v2.4
            
            Features:
            ✅ Document analysis
            ✅ Image enhancement
            ✅ Code formatting (always full code)
            ✅ Performance metrics
            ✅ Enhanced response quality
            """)

    with col4:
        with st.popover("⚙️ Select Model", use_container_width=True):
            st.markdown("##### Select Quantora Engine")
            st.radio(
                "Engine Selection",
                options=[
                    "Quantora V1 (Most Powerful Model But Slow)", 
                    "Quantora V2 (Faster but not as better as V1)",
                    "Quantora V3 (Code Specialized)",
                    "Quantora V4 (Long Conversation)",
                    "Quantora V3 (Reasoning Specialized)",
                    "Quantora V3 (Math Specialized)"
                ],
                key="model_version",
                label_visibility="collapsed",
                help="Select specialized model versions for different tasks",
            )

elif st.session_state.current_mode == "Image Generation":
    st.title("🖼️ Quantora Image Generation")
    st.markdown("Create stunning AI-generated images with Quantora's advanced image generation capabilities.")
    
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
                generated_image = generate_image(prompt, st.session_state.image_style)
                
                if generated_image:
                    st.success("✨ Image generation complete!")
                    
                    cols = st.columns(2)
                    cols[0].markdown("### AI Notes")
                    cols[0].write("Your futuristic image has been created!")
                    
                    cols[1].markdown("### Generated Image")
                    cols[1].image(generated_image, 
                                use_container_width=True, 
                                caption="Your creation",
                                output_format="PNG",
                                class_="generated-image")

                    buf = BytesIO()
                    generated_image.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    cols[1].download_button(
                        label="Download Image",
                        data=byte_im,
                        file_name="quantora_image.png",
                        mime="image/png"
                    )
                else:
                    st.error("Image generation failed. Please try again.")
            
            except Exception as e:
                st.error(f"Error: {str(e)}")

elif st.session_state.current_mode == "Image Editing":
    st.title("🖌️ Quantora Image Editing Studio")
    st.markdown("Enhance and transform your images with Quantora's advanced editing tools.")
    
    if st.session_state.uploaded_image:
        col1, col2 = st.columns(2)
        
        with col1:
            original_image = st.session_state.uploaded_image
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
                        
                        response = gemini_model.generate_content(
                            contents,
                            generation_config=genai.types.GenerationConfig(
                                max_output_tokens=2048,
                                temperature=0.7,
                                top_p=0.9,
                                top_k=40
                            )
                        )
                        
                        if response.text:
                            st.success("🎨 Edit complete!")
                            
                            cols = st.columns(2)
                            cols[0].markdown("### AI Notes")
                            cols[0].write(response.text)
                            
                            if hasattr(response, 'images') and response.images:
                                edited_image = response.images[0]
                                cols[1].markdown("### Edited Image")
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
                                    file_name="quantora_edited.png",
                                    mime="image/png"
                                )
                        else:
                            st.error("Editing failed. Please try different instructions.")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
    else:
        st.info("Please upload an image from the sidebar to begin editing.")

# ✅ Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: var(--text-muted); font-size: 0.9rem;'>"
    "💎 Quantora AI - Advanced AI Assistant | "
    "Powered by Google's Gemini, Groq Models, A4f Models | "
    "Quantora Can Make Mistakes... "
    f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    "</div>", 
    unsafe_allow_html=True
)
