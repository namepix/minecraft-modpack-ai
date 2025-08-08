# 🔧 GCP VM 하이브리드 서버 수동 설치 가이드

## 1. 전체 설치 방법 (한번에)

```bash
#!/bin/bash
# 모든 하이브리드 서버 수동 설치

cd ~

# 1. NeoForge 하이브리드 (Youer/Arclight) - 1.21
echo "📥 NeoForge 1.21 하이브리드 서버 다운로드 중..."
wget -O neoforge-hybrid-1.21.jar "https://api.mohistmc.com/api/v2/projects/youer/versions/1.21.1/builds/latest/download" || \
wget -O neoforge-hybrid-1.21.jar "https://github.com/IzzelAliz/Arclight/releases/download/1.21.1/arclight-neoforge-1.21.1.jar"

# 2. Forge 하이브리드 (Mohist) - 1.20.1
echo "📥 Forge 1.20.1 하이브리드 서버 다운로드 중..."
wget -O mohist-1.20.1.jar "https://api.mohistmc.com/api/v2/projects/mohist/versions/1.20.1/builds/latest/download"

# 3. Forge 하이브리드 (Mohist) - 1.16.5  
echo "📥 Forge 1.16.5 하이브리드 서버 다운로드 중..."
wget -O mohist-1.16.5.jar "https://api.mohistmc.com/api/v2/projects/mohist/versions/1.16.5/builds/latest/download"

# 4. Fabric 하이브리드 (CardBoard) - 1.20.1
echo "📥 Fabric 1.20.1 하이브리드 서버 다운로드 중..."
wget -O cardboard-1.20.1.jar "https://github.com/CardboardPowered/cardboard/releases/download/1.20.1-4.0.6/cardboard-1.20.1-4.0.6.jar" || \
wget -O cardboard-1.20.1.jar "https://github.com/Dueris/Banner/releases/latest/download/banner-1.20.1.jar"

# 각 모드팩에 복사
echo "📋 각 모드팩에 하이브리드 서버 복사 중..."

# NeoForge 모드팩들 (1.21)
for modpack in enigmatica_10 atm10 carpg test; do
    if [ -d "$modpack" ]; then
        # 파일명 호환: 기본 youer-neoforge.jar, 기존 neoforge-hybrid.jar도 함께 유지
        cp neoforge-hybrid-1.21.jar "$modpack/youer-neoforge.jar"
        cp neoforge-hybrid-1.21.jar "$modpack/neoforge-hybrid.jar"
        echo "✅ $modpack/youer-neoforge.jar 및 neoforge-hybrid.jar 복사 완료"
    fi
done

# NeoForge 모드팩 (1.20.1) - enigmatica_9e는 1.20.1 NeoForge
if [ -d "enigmatica_9e" ]; then
    # 1.20.1 NeoForge용 Arclight 다운로드
    wget -O enigmatica_9e/youer-neoforge.jar "https://github.com/IzzelAliz/Arclight/releases/download/1.20.1/arclight-neoforge-1.20.1.jar"
    echo "✅ enigmatica_9e/youer-neoforge.jar (1.20.1) 복사 완료"
fi

# Forge 모드팩들 (1.20.1)
for modpack in integrated_MC beyond_depth cteserver; do
    if [ -d "$modpack" ]; then
        cp mohist-1.20.1.jar "$modpack/"
        echo "✅ $modpack/mohist-1.20.1.jar 복사 완료"
    fi
done

# Forge 모드팩들 (1.16.5) 
for modpack in enigmatica_6 mnm; do
    if [ -d "$modpack" ]; then
        cp mohist-1.16.5.jar "$modpack/"
        echo "✅ $modpack/mohist-1.16.5.jar 복사 완료"
    fi
done

# Fabric 모드팩 (1.20.1)
if [ -d "prominence_2" ]; then
    cp cardboard-1.20.1.jar prominence_2/cardboard.jar
    echo "✅ prominence_2/cardboard.jar 복사 완료"
fi

echo "🎉 모든 하이브리드 서버 설치 완료!"
```

## 2. 개별 설치 방법

### NeoForge 하이브리드 (1.21) - enigmatica_10, atm10, carpg, test

