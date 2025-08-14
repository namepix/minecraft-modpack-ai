#!/usr/bin/env python3
"""
RAG 설정 관리자 - 수동 모드팩 지정 및 설정 관리

이 도구는 다음 기능을 제공합니다:
1. 현재 활성 모드팩 수동 설정
2. RAG 모드 전환 (자동/수동)
3. 설정 상태 확인
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv, set_key, find_dotenv

class RAGConfigManager:
    """RAG 시스템 설정 관리"""
    
    def __init__(self):
        # 표준 환경 파일 경로: ~/minecraft-ai-backend/.env (기존 시스템과 호환)
        runtime_dir = Path.home() / "minecraft-ai-backend"
        self.env_file = runtime_dir / ".env"
        
        # 런타임 디렉토리가 없으면 생성
        if not runtime_dir.exists():
            runtime_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ 런타임 디렉토리 생성: {runtime_dir}")
        
        # .env 파일이 없으면 프로젝트의 env.example에서 복사
        if not self.env_file.exists():
            project_root = Path(__file__).parent.parent
            env_example = project_root / "env.example"
            if env_example.exists():
                import shutil
                shutil.copy2(env_example, self.env_file)
                print(f"✅ 환경 파일 초기화: {self.env_file}")
            else:
                self.env_file.touch()
                print(f"✅ 새 환경 파일 생성: {self.env_file}")
            
        self.config_file = Path(__file__).parent / "rag_config.json"
        load_dotenv(self.env_file)
    
    def get_current_config(self) -> Dict[str, Any]:
        """현재 RAG 설정 상태 조회"""
        # 항상 실제 환경 파일 경로와 현재 환경변수 사용
        config = {
            "env_file": str(self.env_file),  # 실제 사용하는 환경 파일 경로
            "current_modpack": {
                "name": os.getenv('CURRENT_MODPACK_NAME', ''),
                "version": os.getenv('CURRENT_MODPACK_VERSION', '1.0.0')
            },
            "rag_mode": "auto",  # 기본값
            "gcp_enabled": os.getenv('GCP_RAG_ENABLED', 'true').lower() == 'true',
            "gcp_project_id": os.getenv('GCP_PROJECT_ID', ''),  # 현재 환경변수에서 직접 읽기
            "manual_modpack_path": ""
        }
        
        # JSON 설정 파일이 있으면 로드하되, env_file과 gcp_project_id는 덮어쓰지 않음
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    json_config = json.load(f)
                    # env_file과 gcp_project_id는 현재 환경변수 우선
                    actual_env_file = config["env_file"]
                    actual_gcp_project = config["gcp_project_id"]
                    
                    config.update(json_config)
                    
                    # 실제 환경 파일 정보 복원
                    config["env_file"] = actual_env_file
                    config["gcp_project_id"] = actual_gcp_project
                    
            except Exception as e:
                print(f"⚠️ JSON 설정 파일 로드 실패: {e}")
        
        return config
    
    def set_gcp_project(self, project_id: str) -> bool:
        """GCP 프로젝트 ID 설정"""
        try:
            if not self.env_file.exists():
                self.env_file.touch()
                print(f"✅ 새 .env 파일 생성: {self.env_file}")
            
            set_key(self.env_file, "GCP_PROJECT_ID", project_id)
            print(f"✅ GCP 프로젝트 ID 설정 완료: {project_id}")
            
            # 환경변수 즉시 갱신
            os.environ["GCP_PROJECT_ID"] = project_id
            return True
        except Exception as e:
            print(f"❌ GCP 프로젝트 ID 설정 실패: {e}")
            return False

    def set_manual_modpack(self, name: str, version: str, path: Optional[str] = None) -> bool:
        """수동 모드팩 설정"""
        try:
            # .env 파일에 설정
            if self.env_file:
                set_key(self.env_file, "CURRENT_MODPACK_NAME", name)
                set_key(self.env_file, "CURRENT_MODPACK_VERSION", version)
                print(f"✅ .env 파일 업데이트: {name} v{version}")
                
                # 환경변수 즉시 갱신
                os.environ["CURRENT_MODPACK_NAME"] = name
                os.environ["CURRENT_MODPACK_VERSION"] = version
            
            # JSON 설정 파일 업데이트
            config = self.get_current_config()
            config.update({
                "rag_mode": "manual",
                "current_modpack": {
                    "name": name,
                    "version": version
                },
                "manual_modpack_path": path or ""
            })
            
            self._save_config(config)
            print(f"✅ RAG 설정 업데이트: 수동 모드 - {name} v{version}")
            
            return True
            
        except Exception as e:
            print(f"❌ 설정 저장 실패: {e}")
            return False
    
    def set_auto_mode(self) -> bool:
        """자동 모드로 전환"""
        try:
            config = self.get_current_config()
            config["rag_mode"] = "auto"
            
            self._save_config(config)
            print("✅ RAG 모드: 자동으로 전환됨")
            
            return True
            
        except Exception as e:
            print(f"❌ 자동 모드 설정 실패: {e}")
            return False
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """JSON 설정 파일 저장 (env_file과 gcp_project_id 제외)"""
        try:
            # env_file과 gcp_project_id는 JSON에 저장하지 않음 (환경변수가 단일 진실 원천)
            save_config = {k: v for k, v in config.items() 
                          if k not in ["env_file", "gcp_project_id", "gcp_enabled"]}
            
            os.makedirs(self.config_file.parent, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(save_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise Exception(f"설정 파일 저장 실패: {e}")
    
    def print_status(self) -> None:
        """현재 설정 상태 출력"""
        config = self.get_current_config()
        
        print("\n📋 RAG 시스템 설정 상태")
        print("=" * 50)
        
        print(f"🔧 RAG 모드: {config['rag_mode']}")
        print(f"📦 현재 모드팩: {config['current_modpack']['name']} v{config['current_modpack']['version']}")
        
        if config.get('manual_modpack_path'):
            print(f"📁 모드팩 경로: {config['manual_modpack_path']}")
        
        print(f"🌐 GCP RAG: {'✅ 활성화' if config['gcp_enabled'] else '❌ 비활성화'}")
        
        if config['gcp_project_id']:
            print(f"✅ GCP 프로젝트 ID: {config['gcp_project_id']}")
        else:
            print("⚠️  GCP 프로젝트 ID가 설정되지 않음")
        
        print(f"⚙️  환경 파일: {config['env_file']}")
        print(f"📄 설정 파일: {self.config_file}")
        
        if config['rag_mode'] == 'manual':
            print("\n💡 수동 모드 활성화됨")
            print("   - RAG 검색이 지정된 모드팩에만 제한됩니다")
            print("   - 새 모드팩을 인덱싱하려면 rag_manager.py를 사용하세요")
        else:
            print("\n💡 자동 모드 활성화됨")
            print("   - 게임에서 전송되는 모드팩 정보를 자동으로 사용합니다")


def main():
    """CLI 메인 함수"""
    import sys
    
    if len(sys.argv) < 2:
        print_help()
        return
    
    manager = RAGConfigManager()
    command = sys.argv[1]
    
    if command == "status":
        manager.print_status()
    
    elif command == "set-manual":
        if len(sys.argv) < 4:
            print("❌ 사용법: python config_manager.py set-manual <모드팩_이름> <모드팩_버전>")
            return
        name, version = sys.argv[2], sys.argv[3]
        if manager.set_manual_modpack(name, version):
            print("✅ 수동 모드팩 설정 완료")
    
    elif command == "set-auto":
        if manager.set_auto_mode():
            print("✅ 자동 모드 설정 완료")
    
    elif command == "set-gcp-project":
        if len(sys.argv) < 3:
            print("❌ 사용법: python config_manager.py set-gcp-project <프로젝트_ID>")
            return
        project_id = sys.argv[2]
        if manager.set_gcp_project(project_id):
            print("✅ GCP 프로젝트 ID 설정 완료")
    
    else:
        print_help()

def print_help():
    """도움말 출력"""
    print("""
🔧 RAG 설정 관리자

사용법:
  python config_manager.py <명령어> [옵션]

명령어:
  status                              # 현재 설정 상태 확인
  set-manual <모드팩이름> <버전>        # 수동 모드팩 설정
  set-auto                           # 자동 모드로 전환
  set-gcp-project <프로젝트_ID>       # GCP 프로젝트 ID 설정

예시:
  python config_manager.py status
  python config_manager.py set-manual "Pixelmon_Reforged" "9.1.12"
  python config_manager.py set-gcp-project "my-gcp-project"
  python config_manager.py set-auto
""")

if __name__ == "__main__":
    main()