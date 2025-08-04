package com.modpackai.managers;

import com.modpackai.ModpackAIPlugin;
import org.bukkit.Material;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.FileConfiguration;

import java.util.List;

public class ConfigManager {
    
    private final ModpackAIPlugin plugin;
    private FileConfiguration config;
    
    public ConfigManager(ModpackAIPlugin plugin) {
        this.plugin = plugin;
    }
    
    public void loadConfig() {
        plugin.saveDefaultConfig();
        plugin.reloadConfig();
        config = plugin.getConfig();
    }
    
    // AI 서버 설정
    public String getBackendUrl() {
        return config.getString("ai.server_url", "http://localhost:5000");
    }
    
    public String getAIServerUrl() {
        return config.getString("ai.server_url", "http://localhost:5000");
    }
    
    public String getModpackName() {
        return config.getString("ai.modpack_name", "unknown");
    }
    
    public String getModpackVersion() {
        return config.getString("ai.modpack_version", "1.0");
    }
    
    public String getAIAssistantItem() {
        return config.getString("ai_item.material", "BOOK");
    }
    
    // AI 아이템 설정
    public Material getAIItemMaterial() {
        String materialName = config.getString("ai_item.material", "BOOK");
        try {
            return Material.valueOf(materialName.toUpperCase());
        } catch (IllegalArgumentException e) {
            plugin.getLogger().warning("잘못된 아이템 재료: " + materialName + ", BOOK으로 대체합니다.");
            return Material.BOOK;
        }
    }
    
    public String getAIItemName() {
        return config.getString("ai_item.name", "§6§l모드팩 AI 어시스턴트");
    }
    
    public List<String> getAIItemLore() {
        return config.getStringList("ai_item.lore");
    }
    
    // GUI 설정
    public String getChatGUITitle() {
        return config.getString("gui.chat_title", "§6§l모드팩 AI 어시스턴트");
    }
    
    public int getChatGUISize() {
        return config.getInt("gui.chat_size", 54);
    }
    
    public String getRecipeGUITitle() {
        return config.getString("gui.recipe_title", "§6§l제작법");
    }
    
    public int getRecipeGUISize() {
        return config.getInt("gui.recipe_size", 27);
    }
    
    // 메시지 설정
    public String getMessage(String key) {
        return config.getString("messages." + key, "메시지를 찾을 수 없습니다: " + key);
    }
    
    // 권한 설정
    public boolean isPermissionRequired() {
        return config.getBoolean("permissions.require_permission", false);
    }
    
    public String getPermissionNode() {
        return config.getString("permissions.node", "modpackai.use");
    }
    
    // 디버그 설정
    public boolean isDebugEnabled() {
        return config.getBoolean("debug.enabled", false);
    }
    
    // 기본 설정값 설정
    public void setDefaults() {
        config.addDefault("ai.server_url", "http://localhost:5000");
        config.addDefault("ai.modpack_name", "unknown");
        
        config.addDefault("ai_item.material", "BOOK");
        config.addDefault("ai_item.name", "§6§l모드팩 AI 어시스턴트");
        config.addDefault("ai_item.lore", List.of(
            "§7우클릭하여 AI와 대화하세요",
            "§7모드팩 관련 질문에 답변해드립니다",
            "",
            "§e§l사용법:",
            "§f- 우클릭: AI 채팅창 열기",
            "§f- 제작법 질문 시 자동으로 표시"
        ));
        
        config.addDefault("gui.chat_title", "§6§l모드팩 AI 어시스턴트");
        config.addDefault("gui.chat_size", 54);
        config.addDefault("gui.recipe_title", "§6§l제작법");
        config.addDefault("gui.recipe_size", 27);
        
        config.addDefault("messages.no_permission", "§c이 기능을 사용할 권한이 없습니다.");
        config.addDefault("messages.ai_error", "§cAI 서버와 통신 중 오류가 발생했습니다.");
        config.addDefault("messages.recipe_not_found", "§c제작법을 찾을 수 없습니다.");
        config.addDefault("messages.item_given", "§aAI 어시스턴트 아이템을 받았습니다!");
        
        config.addDefault("permissions.require_permission", false);
        config.addDefault("permissions.node", "modpackai.use");
        
        config.addDefault("debug.enabled", false);
        
        config.options().copyDefaults(true);
        plugin.saveConfig();
    }
} 