"""
Video Controller - handles video analysis endpoints
"""
import os
import time
import logging
from datetime import datetime, timezone
from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename
from utils import success_response, error_response, bad_request
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)
video_bp = Blueprint('video', __name__, url_prefix='/api')


def _get_genai_client():
    """Get Google GenAI client instance"""
    return genai.Client(
        http_options=types.HttpOptions(
            base_url=current_app.config.get("GOOGLE_API_BASE")
        ),
        api_key=current_app.config.get("GOOGLE_API_KEY")
    )


def _save_uploaded_file(file):
    """Save uploaded file to temporary location"""
    try:
        # Create uploads directory if not exists
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save file with secure filename
        filename = secure_filename(file.filename)
        # Add timestamp to filename to avoid conflicts
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        file.save(file_path)
        logger.info(f"Uploaded file saved to: {file_path}")
        
        return file_path
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {str(e)}")
        raise


def _cleanup_file(file_path):
    """Clean up temporary file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.error(f"Failed to clean up temporary file: {str(e)}")


@video_bp.route('/video-analysis', methods=['POST'])
def analyze_video():
    """
    POST /api/video-analysis - Analyze video content
    
    Request body:
    - file: Video file (multipart/form-data)
    - prompt: Optional analysis prompt
    
    Response:
    - analysis: Video analysis result
    - file_id: Unique file identifier
    - status: Analysis status
    """
    try:
        # Check if file is provided
        if 'file' not in request.files:
            return bad_request("Video file is required")
        
        file = request.files['file']
        if file.filename == '':
            return bad_request("No file selected")
        
        # Check file type
        if not file.content_type or not file.content_type.startswith('video/'):
            return bad_request("Invalid file type. Please upload a video file.")
        
        # Check file size (200MB limit)
        max_size = 200 * 1024 * 1024  # 200MB
        if file.content_length > max_size:
            return bad_request("File too large. Maximum size is 200MB.")
        
        # Get analysis prompt
        prompt = request.form.get('prompt', '请详细分析这个视频的内容')
        
        logger.info(f"Received video analysis request: {file.filename}, prompt: {prompt}")
        
        # Save uploaded file
        file_path = _save_uploaded_file(file)
        
        try:
            # Initialize GenAI client
            client = _get_genai_client()
            
            # Upload video to GenAI
            logger.info(f"Uploading video to GenAI: {file_path}")
            uploaded_file = client.files.upload(file=file_path)
            logger.info(f"Video uploaded to GenAI, initial state: {uploaded_file.state.name}")
            
            # Wait for video processing to complete
            while uploaded_file.state.name == "PROCESSING":
                logger.info(f"Video processing in progress...")
                time.sleep(3)  # Check every 3 seconds
                uploaded_file = client.files.get(name=uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                logger.error("Video processing failed")
                return error_response('VIDEO_PROCESSING_FAILED', 'Video processing failed', 500)
            
            logger.info(f"Video processing completed (status: {uploaded_file.state.name})")
            
            # Perform video analysis
            logger.info(f"Starting video analysis with prompt: {prompt}")
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[uploaded_file, prompt]
            )
            
            # Extract analysis result
            analysis_result = response.text if hasattr(response, 'text') else ""
            if not analysis_result:
                logger.error("No analysis result returned from GenAI")
                return error_response('ANALYSIS_FAILED', 'Failed to get analysis result', 500)
            
            logger.info("Video analysis completed successfully")
            
            return success_response({
                'analysis': analysis_result,
                'file_id': uploaded_file.name,
                'status': 'COMPLETED'
            })
            
        finally:
            # Clean up temporary file
            _cleanup_file(file_path)
            
    except Exception as e:
        logger.error(f"Video analysis failed: {str(e)}", exc_info=True)
        return error_response('SERVER_ERROR', str(e), 500)
