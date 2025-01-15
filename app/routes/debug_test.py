from flask import Blueprint, jsonify

debug_test_bp = Blueprint('debug_test', __name__)

@debug_test_bp.route('/debug-test')
def test_debug():
    # Good place to set a breakpoint
    test_var = "Hello from debugger!"
    result = process_test_data(test_var)
    return jsonify({"message": result})

def process_test_data(data: str) -> str:
    # Another good place for a breakpoint
    processed = data.upper()
    return f"Processed: {processed}"
