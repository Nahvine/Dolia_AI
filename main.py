import os
import json
import base64
import requests
import pyautogui
import time
import subprocess
from PIL import Image
import io
import logging
import sys
import codecs
import random
import re
import threading
import queue
from controller import ComputerController
from datetime import datetime
import platform
import win32gui
import win32con
import win32process
import psutil

# Cấu hình logging với encoding UTF-8
if platform.system() == 'Windows':
    # Xử lý đặc biệt cho Windows Console
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleCP(65001)  # UTF-8
    kernel32.SetConsoleOutputCP(65001)  # UTF-8
else:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("main.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Cấu hình API
API_KEY = "AIzaSyBQJfAFkGRsv_jhL0FP1Sf4eXVfNhoo7Ec"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# Lưu trữ context của cuộc hội thoại
conversation_context = {
    "last_actions": [],  # Lưu các hành động đã thực hiện
    "failed_approaches": set(),  # Lưu các cách tiếp cận đã thất bại
    "successful_patterns": {},  # Lưu các mẫu thành công để học hỏi
    "current_state": {},  # Lưu trạng thái hiện tại của hệ thống
    "user_preferences": {}  # Lưu các tùy chọn của người dùng
}

def analyze_user_intent(request):
    """Phân tích ý định người dùng một cách thông minh và linh hoạt"""
    try:
        # Chuẩn hóa yêu cầu
        request = request.lower().strip()
        
        # Xử lý các yêu cầu phức hợp đặc biệt
        if "notepad" in request and "save" in request:
            # Tách các thành phần của yêu cầu
            file_name = None
            file_path = None
            code_content = None
            
            # Tìm tên file
            if "name" in request:
                file_name = "name.py"
            
            # Tìm đường dẫn
            if "documents" in request or "document" in request:
                file_path = "%USERPROFILE%\\Documents"
            
            # Tạo nội dung code mẫu
            code_content = """# Python basic example
print("Hello, World!")

def main():
    name = input("Enter your name: ")
    print(f"Hello, {name}!")

if __name__ == "__main__":
    main()
"""
            
            # Tạo chuỗi hành động
            return {
                "action_type": "create_and_save_file",
                "target": "notepad",
                "parameters": {
                    "file_name": file_name or "script.py",
                    "file_path": file_path or "%USERPROFILE%\\Documents",
                    "content": code_content
                },
                "steps": [
                    {
                        "action": "open",
                        "target": "notepad",
                        "parameters": {}
                    },
                    {
                        "action": "type",
                        "target": "notepad",
                        "parameters": {
                            "text": code_content
                        }
                    },
                    {
                        "action": "hotkey",
                        "target": "notepad",
                        "parameters": {
                            "keys": ["ctrl", "s"]
                        }
                    },
                    {
                        "action": "wait",
                        "target": "system",
                        "parameters": {
                            "seconds": 1
                        }
                    },
                    {
                        "action": "type",
                        "target": "save_dialog",
                        "parameters": {
                            "text": os.path.join(file_path or "%USERPROFILE%\\Documents", file_name or "script.py")
                        }
                    },
                    {
                        "action": "press_key",
                        "target": "save_dialog",
                        "parameters": {
                            "key": "enter"
                        }
                    }
                ],
                "fallback_options": [
                    # Phương án 1: Dùng CMD để tạo thư mục và file
                    {
                        "action": "run_command",
                        "target": "system",
                        "parameters": {
                            "command": f"mkdir \"{file_path or '%USERPROFILE%\\Documents'}\" && echo {code_content} > \"{os.path.join(file_path or '%USERPROFILE%\\Documents', file_name or 'script.py')}\""
                        }
                    },
                    # Phương án 2: Dùng PowerShell
                    {
                        "action": "run_command",
                        "target": "system",
                        "parameters": {
                            "command": f"powershell -Command \"New-Item -Path '{file_path or '%USERPROFILE%\\Documents'}' -ItemType Directory -Force; Set-Content -Path '{os.path.join(file_path or '%USERPROFILE%\\Documents', file_name or 'script.py')}' -Value '{code_content}'\""
                        }
                    },
                    # Phương án 3: Dùng Explorer và tổ hợp phím
                    {
                        "action": "open",
                        "target": "explorer",
                        "parameters": {
                            "path": file_path or "%USERPROFILE%\\Documents"
                        }
                    },
                    {
                        "action": "hotkey",
                        "target": "explorer",
                        "parameters": {
                            "keys": ["ctrl", "shift", "n"]
                        }
                    },
                    {
                        "action": "type",
                        "target": "explorer",
                        "parameters": {
                            "text": file_name or "script.py"
                        }
                    },
                    {
                        "action": "press_key",
                        "target": "explorer",
                        "parameters": {
                            "key": "enter"
                        }
                    }
                ]
            }
            
        # Xử lý các yêu cầu đơn giản
        return basic_intent_analysis(request)
        
    except Exception as e:
        logging.error(f"Lỗi khi phân tích ý định: {str(e)}")
        return None

def basic_intent_analysis(request):
    """Phân tích ý định cơ bản khi AI không thể phân tích"""
    try:
        # Chuẩn hóa yêu cầu
        request = request.lower().strip()
        
        # Từ điển ánh xạ từ đồng nghĩa và ngữ cảnh
        context_mapping = {
            # Ánh xạ các ứng dụng web
            "youtube": {
                "action": "open",
                "target": "chrome",
                "url": "https://www.youtube.com"
            },
            "facebook": {
                "action": "open",
                "target": "chrome", 
                "url": "https://www.facebook.com"
            },
            "google": {
                "action": "open",
                "target": "chrome",
                "url": "https://www.google.com"
            },
            
            # Ánh xạ thư mục/folder
            "thư mục": "explorer",
            "folder": "explorer",
            "directory": "explorer",
            "thu muc": "explorer",
            
            # Ánh xạ các thư mục đặc biệt  
            "download": "%USERPROFILE%\\Downloads",
            "downloads": "%USERPROFILE%\\Downloads",
            "documents": "%USERPROFILE%\\Documents",
            "desktop": "%USERPROFILE%\\Desktop",
            
            # Ánh xạ các ứng dụng phổ biến
            "notepad": "notepad",
            "chrome": "chrome",
            "edge": "msedge",
            "firefox": "firefox",
            
            # Ánh xạ các hành động phổ biến
            "mở": "open",
            "đóng": "close",
            "tìm": "search"
        }

        # Phân tích yêu cầu
        words = request.split()
        action_type = None
        target = None
        parameters = {}

        # Tìm action_type 
        for word in words:
            if word in context_mapping:
                if isinstance(context_mapping[word], dict):
                    # Xử lý các ứng dụng web
                    web_app = context_mapping[word]
                    action_type = web_app["action"]
                    target = web_app["target"]
                    parameters["url"] = web_app["url"]
                    break
                elif context_mapping[word] not in ["open", "close", "search"]:
                    target = context_mapping[word]
                    if target in ["%USERPROFILE%\\Downloads", "%USERPROFILE%\\Documents", "%USERPROFILE%\\Desktop"]:
                        parameters["path"] = target
                    break
                else:
                    action_type = context_mapping[word]

        # Nếu không tìm thấy action_type, mặc định là "open"
        if not action_type:
            action_type = "open"

        # Nếu không tìm thấy target, thử tìm trong phần còn lại của câu
        if not target:
            try:
                action_index = words.index(next(w for w in words if w in context_mapping))
                remaining_words = " ".join(words[action_index + 1:])
                for key, value in context_mapping.items():
                    if key in remaining_words:
                        if isinstance(value, dict):
                            web_app = value
                            target = web_app["target"]
                            parameters["url"] = web_app["url"]
                        else:
                            target = value
                            if target in ["%USERPROFILE%\\Downloads", "%USERPROFILE%\\Documents", "%USERPROFILE%\\Desktop"]:
                                parameters["path"] = target
                        break
            except (StopIteration, ValueError):
                pass

        # Nếu vẫn không tìm thấy target, mặc định là explorer
        if not target:
            target = "explorer"
            parameters["path"] = "%USERPROFILE%\\Downloads"

        # Tạo intent với cấu trúc chuẩn
        intent = {
            "action": action_type,
            "target": target,
            "parameters": parameters
        }

        logging.info(f"Phân tích ý định cơ bản: {json.dumps(intent, ensure_ascii=False)}")
        return intent

    except Exception as e:
        logging.error(f"Lỗi khi phân tích ý định cơ bản: {str(e)}")
        return None

def learn_from_success(action_data, result):
    """Học hỏi từ các hành động thành công"""
    if result.get("success"):
        pattern = {
            "intent": action_data.get("intent", {}),
            "approach": action_data.get("approach", ""),
            "action_sequence": action_data.get("steps", [])
        }
        
        # Lưu pattern vào successful_patterns
        key = f"{pattern['intent'].get('action_type')}_{pattern['intent'].get('target')}"
        if key not in conversation_context["successful_patterns"]:
            conversation_context["successful_patterns"][key] = []
        conversation_context["successful_patterns"][key].append(pattern)

def adapt_to_failures(action_data, result):
    """Điều chỉnh chiến lược dựa trên các thất bại"""
    if not result.get("success"):
        # Lưu cách tiếp cận thất bại
        conversation_context["failed_approaches"].add(action_data.get("approach", ""))
        
        # Phân tích lỗi
        error = result.get("error", "")
        if "permission" in error.lower():
            conversation_context["current_state"]["needs_elevation"] = True
        elif "not found" in error.lower():
            conversation_context["current_state"]["needs_alternative_path"] = True

def update_context(request, action_data, result):
    """Cập nhật context dựa trên tương tác"""
    # Lưu hành động gần nhất
    conversation_context["last_actions"].append({
        "request": request,
        "action": action_data,
        "result": result,
        "timestamp": time.time()
    })
    
    # Giới hạn số lượng hành động lưu trữ
    if len(conversation_context["last_actions"]) > 10:
        conversation_context["last_actions"].pop(0)
    
    # Học hỏi từ kết quả
    learn_from_success(action_data, result)
    adapt_to_failures(action_data, result)

def get_smart_suggestions(intent, screenshot_analysis):
    """Đưa ra gợi ý thông minh dựa trên context"""
    suggestions = []
    
    # Kiểm tra patterns thành công trước đây
    key = f"{intent.get('action_type')}_{intent.get('target')}"
    if key in conversation_context["successful_patterns"]:
        suggestions.extend(conversation_context["successful_patterns"][key])
    
    # Phân tích screenshot để tìm các elements phù hợp
    if screenshot_analysis and isinstance(screenshot_analysis, dict):
        elements = screenshot_analysis.get("elements", [])
        for element in elements:
            if intent["target"] and intent["target"].lower() in element.get("text", "").lower():
                suggestions.append({
                    "type": "element_click",
                    "coordinates": element.get("coordinates", {}),
                    "confidence": element.get("confidence", 0.5)
                })
    
    # Thêm các phương án dự phòng
    if not suggestions:
        suggestions.append({
            "type": "search",
            "action": "hotkey",
            "keys": ["win", "s"],
            "confidence": 0.7
        })
    
    return suggestions

# Danh sách các cách thực hiện đã thử
tried_approaches = set()

def capture_screen():
    """Chụp ảnh màn hình hiện tại và chuyển đổi sang base64"""
    try:
        screenshot = pyautogui.screenshot()
        img_byte_arr = io.BytesIO()
        screenshot.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return base64.b64encode(img_byte_arr).decode('utf-8')
    except Exception as e:
        logging.error(f"Lỗi khi chụp màn hình: {str(e)}")
        return None

def convert_context_for_json(context):
    """Chuyển đổi context để có thể serialize thành JSON"""
    converted = {}
    for key, value in context.items():
        if isinstance(value, set):
            converted[key] = list(value)
        elif isinstance(value, dict):
            converted[key] = convert_context_for_json(value)
        else:
            converted[key] = value
    return converted

def analyze_screen_state(screenshot_base64, context):
    """Phân tích trạng thái màn hình hiện tại một cách thông minh"""
    try:
        # Chuyển đổi context để có thể serialize
        serializable_context = convert_context_for_json(context)
        
        # Tạo JSON schema riêng
        json_schema = '''{
            "screen_state": {
                "active_window": {
                    "title": "string",
                    "state": "maximized|minimized|normal",
                    "is_responding": "boolean"
                },
                "visible_elements": [
                    {
                        "type": "window|button|text|menu|dialog",
                        "content": "string",
                        "location": {"x": "number", "y": "number"},
                        "is_clickable": "boolean",
                        "is_visible": "boolean",
                        "state": "enabled|disabled|loading"
                    }
                ],
                "system_state": {
                    "cursor_position": {"x": "number", "y": "number"},
                    "keyboard_focus": "string",
                    "is_loading": "boolean",
                    "has_popups": "boolean"
                }
            },
            "analysis": {
                "current_task_progress": {
                    "status": "not_started|in_progress|completed|failed",
                    "completion_percentage": "number",
                    "current_step": "string",
                    "remaining_steps": ["string"]
                },
                "detected_issues": [
                    {
                        "type": "error|warning|info",
                        "description": "string",
                        "severity": "high|medium|low",
                        "suggested_action": "string"
                    }
                ],
                "opportunities": [
                    {
                        "type": "shortcut|optimization|alternative",
                        "description": "string",
                        "confidence": "number"
                    }
                ]
            },
            "recommendations": {
                "next_action": {
                    "type": "string",
                    "target": "string",
                    "parameters": "object",
                    "reason": "string"
                },
                "fallback_actions": [
                    {
                        "type": "string",
                        "target": "string",
                        "parameters": "object",
                        "conditions": ["string"]
                    }
                ]
            }
        }'''

        # Tạo prompt với context và schema tách biệt
        prompt = f"""
        Bạn là một AI có khả năng quan sát và phân tích màn hình máy tính như một người thật.
        Nhiệm vụ của bạn là phân tích ảnh chụp màn hình và hiểu chính xác những gì đang diễn ra.

        CONTEXT HIỆN TẠI:
        {json.dumps(serializable_context, ensure_ascii=False)}

        NGUYÊN TẮC QUAN SÁT:
        1. Nhìn tổng thể:
           - Các cửa sổ đang mở
           - Vị trí con trỏ
           - Trạng thái hệ thống

        2. Nhìn chi tiết:
           - Text hiển thị
           - Nút bấm, menu
           - Thông báo lỗi
           - Trạng thái loading

        3. Phân tích mối quan hệ:
           - Thứ tự các cửa sổ
           - Luồng tương tác
           - Phụ thuộc giữa các elements

        4. Dự đoán và cảnh báo:
           - Các vấn đề tiềm ẩn
           - Điều kiện cần xử lý
           - Rủi ro có thể xảy ra

        Trả lời với cấu trúc JSON như sau:
        {json_schema}
        """

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": screenshot_base64
                            }
                        }
                    ]
                }
            ]
        }

        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        
        if 'candidates' in response.json() and len(response.json()['candidates']) > 0:
            content = response.json()['candidates'][0]['content']['parts'][0]['text']
            json_match = re.search(r'\{[\s\S]*\}', content)
            
            if json_match:
                return json.loads(json_match.group(0))
                
        return None
    except Exception as e:
        logging.error(f"Lỗi khi phân tích màn hình: {str(e)}")
        return None

