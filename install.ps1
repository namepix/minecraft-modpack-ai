# 마인크래프트 모드팩 AI 시스템 Windows 설치 스크립트
# PowerShell 5.1+ 또는 PowerShell Core 6+ 필요

param(
    [switch]$SkipDependencyCheck,
    [switch]$DevMode
)

# 오류 발생 시 중단
$ErrorActionPreference = "Stop"

# 색상 정의
function Write-ColorText {
    param([string]$Text, [string]$Color)
    switch ($Color) {
        "Red" { Write-Host $Text -ForegroundColor Red }
        "Green" { Write-Host $Text -ForegroundColor Green }
        "Yellow" { Write-Host $Text -ForegroundColor Yellow }
        "Blue" { Write-Host $Text -ForegroundColor Blue }
        "Cyan" { Write-Host $Text -ForegroundColor Cyan }
        default { Write-Host $Text }
    }
}

function Write-Info { param([string]$Message) Write-ColorText "[INFO] $Message" "Blue" }
function Write-Success { param([string]$Message) Write-ColorText "[SUCCESS] $Message" "Green" }
function Write-Warning { param([string]$Message) Write-ColorText "[WARNING] $Message" "Yellow" }
function Write-Error { param([string]$Message) Write-ColorText "[ERROR] $Message" "Red" }

# 관리자 권한 확인
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# 필수 도구 확인
function Test-Prerequisites {
    Write-Info "필수 도구 확인 중..."
    
    # Python 확인
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion -match "Python (\d+)\.(\d+)") {
            $major = [int]$matches[1]
            $minor = [int]$matches[2]
            if ($major -ge 3 -and $minor -ge 8) {
                Write-Success "Python $pythonVersion 확인됨"
            } else {
                throw "Python 3.8+ 필요 (현재: $pythonVersion)"
            }
        }
    } catch {
        Write-Error "Python 3.8+이 설치되어 있지 않습니다. https://python.org에서 설치하세요."
        return $false
    }
    
    # Java 확인
    try {
        $javaVersion = java -version 2>&1 | Select-String "version" | Select-Object -First 1
        if ($javaVersion -match '"(\d+)\.(\d+)') {
            $javaVer = [int]$matches[1]
            if ($javaVer -ge 11) {
                Write-Success "Java $javaVer 확인됨"
            } else {
                throw "Java 11+ 필요"
            }
        }
    } catch {
        Write-Error "Java 11+이 설치되어 있지 않습니다. https://adoptium.net에서 설치하세요."
        return $false
    }
    
    # Maven 확인 (플러그인 빌드용)
    try {
        $mavenVersion = mvn -version 2>$null | Select-String "Apache Maven" | Select-Object -First 1
        Write-Success "Maven 확인됨: $mavenVersion"
    } catch {
        Write-Warning "Maven이 설치되어 있지 않습니다. 플러그인 빌드를 수동으로 해야 합니다."
    }
    
    # Git 확인
    try {
        $gitVersion = git --version 2>$null
        Write-Success "Git 확인됨: $gitVersion"
    } catch {
        Write-Warning "Git이 설치되어 있지 않습니다. 버전 관리 기능을 사용할 수 없습니다."
    }
    
    return $true
}

# Python 가상환경 생성
function New-PythonVenv {
    Write-Info "Python 가상환경 생성 중..."
    
    if (Test-Path "venv") {
        Write-Warning "기존 가상환경이 발견되었습니다. 삭제 후 새로 생성합니다."
        Remove-Item -Recurse -Force "venv"
    }
    
    python -m venv venv
    
    # 가상환경 활성화
    & "venv\Scripts\Activate.ps1"
    
    # pip 업그레이드
    python -m pip install --upgrade pip
    
    Write-Success "Python 가상환경 생성 완료"
}

# Python 의존성 설치
function Install-PythonDependencies {
    Write-Info "Python 의존성 설치 중..."
    
    if (Test-Path "backend\requirements.txt") {
        pip install -r backend\requirements.txt
    } elseif (Test-Path "requirements.txt") {
        pip install -r requirements.txt
    } else {
        Write-Error "requirements.txt 파일을 찾을 수 없습니다."
        exit 1
    }
    
    Write-Success "Python 의존성 설치 완료"
}

# 환경 변수 파일 설정
function New-EnvironmentFile {
    Write-Info "환경 변수 파일 설정 중..."
    
    if (!(Test-Path ".env")) {
        if (Test-Path "env.example") {
            Copy-Item "env.example" ".env"
            Write-Success "환경 변수 파일(.env)이 생성되었습니다."
            Write-Warning "API 키를 설정해주세요: notepad .env"
        } else {
            Write-Error "env.example 파일을 찾을 수 없습니다."
            exit 1
        }
    } else {
        Write-Info "환경 변수 파일(.env)이 이미 존재합니다."
    }
}

