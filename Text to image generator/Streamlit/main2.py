from dotenv import load_dotenv, find_dotenv
import os
import io
import streamlit as st
from PIL import Image
from datetime import datetime
import requests

# Load environment variables
load_dotenv(find_dotenv())
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

def text2image_with_requests(prompt: str):
    """Fallback method using direct API requests"""
    try:
        # Try multiple endpoints in order of preference
        endpoints = [
            "https://api-inference.huggingface.co/models/prompthero/openjourney",
            "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1",
            "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        ]
        
        for api_url in endpoints:
            headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}
            payload = {"inputs": prompt}
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                image_bytes = response.content
                image = Image.open(io.BytesIO(image_bytes))
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"image_{timestamp}.jpg"
                image.save(filename)
                return filename
            elif response.status_code == 429:
                st.warning("Rate limit reached, trying next model...")
                continue
            else:
                st.info(f"Model {api_url.split('/')[-1]} failed, trying next...")
                continue
                
        st.error("All models failed. Please try again later.")
        return None
        
    except Exception as e:
        st.error(f"Error with requests method: {str(e)}")
        return None

def text2image(prompt: str):
    """Main function to generate image using HuggingFace API"""
    return text2image_with_requests(prompt)

def main():
    st.set_page_config(page_title="Text2Image Generator", page_icon="🎨")
    st.title("🎨 Text-to-Image Generator")
    st.markdown("---")
    
    # Sidebar with instructions
    with st.sidebar:
        st.header("📝 Instructions")
        st.write("1. Enter a descriptive prompt")
        st.write("2. Click 'Generate Image'")
        st.write("3. Wait for the magic!")
        st.write("---")
        st.header("💡 Tips")
        st.write("- Be specific in your prompts")
        st.write("- Try different styles")
        st.write("- Patience is key!")
    
    # Main form
    with st.form(key="image_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            query = st.text_area(
                label="Enter your prompt...",
                placeholder="A beautiful sunset over mountains with a lake...",
                height=100,
                max_chars=500
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.form_submit_button("🎨 Generate Image", use_container_width=True)
    
    # Generation section
    if submit and query:
        if len(query.strip()) < 3:
            st.error("Please enter a longer prompt (at least 3 characters)")
            return
            
        st.markdown("---")
        st.subheader("🔄 Generating your image...")
        
        with st.spinner("Creating magic... This may take 30-60 seconds"):
            filename = text2image(query)
            
            if filename:
                # Success section
                st.success("✨ Image generated successfully!")
                
                # Display image
                st.image(filename, caption=f"Generated: {query}", use_container_width=True)
                
                # Download button
                with open(filename, "rb") as file:
                    st.download_button(
                        label="📥 Download Image",
                        data=file.read(),
                        file_name=filename,
                        mime="image/jpeg"
                    )
                
                # Stats
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Model", "Stable Diffusion")
                with col2:
                    st.metric("Status", "Success")
                with col3:
                    st.metric("File", filename)
            else:
                st.error("❌ Failed to generate image. Please try a different prompt or check your API token.")
    
    # Example prompts
    st.markdown("---")
    st.subheader("🎯 Example Prompts")
    example_prompts = [
        "A majestic dragon flying over a castle at sunset",
        "A cute robot sitting in a coffee shop, reading a book",
        "A futuristic city with flying cars and neon lights",
        "A peaceful forest with sunlight filtering through trees",
        "An astronaut discovering a new planet with strange plants"
    ]
    
    cols = st.columns(3)
    for i, prompt in enumerate(example_prompts):
        with cols[i % 3]:
            if st.button(prompt, key=f"example_{i}"):
                st.session_state.example_prompt = prompt
    
    # Use example prompt if selected
    if 'example_prompt' in st.session_state:
        st.info(f"Try this prompt: {st.session_state.example_prompt}")

if __name__ == "__main__":
    main()
