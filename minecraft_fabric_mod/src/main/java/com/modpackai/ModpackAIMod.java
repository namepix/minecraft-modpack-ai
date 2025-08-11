package com.modpackai;

import com.modpackai.managers.ModpackAIConfig;
import com.modpackai.managers.ModpackAIManager;
import com.modpackai.commands.ModpackAICommands;
import net.fabricmc.api.ModInitializer;
import net.fabricmc.fabric.api.command.v2.CommandRegistrationCallback;
import net.fabricmc.fabric.api.event.lifecycle.v1.ServerLifecycleEvents;
import net.minecraft.server.MinecraftServer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ModpackAIMod implements ModInitializer {
    public static final String MOD_ID = "modpackai";
    public static final Logger LOGGER = LoggerFactory.getLogger(ModpackAIMod.class);
    
    private static ModpackAIMod instance;
    private ModpackAIConfig config;
    private ModpackAIManager aiManager;
    private MinecraftServer server;
    
    @Override
    public void onInitialize() {
        instance = this;
        LOGGER.info("ModpackAI Fabric 모드 초기화 시작");
        
        // 설정 초기화
        commonSetup();
        
        // 명령어 등록
        CommandRegistrationCallback.EVENT.register((dispatcher, registryAccess, environment) -> {
            LOGGER.info("ModpackAI 명령어 등록");
            ModpackAICommands.register(dispatcher);
        });
        
        // 서버 시작/정지 이벤트 등록
        ServerLifecycleEvents.SERVER_STARTING.register(this::onServerStarting);
        ServerLifecycleEvents.SERVER_STOPPING.register(this::onServerStopping);
        
        LOGGER.info("ModpackAI Fabric 모드 초기화 완료");
    }
    
    private void commonSetup() {
        LOGGER.info("ModpackAI 공통 설정 시작");
        
        // 설정 로드
        config = new ModpackAIConfig();
        config.loadConfig();
        
        // AI 매니저 초기화
        aiManager = new ModpackAIManager(config);
        
        LOGGER.info("ModpackAI 공통 설정 완료");
    }
    
    private void onServerStarting(MinecraftServer server) {
        this.server = server;
        LOGGER.info("ModpackAI 서버 시작됨");
    }
    
    private void onServerStopping(MinecraftServer server) {
        LOGGER.info("ModpackAI 서버 정지됨");
        this.server = null;
    }
    
    // Getter 메소드들
    public static ModpackAIMod getInstance() {
        return instance;
    }
    
    public ModpackAIConfig getConfig() {
        return config;
    }
    
    public ModpackAIManager getAIManager() {
        return aiManager;
    }
    
    public MinecraftServer getServer() {
        return server;
    }
    
    // 플러그인 호환성을 위한 유틸리티 메소드
    public void sendMessageToPlayer(String playerName, String message) {
        // 플레이어에게 메시지 전송 (Fabric 방식)
        LOGGER.info("플레이어 {}에게 메시지 전송: {}", playerName, message);
    }
    
    public boolean isServerSide() {
        // 서버 사이드 여부 확인
        return server != null;
    }
}