# Minecraft 플러그인 빌드
function Build-MinecraftPlugin {
    Write-Info "Minecraft 플러그인 빌드 중..."
    
    if (Get-Command mvn -ErrorAction SilentlyContinue) {
        Push-Location "minecraft_plugin"
        try {
            mvn clean package
            Write-Success "플러그인 빌드 완료: target\ModpackAI-1.0.jar"
        } catch {
            Write-Error "플러그인 빌드 실패: $_"
            Write-Info "Maven이 설치되어 있는지 확인하세요."
        } finally {
            Pop-Location
        }
    } else {
        Write-Warning "Maven을 찾을 수 없습니다. 플러그인 빌드를 건너뜁니다."
        Write-Info "수동으로 빌드하려면: cd minecraft_plugin && mvn clean package"
    }
}

# 필요한 디렉토리 생성
function New-RequiredDirectories {
    Write-Info "필요한 디렉토리 생성 중..."
    
    $directories = @("logs", "data", "backups")
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir | Out-Null
            Write-Info "디렉토리 생성: $dir"
        }
    }
}

# 백엔드 서비스 테스트
function Test-BackendService {
    Write-Info "백엔드 서비스 테스트 중..."
    
    # 백그라운드에서 서비스 시작
    $job = Start-Job -ScriptBlock {
        Set-Location $args[0]
        & "venv\Scripts\python.exe" "backend\app.py"
    } -ArgumentList $PWD.Path
    
    # 서비스가 시작될 때까지 대기
    Start-Sleep 5
    
    try {
        # Health 체크
        $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Success "백엔드 서비스 테스트 성공"
        } else {
            Write-Warning "백엔드 서비스 응답이 예상과 다릅니다."
        }
    } catch {
        Write-Warning "백엔드 서비스 테스트 실패: $_"
        Write-Info "수동으로 테스트하세요: cd backend && python app.py"
    } finally {
        # 테스트 서비스 중지
        Stop-Job $job -ErrorAction SilentlyContinue
        Remove-Job $job -ErrorAction SilentlyContinue
    }
}

# Windows 서비스 등록 (선택사항)
function Register-WindowsService {
    if (Test-Administrator) {
        Write-Info "Windows 서비스 등록을 원하시면 NSSM을 설치하고 수동으로 설정하세요."
        Write-Info "NSSM 다운로드: https://nssm.cc/"
        Write-Info "서비스 등록 명령어:"
        Write-Info "  nssm install MinecraftAI"
        Write-Info "  nssm set MinecraftAI Application `"$PWD\venv\Scripts\python.exe`""
        Write-Info "  nssm set MinecraftAI AppParameters `"$PWD\backend\app.py`""
        Write-Info "  nssm set MinecraftAI AppDirectory `"$PWD`""
        Write-Info "  nssm set MinecraftAI DisplayName `"Minecraft AI Backend`""
    } else {
        Write-Info "Windows 서비스로 등록하려면 관리자 권한으로 다시 실행하세요."
    }
}

# 메인 설치 함수
function Install-MinecraftAI {
    Write-Info "마인크래프트 모드팩 AI 시스템 Windows 설치 시작..."
    
    # 필수 조건 확인
    if (!$SkipDependencyCheck -and !(Test-Prerequisites)) {
        Write-Error "필수 조건을 만족하지 않습니다."
        exit 1
    }
    
    try {
        # 설치 단계 실행
        New-RequiredDirectories
        New-PythonVenv
        Install-PythonDependencies
        New-EnvironmentFile
        Build-MinecraftPlugin
        
        if (!$DevMode) {
            Test-BackendService
        }
        
        # 설치 완료 메시지
        Write-Success "설치가 완료되었습니다!"
        Write-Host ""
        Write-ColorText "🎉 마인크래프트 모드팩 AI 시스템 Windows 설치 완료!" "Green"
        Write-Host ""
        Write-ColorText "📋 다음 단계:" "Cyan"
        Write-Host "1. API 키 설정:"
        Write-Host "   notepad .env"
        Write-Host ""
        Write-Host "2. 백엔드 서비스 시작:"
        Write-Host "   cd backend"
        Write-Host "   python app.py"
        Write-Host ""
        Write-Host "3. 플러그인 설치:"
        Write-Host "   minecraft_plugin\target\ModpackAI-1.0.jar를 마인크래프트 서버의 plugins 폴더에 복사"
        Write-Host ""
        Write-Host "4. 백엔드 테스트:"
        Write-Host "   http://localhost:5000/health 접속하여 상태 확인"
        Write-Host ""
        Write-ColorText "📚 문서:" "Cyan"
        Write-Host "- guides\01_ADMIN_SETUP.md: 상세 설치 가이드"
        Write-Host "- guides\03_GAME_COMMANDS.md: 게임 내 사용법"
        Write-Host ""
        Write-ColorText "🎮 즐거운 모드팩 플레이 되세요!" "Green"
        
        Register-WindowsService
        
    } catch {
        Write-Error "설치 중 오류가 발생했습니다: $_"
        exit 1
    }
}

# 스크립트 실행
Install-MinecraftAI