def execute_action_with_verification(action, context):
    """Thực thi một hành động và liên tục kiểm tra kết quả"""
    try:
        # Thực hiện hành động
        controller = ComputerController()
        result = controller.execute_action(action)
        
        if not result.get("success"):
            return False, "Thất bại khi thực hiện hành động"

        # Đợi một chút để hệ thống phản hồi
        time.sleep(0.5)

        # Bắt đầu vòng lặp kiểm tra
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            # Chụp màn hình
            screenshot = capture_screen()
            if not screenshot:
                return False, "Không thể chụp màn hình"

            # Phân tích trạng thái hiện tại
            screen_state = analyze_screen_state(screenshot, context)
            if not screen_state:
                return False, "Không thể phân tích màn hình"

            # Kiểm tra tiến độ
            progress = screen_state["analysis"]["current_task_progress"]
            
            if progress["status"] == "completed":
                return True, "Hành động hoàn thành thành công"
            elif progress["status"] == "failed":
                return False, f"Hành động thất bại: {progress.get('current_step')}"
            
            # Xử lý các vấn đề phát hiện được
            issues = screen_state["analysis"]["detected_issues"]
            for issue in issues:
                if issue["severity"] == "high":
                    # Thực hiện hành động khắc phục
                    fix_action = generate_fix_action(issue)
                    if fix_action:
                        controller.execute_action(fix_action)

            # Tận dụng cơ hội tối ưu
            opportunities = screen_state["analysis"]["opportunities"]
            for opp in opportunities:
                if opp["confidence"] > 0.8:
                    optimize_action = generate_optimization_action(opp)
                    if optimize_action:
                        controller.execute_action(optimize_action)

            attempt += 1
            time.sleep(1)

        return False, "Hết thời gian chờ"

    except Exception as e:
        logging.error(f"Lỗi khi thực thi và xác minh hành động: {str(e)}")
        return False, str(e)

