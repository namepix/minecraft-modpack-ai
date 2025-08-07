package com.modpackai.managers;

import com.modpackai.ModpackAIPlugin;
import org.bukkit.entity.Player;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Logger;

public class AIManager {
    private final ModpackAIPlugin plugin;
    private final ConfigManager configManager;
    private final Logger logger;
    private final HttpClient httpClient;
    private final String baseUrl;
    
    public AIManager(ModpackAIPlugin plugin, ConfigManager configManager) {
        this.plugin = plugin;
        this.configManager = configManager;
        this.logger = plugin.getLogger();
        this.httpClient = HttpClient.newHttpClient();
        this.baseUrl = configManager.getBackendUrl();
    }
    
    /**
     * 사용 가능한 AI 모델 목록을 가져옵니다.
     */
    public List<AIModelInfo> getAvailableModels() {
        List<AIModelInfo> models = new ArrayList<>();
        
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/models"))
                    .header("Content-Type", "application/json")
                    .GET()
                    .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JSONObject jsonResponse = new JSONObject(response.body());
                JSONArray modelsArray = jsonResponse.getJSONArray("models");
                
                for (int i = 0; i < modelsArray.length(); i++) {
                    JSONObject modelJson = modelsArray.getJSONObject(i);
                    AIModelInfo model = new AIModelInfo(
                        modelJson.getString("id"),
                        modelJson.getString("name"),
                        modelJson.getString("provider"),
                        modelJson.getBoolean("free_tier"),
                        modelJson.getString("description"),
                        modelJson.getBoolean("available"),
                        modelJson.getBoolean("current")
                    );
                    models.add(model);
                }
            } else {
                logger.warning("AI 모델 목록 조회 실패: " + response.statusCode());
            }
            
        } catch (IOException | InterruptedException e) {
            logger.severe("AI 모델 목록 조회 중 오류: " + e.getMessage());
        }
        
        return models;
    }
    
    /**
     * AI 모델을 전환합니다.
     */
    public boolean switchModel(String modelId) {
        try {
            JSONObject requestBody = new JSONObject();
            requestBody.put("model_id", modelId);
            
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/models/switch"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(requestBody.toString()))
                    .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JSONObject jsonResponse = new JSONObject(response.body());
                if (jsonResponse.getBoolean("success")) {
                    logger.info("AI 모델이 " + modelId + "로 전환되었습니다.");
                    return true;
                }
            } else {
                logger.warning("AI 모델 전환 실패: " + response.statusCode());
            }
            
        } catch (IOException | InterruptedException e) {
            logger.severe("AI 모델 전환 중 오류: " + e.getMessage());
        }
        
        return false;
    }
    
    /**
     * 현재 사용 중인 AI 모델 정보를 가져옵니다.
     */
    public AIModelInfo getCurrentModel() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/models"))
                    .header("Content-Type", "application/json")
                    .GET()
                    .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JSONObject jsonResponse = new JSONObject(response.body());
                String currentModelId = jsonResponse.getString("current_model");
                JSONObject modelInfo = jsonResponse.getJSONObject("model_info");
                
                return new AIModelInfo(
                    currentModelId,
                    modelInfo.getString("name"),
                    modelInfo.getString("provider"),
                    modelInfo.getBoolean("free_tier"),
                    modelInfo.getString("description"),
                    true,
                    true
                );
            } else {
                logger.warning("현재 AI 모델 정보 조회 실패: " + response.statusCode());
            }
            
        } catch (IOException | InterruptedException e) {
            logger.severe("현재 AI 모델 정보 조회 중 오류: " + e.getMessage());
        }
        
        return null;
    }
    
    /**
     * AI 모델 정보를 담는 클래스
     */
    public static class AIModelInfo {
        private final String id;
        private final String name;
        private final String provider;
        private final boolean freeTier;
        private final String description;
        private final boolean available;
        private final boolean current;
        
        public AIModelInfo(String id, String name, String provider, boolean freeTier, 
                          String description, boolean available, boolean current) {
            this.id = id;
            this.name = name;
            this.provider = provider;
            this.freeTier = freeTier;
            this.description = description;
            this.available = available;
            this.current = current;
        }
        
        // Getters
        public String getId() { return id; }
        public String getName() { return name; }
        public String getProvider() { return provider; }
        public boolean isFreeTier() { return freeTier; }
        public String getDescription() { return description; }
        public boolean isAvailable() { return available; }
        public boolean isCurrent() { return current; }
        
        @Override
        public String toString() {
            return String.format("%s (%s) - %s", name, provider, 
                freeTier ? "무료" : "유료");
        }
    }
    
    /**
     * AI 채팅 응답을 생성합니다.
     */
    public String generateResponse(Player player, String message, String modpackName, String modpackVersion) {
        try {
            JSONObject requestBody = new JSONObject();
            requestBody.put("player_uuid", player.getUniqueId().toString());
            requestBody.put("message", message);
            requestBody.put("modpack_name", modpackName);
            requestBody.put("modpack_version", modpackVersion);
            
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/chat"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(requestBody.toString()))
                    .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JSONObject jsonResponse = new JSONObject(response.body());
                if (jsonResponse.getBoolean("success")) {
                    return jsonResponse.getString("response");
                } else {
                    logger.warning("AI 응답 생성 실패: " + jsonResponse.optString("error", "Unknown error"));
                    return "죄송합니다. AI 서비스에 문제가 발생했습니다.";
                }
            } else {
                logger.warning("AI 응답 생성 실패: " + response.statusCode());
                return "죄송합니다. AI 서비스에 문제가 발생했습니다.";
            }
            
        } catch (IOException | InterruptedException e) {
            logger.severe("AI 응답 생성 중 오류: " + e.getMessage());
            return "죄송합니다. AI 서비스에 연결할 수 없습니다.";
        }
    }
    
    /**
     * 플레이어의 채팅 기록을 가져옵니다.
     */
    public String getChatHistory(String playerUuid) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/api/chat/history/" + playerUuid + "?limit=10"))
                    .header("Content-Type", "application/json")
                    .GET()
                    .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                return response.body();
            } else {
                logger.warning("채팅 기록 조회 실패: " + response.statusCode());
                return "{\"history\": []}";
            }
            
        } catch (IOException | InterruptedException e) {
            logger.severe("채팅 기록 조회 중 오류: " + e.getMessage());
            return "{\"history\": []}";
        }
    }
    
    /**
     * 채팅 메시지를 담는 클래스
     */
    public static class ChatMessage {
        private final String userMessage;
        private final String aiResponse;
        private final String timestamp;
        
        public ChatMessage(String userMessage, String aiResponse, String timestamp) {
            this.userMessage = userMessage;
            this.aiResponse = aiResponse;
            this.timestamp = timestamp;
        }
        
        public String getMessage() {
            return userMessage != null ? userMessage : aiResponse;
        }
        
        public boolean isUserMessage() {
            return userMessage != null;
        }
        
        public String getUserMessage() { return userMessage; }
        public String getAiResponse() { return aiResponse; }
        public String getTimestamp() { return timestamp; }
    }
} 