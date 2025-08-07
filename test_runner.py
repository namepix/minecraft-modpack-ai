#!/usr/bin/env python3
"""
🧪 마인크래프트 AI 테스트 러너
GUI와 CLI로 테스트를 실행하고 결과를 알려주는 시스템
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import json
import os
import time
from datetime import datetime
import sys

class TestRunner:
    def __init__(self, root):
        self.root = root
        self.root.title("🧪 마인크래프트 AI 테스트 러너")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 변수들
        self.is_testing = False
        self.test_results = {}
        
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """UI 설정"""
        # 메인 프레임
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제목
        title_label = ttk.Label(main_frame, text="🧪 마인크래프트 AI 테스트 러너", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # 테스트 환경 선택
        env_frame = ttk.LabelFrame(main_frame, text="🌍 테스트 환경 선택", padding="10")
        env_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.env_var = tk.StringVar(value="local")
        
        local_radio = ttk.Radiobutton(env_frame, text="🏠 로컬 환경 (빠른 단위 테스트)", 
                                     variable=self.env_var, value="local")
        local_radio.grid(row=0, column=0, sticky=tk.W, padx=10)
        
        remote_radio = ttk.Radiobutton(env_frame, text="🌐 GCP VM (실제 환경 통합 테스트)", 
                                      variable=self.env_var, value="remote")
        remote_radio.grid(row=1, column=0, sticky=tk.W, padx=10)
        
        both_radio = ttk.Radiobutton(env_frame, text="🚀 전체 (로컬 → 원격 순차 실행)", 
                                    variable=self.env_var, value="both")
        both_radio.grid(row=2, column=0, sticky=tk.W, padx=10)
        
        # 테스트 옵션
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ 테스트 옵션", padding="10")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.verbose_var = tk.BooleanVar(value=True)
        verbose_check = ttk.Checkbutton(options_frame, text="상세한 출력", 
                                       variable=self.verbose_var)
        verbose_check.grid(row=0, column=0, sticky=tk.W)
        
        self.notification_var = tk.BooleanVar(value=True)
        notification_check = ttk.Checkbutton(options_frame, text="완료 시 알림", 
                                            variable=self.notification_var)
        notification_check.grid(row=0, column=1, sticky=tk.W, padx=20)
        
        # 실행 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.run_button = ttk.Button(button_frame, text="🧪 테스트 실행", 
                                    command=self.run_tests, style="Accent.TButton")
        self.run_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ 중지", 
                                     command=self.stop_tests, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=5)
        
        clear_button = ttk.Button(button_frame, text="🗑️ 로그 지우기", 
                                 command=self.clear_log)
        clear_button.grid(row=0, column=2, padx=5)
        
        # 진행률 표시
        self.progress_var = tk.StringVar(value="준비")
        progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        progress_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 로그 출력
        log_frame = ttk.LabelFrame(main_frame, text="📋 테스트 로그", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 결과 요약
        self.result_frame = ttk.LabelFrame(main_frame, text="📊 테스트 결과 요약", padding="10")
        self.result_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.result_text = ttk.Label(self.result_frame, text="테스트를 실행하면 결과가 여기에 표시됩니다.")
        self.result_text.grid(row=0, column=0, sticky=tk.W)
        
        # 그리드 가중치 설정
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def load_config(self):
        """배포 설정 확인"""
        try:
            if os.path.exists("deploy.config"):
                self.log("✅ deploy.config 파일 발견")
                with open("deploy.config", 'r') as f:
                    content = f.read()
                    if "GCP_VM_IP" in content:
                        self.log("✅ GCP VM 설정 확인됨")
                    else:
                        self.log("⚠️ GCP VM 설정이 불완전할 수 있습니다")
            else:
                self.log("⚠️ deploy.config 파일이 없습니다. 원격 테스트 시 필요합니다.")
        except Exception as e:
            self.log(f"❌ 설정 로드 오류: {e}")
    
    def log(self, message):
        """로그 출력"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """로그 지우기"""
        self.log_text.delete(1.0, tk.END)
        self.result_text.config(text="테스트를 실행하면 결과가 여기에 표시됩니다.")
    
    def run_tests(self):
        """테스트 실행"""
        if self.is_testing:
            return
            
        self.is_testing = True
        self.run_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress_bar.start()
        
        # 별도 스레드에서 테스트 실행
        test_thread = threading.Thread(target=self._run_tests_thread)
        test_thread.daemon = True
        test_thread.start()
    
    def _run_tests_thread(self):
        """테스트 실행 스레드"""
        try:
            env_type = self.env_var.get()
            
            self.log(f"🚀 테스트 시작: {env_type} 환경")
            self.progress_var.set(f"{env_type} 테스트 실행 중...")
            
            if env_type == "local":
                self._run_local_tests()
            elif env_type == "remote":
                self._run_remote_tests()
            elif env_type == "both":
                self._run_both_tests()
                
        except Exception as e:
            self.log(f"❌ 테스트 실행 오류: {e}")
        finally:
            self._finish_testing()
    
    def _run_local_tests(self):
        """로컬 테스트 실행"""
        try:
            self.log("🏠 로컬 테스트 시작...")
            
            # Windows에서 bash 스크립트 실행
            if os.name == 'nt':  # Windows
                # Git Bash 또는 WSL 사용
                result = subprocess.run(
                    ["bash", "./test_local.sh"], 
                    capture_output=True, 
                    text=True,
                    timeout=300  # 5분 타임아웃
                )
            else:  # Unix/Linux
                result = subprocess.run(
                    ["./test_local.sh"], 
                    capture_output=True, 
                    text=True,
                    timeout=300
                )
            
            # 결과 출력
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.log(line)
            
            if result.stderr:
                for line in result.stderr.split('\n'):
                    if line.strip():
                        self.log(f"⚠️ {line}")
            
            # 성공/실패 판단
            if result.returncode == 0:
                self.log("✅ 로컬 테스트 성공!")
                self.test_results['local'] = 'success'
            else:
                self.log("❌ 로컬 테스트 실패!")
                self.test_results['local'] = 'failed'
                
        except subprocess.TimeoutExpired:
            self.log("⏰ 로컬 테스트 타임아웃")
            self.test_results['local'] = 'timeout'
        except FileNotFoundError:
            self.log("❌ test_local.sh 파일을 찾을 수 없습니다.")
            self.test_results['local'] = 'error'
        except Exception as e:
            self.log(f"❌ 로컬 테스트 오류: {e}")
            self.test_results['local'] = 'error'
    
    def _run_remote_tests(self):
        """원격 테스트 실행"""
        try:
            self.log("🌐 원격 테스트 시작...")
            
            # deploy.config 존재 확인
            if not os.path.exists("deploy.config"):
                self.log("❌ deploy.config 파일이 필요합니다.")
                self.test_results['remote'] = 'error'
                return
            
            # Windows에서 bash 스크립트 실행
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    ["bash", "./test_remote.sh"], 
                    capture_output=True, 
                    text=True,
                    timeout=600  # 10분 타임아웃
                )
            else:  # Unix/Linux
                result = subprocess.run(
                    ["./test_remote.sh"], 
                    capture_output=True, 
                    text=True,
                    timeout=600
                )
            
            # 결과 출력
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        self.log(line)
            
            if result.stderr:
                for line in result.stderr.split('\n'):
                    if line.strip():
                        self.log(f"⚠️ {line}")
            
            # 성공/실패 판단
            if result.returncode == 0:
                self.log("✅ 원격 테스트 성공!")
                self.test_results['remote'] = 'success'
            else:
                self.log("❌ 원격 테스트 실패!")
                self.test_results['remote'] = 'failed'
                
        except subprocess.TimeoutExpired:
            self.log("⏰ 원격 테스트 타임아웃")
            self.test_results['remote'] = 'timeout'
        except FileNotFoundError:
            self.log("❌ test_remote.sh 파일을 찾을 수 없습니다.")
            self.test_results['remote'] = 'error'
        except Exception as e:
            self.log(f"❌ 원격 테스트 오류: {e}")
            self.test_results['remote'] = 'error'
    
    def _run_both_tests(self):
        """로컬과 원격 테스트 순차 실행"""
        self.log("🚀 전체 테스트 시작 (로컬 → 원격)")
        
        # 로컬 테스트 먼저
        self._run_local_tests()
        
        # 로컬 테스트가 성공한 경우에만 원격 테스트 실행
        if self.test_results.get('local') == 'success':
            self.log("✅ 로컬 테스트 성공, 원격 테스트 진행...")
            self._run_remote_tests()
        else:
            self.log("❌ 로컬 테스트 실패, 원격 테스트 건너뛰기")
            self.test_results['remote'] = 'skipped'
    
    def _finish_testing(self):
        """테스트 완료 처리"""
        self.is_testing = False
        self.run_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress_bar.stop()
        
        # 결과 요약 생성
        self._update_result_summary()
        
        # 알림 (옵션이 켜져 있는 경우)
        if self.notification_var.get():
            self._show_notification()
        
        self.progress_var.set("테스트 완료")
        self.log("🏁 모든 테스트 완료")
    
    def _update_result_summary(self):
        """결과 요약 업데이트"""
        summary_parts = []
        
        # 아이콘 매핑
        status_icons = {
            'success': '✅',
            'failed': '❌', 
            'error': '💥',
            'timeout': '⏰',
            'skipped': '⏭️'
        }
        
        for test_type, result in self.test_results.items():
            icon = status_icons.get(result, '❓')
            summary_parts.append(f"{icon} {test_type.upper()}: {result}")
        
        if summary_parts:
            summary_text = " | ".join(summary_parts)
            self.result_text.config(text=summary_text)
        else:
            self.result_text.config(text="테스트 결과 없음")
    
    def _show_notification(self):
        """완료 알림 표시"""
        success_count = sum(1 for result in self.test_results.values() if result == 'success')
        total_count = len(self.test_results)
        
        if success_count == total_count and total_count > 0:
            messagebox.showinfo("테스트 완료", f"🎉 모든 테스트 성공! ({success_count}/{total_count})")
        elif success_count > 0:
            messagebox.showwarning("테스트 완료", f"⚠️ 일부 테스트 성공 ({success_count}/{total_count})")
        else:
            messagebox.showerror("테스트 완료", "❌ 모든 테스트 실패")
    
    def stop_tests(self):
        """테스트 중지 (현재는 간단한 구현)"""
        self.log("⏹️ 테스트 중지 요청됨")
        # 실제 구현에서는 subprocess를 종료해야 함
        self.is_testing = False
        self.progress_bar.stop()
        self.progress_var.set("중지됨")

def main():
    """메인 함수"""
    # CLI 인수 확인
    if len(sys.argv) > 1:
        # CLI 모드
        env_type = sys.argv[1] if sys.argv[1] in ['local', 'remote', 'both'] else 'local'
        print(f"🧪 CLI 모드로 {env_type} 테스트 실행")
        
        if env_type == "local":
            os.system("bash ./test_local.sh")
        elif env_type == "remote":
            os.system("bash ./test_remote.sh")
        elif env_type == "both":
            print("🏠 로컬 테스트 먼저 실행...")
            local_result = os.system("bash ./test_local.sh")
            if local_result == 0:
                print("✅ 로컬 성공, 🌐 원격 테스트 실행...")
                os.system("bash ./test_remote.sh")
            else:
                print("❌ 로컬 테스트 실패, 원격 테스트 건너뛰기")
    else:
        # GUI 모드
        try:
            root = tk.Tk()
            app = TestRunner(root)
            root.mainloop()
        except Exception as e:
            print(f"GUI 모드 실행 실패: {e}")
            print("CLI 모드로 사용하세요: python test_runner.py [local|remote|both]")

if __name__ == "__main__":
    main()