class SmartActionExecutor:
    """Lớp thực thi hành động thông minh với khả năng tự học"""
    
    def __init__(self):
        self.learning_data = {
            "successful_patterns": {},  # Lưu các mẫu thành công
            "error_solutions": {},      # Lưu các giải pháp cho lỗi
            "app_locations": {},        # Lưu vị trí các ứng dụng
            "common_apps": {
                "discord": {
                    "paths": [
                        "%LOCALAPPDATA%\\Discord\\app-1.0.9027\\Discord.exe",
                        "%LOCALAPPDATA%\\Discord\\Update.exe --processStart Discord.exe",
                        "discord.exe"
                    ],
                    "alternatives": ["browser", "https://discord.com/app"]
                },
                "chrome": {
                    "paths": [
                        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                        "chrome.exe"
                    ]
                },
                "explorer": {
                    "paths": ["explorer.exe"],
                    "special_folders": {
                        "downloads": "%USERPROFILE%\\Downloads",
                        "documents": "%USERPROFILE%\\Documents",
                        "desktop": "%USERPROFILE%\\Desktop",
                        "pictures": "%USERPROFILE%\\Pictures",
                        "music": "%USERPROFILE%\\Music",
                        "videos": "%USERPROFILE%\\Videos"
                    }
                }
            }
        }
        
    def learn_from_error(self, error, context):
        """Học từ lỗi và lưu giải pháp"""
        error_type = self._categorize_error(error)
        if error_type not in self.learning_data["error_solutions"]:
            self.learning_data["error_solutions"][error_type] = []
            
        solution = self._generate_solution(error, context)
        if solution:
            self.learning_data["error_solutions"][error_type].append(solution)
            
    def _categorize_error(self, error):
        """Phân loại lỗi để tìm giải pháp phù hợp"""
        error_str = str(error).lower()
        if "not found" in error_str or "no such file" in error_str:
            return "file_not_found"
        elif "permission" in error_str or "access denied" in error_str:
            return "permission_denied"
        elif "method not found" in error_str or "attribute error" in error_str:
            return "method_not_found"
        elif "timeout" in error_str:
            return "timeout"
        return "unknown"
        
    def _generate_solution(self, error, context):
        """Tạo giải pháp cho lỗi"""
        error_type = self._categorize_error(error)
        
        if error_type == "file_not_found":
            return {
                "type": "search_alternative_paths",
                "action": lambda: self._find_alternative_paths(context.get("target"))
            }
        elif error_type == "permission_denied":
            return {
                "type": "elevate_privileges",
                "action": lambda: self._run_as_admin(context.get("command"))
            }
        elif error_type == "method_not_found":
            return {
                "type": "use_alternative_method",
                "action": lambda: self._find_alternative_method(context)
            }
            
        return None
        
    def _find_alternative_paths(self, target):
        """Tìm đường dẫn thay thế cho ứng dụng"""
        if target in self.learning_data["common_apps"]:
            app_info = self.learning_data["common_apps"][target]
            
            # Thử từng đường dẫn có thể
            for path in app_info["paths"]:
                expanded_path = os.path.expandvars(path)
                if os.path.exists(expanded_path):
                    return expanded_path
                    
            # Thử phương án thay thế
            if "alternatives" in app_info:
                return app_info["alternatives"][0]
                
        # Tìm kiếm trong các thư mục phổ biến
        common_locations = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
            os.environ.get("LOCALAPPDATA"),
            os.environ.get("APPDATA")
        ]
        
        for location in common_locations:
            for root, dirs, files in os.walk(location):
                for file in files:
                    if file.lower() == f"{target}.exe":
                        return os.path.join(root, file)
                        
        return None
        
    def _run_as_admin(self, command):
        """Chạy lệnh với quyền admin"""
        try:
            return {
                "action": "elevate",
                "command": command,
                "use_shell": True
            }
        except Exception:
            return None
            
    def _find_alternative_method(self, context):
        """Tìm phương thức thay thế khi gặp lỗi method not found"""
        if context.get("action") == "focus_application":
            return {
                "action": "alternative_focus",
                "methods": [
                    lambda: pyautogui.hotkey('alt', 'tab'),
                    lambda: subprocess.run(["powershell", "-Command", f"(New-Object -ComObject Shell.Application).Windows() | Where-Object {{$_.Name -like '*{context.get('target')}*'}} | Select-Object -First 1"]),
                    lambda: os.system(f"explorer shell:appsfolder\\{context.get('target')}")
                ]
            }
        return None
        
    def execute_with_learning(self, action_data):
        """Thực thi hành động với khả năng học hỏi"""
        try:
            # Thử thực thi bình thường
            controller = ComputerController()
            result = controller.execute_action(action_data)
            
            if not result[0]:  # Nếu thất bại
                # Học từ lỗi
                self.learn_from_error(result[1], action_data)
                
                # Tìm giải pháp
                error_type = self._categorize_error(result[1])
                if error_type in self.learning_data["error_solutions"]:
                    for solution in self.learning_data["error_solutions"][error_type]:
                        try:
                            if solution["type"] == "search_alternative_paths":
                                alt_path = solution["action"]()
                                if alt_path:
                                    if isinstance(alt_path, str) and alt_path.startswith("http"):
                                        # Mở trong trình duyệt
                                        action_data["target"] = "chrome"
                                        action_data["parameters"]["url"] = alt_path
                                    else:
                                        # Cập nhật đường dẫn
                                        action_data["parameters"]["path"] = alt_path
                                    return controller.execute_action(action_data)
                                    
                            elif solution["type"] == "elevate_privileges":
                                elevated_action = solution["action"]()
                                if elevated_action:
                                    return controller.execute_action(elevated_action)
                                    
                            elif solution["type"] == "use_alternative_method":
                                alt_methods = solution["action"]()
                                if alt_methods:
                                    for method in alt_methods["methods"]:
                                        try:
                                            method()
                                            return True, "Thực hiện thành công bằng phương thức thay thế"
                                        except Exception:
                                            continue
                                            
                        except Exception as e:
                            logging.warning(f"Lỗi khi thử giải pháp: {str(e)}")
                            continue
                            
            return result
            
        except Exception as e:
            logging.error(f"Lỗi khi thực thi hành động: {str(e)}")
            return False, str(e)

def execute_complex_action(action_data):
    """Thực thi chuỗi hành động phức hợp"""
    try:
        # Kiểm tra xem có phải là hành động phức hợp không
        if "steps" not in action_data:
            return False, "Không phải hành động phức hợp"

        controller = ComputerController()
        steps = action_data["steps"]
        
        # Thực thi từng bước
        for i, step in enumerate(steps):
            logging.info(f"Thực hiện bước {i+1}/{len(steps)}: {step}")
            
            # Thực thi bước hiện tại
            result = controller.execute_action(step)
            
            # Kiểm tra kết quả
            if isinstance(result, tuple) and len(result) == 2:
                success, message = result
            else:
                success = False
                message = f"Kết quả không hợp lệ: {result}"
            
            if not success:
                logging.error(f"Lỗi ở bước {i+1}: {message}")
                
                # Nếu lỗi ở bước tạo thư mục, thử các phương án dự phòng
                if step.get("action") == "create_folder":
                    fallback_options = [
                        # Phương án 1: Dùng CMD để tạo thư mục
                        {
                            "action": "run_command",
                            "target": "system",
                            "parameters": {
                                "command": f"mkdir \"{step['parameters']['path']}\""
                            }
                        },
                        # Phương án 2: Dùng Explorer và tổ hợp phím
                        {
                            "action": "open",
                            "target": "explorer",
                            "parameters": {
                                "path": os.path.dirname(step['parameters']['path'])
                            }
                        },
                        {
                            "action": "hotkey",
                            "target": "explorer",
                            "parameters": {
                                "keys": ["ctrl", "shift", "n"]
                            }
                        },
                        {
                            "action": "type",
                            "target": "explorer",
                            "parameters": {
                                "text": os.path.basename(step['parameters']['path'])
                            }
                        },
                        {
                            "action": "press_key",
                            "target": "explorer",
                            "parameters": {
                                "key": "enter"
                            }
                        },
                        # Phương án 3: Dùng PowerShell
                        {
                            "action": "run_command",
                            "target": "system",
                            "parameters": {
                                "command": f"powershell -Command \"New-Item -Path '{step['parameters']['path']}' -ItemType Directory -Force\""
                            }
                        }
                    ]
                else:
                    fallback_options = action_data.get("fallback_options", [])
                
                # Thử từng phương án dự phòng
                for fallback in fallback_options:
                    logging.info(f"Thử phương án dự phòng: {fallback}")
                    result = controller.execute_action(fallback)
                    
                    # Kiểm tra kết quả
                    if isinstance(result, tuple) and len(result) == 2:
                        success, message = result
                    else:
                        success = False
                        message = f"Kết quả không hợp lệ: {result}"
                        
                    if success:
                        break
                
                if not success:
                    return False, f"Lỗi ở bước {i+1}: {message}"
            
            # Đợi một chút giữa các bước
            time.sleep(1)
        
        return True, "Thực hiện thành công tất cả các bước"
        
    except Exception as e:
        logging.error(f"Lỗi khi thực thi chuỗi hành động: {str(e)}")
        return False, str(e)

