from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import json
import traceback
import logging
from datetime import datetime
from src.data_analyzer import DataAnalyzer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=['*'])

# Configure upload folder
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize the analyzer
try:
    analyzer = DataAnalyzer()
    logger.info("DataAnalyzer initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize DataAnalyzer: {e}")
    analyzer = None

@app.route('/')
def home():
    """Landing page"""
    return render_template('index.html')

@app.route('/docs')
def docs():
    """API documentation page"""
    return render_template('api_docs.html')

@app.route('/api/', methods=['POST'])
def analyze_data():
    """Main API endpoint for data analysis"""
    start_time = datetime.now()
    
    try:
        if not analyzer:
            return jsonify({"error": "Service temporarily unavailable"}), 503
        
        # Validate request
        if 'questions.txt' not in request.files:
            return jsonify({"error": "questions.txt file is required"}), 400
        
        # Get the questions file
        questions_file = request.files['questions.txt']
        if questions_file.filename == '':
            return jsonify({"error": "No questions.txt file selected"}), 400
        
        questions = questions_file.read().decode('utf-8')
        logger.info(f"Processing questions: {questions[:100]}...")
        
        # Get additional files
        additional_files = {}
        for key, file in request.files.items():
            if key != 'questions.txt' and file.filename != '':
                logger.info(f"Processing additional file: {key}")
                additional_files[key] = file
        
        # Process the analysis
        result = analyzer.analyze(questions, additional_files)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Analysis completed in {processing_time:.2f} seconds")
        
        # Add metadata to result
        if isinstance(result, list):
            return jsonify(result)
        else:
            return jsonify({
                "result": result,
                "metadata": {
                    "processing_time": processing_time,
                    "timestamp": start_time.isoformat()
                }
            })
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Analysis failed", 
            "message": str(e),
            "type": type(e).__name__
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "analyzer_ready": analyzer is not None
        }
        
        if analyzer:
            # Quick analyzer health check
            test_result = analyzer.health_check()
            status["analyzer_status"] = test_result
        
        return jsonify(status)
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/status')
def api_status():
    """API status and capabilities"""
    return jsonify({
        "api_version": "1.0.0",
        "supported_formats": ["csv", "json", "xlsx", "txt"],
        "max_file_size": "50MB",
        "features": [
            "Web scraping",
            "Statistical analysis", 
            "Data visualization",
            "AI-powered insights",
            "Correlation analysis"
        ],
        "ai_model": "Gemini Pro"
    })

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 50MB."}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
