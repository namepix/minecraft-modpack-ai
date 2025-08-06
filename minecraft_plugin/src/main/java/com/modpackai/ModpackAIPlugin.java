package com.modpackai;

import com.modpackai.commands.ModpackAICommand;
import com.modpackai.commands.AICommand;
import com.modpackai.gui.AIChatGUI;
import com.modpackai.gui.ModelSelectionGUI;
import com.modpackai.gui.RecipeGUI;
import com.modpackai.listeners.InventoryListener;
import com.modpackai.listeners.PlayerInteractListener;
import com.modpackai.managers.AIManager;
import com.modpackai.managers.ConfigManager;
import com.modpackai.managers.RecipeManager;
import org.bukkit.plugin.java.JavaPlugin;

public class ModpackAIPlugin extends JavaPlugin {
    
    private static ModpackAIPlugin instance;
    private ConfigManager configManager;
    private AIManager aiManager;
    private RecipeManager recipeManager;
    private AIChatGUI aiChatGUI;
    private RecipeGUI recipeGUI;
    
    @Override
    public void onEnable() {
        // 플러그인 초기화
        initializeManagers();
        
        // 명령어 등록
        getCommand("modpackai").setExecutor(new ModpackAICommand(this));
        getCommand("ai").setExecutor(new AICommand(this));
        
        // 이벤트 리스너 등록
        getServer().getPluginManager().registerEvents(new PlayerInteractListener(this), this);
        getServer().getPluginManager().registerEvents(new InventoryListener(this), this);
        
        getLogger().info("ModpackAI 플러그인이 활성화되었습니다!");
    }
    
    @Override
    public void onDisable() {
        getLogger().info("모드팩 AI 플러그인이 비활성화되었습니다.");
    }
    
    public static ModpackAIPlugin getInstance() {
        return instance;
    }
    
    public ConfigManager getConfigManager() {
        return configManager;
    }
    
    public AIManager getAIManager() {
        return aiManager;
    }
    
    public RecipeManager getRecipeManager() {
        return recipeManager;
    }
    
    public AIChatGUI getAIChatGUI() {
        return aiChatGUI;
    }
    
    public RecipeGUI getRecipeGUI() {
        return recipeGUI;
    }
    
    public ModelSelectionGUI getModelSelectionGUI() {
        return new ModelSelectionGUI(this);
    }

    private void initializeManagers() {
        instance = this;
        
        // 설정 매니저 초기화
        configManager = new ConfigManager(this);
        configManager.loadConfig();
        
        // AI 매니저 초기화
        aiManager = new AIManager(this, configManager);
        
        // 제작법 매니저 초기화
        recipeManager = new RecipeManager(this);
        
        // GUI 초기화
        aiChatGUI = new AIChatGUI(this);
        recipeGUI = new RecipeGUI(this);
        
        getLogger().info("매니저 초기화 완료");
    }
} 