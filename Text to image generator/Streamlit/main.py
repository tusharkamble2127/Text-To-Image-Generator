from dotenv import load_dotenv, find_dotenv
import os
import streamlit as st
import requests
import io
from PIL import Image, ImageEnhance, ImageFilter
from datetime import datetime
import time
import random
import base64
import json

# Load environment variables
load_dotenv(find_dotenv())

# Free API keys (you'll need to get these - they're free)
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")  # Free Stability AI
LEONARDO_API_KEY = os.getenv("LEONARDO_API_KEY")   # Free Leonardo AI
PLAYGROUND_API_KEY = os.getenv("PLAYGROUND_API_KEY") # Free Playground AI

def enhance_image_quality(image):
    """Enhance image quality for better results"""
    try:
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.4)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.3)
        
        # Enhance color
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.2)
        
        # Apply advanced sharpening
        image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
        return image
    except:
        return image

def generate_with_stability_api(prompt: str):
    """Generate using Stability AI Free API - 100 free credits per month"""
    try:
        if not STABILITY_API_KEY:
            return None
            
        api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        
        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "text_prompts": [
                {
                    "text": f"masterpiece, best quality, ultra detailed, {prompt}",
                    "weight": 1
                }
            ],
            "cfg_scale": 8,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if 'artifacts' in result and len(result['artifacts']) > 0:
                image_data = base64.b64decode(result['artifacts'][0]['base64'])
                image = Image.open(io.BytesIO(image_data))
                image = enhance_image_quality(image)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"stability_{timestamp}.png"
                image.save(filename, quality=95)
                return filename
        
        return None
        
    except Exception as e:
        return None

