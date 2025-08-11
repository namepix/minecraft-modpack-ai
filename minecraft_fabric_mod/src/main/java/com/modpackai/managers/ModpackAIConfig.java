package com.modpackai.managers;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.Item;
import net.fabricmc.loader.api.FabricLoader;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Fabric 모드용 설정 관리자
 * NeoForge 모드 설정을 Fabric API로 변환
 */
public class ModpackAIConfig {
    private static final Logger LOGGER = LoggerFactory.getLogger(ModpackAIConfig.class);
    private static final String CONFIG_FILE_NAME = "modpackai-config.json";
    
    private JsonObject config;
    private Path configPath;
    
    // 기본 설정값들
    private String backendUrl = "http://localhost:5000";
    private Item aiItemMaterial = Items.NETHER_STAR;
    private String aiItemName = "§6§l모드팩 AI 어시스턴트";
    private String aiItemLore = "§7우클릭으로 AI 채팅창을 열 수 있습니다";
    private int requestTimeout = 10000;
    private String primaryModel = "gemini";
    private boolean webSearchEnabled = true;
    private String modpackName = "Unknown Modpack";
    private String modpackVersion = "1.0.0";
    
    public ModpackAIConfig() {
        this.configPath = FabricLoader.getInstance().getConfigDir().resolve(CONFIG_FILE_NAME);
        this.config = new JsonObject();
    }
    
    /**
     * 설정 파일 로드
     */
    public void loadConfig() {
        LOGGER.info("ModpackAI Fabric 설정 로드 시작: {}", configPath);
        
        try {
            if (Files.exists(configPath)) {
                // 기존 설정 파일 읽기
                String content = Files.readString(configPath);
                Gson gson = new Gson();
                config = gson.fromJson(content, JsonObject.class);
                
                // 설정값 로드
                loadConfigValues();
                LOGGER.info("기존 설정 파일 로드 완료");
            } else {
                // 기본 설정 생성
                createDefaultConfig();
                saveConfig();
                LOGGER.info("기본 설정 파일 생성 완료");
            }
        } catch (Exception e) {
            LOGGER.error("설정 파일 로드 실패", e);
            createDefaultConfig();
        }
    }
    
    /**
     * 기본 설정 생성
     */
    private void createDefaultConfig() {
        config = new JsonObject();
        
        // AI 백엔드 설정
        JsonObject backend = new JsonObject();
        backend.addProperty("url", backendUrl);
        backend.addProperty("timeout", requestTimeout);
        config.add("backend", backend);
        
        // AI 아이템 설정
        JsonObject aiItem = new JsonObject();
        aiItem.addProperty("material", "NETHER_STAR");
        aiItem.addProperty("name", aiItemName);
        aiItem.addProperty("lore", aiItemLore);
        config.add("ai_item", aiItem);
        
        // AI 모델 설정
        JsonObject ai = new JsonObject();
        ai.addProperty("primary_model", primaryModel);
        ai.addProperty("web_search_enabled", webSearchEnabled);
        config.add("ai", ai);

        // 모드팩 정보 설정
        JsonObject modpack = new JsonObject();
        modpack.addProperty("name", modpackName);
        modpack.addProperty("version", modpackVersion);
        config.add("modpack", modpack);
        
        LOGGER.info("기본 설정 생성 완료");
    }
    