def process_user_request(request):
    """Xử lý yêu cầu của người dùng với Multi-Step Reasoning"""
    try:
        # Khởi tạo controller
        controller = ComputerController()
        
        # Phân tích trạng thái hiện tại
        current_state = controller.analyze_screen_state()
        if not current_state:
            return False, "Không thể phân tích trạng thái màn hình"

        # Tạo kế hoạch hành động
        action_plan = controller.create_action_plan(request, current_state)
        if not action_plan:
            return False, "Không thể tạo kế hoạch hành động"

        # Thực thi kế hoạch với phản hồi trực quan
        success = controller.execute_with_visual_feedback(action_plan)
        if not success:
            return False, "Lỗi khi thực thi kế hoạch"

        # Lưu kết quả để học hỏi
        _learn_from_execution(request, action_plan, success, "Hoàn thành")
        
        return True, "Hoàn thành yêu cầu thành công"
    except Exception as e:
        logging.error(f"Lỗi khi xử lý yêu cầu: {str(e)}")
        return False, f"Lỗi: {str(e)}"

def _learn_from_execution(request, action_plan, success, message):
    """Học hỏi từ kết quả thực thi"""
    try:
        # Lưu kết quả vào cơ sở dữ liệu học tập
        learning_data = {
            "request": request,
            "action_plan": action_plan,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Cập nhật prompt cho Gemini dựa trên kết quả
        if success:
            _update_successful_patterns(learning_data)
        else:
            _update_failure_patterns(learning_data)
            
    except Exception as e:
        logging.error(f"Lỗi khi học hỏi từ kết quả: {str(e)}")

def _update_successful_patterns(learning_data):
    """Cập nhật các mẫu thành công"""
    try:
        # Lưu mẫu thành công vào cơ sở dữ liệu
        successful_patterns.append(learning_data)
        
        # Cập nhật prompt cho Gemini
        prompt_update = {
            "parts": [
                {"text": "Cập nhật mẫu thành công:"},
                {"text": f"Dữ liệu: {json.dumps(learning_data, ensure_ascii=False)}"},
                {"text": "Cập nhật các mẫu xử lý thành công"}
            ]
        }
        
        controller = ComputerController()
        controller._call_gemini_api(prompt_update)
    except Exception as e:
        logging.error(f"Lỗi khi cập nhật mẫu thành công: {str(e)}")

def _update_failure_patterns(learning_data):
    """Cập nhật các mẫu thất bại"""
    try:
        # Lưu mẫu thất bại vào cơ sở dữ liệu
        failure_patterns.append(learning_data)
        
        # Cập nhật prompt cho Gemini
        prompt_update = {
            "parts": [
                {"text": "Cập nhật mẫu thất bại:"},
                {"text": f"Dữ liệu: {json.dumps(learning_data, ensure_ascii=False)}"},
                {"text": "Cập nhật các mẫu xử lý thất bại và tìm giải pháp thay thế"}
            ]
        }
        
        controller = ComputerController()
        controller._call_gemini_api(prompt_update)
    except Exception as e:
        logging.error(f"Lỗi khi cập nhật mẫu thất bại: {str(e)}")

def is_application_running(target):
    """Kiểm tra xem ứng dụng có đang chạy không"""
    try:
        result = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {target}.exe"], 
                             capture_output=True, text=True)
        return target in result.stdout
    except Exception:
        return False

def is_url_opened(url):
    """Kiểm tra xem URL đã được mở trong trình duyệt chưa"""
    try:
        # Thực hiện OCR trên màn hình để tìm URL trong thanh địa chỉ
        screenshot = capture_screen()
        # TODO: Implement OCR logic here
        return False
    except Exception:
        return False

def focus_application(target):
    """Focus vào ứng dụng đang chạy"""
    try:
        subprocess.run(["powershell", "-Command", f"(New-Object -ComObject Shell.Application).Windows() | Where-Object {{$_.Name -like '*{target}*'}} | ForEach-Object {{$_.Activate()}}"])
    except Exception:
        pass

def switch_to_tab(url):
    """Chuyển đến tab có URL cụ thể"""
    try:
        # Sử dụng Alt+Tab để chuyển cửa sổ
        pyautogui.hotkey('alt', 'tab')
        time.sleep(0.5)
        # TODO: Implement tab switching logic
    except Exception:
        pass

def verify_action_success(intent, screen_state):
    """Xác minh xem hành động có thành công không dựa trên phân tích màn hình"""
    try:
        if intent["action"] == "open":
            # Kiểm tra cửa sổ active
            active_window = screen_state["screen_state"]["active_window"]
            if active_window["title"].lower().find(intent["target"]) != -1:
                return True
                
            # Kiểm tra các elements visible
            for element in screen_state["screen_state"]["visible_elements"]:
                if element["type"] == "window" and element["content"].lower().find(intent["target"]) != -1:
                    return True
                    
        return False
    except Exception:
        return False

