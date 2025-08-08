package com.modpackai;

import com.modpackai.managers.ModpackAIConfig;
import com.modpackai.managers.ModpackAIManager;
import com.modpackai.commands.ModpackAICommands;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLClientSetupEvent;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.client.event.RegisterKeyMappingsEvent;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Mod(ModpackAIMod.MOD_ID)
public class ModpackAIMod {
    public static final String MOD_ID = "modpackai";
    public static final Logger LOGGER = LoggerFactory.getLogger(ModpackAIMod.class);
    
    private static ModpackAIMod instance;
    private ModpackAIConfig config;
    private ModpackAIManager aiManager;
    
    public ModpackAIMod(IEventBus modEventBus, ModContainer modContainer) {
        instance = this;
        LOGGER.info("ModpackAI 모드 초기화 시작");
        
        // 이벤트 등록
        modEventBus.addListener(this::commonSetup);
        modEventBus.addListener(this::clientSetup);
        modEventBus.addListener(this::registerKeyMappings);
        
        // NeoForge 이벤트 버스에 등록
        NeoForge.EVENT_BUS.register(this);
        NeoForge.EVENT_BUS.addListener(this::registerCommands);
        
        LOGGER.info("ModpackAI 모드 초기화 완료");
    }
    
    private void commonSetup(final FMLCommonSetupEvent event) {
        LOGGER.info("ModpackAI 공통 설정 시작");
        
        // 설정 로드
        config = new ModpackAIConfig();
        config.loadConfig();
        
        // AI 매니저 초기화
        aiManager = new ModpackAIManager(config);
        
        LOGGER.info("ModpackAI 공통 설정 완료");
    }
    
    private void clientSetup(final FMLClientSetupEvent event) {
        LOGGER.info("ModpackAI 클라이언트 설정 시작");
        // 클라이언트별 초기화 로직
        LOGGER.info("ModpackAI 클라이언트 설정 완료");
    }
    
    private void registerKeyMappings(RegisterKeyMappingsEvent event) {
        // 키 바인딩 등록 (AI GUI 열기용)
        LOGGER.info("ModpackAI 키 매핑 등록");
    }
    
    @SubscribeEvent
    public void registerCommands(RegisterCommandsEvent event) {
        LOGGER.info("ModpackAI 명령어 등록");
        ModpackAICommands.register(event.getDispatcher());
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
    
    // 플러그인 호환성을 위한 유틸리티 메소드
    public void sendMessageToPlayer(String playerName, String message) {
        // 플레이어에게 메시지 전송 (NeoForge 방식)
        LOGGER.info("플레이어 {}에게 메시지 전송: {}", playerName, message);
    }
    
    public boolean isServerSide() {
        // 서버 사이드 여부 확인
        return true; // TODO: 실제 구현
    }
}