    /**
     * 설정값들을 변수에 로드
     */
    private void loadConfigValues() {
        try {
            // 백엔드 설정
            if (config.has("backend")) {
                JsonObject backend = config.getAsJsonObject("backend");
                backendUrl = backend.has("url") ? backend.get("url").getAsString() : backendUrl;
                requestTimeout = backend.has("timeout") ? backend.get("timeout").getAsInt() : requestTimeout;
            }
            
            // AI 아이템 설정
            if (config.has("ai_item")) {
                JsonObject aiItem = config.getAsJsonObject("ai_item");
                if (aiItem.has("name")) {
                    aiItemName = aiItem.get("name").getAsString();
                }
                if (aiItem.has("lore")) {
                    aiItemLore = aiItem.get("lore").getAsString();
                }
                // Material은 NETHER_STAR로 고정 (통일성을 위해)
                aiItemMaterial = Items.NETHER_STAR;
            }
            
            // AI 설정
            if (config.has("ai")) {
                JsonObject ai = config.getAsJsonObject("ai");
                primaryModel = ai.has("primary_model") ? ai.get("primary_model").getAsString() : primaryModel;
                webSearchEnabled = ai.has("web_search_enabled") ? ai.get("web_search_enabled").getAsBoolean() : webSearchEnabled;
            }

            // 모드팩 정보 설정
            if (config.has("modpack")) {
                JsonObject modpack = config.getAsJsonObject("modpack");
                modpackName = modpack.has("name") ? modpack.get("name").getAsString() : modpackName;
                modpackVersion = modpack.has("version") ? modpack.get("version").getAsString() : modpackVersion;
            }
            
            LOGGER.info("설정값 로드 완료 - Backend: {}, AI Item: {}", backendUrl, aiItemMaterial);
        } catch (Exception e) {
            LOGGER.error("설정값 로드 중 오류 발생", e);
        }
    }
    
    /**
     * 설정 파일 저장
     */
    public void saveConfig() {
        try {
            // 디렉토리 생성
            Files.createDirectories(configPath.getParent());
            
            // JSON 포맷팅
            Gson gson = new GsonBuilder().setPrettyPrinting().create();
            String jsonContent = gson.toJson(config);
            
            // 파일 저장
            Files.writeString(configPath, jsonContent);
            LOGGER.info("설정 파일 저장 완료: {}", configPath);
            
        } catch (IOException e) {
            LOGGER.error("설정 파일 저장 실패", e);
        }
    }
    
    // Getter 메소드들 (기존 API와 동일한 인터페이스 제공)
    public String getBackendUrl() {
        return backendUrl;
    }
    
    public Item getAIItemMaterial() {
        return aiItemMaterial;
    }
    
    public String getAIItemName() {
        return aiItemName;
    }
    
    public String getAIItemLore() {
        return aiItemLore;
    }
    
    public int getRequestTimeout() {
        return requestTimeout;
    }
    
    public String getPrimaryModel() {
        return primaryModel;
    }
    
    public boolean isWebSearchEnabled() {
        return webSearchEnabled;
    }

    public String getModpackName() {
        return modpackName;
    }

    public String getModpackVersion() {
        return modpackVersion;
    }
    
    // Setter 메소드들
    public void setBackendUrl(String backendUrl) {
        this.backendUrl = backendUrl;
        if (!config.has("backend")) {
            config.add("backend", new JsonObject());
        }
        config.getAsJsonObject("backend").addProperty("url", backendUrl);
    }
    
    public void setPrimaryModel(String model) {
        this.primaryModel = model;
        if (!config.has("ai")) {
            config.add("ai", new JsonObject());
        }
        config.getAsJsonObject("ai").addProperty("primary_model", model);
    }
    
    public void setWebSearchEnabled(boolean enabled) {
        this.webSearchEnabled = enabled;
        if (!config.has("ai")) {
            config.add("ai", new JsonObject());
        }
        config.getAsJsonObject("ai").addProperty("web_search_enabled", enabled);
    }

    public void setModpackInfo(String name, String version) {
        this.modpackName = name != null && !name.isBlank() ? name : this.modpackName;
        this.modpackVersion = version != null && !version.isBlank() ? version : this.modpackVersion;
        if (!config.has("modpack")) {
            config.add("modpack", new JsonObject());
        }
        JsonObject modpack = config.getAsJsonObject("modpack");
        modpack.addProperty("name", this.modpackName);
        modpack.addProperty("version", this.modpackVersion);
    }
}