package com.modpackai.managers;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.concurrent.CompletableFuture;

/**
 * Fabric 모드용 AI 매니저
 * HTTP 통신을 통해 Flask 백엔드와 연동
 */
public class ModpackAIManager {
    private static final Logger LOGGER = LoggerFactory.getLogger(ModpackAIManager.class);
    
    private final ModpackAIConfig config;
    private final HttpClient httpClient;
    private final Gson gson;
    
    public ModpackAIManager(ModpackAIConfig config) {
        this.config = config;
        this.httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();
        this.gson = new Gson();
        
        LOGGER.info("AI 매니저 초기화 완료 (Fabric) - Backend: {}", config.getBackendUrl());
    }
    
    /**
     * AI에게 질문하고 응답 받기 (비동기)
     */
    public CompletableFuture<String> askAIAsync(String playerUuid, String message, String modpackName) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return askAI(playerUuid, message, modpackName);
            } catch (Exception e) {
                LOGGER.error("비동기 AI 질문 처리 실패", e);
                return "AI 응답 처리 중 오류가 발생했습니다.";
            }
        });
    }
    
    /**
     * AI에게 질문하고 응답 받기 (동기)
     */
    public String askAI(String playerUuid, String message, String modpackName) throws Exception {
        LOGGER.info("AI 질문 처리: Player={}, Message={}", playerUuid, message.substring(0, Math.min(50, message.length())));
        
        // 요청 데이터 구성
        JsonObject requestData = new JsonObject();
        requestData.addProperty("message", message);
        requestData.addProperty("player_uuid", playerUuid);
        requestData.addProperty("modpack_name", modpackName != null ? modpackName : "Unknown");
        requestData.addProperty("modpack_version", "1.0.0");
        
        // HTTP 요청 생성
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(config.getBackendUrl() + "/chat"))
                .header("Content-Type", "application/json")
                .timeout(Duration.ofSeconds(config.getRequestTimeout() / 1000))
                .POST(HttpRequest.BodyPublishers.ofString(requestData.toString()))
                .build();
        
        try {
            // HTTP 요청 전송
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                // 성공 응답 처리
                JsonObject responseData = gson.fromJson(response.body(), JsonObject.class);
                if (responseData.has("success") && responseData.get("success").getAsBoolean()) {
                    String aiResponse = responseData.get("response").getAsString();
                    LOGGER.info("AI 응답 성공: {}", aiResponse.substring(0, Math.min(100, aiResponse.length())));
                    return aiResponse;
                } else {
                    String error = responseData.has("error") ? responseData.get("error").getAsString() : "알 수 없는 오류";
                    LOGGER.error("AI 응답 실패: {}", error);
                    return "AI 응답 처리 중 오류가 발생했습니다: " + error;
                }
            } else {
                LOGGER.error("HTTP 요청 실패: {} - {}", response.statusCode(), response.body());
                return "백엔드 서버 연결 실패 (HTTP " + response.statusCode() + ")";
            }
            
        } catch (IOException e) {
            LOGGER.error("네트워크 연결 실패", e);
            return "백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.";
        } catch (Exception e) {
            LOGGER.error("AI 요청 처리 실패", e);
            return "AI 요청 처리 중 예상치 못한 오류가 발생했습니다.";
        }
    }
    
    /**
     * 레시피 조회 (비동기)
     */
    public CompletableFuture<JsonObject> getRecipeAsync(String itemName) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return getRecipe(itemName);
            } catch (Exception e) {
                LOGGER.error("비동기 레시피 조회 실패", e);
                JsonObject errorResponse = new JsonObject();
                errorResponse.addProperty("success", false);
                errorResponse.addProperty("error", "레시피 조회 중 오류가 발생했습니다.");
                return errorResponse;
            }
        });
    }
    
    /**
     * 레시피 조회 (동기)
     */
    public JsonObject getRecipe(String itemName) throws Exception {
        LOGGER.info("레시피 조회: {}", itemName);
        
        // HTTP 요청 생성
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(config.getBackendUrl() + "/recipe/" + itemName))
                .header("Accept", "application/json")
                .timeout(Duration.ofSeconds(config.getRequestTimeout() / 1000))
                .GET()
                .build();
        
        try {
            // HTTP 요청 전송
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JsonObject responseData = gson.fromJson(response.body(), JsonObject.class);
                LOGGER.info("레시피 조회 성공: {}", itemName);
                return responseData;
            } else {
                LOGGER.error("레시피 조회 실패: {} - {}", response.statusCode(), response.body());
                JsonObject errorResponse = new JsonObject();
                errorResponse.addProperty("success", false);
                errorResponse.addProperty("error", "레시피를 찾을 수 없습니다.");
                return errorResponse;
            }
            
        } catch (Exception e) {
            LOGGER.error("레시피 조회 중 오류 발생", e);
            throw e;
        }
    }
    
    /**
     * 사용 가능한 AI 모델 목록 조회 (비동기)
     */
    public CompletableFuture<JsonObject> getAvailableModelsAsync() {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return getAvailableModels();
            } catch (Exception e) {
                LOGGER.error("모델 목록 조회 실패", e);
                JsonObject errorResponse = new JsonObject();
                errorResponse.addProperty("success", false);
                errorResponse.addProperty("error", "모델 목록을 가져올 수 없습니다.");
                return errorResponse;
            }
        });
    }
    
    /**
     * 사용 가능한 AI 모델 목록 조회 (동기)
     */
    public JsonObject getAvailableModels() throws Exception {
        LOGGER.info("AI 모델 목록 조회");
        
        // HTTP 요청 생성
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(config.getBackendUrl() + "/models"))
                .header("Accept", "application/json")
                .timeout(Duration.ofSeconds(config.getRequestTimeout() / 1000))
                .GET()
                .build();
        
        try {
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JsonObject responseData = gson.fromJson(response.body(), JsonObject.class);
                LOGGER.info("모델 목록 조회 성공");
                return responseData;
            } else {
                LOGGER.error("모델 목록 조회 실패: {}", response.statusCode());
                JsonObject errorResponse = new JsonObject();
                errorResponse.addProperty("success", false);
                errorResponse.addProperty("error", "모델 목록을 가져올 수 없습니다.");
                return errorResponse;
            }
            
        } catch (Exception e) {
            LOGGER.error("모델 목록 조회 중 오류 발생", e);
            throw e;
        }
    }
    
    /**
     * RAG 시스템 상태 확인 (비동기)
     */
    public CompletableFuture<JsonObject> getRAGStatusAsync() {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return getRAGStatus();
            } catch (Exception e) {
                LOGGER.error("비동기 RAG 상태 확인 실패", e);
                JsonObject errorResponse = new JsonObject();
                errorResponse.addProperty("success", false);
                errorResponse.addProperty("error", "RAG 상태 확인 중 오류가 발생했습니다.");
                return errorResponse;
            }
        });
    }
    
    /**
     * RAG 시스템 상태 확인 (동기)
     */
    public JsonObject getRAGStatus() throws Exception {
        LOGGER.info("RAG 시스템 상태 확인");
        
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(config.getBackendUrl() + "/gcp-rag/status"))
                .header("Accept", "application/json")
                .timeout(Duration.ofSeconds(10))
                .GET()
                .build();
        
        try {
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JsonObject responseData = gson.fromJson(response.body(), JsonObject.class);
                LOGGER.info("RAG 상태 확인 성공");
                return responseData;
            } else {
                LOGGER.error("RAG 상태 확인 실패: {}", response.statusCode());
                JsonObject errorResponse = new JsonObject();
                errorResponse.addProperty("success", false);
                errorResponse.addProperty("error", "RAG 상태를 확인할 수 없습니다.");
                return errorResponse;
            }
            
        } catch (Exception e) {
            LOGGER.error("RAG 상태 확인 중 오류 발생", e);
            throw e;
        }
    }
    
    /**
     * RAG 인덱스 구축 (비동기)
     */
    public CompletableFuture<JsonObject> buildRAGIndexAsync(String modpackName, String modpackVersion, String modpackPath) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return buildRAGIndex(modpackName, modpackVersion, modpackPath);
            } catch (Exception e) {
                LOGGER.error("비동기 RAG 인덱스 구축 실패", e);
                JsonObject errorResponse = new JsonObject();
                errorResponse.addProperty("success", false);
                errorResponse.addProperty("error", "RAG 인덱스 구축 중 오류가 발생했습니다.");
                return errorResponse;
            }
        });
    }
    
    /**
     * RAG 인덱스 구축 (동기)
     */
    public JsonObject buildRAGIndex(String modpackName, String modpackVersion, String modpackPath) throws Exception {
        LOGGER.info("RAG 인덱스 구축: {} v{} at {}", modpackName, modpackVersion, modpackPath);
        
        JsonObject requestData = new JsonObject();
        requestData.addProperty("modpack_name", modpackName);
        requestData.addProperty("modpack_version", modpackVersion);
        requestData.addProperty("modpack_path", modpackPath);
        
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(config.getBackendUrl() + "/gcp-rag/build"))
                .header("Content-Type", "application/json")
                .timeout(Duration.ofSeconds(600))  // 10분 타임아웃
                .POST(HttpRequest.BodyPublishers.ofString(requestData.toString()))
                .build();
        
        try {
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JsonObject responseData = gson.fromJson(response.body(), JsonObject.class);
                LOGGER.info("RAG 인덱스 구축 완료");
                return responseData;
            } else {
                LOGGER.error("RAG 인덱스 구축 실패: {} - {}", response.statusCode(), response.body());
                JsonObject errorResponse = new JsonObject();
                errorResponse.addProperty("success", false);
                errorResponse.addProperty("error", "RAG 인덱스를 구축할 수 없습니다.");
                return errorResponse;
            }
            
        } catch (Exception e) {
            LOGGER.error("RAG 인덱스 구축 중 오류 발생", e);
            throw e;
        }
    }
    
    /**
     * RAG 모드팩 목록 조회 (비동기)
     */
    public CompletableFuture<JsonObject> getRAGModpacksAsync() {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return getRAGModpacks();
            } catch (Exception e) {
                LOGGER.error("비동기 RAG 모드팩 목록 조회 실패", e);
                JsonObject errorResponse = new JsonObject();
                errorResponse.addProperty("success", false);
                errorResponse.addProperty("error", "RAG 모드팩 목록을 가져올 수 없습니다.");
                return errorResponse;
            }
        });
    }
    
    /**
     * RAG 모드팩 목록 조회 (동기)
     */
    public JsonObject getRAGModpacks() throws Exception {
        LOGGER.info("RAG 모드팩 목록 조회");
        
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(config.getBackendUrl() + "/gcp-rag/modpacks"))
                .header("Accept", "application/json")
                .timeout(Duration.ofSeconds(10))
                .GET()
                .build();
        
        try {
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JsonObject responseData = gson.fromJson(response.body(), JsonObject.class);
                LOGGER.info("RAG 모드팩 목록 조회 성공");
                return responseData;
            } else {
                LOGGER.error("RAG 모드팩 목록 조회 실패: {}", response.statusCode());
                JsonObject errorResponse = new JsonObject();
                errorResponse.addProperty("success", false);
                errorResponse.addProperty("error", "RAG 모드팩 목록을 가져올 수 없습니다.");
                return errorResponse;
            }
            
        } catch (Exception e) {
            LOGGER.error("RAG 모드팩 목록 조회 중 오류 발생", e);
            throw e;
        }
    }
    
    /**
     * RAG 검색 테스트 (비동기)
     */
    public CompletableFuture<JsonObject> testRAGSearchAsync(String query, String modpackName, String modpackVersion) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                return testRAGSearch(query, modpackName, modpackVersion);
            } catch (Exception e) {
                LOGGER.error("비동기 RAG 검색 테스트 실패", e);
                JsonObject errorResponse = new JsonObject();
                errorResponse.addProperty("success", false);
                errorResponse.addProperty("error", "RAG 검색 테스트 중 오류가 발생했습니다.");
                return errorResponse;
            }
        });
    }
    
    /**
     * RAG 검색 테스트 (동기)
     */
    public JsonObject testRAGSearch(String query, String modpackName, String modpackVersion) throws Exception {
        LOGGER.info("RAG 검색 테스트: query={}, modpack={}:{}", query, modpackName, modpackVersion);
        
        JsonObject requestData = new JsonObject();
        requestData.addProperty("query", query);
        requestData.addProperty("modpack_name", modpackName);
        requestData.addProperty("modpack_version", modpackVersion);
        requestData.addProperty("top_k", 5);
        requestData.addProperty("min_score", 0.6);
        
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(config.getBackendUrl() + "/gcp-rag/search"))
                .header("Content-Type", "application/json")
                .timeout(Duration.ofSeconds(30))
                .POST(HttpRequest.BodyPublishers.ofString(requestData.toString()))
                .build();
        
        try {
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                JsonObject responseData = gson.fromJson(response.body(), JsonObject.class);
                LOGGER.info("RAG 검색 테스트 성공");
                return responseData;
            } else {
                LOGGER.error("RAG 검색 테스트 실패: {} - {}", response.statusCode(), response.body());
                JsonObject errorResponse = new JsonObject();
                errorResponse.addProperty("success", false);
                errorResponse.addProperty("error", "RAG 검색 테스트를 수행할 수 없습니다.");
                return errorResponse;
            }
            
        } catch (Exception e) {
            LOGGER.error("RAG 검색 테스트 중 오류 발생", e);
            throw e;
        }
    }

    /**
     * 백엔드 서버 상태 확인
     */
    public boolean isBackendHealthy() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(config.getBackendUrl() + "/health"))
                    .timeout(Duration.ofSeconds(5))
                    .GET()
                    .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            boolean healthy = response.statusCode() == 200;
            
            if (healthy) {
                LOGGER.debug("백엔드 서버 상태 양호");
            } else {
                LOGGER.warn("백엔드 서버 상태 불량: HTTP {}", response.statusCode());
            }
            
            return healthy;
        } catch (Exception e) {
            LOGGER.warn("백엔드 서버 상태 확인 실패", e);
            return false;
        }
    }
}