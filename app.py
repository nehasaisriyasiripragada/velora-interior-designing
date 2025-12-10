from flask import Flask, render_template, request, jsonify, send_from_directory, send_file, make_response
from io import BytesIO
from huggingface_hub import InferenceClient
import os
from datetime import datetime
import uuid
import json
from pathlib import Path
import base64
from PIL import Image
import torch
import cv2
import numpy as np
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, UniPCMultistepScheduler
from transformers import AutoModel


app = Flask(__name__)
from dotenv import load_dotenv
import os
from huggingface_hub import login

# Automatically use CUDA if available, otherwise fall back to CPU
device = torch.device("cpu")

# Use float16 for better performance on GPU (optional)
dtype = torch.float32


# Configure upload folder for generated images
UPLOAD_FOLDER = 'static/generated'
METADATA_FILE = 'design_metadata.json'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['METADATA_FILE'] = METADATA_FILE

# Initialize metadata file if it doesn't exist
if not os.path.exists(METADATA_FILE):
    with open(METADATA_FILE, 'w') as f:
        json.dump({}, f)

# Initialize the Hugging Face client
client = InferenceClient(model="stabilityai/stable-diffusion-xl-base-1.0")
def save_metadata(filename, prompt):
    """Save design metadata to JSON file"""
    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
    
    metadata[filename] = {
        'prompt': prompt,
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'filepath': f"/static/generated/{filename}"
    }
    
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

def get_metadata():
    """Get all design metadata"""
    with open(METADATA_FILE, 'r') as f:
        return json.load(f)

try:
    controlnet = ControlNetModel.from_pretrained(
        "lllyasviel/sd-controlnet-canny", 
        torch_dtype=dtype
    )
    pipe = StableDiffusionControlNetPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        controlnet=controlnet,
        torch_dtype=dtype,
    ).to(device)
    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
    if device == "cuda":
        pipe.enable_xformers_memory_efficient_attention()
except Exception as e:
    print(f"Error loading models: {e}")
    pipe = None

def get_canny(image):
    image = np.array(image)
    image = cv2.Canny(image, 100, 200)
    image = image[:, :, None]
    image = np.concatenate([image] * 3, axis=2)
    return Image.fromarray(image)



# Routes
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/models')
def models():
    return render_template('models.html')
@app.route('/modelsafter')
def modelsafter():
    return render_template('modelsafter.html')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/design')
def design():
    return render_template('design.html')
@app.route('/designafter')
def designafter():
    return render_template('designafter.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/contactafter')
def contactafter():
    return render_template('contactafter.html')
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/prompt')
def prompt():
    return render_template('prompt.html')
@app.route('/upload')
def upload():
    return render_template('upload.html')
@app.route('/article')
def article():
    return render_template('article.html')
@app.route('/articlematerial')
def articlematerial():
    return render_template('articlematerial.html')
@app.route('/articlesmall')
def articlesmall():
    return render_template('articlesmall.html')
@app.route('/projects')
def projects():
    """Display all generated designs"""
    metadata = get_metadata()
    # Sort by creation date (newest first)
    sorted_designs = sorted(
        metadata.items(),
        key=lambda x: x[1]['created_at'],
        reverse=True
    )
    return render_template('projects.html', designs=sorted_designs)
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        # Read image directly to memory
        img = Image.open(file.stream).convert("RGB")
        
        # Convert to base64
        img_io = BytesIO()
        img.save(img_io, 'JPEG', quality=85)
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        
        return jsonify({
            'status': 'success',
            'image_data': img_base64
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/generate', methods=['POST'])
def generate_design1():
    if not pipe:
        return jsonify({'error': 'AI model not loaded'}), 500
        
    data = request.json
    
    try:
        # Get image data from base64
        image_bytes = base64.b64decode(data['image_data'])
        input_image = Image.open(BytesIO(image_bytes)).convert("RGB").resize((512, 512))
        
        # Generate canny edge map
        control_image = get_canny(input_image)
        
        # Map color theme names to descriptive terms
        color_mapping = {
            "neutral": "Neutral white and grey",
            "warm": "Warm orange and yellow",
            "cool": "Cool blue and light blue",
            "earthy": "Earthy green and brown",
            "bold": "Bold red and black",
            "rich": "Rich purple and gold"
        }
        
        color_description = color_mapping.get(data['color_theme'], "Balanced")
        
        # Create prompt
        prompt = (
            f"{data['design_style']} interior design of a {data['room_type']} with "
            f"{', '.join(data['furniture_preferences'])}. {color_description} color theme. "
            f"Budget range: {data['budget_range']}. Photorealistic, highly detailed, same layout and camera angle."
        )
        
        print(f"Generated prompt: {prompt}")
        
        negative_prompt = "low quality, blurry, distorted, cartoon, different angle, poor lighting"
        
        # Generate output
        output = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=control_image,
            num_inference_steps=30,
            guidance_scale=9.0
        ).images[0]
        
        # Convert output to base64
        output_io = BytesIO()
        output.save(output_io, 'JPEG', quality=90)
        output_base64 = base64.b64encode(output_io.getvalue()).decode('utf-8')
        
        return jsonify({
            'status': 'success',
            'before_image': data['image_data'],  # Original image
            'after_image': output_base64,        # Generated image
            'generation_id': str(uuid.uuid4())
        })
    except Exception as e:
        print(f"Error in generation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download', methods=['POST'])
def download_image():
    data = request.json
    try:
        image_bytes = base64.b64decode(data['image_data'])
        response = make_response(image_bytes)
        response.headers.set('Content-Type', 'image/jpeg')
        response.headers.set(
            'Content-Disposition', 'attachment',
            filename=f"velora-design-{data.get('generation_id', 'output')}.jpg"
        )
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Feedback endpoint
@app.route('/feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    try:
        # Here you would typically save this to a database
        # For now, we'll just acknowledge receipt
        print(f"Received feedback: Rating: {data.get('rating')}, Comments: {data.get('comments')}")
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500





@app.route('/generate-design', methods=['POST'])
def generate_design():
    try:
        # Get form data (works for both form-data and x-www-form-urlencoded)
        if request.is_json:
            data = request.get_json()
            design_prompt = data.get('designPrompt')
            style_preference = data.get('stylePreference')
            color_scheme = data.get('colorScheme')
        else:
            design_prompt = request.form.get('designPrompt')
            style_preference = request.form.get('stylePreference')
            color_scheme = request.form.get('colorScheme')
        
        if not all([design_prompt, style_preference, color_scheme]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        
        # Enhance the prompt with style and color preferences
        enhanced_prompt = f"{design_prompt}, {style_preference} style, {color_scheme} color scheme, high quality interior design, photorealistic, 4k"
        
        # Generate the image using Stable Diffusion
        image = client.text_to_image(enhanced_prompt)
        
        # Save the generated image with a unique filename
        filename = f"design_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)
        
        # Return the URL of the generated image
        image_url = f"/static/generated/{filename}"
        # Save metadata
        save_metadata(filename, enhanced_prompt)
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'prompt': enhanced_prompt
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/static/generated/<filename>')
def serve_generated_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True) 