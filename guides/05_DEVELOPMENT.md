# 🛠️ 개발자를 위한 가이드

## 📋 개요

이 가이드는 마인크래프트 모드팩 AI 시스템을 개발하고 확장하려는 개발자를 위한 문서입니다.
현재 시스템은 Python Flask 백엔드와 Java Minecraft 플러그인으로 구성된 간소화된 아키텍처입니다.

## 🏗️ 개발 환경 설정

### 1. 필수 도구

**Python 개발:**
- Python 3.8+ 
- pip (패키지 관리자)
- venv (가상환경)

**Java 개발:**
- JDK 11+ 
- Maven 3.6+
- IntelliJ IDEA 또는 Eclipse (권장)

**기타 도구:**
- Git (버전 관리)
- Postman 또는 curl (API 테스트)
- VS Code (편집기, 선택사항)

### 2. 프로젝트 클론 및 설정

```bash
# 프로젝트 클론
git clone https://github.com/your-username/minecraft-modpack-ai.git
cd minecraft-modpack-ai

# Python 가상환경 생성
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Python 의존성 설치
pip install -r backend/requirements.txt
```

### 3. 개발 환경 변수 설정

```bash
cp env.example .env
# .env 파일을 편집하여 개발용 API 키 설정
```

```env
# 개발 환경 설정
DEBUG=true
LOG_LEVEL=DEBUG
GOOGLE_API_KEY=your-development-api-key

# 개발용 포트 (선택사항)
PORT=5001
```

## 🐍 Python 백엔드 개발

### 1. 프로젝트 구조

```
backend/
├── app.py                      # 메인 Flask 애플리케이션
├── middleware/
│   ├── __init__.py
│   ├── security.py            # 보안 미들웨어
│   └── monitoring.py          # 모니터링 미들웨어
├── tests/                     # 테스트 코드
│   ├── __init__.py
│   ├── conftest.py           # 테스트 설정
│   ├── test_app_integration.py
│   └── test_cli_scripts.py
├── requirements.txt           # Python 의존성
├── run_tests.py              # 테스트 실행 스크립트
└── pytest.ini               # pytest 설정
```

### 2. 개발 서버 실행

```bash
cd backend
python app.py
```

**개발 모드에서는 다음 기능이 활성화됩니다:**
- Hot reload (파일 변경 시 자동 재시작)
- 상세한 에러 메시지
- 디버그 로깅
- CORS 허용 범위 확대

### 3. 새로운 API 엔드포인트 추가

**app.py**에 새 엔드포인트 추가:

```python
@app.route('/api/new-endpoint', methods=['POST'])
@require_valid_input
@track_user_activity
@measure_performance("New Endpoint")
def new_endpoint():
    try:
        data = request.json
        # 비즈니스 로직 구현
        
        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
```

### 4. AI 모델 추가

새로운 AI 모델 지원을 위한 코드 추가:

```python
# app.py에서 새 모델 초기화
NEW_MODEL_API_KEY = os.getenv('NEW_MODEL_API_KEY')
new_model_client = None

if NEW_MODEL_API_KEY:
    try:
        # 새 모델 클라이언트 초기화
        new_model_client = NewModelClient(api_key=NEW_MODEL_API_KEY)
        print("✅ 새 모델 클라이언트 초기화 완료")
    except Exception as e:
        print(f"⚠️ 새 모델 초기화 실패: {e}")

# 채팅 엔드포인트에서 새 모델 처리 로직 추가
elif current_model == "new_model" and new_model_client:
    try:
        response = new_model_client.generate_response(message)
        ai_response = response.text
    except Exception as e:
        ai_response = f"새 모델 API 오류: {str(e)}"
```

## ☕ Java 플러그인 개발

### 1. 플러그인 구조

```
minecraft_plugin/src/main/java/com/modpackai/
├── ModpackAIPlugin.java          # 메인 플러그인 클래스
├── commands/
│   ├── AICommand.java            # /ai 명령어
│   └── ModpackAICommand.java     # /modpackai 명령어
├── gui/
│   ├── AIChatGUI.java           # AI 채팅 GUI
│   ├── ModelSelectionGUI.java   # 모델 선택 GUI
│   └── RecipeGUI.java           # 제작법 GUI
├── listeners/
│   ├── InventoryListener.java   # GUI 클릭 이벤트
│   └── PlayerInteractListener.java # 아이템 상호작용
├── managers/
│   ├── AIManager.java           # AI API 통신
│   ├── ConfigManager.java       # 설정 관리
│   └── RecipeManager.java       # 제작법 관리
└── utils/
    └── MessageUtils.java        # 메시지 유틸리티
```

### 2. 플러그인 빌드

```bash
cd minecraft_plugin
mvn clean package

# 빌드된 JAR 파일 확인
ls -la target/ModpackAI-1.0.jar
```

### 3. 새로운 명령어 추가

**새 명령어 클래스 생성:**

```java
// commands/NewCommand.java
package com.modpackai.commands;

import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;

public class NewCommand implements CommandExecutor {
    
    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!(sender instanceof Player)) {
            sender.sendMessage("§c이 명령어는 플레이어만 사용할 수 있습니다.");
            return true;
        }
        
        Player player = (Player) sender;
        
        // 명령어 로직 구현
        player.sendMessage("§a새로운 기능이 실행되었습니다!");
        
        return true;
    }
}
```

**plugin.yml에 명령어 등록:**

```yaml
commands:
  newcommand:
    description: "새로운 기능"
    usage: "/newcommand"
    permission: modpackai.new
```

**플러그인 메인 클래스에서 등록:**

```java
// ModpackAIPlugin.java에서
@Override
public void onEnable() {
    // 기존 코드...
    
    getCommand("newcommand").setExecutor(new NewCommand());
}
```

