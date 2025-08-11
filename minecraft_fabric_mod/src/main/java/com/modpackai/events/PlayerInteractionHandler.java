package com.modpackai.events;

import com.modpackai.ModpackAIMod;
import com.modpackai.gui.AIChatScreen;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;
import net.fabricmc.fabric.api.event.player.UseItemCallback;
import net.minecraft.client.Minecraft;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.ItemStack;
import net.minecraft.network.chat.Component;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Fabric용 플레이어 상호작용 이벤트 핸들러
 * AI 아이템 사용 감지 및 처리
 */
public class PlayerInteractionHandler {
    private static final Logger LOGGER = LoggerFactory.getLogger(PlayerInteractionHandler.class);
    
    public static void register() {
        // 아이템 사용 이벤트 등록
        UseItemCallback.EVENT.register((player, world, hand) -> {
            ItemStack itemStack = player.getItemInHand(hand);
            
            // AI 아이템인지 확인
            if (isAIItem(itemStack)) {
                LOGGER.info("플레이어 {}가 AI 아이템 사용", player.getName().getString());
                
                if (world.isClientSide) {
                    // 클라이언트 측에서 GUI 열기
                    openAIGui();
                } else {
                    // 서버 측에서 안내 메시지 전송
                    player.sendSystemMessage(Component.literal("§6[ModpackAI] §fAI 채팅창이 열렸습니다!"));
                }
                
                return InteractionResult.SUCCESS;
            }
            
            return InteractionResult.PASS;
        });
        
        LOGGER.info("Fabric PlayerInteractionHandler 등록 완료");
    }
    
    /**
     * AI 아이템인지 확인
     */
    private static boolean isAIItem(ItemStack itemStack) {
        if (itemStack.isEmpty()) {
            return false;
        }
        
        // 설정된 AI 아이템 타입과 비교
        if (ModpackAIMod.getInstance() != null && ModpackAIMod.getInstance().getConfig() != null) {
            return itemStack.getItem() == ModpackAIMod.getInstance().getConfig().getAIItemMaterial();
        }
        
        return false;
    }
    
    /**
     * AI GUI 열기 (클라이언트 측)
     */
    @Environment(EnvType.CLIENT)
    private static void openAIGui() {
        Minecraft minecraft = Minecraft.getInstance();
        if (minecraft != null && minecraft.player != null) {
            minecraft.execute(() -> {
                minecraft.setScreen(new AIChatScreen());
            });
        }
    }
}