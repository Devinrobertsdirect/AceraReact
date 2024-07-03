from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/activate-gesture-control', methods=['GET'])
def activate_gesture_control():
    try:
        # Execute tracking.py script for gesture control
        subprocess.run(['python', './tracking.py'], check=True)
        return jsonify({'message': 'Gesture control activated successfully'})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500  # Handle subprocess error
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Handle any other exceptions

@app.route('/activate-acera-ai', methods=['GET'])
def activate_acera_ai():
    try:
        # Execute acera_ai.py script for Acera AI
        subprocess.run(['python', './AceraAI.py'], check=True)
        return jsonify({'message': 'Acera AI activated successfully'})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500  # Handle subprocess error
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Handle any other exceptions

if __name__ == '__main__':
    app.run(debug=True)
