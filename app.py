import os
import io
import time
import uuid
import base64
import logging
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
from dotenv import load_dotenv
import replicate

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = Path(os.environ.get('UPLOAD_DIR', 'uploads'))
UPLOAD_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allowed image types and max file size (10MB)
ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/bmp', 'image/tiff'}
MAX_FILE_SIZE = 10 * 1024 * 1024
# Max image dimension for API input (Replicate limits)
MAX_DIMENSION = 2048


def validate_image(file) -> tuple[Image.Image | None, str | None]:
    """Validate uploaded file and return PIL Image or error."""
    if not file:
        return None, '没有收到文件'

    if file.content_type not in ALLOWED_TYPES:
        return None, f'不支持的格式: {file.content_type}，只支持 JPG/PNG/WebP/BMP'

    data = file.read()
    if len(data) > MAX_FILE_SIZE:
        return None, f'文件过大，最大支持 10MB'

    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except Exception:
        return None, '无法解析图片文件'

    # Convert to RGB if needed
    if img.mode in ('RGBA', 'LA', 'P'):
        if img.mode == 'P':
            img = img.convert('RGBA')
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'RGBA':
            background.paste(img, mask=img.split()[3])
        else:
            background.paste(img)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize if too large
    if max(img.size) > MAX_DIMENSION:
        ratio = MAX_DIMENSION / max(img.size)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    return img, None


def save_upload(img: Image.Image) -> Path:
    """Save image to disk and return path."""
    filename = f"{uuid.uuid4().hex}.png"
    filepath = UPLOAD_DIR / filename
    img.save(filepath, 'PNG', optimize=True)
    return filepath


def img_to_data_url(img: Image.Image) -> str:
    """Convert PIL Image to base64 data URL."""
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=85, optimize=True)
    data = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/jpeg;base64,{data}"


def call_replicate(model_ref: str, input_data: dict, timeout: int = 120) -> bytes | None:
    """Call Replicate API and return output image bytes."""
    api_token = os.getenv('REPLICATE_API_TOKEN')
    if not api_token:
        raise ValueError('请先设置 REPLICATE_API_TOKEN 环境变量')

    client = replicate.Client(api_token=api_token)
    logger.info(f"Calling {model_ref} with keys: {list(input_data.keys())}")

    output = client.run(model_ref, input=input_data)

    # output can be a URL string, FileOutput, or list
    if isinstance(output, list):
        output = output[0] if output else None

    if output is None:
        raise RuntimeError('模型返回空结果')

    if hasattr(output, 'read'):
        return output.read()

    if isinstance(output, str):
        import requests
        resp = requests.get(output, timeout=timeout)
        resp.raise_for_status()
        return resp.content

    raise RuntimeError(f'未知输出类型: {type(output)}')


# ─── Routes ────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/terms')
def terms():
    return render_template('terms.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/ads.txt')
def ads_txt():
    return send_file('static/ads.txt', mimetype='text/plain')


@app.route('/robots.txt')
def robots_txt():
    return send_file('static/robots.txt', mimetype='text/plain')


@app.route('/sitemap.xml')
def sitemap():
    return send_file('static/sitemap.xml', mimetype='application/xml')


@app.route('/api/tools/enhance', methods=['POST'])
def enhance():
    """AI 图片增强 (Real-ESRGAN 超分辨率)"""
    img, err = validate_image(request.files.get('image'))
    if err:
        return jsonify({'error': err}), 400

    filepath = save_upload(img)

    try:
        result_bytes = call_replicate(
            'nightmareai/real-esrgan:42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738dd1b1',
            {'image': open(filepath, 'rb')},
        )
        result_img = Image.open(io.BytesIO(result_bytes))
        data_url = img_to_data_url(result_img)

        return jsonify({
            'success': True,
            'result': data_url,
            'original_size': f'{img.width}x{img.height}',
            'enhanced_size': f'{result_img.width}x{result_img.height}',
        })
    except Exception as e:
        logger.exception('Enhance failed')
        return jsonify({'error': f'增强失败: {str(e)}'}), 500


@app.route('/api/tools/remove-bg', methods=['POST'])
def remove_bg():
    """AI 背景移除"""
    img, err = validate_image(request.files.get('image'))
    if err:
        return jsonify({'error': err}), 400

    filepath = save_upload(img)

    try:
        result_bytes = call_replicate(
            'cjwbw/rembg:fb8af171cfa1616f9a0961b2f778c8c2b9035d81dec669a88a9e17f8d829a7db',
            {'image': open(filepath, 'rb')},
        )
        result_img = Image.open(io.BytesIO(result_bytes))
        data_url = img_to_data_url(result_img)

        return jsonify({
            'success': True,
            'result': data_url,
            'original_size': f'{img.width}x{img.height}',
        })
    except Exception as e:
        logger.exception('Remove BG failed')
        return jsonify({'error': f'背景移除失败: {str(e)}'}), 500


@app.route('/api/tools/restore', methods=['POST'])
def restore():
    """AI 老照片修复 (GFPGAN 面部修复 + 上色)"""
    img, err = validate_image(request.files.get('image'))
    if err:
        return jsonify({'error': err}), 400

    filepath = save_upload(img)

    try:
        # Use GFPGAN for face restoration
        result_bytes = call_replicate(
            'tencentarc/gfpgan:9283608cc6b7be6b65a8e44983db012355fde4132009bf99d976b2f0896856a3',
            {'img': open(filepath, 'rb'), 'scale': 2, 'version': 'v1.4'},
        )
        result_img = Image.open(io.BytesIO(result_bytes))
        data_url = img_to_data_url(result_img)

        return jsonify({
            'success': True,
            'result': data_url,
            'original_size': f'{img.width}x{img.height}',
            'restored_size': f'{result_img.width}x{result_img.height}',
        })
    except Exception as e:
        logger.exception('Restore failed')
        return jsonify({'error': f'修复失败: {str(e)}'}), 500


@app.route('/api/tools/generate', methods=['POST'])
def generate():
    """AI 文字生成图片 (Stable Diffusion)"""
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({'error': '请输入描述文字'}), 400

    prompt = data['prompt'].strip()
    if len(prompt) < 2:
        return jsonify({'error': '描述文字太短'}), 400

    negative = data.get('negative', 'ugly, blurry, low quality, distorted, deformed')
    width = min(int(data.get('width', 512)), 1024)
    height = min(int(data.get('height', 512)), 1024)

    try:
        result_bytes = call_replicate(
            'stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b',
            {
                'prompt': prompt,
                'negative_prompt': negative,
                'width': width,
                'height': height,
                'num_outputs': 1,
                'num_inference_steps': 25,
                'guidance_scale': 7.5,
            },
            timeout=180,
        )

        buf = io.BytesIO(result_bytes)
        data_url = 'data:image/png;base64,' + base64.b64encode(result_bytes).decode('utf-8')

        return jsonify({
            'success': True,
            'result': data_url,
            'prompt': prompt,
        })
    except Exception as e:
        logger.exception('Generate failed')
        return jsonify({'error': f'生成失败: {str(e)}'}), 500


# ─── Cleanup old uploads periodically (keep 1 hour) ──────

@app.before_request
def cleanup():
    now = time.time()
    for f in UPLOAD_DIR.glob('*.png'):
        if now - f.stat().st_mtime > 3600:
            try:
                f.unlink()
            except OSError:
                pass


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
