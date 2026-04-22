"""
Flask Application with Input Sanitisation Middleware
Integrates the InputSanitiser to protect all endpoints
"""

from flask import Flask, request, jsonify
from services.input_sanitiser import InputSanitiser
import logging

# Initialize Flask app
app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# MIDDLEWARE: Input Validation (runs before every request)
# ============================================================================

@app.before_request
def validate_user_input():
    """
    Middleware to validate all incoming request data.
    Runs BEFORE every request to any endpoint.

    Rejects requests with dangerous patterns:
    - HTML/JavaScript tags
    - Prompt injection keywords
    - Email header injection attempts
    """

    # Only validate POST and PUT requests (when users send data)
    if request.method not in ['POST', 'PUT']:
        return None  # Let GET, DELETE, etc. through

    # Get the JSON data from the request
    data = request.get_json(silent=True)

    if not data:
        return None  # No data to validate

    # Validate all fields
    is_valid, error_message = InputSanitiser.validate_all_fields(data)

    # If validation fails, reject the request
    if not is_valid:
        logger.warning(f"⚠️  Input validation failed: {error_message}")
        return jsonify({
            "error": error_message,
            "status": "INPUT_VALIDATION_FAILED"
        }), 400

    # If validation passes, continue to the endpoint
    logger.info(f"✅ Input validation passed for {request.method} {request.path}")
    return None


# ============================================================================
# EXAMPLE ENDPOINTS (for testing)
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AI Service",
        "input_sanitisation": "enabled"
    }), 200


@app.route('/describe', methods=['POST'])
def describe():
    """
    Example AI endpoint: Describe a filing

    Request:
    {
        "filing_id": "123",
        "content": "Q1 Compliance Report"
    }

    Response:
    {
        "description": "This is a quarterly compliance filing..."
    }
    """
    try:
        data = request.get_json()

        # At this point, input has already been validated by middleware
        filing_id = data.get('filing_id')
        content = data.get('content')

        # Simulate AI processing
        description = f"Analysis of filing {filing_id}: {content}"

        return jsonify({
            "filing_id": filing_id,
            "description": description,
            "status": "success"
        }), 200

    except Exception as e:
        logger.error(f"❌ Error in /describe: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "status": "ERROR"
        }), 500


@app.route('/categorise', methods=['POST'])
def categorise():
    """
    Example AI endpoint: Categorise a filing

    Request:
    {
        "content": "Financial statement for Q1"
    }

    Response:
    {
        "category": "FINANCIAL",
        "confidence": 0.95
    }
    """
    try:
        data = request.get_json()

        # Input is already validated by middleware
        content = data.get('content')

        # Simulate AI categorisation
        category = "REGULATORY"
        confidence = 0.92

        return jsonify({
            "content": content[:50] + "...",  # Return first 50 chars
            "category": category,
            "confidence": confidence,
            "status": "success"
        }), 200

    except Exception as e:
        logger.error(f"❌ Error in /categorise: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "status": "ERROR"
        }), 500


@app.route('/generate-report', methods=['POST'])
def generate_report():
    """
    Example AI endpoint: Generate regulatory report

    Request:
    {
        "filing_id": "123",
        "document_type": "COMPLIANCE"
    }

    Response:
    {
        "report_id": "report_abc123",
        "content": "Generated report..."
    }
    """
    try:
        data = request.get_json()

        # Input is already validated by middleware
        filing_id = data.get('filing_id')
        document_type = data.get('document_type')

        # Simulate report generation
        report = f"Report for {filing_id} of type {document_type}"

        return jsonify({
            "filing_id": filing_id,
            "document_type": document_type,
            "report": report,
            "status": "success"
        }), 200

    except Exception as e:
        logger.error(f"❌ Error in /generate-report: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "status": "ERROR"
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    return jsonify({
        "error": "Bad request",
        "status": "ERROR"
    }), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "status": "ERROR"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"❌ Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "status": "ERROR"
    }), 500


# ============================================================================
# RUN THE APP
# ============================================================================

if __name__ == '__main__':
    print("🚀 Starting AI Service with Input Sanitisation Middleware")
    print("📝 Input Sanitisation: ENABLED")
    print("🔒 Protections Active:")
    print("   - HTML/JavaScript injection prevention")
    print("   - Prompt injection prevention")
    print("   - Email header injection prevention")
    print("\n📍 Server running on: http://localhost:5000")
    print("💊 Health check: http://localhost:5000/health\n")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )