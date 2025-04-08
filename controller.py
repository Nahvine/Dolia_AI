import os
import subprocess
import pyautogui
import time
import platform
import json
import sys
import logging
import codecs
import io
import base64
import requests
import re
import win32gui
import win32con
import win32process
import psutil
from PIL import Image, ImageGrab

# Cấu hình logging với encoding UTF-8
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("controller.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Biến toàn cục để lưu trữ patterns
successful_patterns = []
failure_patterns = []

class ComputerController:
    def __init__(self):
        self.system = platform.system()
        self.screen_width, self.screen_height = pyautogui.size()
        logging.info(f"Hệ điều hành: {self.system}, Kích thước màn hình: {self.screen_width}x{self.screen_height}")
        
        # Thiết lập fail-safe
        pyautogui.FAILSAFE = True
        
        # API Key cho Gemini
        self.gemini_api_key = "AIzaSyBQJfAFkGRsv_jhL0FP1Sf4eXVfNhoo7Ec"
        self.gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_api_key}"
        
        # Định nghĩa các phím tắt Windows
        self.windows_keys = {
            "win": "win", "windows": "win", "start": "win",
            "alt": "alt", "ctrl": "ctrl", "control": "ctrl", "shift": "shift",
            "tab": "tab", "enter": "enter", "space": "space", "esc": "esc", "escape": "esc",
            "backspace": "backspace", "delete": "delete", "up": "up", "down": "down",
            "left": "left", "right": "right", "home": "home", "end": "pageup",
            "pagedown": "pagedown", "pageup": "pageup", "insert": "insert",
            "f1": "f1", "f2": "f2", "f3": "f3", "f4": "f4", "f5": "f5",
            "f6": "f6", "f7": "f7", "f8": "f8", "f9": "f9", "f10": "f10",
            "f11": "f11", "f12": "f12", "r": "r", "d": "d", "s": "s", "e": "e",
            "l": "l", "m": "m", "t": "t", "a": "a", "c": "c", "v": "v", "x": "x",
            "z": "z", "y": "y", "p": "p", "b": "b", "n": "n", "o": "o", "i": "i",
            "u": "u", "h": "h", "j": "j", "k": "k", "g": "g", "f": "f", "q": "q",
            "w": "w", "1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6",
            "7": "7", "8": "8", "9": "9", "0": "0", "+": "+", "-": "-", "=": "=",
            "[": "[", "]": "]", "\\": "\\", ";": ";", "'": "'", ",": ",", ".": ".",
            "/": "/", "`": "`"
        }
        
        # Danh sách các ứng dụng phổ biến và đường dẫn
        self.common_apps = {
            "notepad": {
                "paths": ["notepad.exe", "C:\\Windows\\System32\\notepad.exe"],
                "process_name": "notepad.exe"
            },
            "chrome": {
                "paths": [
                    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                    "%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe"
                ],
                "process_name": "chrome.exe"
            },
            "edge": {
                "paths": [
                    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                    "%LOCALAPPDATA%\\Microsoft\\Edge\\Application\\msedge.exe"
                ],
                "process_name": "msedge.exe"
            },
            "firefox": {
                "paths": [
                    "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                    "C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe"
                ],
                "process_name": "firefox.exe"
            },
            "explorer": {
                "paths": ["explorer.exe", "C:\\Windows\\explorer.exe"],
                "process_name": "explorer.exe"
            },
            "discord": {
                "paths": [
                    "%LOCALAPPDATA%\\Discord\\Update.exe --processStart Discord.exe",
                    "%LOCALAPPDATA%\\Discord\\app-1.0.9027\\Discord.exe"
                ],
                "process_name": "Discord.exe"
            }
        }
        
        # Thư mục đặc biệt
        self.special_folders = {
            "documents": "%USERPROFILE%\\Documents",
            "downloads": "%USERPROFILE%\\Downloads",
            "desktop": "%USERPROFILE%\\Desktop",
            "pictures": "%USERPROFILE%\\Pictures",
            "music": "%USERPROFILE%\\Music",
            "videos": "%USERPROFILE%\\Videos"
        }
        
    def capture_screen(self):
        """Chụp ảnh màn hình hiện tại và chuyển đổi sang base64"""
        try:
            screenshot = ImageGrab.grab()
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            return base64.b64encode(img_byte_arr).decode('utf-8')
        except Exception as e:
            logging.error(f"Lỗi khi chụp màn hình: {str(e)}")
            return None
    
    def execute_cmd(self, command):
        """Thực thi lệnh cmd/bash"""
        try:
            logging.info(f"Thực thi lệnh: {command}")
            if self.system == "Windows":
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
            else:
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, executable="/bin/bash", encoding='utf-8')
            
            stdout, stderr = process.communicate()
            
            if stdout:
                logging.info(f"Kết quả: {stdout}")
            if stderr:
                logging.warning(f"Lỗi: {stderr}")
                
            return {
                "success": process.returncode == 0,
                "stdout": stdout,
                "stderr": stderr,
                "return_code": process.returncode
            }
        except Exception as e:
            logging.error(f"Lỗi khi thực thi lệnh: {str(e)}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }
    
    def click(self, x, y):
        """Click chuột tại tọa độ x, y"""
        try:
            logging.info(f"Click tại tọa độ ({x}, {y})")
            pyautogui.click(x, y)
            return {"success": True}
        except Exception as e:
            logging.error(f"Lỗi khi click: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def double_click(self, x, y):
        """Double click chuột tại tọa độ x, y"""
        try:
            logging.info(f"Double click tại tọa độ ({x}, {y})")
            pyautogui.doubleClick(x, y)
            return {"success": True}
        except Exception as e:
            logging.error(f"Lỗi khi double click: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def right_click(self, x, y):
        """Right click chuột tại tọa độ x, y"""
        try:
            logging.info(f"Right click tại tọa độ ({x}, {y})")
            pyautogui.rightClick(x, y)
            return {"success": True}
        except Exception as e:
            logging.error(f"Lỗi khi right click: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def type_text(self, text):
        """Nhập text"""
        try:
            logging.info(f"Nhập text: {text}")
            # Đợi một chút để đảm bảo cửa sổ đã focus
            time.sleep(0.5)
            # Xóa text hiện tại nếu có
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('delete')
            # Nhập text mới
            pyautogui.write(text, interval=0.1)  # Thêm interval để nhập từng ký tự
            return {"success": True}
        except Exception as e:
            logging.error(f"Lỗi khi nhập text: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def press_key(self, key):
        """Nhấn phím"""
        try:
            logging.info(f"Nhấn phím: {key}")
            pyautogui.press(key)
            return {"success": True}
        except Exception as e:
            logging.error(f"Lỗi khi nhấn phím: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def hotkey(self, *args):
        """Nhấn tổ hợp phím"""
        try:
            # Chuyển đổi các phím thành định dạng pyautogui
            converted_keys = []
            for key in args:
                key_lower = key.lower()
                if key_lower in self.windows_keys:
                    converted_keys.append(self.windows_keys[key_lower])
                else:
                    converted_keys.append(key)
            
            logging.info(f"Nhấn tổ hợp phím: {converted_keys}")
            pyautogui.hotkey(*converted_keys)
            return {"success": True}
        except Exception as e:
            logging.error(f"Lỗi khi nhấn tổ hợp phím: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def scroll(self, amount):
        """Scroll màn hình"""
        try:
            logging.info(f"Scroll: {amount}")
            pyautogui.scroll(amount)
            return {"success": True}
        except Exception as e:
            logging.error(f"Lỗi khi scroll: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def move_to(self, x, y, duration=0.5):
        """Di chuyển chuột đến tọa độ x, y"""
        try:
            logging.info(f"Di chuyển chuột đến ({x}, {y})")
            pyautogui.moveTo(x, y, duration=duration)
            return {"success": True}
        except Exception as e:
            logging.error(f"Lỗi khi di chuyển chuột: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def drag_to(self, x, y, duration=0.5):
        """Kéo chuột đến tọa độ x, y"""
        try:
            logging.info(f"Kéo chuột đến ({x}, {y})")
            pyautogui.dragTo(x, y, duration=duration)
            return {"success": True}
        except Exception as e:
            logging.error(f"Lỗi khi kéo chuột: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def wait(self, seconds):
        """Đợi số giây"""
        try:
            logging.info(f"Đợi {seconds} giây")
            time.sleep(seconds)
            return {"success": True}
        except Exception as e:
            logging.error(f"Lỗi khi đợi: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def open_application(self, app_name):
        """Mở ứng dụng với xử lý lỗi tốt hơn"""
        try:
            app_name = app_name.lower()
            
            # Kiểm tra ứng dụng đã chạy chưa
            if app_name in self.common_apps:
                process_name = self.common_apps[app_name]["process_name"]
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                        # Nếu đã chạy, focus vào cửa sổ
                        hwnd = win32gui.FindWindow(None, process_name)
                        if hwnd:
                            win32gui.SetForegroundWindow(hwnd)
                            return True

            # Nếu là thư mục đặc biệt
            if app_name in self.special_folders:
                path = os.path.expandvars(self.special_folders[app_name])
                os.startfile(path)
                return True

            # Nếu là ứng dụng thông thường
            if app_name in self.common_apps:
                app_info = self.common_apps[app_name]
                for path in app_info["paths"]:
                    try:
                        expanded_path = os.path.expandvars(path)
                        if os.path.exists(expanded_path):
                            subprocess.Popen(expanded_path)
                            # Đợi ứng dụng khởi động
                            if self.wait_for_application(app_info["process_name"]):
                                return True
                    except Exception as e:
                        logging.warning(f"Không thể mở {path}: {str(e)}")
                        continue

            # Thử mở trực tiếp
            try:
                subprocess.Popen(app_name)
                return True
            except Exception as e:
                logging.error(f"Không thể mở ứng dụng {app_name}: {str(e)}")
                return False

        except Exception as e:
            logging.error(f"Lỗi khi mở ứng dụng {app_name}: {str(e)}")
            return False

    def _is_application_running(self, app_name):
        """Kiểm tra xem ứng dụng có đang chạy không"""
        try:
            # Chuẩn hóa tên ứng dụng
            app_name_lower = app_name.lower()
            
            # Kiểm tra xem có phải là ứng dụng phổ biến không
            if app_name_lower in self.common_apps:
                process_name = self.common_apps[app_name_lower]["process_name"]
            else:
                process_name = f"{app_name}.exe"
            
            # Kiểm tra process
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                    return True
            
            return False
        except Exception as e:
            logging.error(f"Lỗi khi kiểm tra ứng dụng {app_name}: {str(e)}")
            return False

    def get_active_window(self):
        """Lấy thông tin về cửa sổ đang active"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            rect = win32gui.GetWindowRect(hwnd)
            x, y, width, height = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
            
            # Lấy process ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            process_name = process.name()
            
            return {
                "title": title,
                "process_name": process_name,
                "position": {"x": x, "y": y},
                "size": {"width": width, "height": height},
                "hwnd": hwnd
            }
        except Exception as e:
            logging.error(f"Lỗi khi lấy cửa sổ active: {str(e)}")
            return None
    
    def get_visible_windows(self):
        """Lấy danh sách các cửa sổ đang hiển thị"""
        try:
            windows = []
            
            def enum_windows_callback(hwnd, results):
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    rect = win32gui.GetWindowRect(hwnd)
                    x, y, width, height = rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]
                    
                    # Lấy process ID
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    try:
                        process = psutil.Process(pid)
                        process_name = process.name()
                    except:
                        process_name = "unknown"
                    
                    results.append({
                        "title": title,
                        "process_name": process_name,
                        "position": {"x": x, "y": y},
                        "size": {"width": width, "height": height},
                        "hwnd": hwnd
                    })
            
            win32gui.EnumWindows(enum_windows_callback, windows)
            return windows
        except Exception as e:
            logging.error(f"Lỗi khi lấy danh sách cửa sổ: {str(e)}")
            return []
    
    def get_screen_elements(self):
        """Lấy thông tin về các phần tử trên màn hình"""
        try:
            # Chụp ảnh màn hình
            screenshot = self.capture_screen()
            if not screenshot:
                return []
            
            # Tạo prompt cho Gemini
            prompt = """Phân tích ảnh màn hình và liệt kê các phần tử có thể tương tác (buttons, input fields, links, etc.).
            Trả về kết quả dưới dạng JSON với cấu trúc sau:
            {
                "elements": [
                    {
                        "type": "button|input|link|text|image",
                        "text": "Nội dung hiển thị",
                        "position": {"x": 100, "y": 200},
                        "size": {"width": 50, "height": 30},
                        "is_clickable": true,
                        "is_visible": true
                    }
                ]
            }"""
            
            # Gọi Gemini API
            result = self._call_gemini_api(prompt, screenshot)
            if result and "elements" in result:
                return result["elements"]
            
            return []
        except Exception as e:
            logging.error(f"Lỗi khi lấy thông tin phần tử màn hình: {str(e)}")
            return []
    
    def analyze_screen_state(self):
        """Phân tích trạng thái màn hình hiện tại"""
        try:
            # Chụp màn hình
            screenshot_base64 = self.capture_screen()
            if not screenshot_base64:
                return None
                
            # Tạo prompt cho Gemini
            prompt = """
            Phân tích màn hình và trả về kết quả dưới dạng JSON với các thông tin:
            - Các cửa sổ đang mở
            - Các nút bấm có thể nhìn thấy
            - Vị trí của các phần tử tương tác
            - Trạng thái của các ứng dụng
            """
            
            # Gọi API với ảnh
            response = self._call_gemini_api(prompt, screenshot_base64)
            if not response:
                return None
                
            # Parse JSON từ response
            screen_state = self._parse_json_response(response.get("text", ""))
            if screen_state:
                logging.info(f"Phân tích màn hình thành công: {json.dumps(screen_state, ensure_ascii=False)}")
                return screen_state
                
            return None
            
        except Exception as e:
            logging.error(f"Lỗi khi phân tích màn hình: {str(e)}")
            return None

    def wait_for_application(self, process_name, timeout=10):
        """Đợi ứng dụng khởi động và sẵn sàng"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Kiểm tra process có tồn tại không
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                        # Đợi thêm 1 giây để UI load xong
                        time.sleep(1)
                        return True
                time.sleep(0.5)
            return False
        except Exception as e:
            logging.error(f"Lỗi khi đợi ứng dụng: {str(e)}")
            return False

    def create_action_plan(self, user_request, current_state):
        """Tạo kế hoạch hành động dựa trên yêu cầu và trạng thái hiện tại"""
        try:
            prompt = f"""
            Tạo kế hoạch hành động chi tiết dựa trên:
            
            Yêu cầu người dùng: {user_request}
            
            Trạng thái hiện tại: {json.dumps(current_state, ensure_ascii=False)}
            
            Trả về JSON với format:
            {{
                "steps": [
                    {{
                        "action": "tên_hành_động",
                        "params": {{"param1": "value1"}},
                        "success_criteria": ["tiêu_chí_1", "tiêu_chí_2"],
                        "fallback_actions": [
                            {{
                                "action": "hành_động_thay_thế",
                                "params": {{"param1": "value1"}}
                            }}
                        ]
                    }}
                ],
                "stop_conditions": ["điều_kiện_dừng_1", "điều_kiện_dừng_2"]
            }}
            """
            
            response = self._call_gemini_api(prompt)
            if not response:
                return None
                
            action_plan = self._parse_json_response(response.get("text", ""))
            if action_plan:
                logging.info(f"Tạo kế hoạch hành động thành công: {json.dumps(action_plan, ensure_ascii=False)}")
                return action_plan
                
            return None
            
        except Exception as e:
            logging.error(f"Lỗi khi tạo kế hoạch hành động: {str(e)}")
            return None

    def execute_with_visual_feedback(self, action_plan):
        """Thực hiện kế hoạch hành động với phản hồi trực quan"""
        try:
            if not action_plan or "steps" not in action_plan:
                logging.error("Kế hoạch hành động không hợp lệ")
                return False

            # Kiểm tra điều kiện dừng trước khi bắt đầu
            if self._check_stop_conditions(action_plan.get("stop_conditions", [])):
                logging.info("Điều kiện dừng được kích hoạt")
                return False

            # Thực hiện từng bước trong kế hoạch
            for step in action_plan["steps"]:
                # Thực hiện hành động
                success = self._execute_step(step)
                
                if not success:
                    # Thử các phương án dự phòng
                    if not self._try_fallback(step.get("fallback_actions", [])):
                        logging.error(f"Bước {step['step_id']} thất bại và không có phương án dự phòng thành công")
                        return False
                
                # Kiểm tra tiêu chí thành công
                if not self._verify_step_success(step.get("success_criteria", [])):
                    logging.error(f"Bước {step['step_id']} không đạt tiêu chí thành công")
                    return False
                
                # Kiểm tra điều kiện dừng sau mỗi bước
                if self._check_stop_conditions(action_plan.get("stop_conditions", [])):
                    logging.info("Điều kiện dừng được kích hoạt sau khi thực hiện bước")
                    return False

            return True

        except Exception as e:
            logging.error(f"Lỗi khi thực hiện kế hoạch hành động: {str(e)}")
            return False

    def _execute_step(self, step):
        """Thực hiện một bước trong kế hoạch"""
        try:
            action = step.get("action", "")
            target = step.get("target", "")
            parameters = step.get("parameters", {})
            
            logging.info(f"Thực hiện bước: {action} - Target: {target} - Parameters: {parameters}")
            
            if action == "click":
                return self.click(parameters.get("x", 0), parameters.get("y", 0))
            elif action == "double_click":
                return self.double_click(parameters.get("x", 0), parameters.get("y", 0))
            elif action == "right_click":
                return self.right_click(parameters.get("x", 0), parameters.get("y", 0))
            elif action == "type":
                return self.type_text(parameters.get("text", ""))
            elif action == "press_key":
                return self.press_key(parameters.get("key", ""))
            elif action == "hotkey":
                keys = parameters.get("keys", [])
                return self.hotkey(*keys)
            elif action == "scroll":
                return self.scroll(parameters.get("amount", 0))
            elif action == "move_to":
                return self.move_to(parameters.get("x", 0), parameters.get("y", 0))
            elif action == "drag_to":
                return self.drag_to(parameters.get("x", 0), parameters.get("y", 0))
            elif action == "wait":
                return self.wait(parameters.get("seconds", 1))
            elif action == "open":
                return self.open_application(target)
            elif action == "run_command":
                return self.execute_cmd(parameters.get("command", ""))
            else:
                logging.error(f"Hành động không được hỗ trợ: {action}")
                return {"success": False, "error": f"Hành động không được hỗ trợ: {action}"}
                
        except Exception as e:
            logging.error(f"Lỗi khi thực hiện bước: {str(e)}")
            return {"success": False, "error": str(e)}

    def _verify_step_success(self, success_criteria):
        """Kiểm tra xem một bước có đạt tiêu chí thành công không"""
        try:
            for criterion in success_criteria:
                if not self._check_criterion(criterion):
                    return False
            return True
        except Exception as e:
            logging.error(f"Lỗi khi kiểm tra tiêu chí thành công: {str(e)}")
            return False

    def _try_fallback(self, fallback_actions):
        """Thử các phương án dự phòng"""
        try:
            for action in fallback_actions:
                # Kiểm tra điều kiện trước khi thử
                if self._check_fallback_conditions(action.get("conditions", [])):
                    success = self._execute_step(action)
                    if success.get("success", False):
                        return True
            return False
        except Exception as e:
            logging.error(f"Lỗi khi thử phương án dự phòng: {str(e)}")
            return False

    def _check_stop_conditions(self, stop_conditions):
        """Kiểm tra các điều kiện dừng"""
        try:
            for condition in stop_conditions:
                if self._check_criterion(condition):
                    return True
            return False
        except Exception as e:
            logging.error(f"Lỗi khi kiểm tra điều kiện dừng: {str(e)}")
            return False

    def _check_criterion(self, criterion):
        """Kiểm tra một tiêu chí cụ thể"""
        try:
            criterion_type = criterion.get("type", "")
            criterion_value = criterion.get("value", "")
            timeout = criterion.get("timeout", 5)

            start_time = time.time()
            while time.time() - start_time < timeout:
                if criterion_type == "window_exists":
                    return self._check_window_exists(criterion_value)
                elif criterion_type == "element_visible":
                    return self._check_element_visible(criterion_value)
                elif criterion_type == "text_present":
                    return self._check_text_present(criterion_value)
                elif criterion_type == "process_running":
                    return self._is_application_running(criterion_value)
                time.sleep(0.5)
            
            return False
        except Exception as e:
            logging.error(f"Lỗi khi kiểm tra tiêu chí: {str(e)}")
            return False

    def _check_window_exists(self, window_title):
        """Kiểm tra xem cửa sổ có tồn tại không"""
        try:
            windows = self.get_visible_windows()
            return any(window_title.lower() in window.get("title", "").lower() for window in windows)
        except Exception as e:
            logging.error(f"Lỗi khi kiểm tra cửa sổ: {str(e)}")
            return False

    def _check_element_visible(self, element_id):
        """Kiểm tra xem phần tử có hiển thị không"""
        try:
            elements = self.get_screen_elements()
            return any(element_id in element.get("text", "") for element in elements)
        except Exception as e:
            logging.error(f"Lỗi khi kiểm tra phần tử: {str(e)}")
            return False

    def _check_text_present(self, text):
        """Kiểm tra xem văn bản có xuất hiện trên màn hình không"""
        try:
            # Chụp ảnh màn hình và sử dụng Gemini để tìm văn bản
            screenshot = self.capture_screen()
            if not screenshot:
                return False
                
            prompt = f"""Kiểm tra xem văn bản "{text}" có xuất hiện trên màn hình không.
            Trả về kết quả dưới dạng JSON với cấu trúc sau:
            {{
                "text_found": boolean,
                "position": {{"x": number, "y": number}},
                "confidence": number
            }}"""
            
            result = self._call_gemini_api(prompt, screenshot)
            if result and "text_found" in result:
                return result["text_found"]
                
            return False
        except Exception as e:
            logging.error(f"Lỗi khi kiểm tra văn bản: {str(e)}")
            return False

    def _check_fallback_conditions(self, conditions):
        """Kiểm tra điều kiện trước khi thử phương án dự phòng"""
        try:
            for condition in conditions:
                if not self._check_criterion({"type": "text_present", "value": condition}):
                    return False
            return True
        except Exception as e:
            logging.error(f"Lỗi khi kiểm tra điều kiện dự phòng: {str(e)}")
            return False

    def _parse_json_response(self, response_text):
        """Phân tích JSON từ response text"""
        try:
            # Tìm JSON trong response text
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                return json.loads(json_str)
            return None
        except Exception as e:
            logging.error(f"Lỗi khi parse JSON: {str(e)}")
            return None

    def _call_gemini_api(self, prompt, image_data=None):
        """Gọi Gemini API với prompt và ảnh (nếu có)"""
        try:
            data = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            if image_data:
                data["contents"][0]["parts"].append({
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": image_data
                    }
                })
            
            response = requests.post(
                self.gemini_api_url,
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Lỗi API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Lỗi khi gọi Gemini API: {str(e)}")
            return None

    def execute_action(self, action_data):
        """Thực thi một hành động"""
        try:
            if not action_data:
                return {"success": False, "error": "Không có dữ liệu hành động"}

            action_type = action_data.get("type", "")
            if action_type == "command":
                command = action_data.get("command", "")
                if not command:
                    return {"success": False, "error": "Không có lệnh được cung cấp"}

                # Phân tích lệnh
                if command.startswith("mở"):
                    # Xử lý lệnh mở ứng dụng
                    app_name = command[3:].strip().lower()
                    if self.open_application(app_name):
                        return {"success": True, "message": f"Đã mở {app_name}"}
                    return {"success": False, "error": f"Không thể mở {app_name}"}
                elif command.startswith("ghi"):
                    # Xử lý lệnh ghi text
                    text = command[3:].strip()
                    if self.type_text(text):
                        return {"success": True, "message": f"Đã ghi text: {text}"}
                    return {"success": False, "error": "Không thể ghi text"}
                else:
                    # Thực thi lệnh cmd
                    result = self.execute_cmd(command)
                    return result

            return {"success": False, "error": f"Loại hành động không được hỗ trợ: {action_type}"}

        except Exception as e:
            logging.error(f"Lỗi khi thực thi hành động: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_current_state(self):
        """Lấy trạng thái hiện tại của hệ thống"""
        try:
            # Lấy cửa sổ đang active
            active_window = self.get_active_window()
            
            # Lấy danh sách cửa sổ đang hiển thị
            visible_windows = self.get_visible_windows()
            
            # Lấy các phần tử trên màn hình
            screen_elements = self.get_screen_elements()
            
            # Tạo trạng thái
            state = {
                "active_window": active_window,
                "visible_windows": visible_windows,
                "screen_elements": screen_elements,
                "timestamp": time.time()
            }
            
            return state
            
        except Exception as e:
            logging.error(f"Lỗi khi lấy trạng thái: {str(e)}")
            return None

def main():
    """Hàm chính để chạy controller từ command line"""
    if len(sys.argv) < 2:
        print("Sử dụng: python controller.py <action_json>")
        return
    
    try:
        action_json = sys.argv[1]
        action_data = json.loads(action_json)
        
        controller = ComputerController()
        
        if action_data.get("action") == "sequence":
            results = controller.execute_sequence(action_data)
            print(json.dumps({"results": results}, ensure_ascii=False))
        else:
            result = controller.execute_action(action_data)
            print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False))

if __name__ == "__main__":
    main() 