def generate_alternative_action(intent, screen_state):
    """Tạo hành động thay thế dựa trên phân tích màn hình"""
    try:
        if intent["action"] == "open":
            # Thử tìm button hoặc menu item phù hợp
            for element in screen_state["screen_state"]["visible_elements"]:
                if element["type"] in ["button", "menu"] and element["content"].lower().find(intent["target"]) != -1:
                    return {
                        "action": "click",
                        "target": "coordinates",
                        "parameters": {
                            "x": element["location"]["x"],
                            "y": element["location"]["y"]
                        }
                    }
        return None
    except Exception:
        return None

def generate_fix_action(issue):
    """Tạo hành động khắc phục dựa trên vấn đề phát hiện được"""
    try:
        if issue["type"] == "error":
            if "not responding" in issue["description"].lower():
                return {
                    "action": "terminate",
                    "target": issue.get("target"),
                    "parameters": {"force": True}
                }
            elif "permission" in issue["description"].lower():
                return {
                    "action": "elevate",
                    "target": issue.get("target"),
                    "parameters": {}
                }
        return None
    except Exception as e:
        logging.error(f"Lỗi khi tạo hành động khắc phục: {str(e)}")
        return None

def generate_optimization_action(opportunity):
    """Tạo hành động tối ưu dựa trên cơ hội phát hiện được"""
    try:
        if opportunity["type"] == "shortcut":
            return {
                "action": "hotkey",
                "target": opportunity.get("target"),
                "parameters": {"keys": opportunity.get("keys", [])}
            }
        elif opportunity["type"] == "optimization":
            return {
                "action": opportunity.get("suggested_action", ""),
                "target": opportunity.get("target"),
                "parameters": opportunity.get("parameters", {})
            }
        return None
    except Exception as e:
        logging.error(f"Lỗi khi tạo hành động tối ưu: {str(e)}")
        return None

