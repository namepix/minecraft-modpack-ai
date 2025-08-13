package com.modpackai.client;

import com.modpackai.events.PlayerInteractionHandler;
import com.modpackai.gui.AIChatScreen;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.fabricmc.fabric.api.client.event.lifecycle.v1.ClientTickEvents;
import net.fabricmc.fabric.api.client.keybinding.v1.KeyBindingHelper;
import net.minecraft.client.option.KeyBinding;
import net.minecraft.client.MinecraftClient;
import org.lwjgl.glfw.GLFW;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Environment(EnvType.CLIENT)
public class ModpackAIClientMod implements ClientModInitializer {
    private static final Logger LOGGER = LoggerFactory.getLogger(ModpackAIClientMod.class);
    
    private static KeyBinding aiGuiKey;
    
    @Override
    public void onInitializeClient() {
        LOGGER.info("ModpackAI 클라이언트 초기화 시작");
        
        // 키 바인딩 등록
        aiGuiKey = KeyBindingHelper.registerKeyBinding(new KeyBinding(
                "key.modpackai.open_gui",
                GLFW.GLFW_KEY_G,
                "category.modpackai.general"
        ));
        
        // 플레이어 상호작용 핸들러 등록
        PlayerInteractionHandler.register();
        
        // 클라이언트 틱 이벤트 등록
        ClientTickEvents.END_CLIENT_TICK.register(this::onClientTick);
        
        LOGGER.info("ModpackAI 클라이언트 초기화 완료");
    }
    
    private void onClientTick(MinecraftClient client) {
        // AI GUI 키 처리
        while (aiGuiKey.wasPressed()) {
            // AI 채팅 스크린 열기
            if (client.player != null) {
                LOGGER.info("AI 채팅 GUI 열기 요청");
                client.setScreen(new AIChatScreen());
            }
        }
    }
    
    public static KeyBinding getAiGuiKey() {
        return aiGuiKey;
    }
}