### 4. 새로운 GUI 추가

```java
// gui/NewGUI.java
package com.modpackai.gui;

import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

public class NewGUI {
    
    public void openGUI(Player player) {
        Inventory gui = Bukkit.createInventory(null, 27, "§6새로운 GUI");
        
        // GUI 아이템 설정
        ItemStack item = new ItemStack(Material.DIAMOND);
        ItemMeta meta = item.getItemMeta();
        meta.setDisplayName("§b새로운 기능");
        item.setItemMeta(meta);
        
        gui.setItem(13, item); // 가운데에 배치
        
        player.openInventory(gui);
    }
}
```

## 🧪 테스트

### 1. Python 백엔드 테스트

```bash
cd backend

# 모든 테스트 실행
python -m pytest

# 특정 테스트 파일 실행
python -m pytest tests/test_app_integration.py

# 커버리지와 함께 테스트
python -m pytest --cov=.
```

**새 테스트 작성:**

```python
# tests/test_new_feature.py
import pytest
from app import app

def test_new_endpoint():
    """새 엔드포인트 테스트"""
    client = app.test_client()
    
    response = client.post('/api/new-endpoint', 
                          json={"test": "data"})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
```

### 2. 수동 API 테스트

**curl을 사용한 테스트:**

```bash
# Health 체크
curl http://localhost:5000/health

# 채팅 테스트
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "테스트 질문",
    "player_uuid": "test-uuid",
    "modpack_name": "test",
    "modpack_version": "1.0"
  }'

# 모델 목록 확인
curl http://localhost:5000/models
```

## 🔧 디버깅

### 1. Python 백엔드 디버깅

**로깅 설정:**

```python
import logging

# 개발 모드에서 자세한 로깅
if os.getenv('DEBUG') == 'true':
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
```

**중단점 설정:**

```python
import pdb

def problematic_function():
    pdb.set_trace()  # 여기서 실행 중단
    # 디버깅할 코드
```

### 2. Java 플러그인 디버깅

**콘솔 로깅:**

```java
// ModpackAIPlugin.java에서
getLogger().info("디버그 메시지");
getLogger().warning("경고 메시지");
getLogger().severe("오류 메시지");
```

**플레이어 메시지로 디버깅:**

```java
player.sendMessage("§e[DEBUG] 변수값: " + variable);
```

## 📦 배포 준비

### 1. 프로덕션 빌드

**Python 백엔드:**

```bash
# 프로덕션 의존성 확인
pip freeze > requirements.txt

# 환경 변수 파일 준비
cp .env .env.production
# .env.production에서 DEBUG=false로 설정
```

**Java 플러그인:**

```bash
cd minecraft_plugin
mvn clean package -Dmaven.test.skip=true

# 최종 JAR 파일 복사
cp target/ModpackAI-1.0.jar ../releases/
```

### 2. 버전 관리

**태그 생성:**

```bash
git tag -a v1.1.0 -m "새로운 기능 추가"
git push origin v1.1.0
```

**CHANGELOG.md 업데이트:**

```markdown
## [1.1.0] - 2025-01-01

### Added
- 새로운 AI 모델 지원
- 향상된 GUI 시스템

### Fixed
- API 응답 시간 개선
- 메모리 누수 해결

### Changed
- 설정 파일 구조 개선
```

## 🔌 확장 가능성

### 1. 플러그인 아키텍처

**새로운 기능 모듈 추가:**

```python
# backend/modules/new_feature.py
class NewFeatureModule:
    def __init__(self, app):
        self.app = app
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/api/new-feature')
        def new_feature_endpoint():
            return {"message": "새로운 기능"}

# app.py에서 모듈 로드
from modules.new_feature import NewFeatureModule
new_feature = NewFeatureModule(app)
```

### 2. 데이터베이스 연동

**SQLAlchemy를 사용한 데이터베이스 추가:**

```python
# requirements.txt에 추가
# SQLAlchemy==2.0.0
# Flask-SQLAlchemy==3.0.0

from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///minecraft_ai.db'
db = SQLAlchemy(app)

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_uuid = db.Column(db.String(36), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

### 3. WebSocket 지원

**실시간 통신을 위한 WebSocket:**

```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('ai_message')
def handle_ai_message(data):
    # AI 처리 후 실시간 응답
    response = process_ai_message(data['message'])
    emit('ai_response', {'response': response})
```

## 📚 참고 자료

### 1. API 문서

- **Flask**: https://flask.palletsprojects.com/
- **Bukkit API**: https://hub.spigotmc.org/javadocs/bukkit/
- **Google AI**: https://ai.google.dev/docs
- **OpenAI API**: https://platform.openai.com/docs

### 2. 개발 도구

- **Maven**: https://maven.apache.org/guides/
- **pytest**: https://docs.pytest.org/
- **Git**: https://git-scm.com/docs

### 3. 마인크래프트 개발

- **SpigotMC**: https://www.spigotmc.org/wiki/
- **Bukkit Tutorial**: https://bukkit.fandom.com/wiki/Plugin_Tutorial
- **Minecraft Protocol**: https://wiki.vg/Protocol

## 💡 개발 팁

### 1. 성능 최적화

- AI API 호출 최소화 (캐싱 활용)
- 데이터베이스 쿼리 최적화
- 메모리 사용량 모니터링

### 2. 보안 고려사항

- API 키 안전한 보관
- 입력 데이터 검증
- Rate Limiting 구현
- HTTPS 사용 권장

### 3. 코드 품질

- Type Hints 사용 (Python)
- 적절한 예외 처리
- 코드 주석 및 문서화
- 테스트 커버리지 유지

---

**🛠️ 개발에 도움이 필요하면 GitHub Issues를 통해 문의해주세요!** 🚀