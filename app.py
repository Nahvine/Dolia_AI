from flask import Flask, render_template, request, jsonify
from main import DoliaAI
import logging
import json
import time

app = Flask(__name__)
dolia = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    try:
        global dolia
        if dolia is None:
            dolia = DoliaAI()
            if not dolia.start():
                return jsonify({'success': False, 'error': 'Không thể khởi động DoliaAI'})
        
        data = request.get_json()
        command = data.get('command', '')
        
        if not command:
            return jsonify({'success': False, 'error': 'Không có lệnh được cung cấp'})
        
        # Phân tích lệnh phức hợp
        commands = command.split(' và ')
        results = []
        
        for cmd in commands:
            # Chuyển đổi lệnh thành action data
            action_data = {
                "type": "command",
                "command": cmd.strip()
            }
            
            # Thực thi hành động
            result = dolia.execute_action(action_data)
            results.append(result)
            
            # Nếu có lỗi, dừng lại
            if not result.get('success', False):
                return jsonify({'success': False, 'error': result.get('error', 'Lỗi không xác định')})
            
            # Đợi một chút giữa các lệnh
            time.sleep(1)
            
        return jsonify({'success': True, 'results': results})
            
    except Exception as e:
        logging.error(f"Lỗi khi xử lý lệnh: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/stop', methods=['POST'])
def stop():
    try:
        global dolia
        if dolia:
            dolia.stop()
            dolia = None
        return jsonify({'success': True, 'message': 'Đã dừng DoliaAI'})
    except Exception as e:
        logging.error(f"Lỗi khi dừng DoliaAI: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 