class DoliaAI:
    def __init__(self):
        self.controller = ComputerController()
        self.action_queue = queue.Queue()
        self.is_running = False
        self.current_state = None
        self.last_action_time = time.time()
        self.action_timeout = 30  # Thời gian tối đa cho một hành động (giây)
        self.knowledge_base = {
            "successful_patterns": {},  # Lưu các mẫu hành động thành công
            "failed_patterns": {},     # Lưu các mẫu hành động thất bại
            "context_rules": {},       # Quy tắc dựa trên ngữ cảnh
            "error_solutions": {}      # Giải pháp cho các lỗi đã gặp
        }
        
    def start(self):
        """Khởi động DoliaAI"""
        try:
            logging.info("Khởi động DoliaAI...")
            self.is_running = True
            
            # Khởi động thread xử lý hành động
            action_thread = threading.Thread(target=self._process_actions)
            action_thread.daemon = True
            action_thread.start()
            
            # Khởi động thread cập nhật trạng thái
            state_thread = threading.Thread(target=self._update_state)
            state_thread.daemon = True
            state_thread.start()
            
            logging.info("DoliaAI đã khởi động thành công")
            return True
        except Exception as e:
            logging.error(f"Lỗi khi khởi động DoliaAI: {str(e)}")
            return False
    
    def stop(self):
        """Dừng DoliaAI"""
        try:
            logging.info("Đang dừng DoliaAI...")
            self.is_running = False
            logging.info("DoliaAI đã dừng")
            return True
        except Exception as e:
            logging.error(f"Lỗi khi dừng DoliaAI: {str(e)}")
            return False
    
    def execute_action(self, action):
        """Thực hiện một hành động"""
        try:
            # Kiểm tra timeout
            if time.time() - self.last_action_time > self.action_timeout:
                raise TimeoutError("Hành động quá thời gian cho phép")
                
            # Cập nhật thời gian bắt đầu
            self.last_action_time = time.time()
            
            # Thực hiện hành động
            result = self.controller.execute_action(action)
            
            # Học hỏi từ kết quả
            if result.get("success", False):
                self._learn_from_success(action, result)
            else:
                self._learn_from_failure(action, result)
                
                # Tự động xử lý lỗi
                error = result.get("error", "Unknown error")
                error_msg = str(error).lower()
                
                # Phân tích loại lỗi
                if "path" in error_msg or "file" in error_msg:
                    logging.info("Phát hiện lỗi đường dẫn, tìm đường dẫn thay thế...")
                    self._handle_path_error({"action": action, "error": error})
                    
                elif "permission" in error_msg or "access" in error_msg:
                    logging.info("Phát hiện lỗi quyền truy cập, thử chạy với quyền admin...")
                    self._handle_permission_error({"action": action, "error": error})
                    
                elif "not responding" in error_msg or "hang" in error_msg:
                    logging.info("Phát hiện lỗi ứng dụng không phản hồi, thử khởi động lại...")
                    self._handle_app_not_responding({"action": action, "error": error})
                    
                else:
                    # Tìm giải pháp từ cơ sở kiến thức
                    solution = this._find_solution_from_knowledge(error_msg)
                    if solution:
                        logging.info(f"Tìm thấy giải pháp từ cơ sở kiến thức: {solution}")
                        # Thử lại hành động với giải pháp mới
                        action.update(solution)
                        return this.execute_action(action)
                    else:
                        logging.warning("Không tìm thấy giải pháp cho lỗi này")
                
            # Cập nhật cơ sở kiến thức
            this._update_knowledge_base()
            
            # Cập nhật trạng thái hiện tại
            this.current_state = this.controller.get_current_state()
            
            return result
            
        except Exception as e:
            error_msg = f"Lỗi khi thực hiện hành động: {str(e)}"
            logging.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def execute_sequence(self, sequence_data):
        """Thực thi chuỗi hành động"""
        try:
            if not self.is_running:
                return {"success": False, "error": "DoliaAI chưa được khởi động"}
            
            # Kiểm tra dữ liệu đầu vào
            if not sequence_data or "steps" not in sequence_data:
                return {"success": False, "error": "Dữ liệu chuỗi hành động không hợp lệ"}
            
            # Thêm từng bước vào hàng đợi
            for step in sequence_data["steps"]:
                self.action_queue.put(step)
            
            logging.info(f"Đã thêm chuỗi hành động vào hàng đợi: {json.dumps(sequence_data, ensure_ascii=False)}")
            return {"success": True}
        except Exception as e:
            logging.error(f"Lỗi khi thêm chuỗi hành động: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_current_state(self):
        """Lấy trạng thái hiện tại"""
        try:
            if not self.is_running:
                return {"success": False, "error": "DoliaAI chưa được khởi động"}
            
            if not self.current_state:
                return {"success": False, "error": "Chưa có thông tin trạng thái"}
            
            return {"success": True, "state": self.current_state}
        except Exception as e:
            logging.error(f"Lỗi khi lấy trạng thái: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _process_actions(self):
        """Xử lý các hành động trong hàng đợi"""
        while self.is_running:
            try:
                # Lấy hành động từ hàng đợi
                action = self.action_queue.get(timeout=1)
                
                # Cập nhật thời gian bắt đầu hành động
                self.last_action_time = time.time()
                
                # Thực hiện hành động
                result = self.controller.execute_action(action)
                
                # Kiểm tra kết quả
                if not result.get("success", False):
                    logging.warning(f"Hành động thất bại: {result.get('error', 'Unknown error')}")
                    
                    # Thử phương án dự phòng nếu có
                    if "fallback" in action:
                        fallback_result = self.controller.execute_action(action["fallback"])
                        if not fallback_result.get("success", False):
                            logging.error(f"Phương án dự phòng cũng thất bại: {fallback_result.get('error', 'Unknown error')}")
                
                # Đánh dấu hành động đã hoàn thành
                self.action_queue.task_done()
                
            except queue.Empty:
                # Không có hành động nào trong hàng đợi
                continue
            except Exception as e:
                logging.error(f"Lỗi khi xử lý hành động: {str(e)}")
                continue
    
    def _update_state(self):
        """Cập nhật trạng thái hệ thống"""
        while self.is_running:
            try:
                # Kiểm tra timeout
                if time.time() - self.last_action_time > self.action_timeout:
                    logging.warning("Hành động đang thực hiện quá lâu, có thể bị treo")
                    # TODO: Xử lý trường hợp timeout
                
                # Cập nhật trạng thái
                self.current_state = self.controller.analyze_screen_state()
                
                # Đợi 1 giây trước khi cập nhật tiếp
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Lỗi khi cập nhật trạng thái: {str(e)}")
                time.sleep(1)
                continue

    def _learn_from_success(self, action, result):
        """Học hỏi từ hành động thành công"""
        try:
            # Lưu mẫu thành công
            pattern = {
                "action": action,
                "state": self.current_state,
                "result": result,
                "timestamp": time.time()
            }
            
            # Sử dụng action_type làm khóa thay vì action dict
            action_type = action.get("type", "unknown")
            if action_type not in self.knowledge_base["successful_patterns"]:
                self.knowledge_base["successful_patterns"][action_type] = []
            
            self.knowledge_base["successful_patterns"][action_type].append(pattern)
            
            # Cập nhật cơ sở kiến thức
            self._update_knowledge_base()
            
            logging.info(f"Đã học từ hành động thành công: {action_type}")
            
        except Exception as e:
            logging.error(f"Lỗi khi học từ hành động thành công: {str(e)}")
            
    def _update_knowledge_base(self):
        """Cập nhật cơ sở kiến thức"""
        try:
            # Giới hạn số lượng mẫu lưu trữ
            max_patterns = 1000
            for action_type in self.knowledge_base["successful_patterns"]:
                if len(self.knowledge_base["successful_patterns"][action_type]) > max_patterns:
                    self.knowledge_base["successful_patterns"][action_type] = self.knowledge_base["successful_patterns"][action_type][-max_patterns:]
            
            for action_type in self.knowledge_base["failed_patterns"]:
                if len(self.knowledge_base["failed_patterns"][action_type]) > max_patterns:
                    self.knowledge_base["failed_patterns"][action_type] = self.knowledge_base["failed_patterns"][action_type][-max_patterns:]
                
            # Lưu cơ sở kiến thức vào file
            knowledge = {
                "successful_patterns": self.knowledge_base["successful_patterns"],
                "failed_patterns": self.knowledge_base["failed_patterns"],
                "last_updated": time.time()
            }
            
            with open("knowledge_base.json", "w", encoding="utf-8") as f:
                json.dump(knowledge, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logging.error(f"Lỗi khi cập nhật cơ sở kiến thức: {str(e)}")
            
    def _learn_from_failure(self, action, result):
        """Học hỏi từ hành động thất bại"""
        try:
            # Lưu mẫu thất bại
            pattern = {
                "action": action,
                "state": self.current_state,
                "error": result.get("error", "Unknown error"),
                "timestamp": time.time()
            }
            
            # Sử dụng action_type làm khóa thay vì action dict
            action_type = action.get("type", "unknown")
            if action_type not in self.knowledge_base["failed_patterns"]:
                self.knowledge_base["failed_patterns"][action_type] = []
            
            self.knowledge_base["failed_patterns"][action_type].append(pattern)
            
            # Phân tích lỗi và tìm giải pháp
            self._analyze_error(result.get("error", "Unknown error"), pattern)
            
            logging.info(f"Đã học từ hành động thất bại: {action_type}")
            
        except Exception as e:
            logging.error(f"Lỗi khi học từ hành động thất bại: {str(e)}")
            
    def _analyze_error(self, error, failure_pattern):
        """Phân tích lỗi và tìm giải pháp"""
        try:
            error_msg = str(error).lower()
            
            # Phân tích loại lỗi
            if "path" in error_msg or "file" in error_msg:
                logging.info("Phát hiện lỗi đường dẫn, tìm đường dẫn thay thế...")
                self._handle_path_error(failure_pattern)
                
            elif "permission" in error_msg or "access" in error_msg:
                logging.info("Phát hiện lỗi quyền truy cập, thử chạy với quyền admin...")
                self._handle_permission_error(failure_pattern)
                
            elif "not responding" in error_msg or "hang" in error_msg:
                logging.info("Phát hiện lỗi ứng dụng không phản hồi, thử khởi động lại...")
                self._handle_app_not_responding(failure_pattern)
                
            else:
                # Tìm giải pháp từ cơ sở kiến thức
                solution = this._find_solution_from_knowledge(error_msg)
                if solution:
                    logging.info(f"Tìm thấy giải pháp từ cơ sở kiến thức: {solution}")
                    # Thử lại hành động với giải pháp mới
                    failure_pattern["action"].update(solution)
                    return this.execute_action(failure_pattern["action"])
                else:
                    logging.warning("Không tìm thấy giải pháp cho lỗi này")
                    
        except Exception as e:
            logging.error(f"Lỗi khi phân tích lỗi: {str(e)}")
            
    def _find_solution_from_knowledge(self, error_msg):
        """Tìm giải pháp từ cơ sở kiến thức"""
        try:
            # Tìm mẫu thất bại tương tự
            for action_type, patterns in self.knowledge_base["failed_patterns"].items():
                for pattern in patterns:
                    if pattern["error"].lower() in error_msg:
                        # Kiểm tra xem có mẫu thành công tương ứng không
                        if action_type in self.knowledge_base["successful_patterns"]:
                            for success in self.knowledge_base["successful_patterns"][action_type]:
                                if success["action"]["type"] == pattern["action"]["type"]:
                                    # Trả về giải pháp từ mẫu thành công
                                    return success["action"]
                            
            return None
            
        except Exception as e:
            logging.error(f"Lỗi khi tìm giải pháp từ cơ sở kiến thức: {str(e)}")
            return None

    def _handle_path_error(self, failure_pattern):
        """Xử lý lỗi đường dẫn không tìm thấy"""
        try:
            action = failure_pattern["action"]
            if "path" in action:
                # Tìm đường dẫn thay thế
                alternative_path = self._find_alternative_path(action["path"])
                if alternative_path:
                    # Cập nhật hành động với đường dẫn mới
                    action["path"] = alternative_path
                    # Thử lại hành động
                    self.execute_action(action)
                    logging.info(f"Đã tìm thấy đường dẫn thay thế: {alternative_path}")
                else:
                    logging.warning(f"Không tìm thấy đường dẫn thay thế cho: {action['path']}")
                    
        except Exception as e:
            logging.error(f"Lỗi khi xử lý lỗi đường dẫn: {str(e)}")
            
    def _handle_permission_error(self, failure_pattern):
        """Xử lý lỗi quyền truy cập"""
        try:
            action = failure_pattern["action"]
            # Thử chạy với quyền admin
            if self._run_as_admin(action):
                logging.info("Đã thực hiện hành động với quyền admin")
            else:
                logging.warning("Không thể thực hiện hành động với quyền admin")
                
        except Exception as e:
            logging.error(f"Lỗi khi xử lý lỗi quyền truy cập: {str(e)}")
            
    def _handle_app_not_responding(self, failure_pattern):
        """Xử lý lỗi ứng dụng không phản hồi"""
        try:
            action = failure_pattern["action"]
            if "app" in action:
                # Thử khởi động lại ứng dụng
                app_name = action["app"]
                if self._restart_application(app_name):
                    logging.info(f"Đã khởi động lại ứng dụng: {app_name}")
                    # Thử lại hành động
                    self.execute_action(action)
                else:
                    logging.warning(f"Không thể khởi động lại ứng dụng: {app_name}")
                    
        except Exception as e:
            logging.error(f"Lỗi khi xử lý lỗi ứng dụng không phản hồi: {str(e)}")
            
    def _find_alternative_path(self, original_path):
        """Tìm đường dẫn thay thế cho ứng dụng"""
        try:
            # Kiểm tra các đường dẫn phổ biến
            common_paths = [
                os.path.join(os.environ["ProgramFiles"], "**", "*"),
                os.path.join(os.environ["ProgramFiles(x86)"], "**", "*"),
                os.path.join(os.environ["LOCALAPPDATA"], "**", "*"),
                os.path.join(os.environ["APPDATA"], "**", "*")
            ]
            
            app_name = os.path.basename(original_path).lower()
            
            for base_path in common_paths:
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        if file.lower() == app_name:
                            return os.path.join(root, file)
                            
            return None
            
        except Exception as e:
            logging.error(f"Lỗi khi tìm đường dẫn thay thế: {str(e)}")
            return None
            
    def _run_as_admin(self, action):
        """Chạy hành động với quyền admin"""
        try:
            if sys.platform == "win32":
                import ctypes
                if not ctypes.windll.shell32.IsUserAnAdmin():
                    # Tạo file batch tạm thời
                    temp_batch = "temp_admin.bat"
                    with open(temp_batch, "w") as f:
                        f.write(f'"{sys.executable}" "{action["path"]}"')
                        
                    # Chạy với quyền admin
                    ctypes.windll.shell32.ShellExecuteW(
                        None, "runas", temp_batch, None, None, 1
                    )
                    
                    # Xóa file tạm
                    os.remove(temp_batch)
                    return True
                    
            return False
            
        except Exception as e:
            logging.error(f"Lỗi khi chạy với quyền admin: {str(e)}")
            return False
            
    def _restart_application(self, app_name):
        """Khởi động lại ứng dụng"""
        try:
            # Tìm process ID
            for proc in psutil.process_iter(["pid", "name"]):
                if app_name.lower() in proc.info["name"].lower():
                    # Kết thúc process
                    proc.kill()
                    # Đợi process kết thúc
                    proc.wait(timeout=5)
                    # Khởi động lại ứng dụng
                    subprocess.Popen([app_name])
                    return True
                    
            return False
            
        except Exception as e:
            logging.error(f"Lỗi khi khởi động lại ứng dụng: {str(e)}")
            return False

def main():
    """Hàm chính để chạy DoliaAI từ command line"""
    if len(sys.argv) < 2:
        print("Sử dụng: python main.py <action_json>")
        return
    
    try:
        # Khởi tạo DoliaAI
        dolia = DoliaAI()
        if not dolia.start():
            print(json.dumps({"success": False, "error": "Không thể khởi động DoliaAI"}, ensure_ascii=False))
            return
        
        # Đọc dữ liệu hành động
        action_json = sys.argv[1]
        action_data = json.loads(action_json)
        
        # Thực thi hành động
        if action_data.get("type") == "sequence":
            result = dolia.execute_sequence(action_data)
        else:
            result = dolia.execute_action(action_data)
        
        # In kết quả
        print(json.dumps(result, ensure_ascii=False))
        
        # Dừng DoliaAI
        dolia.stop()
        
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))

if __name__ == "__main__":
    main() 