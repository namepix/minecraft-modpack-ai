package com.modpackai.managers;

import com.modpackai.ModpackAIPlugin;
import org.json.JSONObject;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.logging.Logger;

public class RecipeManager {
    private final ModpackAIPlugin plugin;
    private final ConfigManager configManager;
    private final Logger logger;
    private final HttpClient httpClient;
    private final String baseUrl;
    
    public RecipeManager(ModpackAIPlugin plugin) {
        this.plugin = plugin;
        this.configManager = plugin.getConfigManager();
        this.logger = plugin.getLogger();
        this.httpClient = HttpClient.newHttpClient();
        this.baseUrl = configManager.getBackendUrl();
    }
    
    /**
     * 아이템의 제작법을 가져옵니다.
     */
    public String getRecipe(String itemName) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/api/recipe/" + encodeUrl(itemName)))
                    .header("Content-Type", "application/json")
                    .GET()
                    .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                return response.body();
            } else {
                logger.warning("제작법 조회 실패: " + response.statusCode() + " - " + itemName);
                return createErrorResponse("제작법을 찾을 수 없습니다: " + itemName);
            }
            
        } catch (IOException | InterruptedException e) {
            logger.severe("제작법 조회 중 오류: " + e.getMessage());
            return createErrorResponse("제작법 조회 중 오류가 발생했습니다: " + e.getMessage());
        }
    }
    
    /**
     * 모드팩의 제작법 통계를 가져옵니다.
     */
    public String getModpackStats(String modpackName) {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create(baseUrl + "/api/modpack/stats/" + encodeUrl(modpackName)))
                    .header("Content-Type", "application/json")
                    .GET()
                    .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                return response.body();
            } else {
                logger.warning("모드팩 통계 조회 실패: " + response.statusCode());
                return createErrorResponse("모드팩 통계를 가져올 수 없습니다.");
            }
            
        } catch (IOException | InterruptedException e) {
            logger.severe("모드팩 통계 조회 중 오류: " + e.getMessage());
            return createErrorResponse("모드팩 통계 조회 중 오류가 발생했습니다.");
        }
    }
    
    /**
     * URL 인코딩을 수행합니다.
     */
    private String encodeUrl(String text) {
        try {
            return java.net.URLEncoder.encode(text, "UTF-8");
        } catch (Exception e) {
            return text;
        }
    }
    
    /**
     * 오류 응답을 생성합니다.
     */
    private String createErrorResponse(String errorMessage) {
        JSONObject error = new JSONObject();
        error.put("error", errorMessage);
        return error.toString();
    }
} 