```bash
# Youer (권장)
cd ~/enigmatica_10
wget -O youer-neoforge.jar "https://api.mohistmc.com/api/v2/projects/youer/versions/1.21.1/builds/latest/download"

# 실패 시 Arclight 사용
wget -O youer-neoforge.jar "https://github.com/IzzelAliz/Arclight/releases/download/1.21.1/arclight-neoforge-1.21.1.jar"

# 다른 모드팩에 복사 (기존 파일명 호환 포함)
cp ~/enigmatica_10/youer-neoforge.jar ~/atm10/
cp ~/enigmatica_10/youer-neoforge.jar ~/atm10/neoforge-hybrid.jar
cp ~/enigmatica_10/youer-neoforge.jar ~/carpg/
cp ~/enigmatica_10/youer-neoforge.jar ~/carpg/neoforge-hybrid.jar
cp ~/enigmatica_10/youer-neoforge.jar ~/test/
cp ~/enigmatica_10/youer-neoforge.jar ~/test/neoforge-hybrid.jar
```

### NeoForge 하이브리드 (1.20.1) - enigmatica_9e

```bash
cd ~/enigmatica_9e
wget -O youer-neoforge.jar "https://github.com/IzzelAliz/Arclight/releases/download/1.20.1/arclight-neoforge-1.20.1.jar"
cp youer-neoforge.jar neoforge-hybrid.jar
```

### Forge 하이브리드 (1.20.1) - integrated_MC, beyond_depth, cteserver

```bash
cd ~/integrated_MC
wget -O mohist-1.20.1.jar "https://api.mohistmc.com/api/v2/projects/mohist/versions/1.20.1/builds/latest/download"

# 다른 모드팩에 복사
cp ~/integrated_MC/mohist-1.20.1.jar ~/beyond_depth/
cp ~/integrated_MC/mohist-1.20.1.jar ~/cteserver/
```

### Forge 하이브리드 (1.16.5) - enigmatica_6, mnm

```bash
cd ~/enigmatica_6
wget -O mohist-1.16.5.jar "https://api.mohistmc.com/api/v2/projects/mohist/versions/1.16.5/builds/latest/download"

# 다른 모드팩에 복사
cp ~/enigmatica_6/mohist-1.16.5.jar ~/mnm/
```

### Fabric 하이브리드 (1.20.1) - prominence_2

```bash
cd ~/prominence_2
wget -O cardboard.jar "https://github.com/CardboardPowered/cardboard/releases/download/1.20.1-4.0.6/cardboard-1.20.1-4.0.6.jar"

# 실패 시 Banner 사용
wget -O cardboard.jar "https://github.com/Dueris/Banner/releases/latest/download/banner-1.20.1.jar"
```

## 3. 설치 확인

```bash
# 각 모드팩에서 하이브리드 서버 파일 확인 (양쪽 이름 모두 확인)
ls -la ~/*/youer-neoforge.jar ~/*/neoforge-hybrid.jar ~/*/mohist-*.jar ~/*/cardboard.jar

# AI 지원 시작 스크립트 테스트
cd ~/enigmatica_10
ls -la start_with_ai.sh
cat start_with_ai.sh
```

## 4. 테스트 실행

```bash
# AI 백엔드 시작 (먼저)
sudo systemctl start mc-ai-backend
sudo systemctl status mc-ai-backend

# 모드팩 서버 시작 (AI 지원)
cd ~/enigmatica_10
./start_with_ai.sh
```

## 5. 문제 해결

### 다운로드 실패 시
```bash
# 수동 다운로드 후 직접 업로드
scp ~/Downloads/mohist-1.20.1.jar namepix080@34.64.217.151:~/integrated_MC/
```

### 권한 문제 시
```bash
chmod +x ~/*/start_with_ai.sh
```

### Java 메모리 부족 시
```bash
# start_with_ai.sh에서 -Xmx 값 조정
nano ~/enigmatica_10/start_with_ai.sh
# -Xmx10G → -Xmx6G 로 변경
```

## 6. UFW 방화벽 문제 해결

```bash
# Debian에서는 iptables 사용
sudo apt install ufw
sudo ufw allow 22/tcp
sudo ufw allow 25565/tcp  
sudo ufw allow 5000/tcp
sudo ufw --force enable
```