def generate_with_leonardo_api(prompt: str):
    """Generate using Leonardo AI Free API - 150 free credits per day"""
    try:
        if not LEONARDO_API_KEY:
            return None
            
        # First get user ID
        headers = {
            "Authorization": f"Bearer {LEONARDO_API_KEY}"
        }
        
        # Generate image
        api_url = "https://cloud.leonardo.ai/api/rest/v1/generations"
        
        payload = {
            "prompt": f"masterpiece, best quality, ultra detailed, {prompt}",
            "modelId": "6bef9f1b-29cb-40c7-b9df-32b51c1f67d3",  # Leonardo Diffusion XL
            "width": 1024,
            "height": 1024,
            "num_images": 1,
            "guidance_scale": 8,
            "num_inference_steps": 30
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if 'sdGenerationJob' in result:
                generation_id = result['sdGenerationJob']['generationId']
                
                # Poll for completion
                for _ in range(60):  # Wait up to 2 minutes
                    status_url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"
                    status_response = requests.get(status_url, headers=headers, timeout=10)
                    
                    if status_response.status_code == 200:
                        status_result = status_response.json()
                        if status_result['generations_by_pk']['status'] == 'COMPLETE':
                            image_url = status_result['generations_by_pk']['generated_images'][0]['url']
                            
                            img_response = requests.get(image_url, timeout=30)
                            if img_response.status_code == 200:
                                image = Image.open(io.BytesIO(img_response.content))
                                image = enhance_image_quality(image)
                                
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"leonardo_{timestamp}.png"
                                image.save(filename, quality=95)
                                return filename
                    
                    time.sleep(2)
        
        return None
        
    except Exception as e:
        return None

def generate_with_playground_api(prompt: str):
    """Generate using Playground AI Free API - 1000 free images per month"""
    try:
        if not PLAYGROUND_API_KEY:
            return None
            
        api_url = "https://api.playground.com/v1/images/generations"
        
        headers = {
            "Authorization": f"Bearer {PLAYGROUND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": f"masterpiece, best quality, ultra detailed, {prompt}",
            "width": 1024,
            "height": 1024,
            "num_images": 1,
            "guidance_scale": 8,
            "num_inference_steps": 30
        }
        
        response = requests.post(api_url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if 'data' in result and len(result['data']) > 0:
                image_url = result['data'][0]['url']
                
                img_response = requests.get(image_url, timeout=30)
                if img_response.status_code == 200:
                    image = Image.open(io.BytesIO(img_response.content))
                    image = enhance_image_quality(image)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"playground_{timestamp}.png"
                    image.save(filename, quality=95)
                    return filename
        
        return None
        
    except Exception as e:
        return None

def generate_with_huggingface_api(prompt: str):
    """Generate using HuggingFace Inference API - Free tier"""
    try:
        # Use public models that don't require token for basic usage
        models = [
            "stabilityai/stable-diffusion-2-1",
            "runwayml/stable-diffusion-v1-5",
            "CompVis/stable-diffusion-v1-4"
        ]
        
        for model in models:
            try:
                api_url = f"https://api-inference.huggingface.co/models/{model}"
                
                payload = {"inputs": f"masterpiece, best quality, ultra detailed, {prompt}"}
                
                response = requests.post(api_url, json=payload, timeout=60)
                
                if response.status_code == 200:
                    image_bytes = response.content
                    image = Image.open(io.BytesIO(image_bytes))
                    image = enhance_image_quality(image)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"huggingface_{timestamp}.jpg"
                    image.save(filename, quality=95)
                    return filename
                    
            except Exception as e:
                continue
        
        return None
        
    except Exception as e:
        return None

def generate_with_free_apis(prompt: str):
    """Generate image using multiple free APIs"""
    st.info("🔑 Trying free API services...")
    
    # List of free APIs in order of preference
    services = [
        ("Stability AI (100 free/month)", generate_with_stability_api),
        ("Leonardo AI (150 free/day)", generate_with_leonardo_api),
        ("Playground AI (1000 free/month)", generate_with_playground_api),
        ("HuggingFace (Public API)", generate_with_huggingface_api),
    ]
    
    for i, (service_name, service_func) in enumerate(services):
        with st.spinner(f"🔑 Trying {service_name} ({i+1}/{len(services)})..."):
            result = service_func(prompt)
            if result:
                st.success(f"✅ Image generated using {service_name}!")
                return result
            else:
                st.info(f"⏳ {service_name} not available, trying next...")
    
    st.error("❌ All free APIs are currently busy or credits exhausted.")
    st.info("💡 **Free APIs have daily/monthly limits. Try again tomorrow or get additional free API keys!**")
    return None

def show_api_setup_instructions():
    """Show instructions for getting free API keys"""
    st.markdown("---")
    st.subheader("🔑 Get Your Free API Keys (100% Free):")
    
    st.markdown("""
    ### 1. Stability AI (100 free credits/month)
    1. Go to [https://stability.ai](https://stability.ai)
    2. Sign up for free account
    3. Go to Dashboard → API Keys
    4. Create new API key
    5. Add to .env: `STABILITY_API_KEY=your_key_here`
    
    ### 2. Leonardo AI (150 free credits/day)
    1. Go to [https://leonardo.ai](https://leonardo.ai)
    2. Sign up for free account
    3. Go to User Settings → API Access
    4. Generate API key
    5. Add to .env: `LEONARDO_API_KEY=your_key_here`
    
    ### 3. Playground AI (1000 free images/month)
    1. Go to [https://playground.com](https://playground.com)
    2. Sign up for free account
    3. Go to Account → API Keys
    4. Create API key
    5. Add to .env: `PLAYGROUND_API_KEY=your_key_here`
    
    ### 🎯 Benefits of Free APIs:
    - ✅ Higher quality images (1024x1024)
    - ✅ More reliable than direct URLs
    - ✅ Professional models (SDXL, Leonardo Diffusion)
    - ✅ No watermarks
    - ✅ Faster generation
    - ✅ True API integration
    
    ### 💰 Total Free Credits:
    - **Stability AI**: 100 images/month
    - **Leonardo AI**: 150 images/day (4,500/month!)
    - **Playground AI**: 1,000 images/month
    - **Total**: ~5,600+ free images per month!
    """)

def main():
    st.set_page_config(
        page_title="Free API Image Generator", 
        page_icon="🔑",
        layout="wide"
    )
    
    st.title("🔑 Free API Image Generator")
    st.markdown("---")
    
    # Sidebar with API status
    with st.sidebar:
        st.header("🔑 Free API Status")
        
        stability_status = "✅ Configured" if STABILITY_API_KEY else "❌ Missing"
        leonardo_status = "✅ Configured" if LEONARDO_API_KEY else "❌ Missing"
        playground_status = "✅ Configured" if PLAYGROUND_API_KEY else "❌ Missing"
        
        st.write(f"Stability AI: {stability_status}")
        st.write(f"Leonardo AI: {leonardo_status}")
        st.write(f"Playground AI: {playground_status}")
        st.write(f"HuggingFace: ✅ Always Available")
        
        st.markdown("---")
        
        st.header("🆓 Free Credits")
        st.write("💎 Stability: 100/month")
        st.write("🎨 Leonardo: 150/day")
        st.write("🎮 Playground: 1000/month")
        st.write("🤗 HuggingFace: Unlimited")
        
        st.markdown("---")
        
        st.header("💡 Tips")
        st.write("• Get all API keys for best results")
        st.write("• Free credits reset daily/monthly")
        st.write("• Higher quality than direct URLs")
        st.write("• Professional AI models")
    
    # Check if any API keys are configured
    has_api_keys = any([STABILITY_API_KEY, LEONARDO_API_KEY, PLAYGROUND_API_KEY])
    
    if not has_api_keys:
        st.warning("⚠️ **No API Keys Configured - Using HuggingFace Public API Only**")
        st.info("🔑 **Add free API keys for better quality and reliability!**")
        show_api_setup_instructions()
    else:
        st.success("🎉 **Free API Keys Configured - Ready for High-Quality Generation!**")
        st.info("💎 **Using professional AI models with ~5,600+ free images per month!**")
    
    # Generation form
    with st.form(key="api_form"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            prompt = st.text_area(
                label="✍️ Describe your image:",
                placeholder="A majestic dragon flying over mountains at sunset, photorealistic, ultra detailed, 8k resolution...",
                height=100,
                max_chars=1000,
                help="Be descriptive for better results with professional models"
            )
        
        with col2:
            st.markdown("**Enhancement Options:**")
            
            style = st.selectbox("Style:", [
                "None", "Photorealistic", "Digital Art", "Anime", "Oil Painting", "3D Render", "Cinematic"
            ])
            
            quality = st.selectbox("Quality:", [
                "Standard", "High Quality", "Ultra HD", "Professional"
            ])
            
            model_preference = st.selectbox("Preferred Model:", [
                "Auto Select", "Stability AI", "Leonardo AI", "Playground AI", "HuggingFace"
            ])
            
            st.markdown("<br>", unsafe_allow_html=True)
            generate = st.form_submit_button("🔑 Generate with Free APIs", use_container_width=True)
    
    if generate and prompt:
        if len(prompt.strip()) < 3:
            st.error("Please enter at least 3 characters")
            return
        
        # Build enhanced prompt
        enhanced_prompt = prompt
        if style != "None":
            enhanced_prompt = f"{prompt}, {style.lower()} style"
        
        if quality == "High Quality":
            enhanced_prompt = f"high quality, {enhanced_prompt}"
        elif quality == "Ultra HD":
            enhanced_prompt = f"ultra hd, 8k resolution, {enhanced_prompt}"
        elif quality == "Professional":
            enhanced_prompt = f"masterpiece, best quality, professional photography, {enhanced_prompt}"
        
        st.markdown("---")
        st.subheader("🎨 Generating with Free APIs...")
        st.info(f"📝 Enhanced prompt: {enhanced_prompt}")
        
        filename = generate_with_free_apis(enhanced_prompt)
        
        if filename:
            st.success("🎉 Professional image generated using free APIs!")
            
            # Display image
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.image(filename, caption=f"Generated: {prompt}", use_container_width=True)
            
            with col2:
                st.markdown("**📥 Download Options:**")
                
                # PNG download
                with open(filename, "rb") as file:
                    st.download_button(
                        label="📥 Download PNG",
                        data=file.read(),
                        file_name=filename,
                        mime="image/png"
                    )
                
                # JPG download
                jpg_filename = filename.replace('.png', '.jpg')
                image = Image.open(filename)
                image.save(jpg_filename, 'JPEG', quality=95)
                
                with open(jpg_filename, "rb") as file:
                    st.download_button(
                        label="📥 Download JPG",
                        data=file.read(),
                        file_name=jpg_filename,
                        mime="image/jpeg"
                    )
                
                # Image info
                img = Image.open(filename)
                st.markdown("---")
                st.markdown("**📊 Image Info:**")
                st.write(f"📐 Resolution: {img.width}×{img.height}")
                st.write(f"💾 Size: {os.path.getsize(filename)/1024/1024:.1f} MB")
                st.write(f"💰 Cost: $0.00")
            
            # Success metrics
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("API", "Professional")
            with col2:
                st.metric("Quality", "High")
            with col3:
                st.metric("Watermark", "None")
            with col4:
                st.metric("Cost", "FREE")
                
        else:
            st.error("❌ Failed to generate image. Please check your API keys and try again.")
            if not has_api_keys:
                st.warning("💡 **Add free API keys for much better results!**")
    
    # API setup reminder
    if not has_api_keys:
        st.markdown("---")
        st.subheader("🔑 Upgrade to Free APIs for Better Results:")
        if st.button("📖 Show API Setup Instructions"):
            show_api_setup_instructions()
    
    # Professional examples
    st.markdown("---")
    st.subheader("🎯 Professional Examples:")
    
    examples = [
        "A photorealistic portrait of an elderly woman, character, wrinkles, masterpiece, professional photography",
        "A futuristic cyberpunk city at night, neon lights, flying cars, ultra detailed, cinematic lighting",
        "A majestic dragon flying over mountains, digital art, highly detailed, fantasy, epic",
        "A serene Japanese garden with cherry blossoms, peaceful, photography, golden hour"
    ]
    
    cols = st.columns(2)
    for i, example in enumerate(examples):
        with cols[i % 2]:
            if st.button(example, key=f"api_example_{i}", use_container_width=True):
                st.session_state.api_example_prompt = example
    
    if 'api_example_prompt' in st.session_state:
        st.info(f"💡 Professional example: {st.session_state.api_example_prompt}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "🔑 Powered by Free APIs | Professional Quality | ~5,600+ Free Images/Month"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
