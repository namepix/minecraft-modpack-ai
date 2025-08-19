package com.modpackai.events;

import com.modpackai.ModpackAIMod;
import com.modpackai.gui.AIChatScreen;
import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.common.NeoForge;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * NeoForge 모드용 플레이어 상호작용 이벤트 핸들러
 * Bukkit PlayerInteractListener를 NeoForge 이벤트로 변환
 * 다중 Java 버전 지원 (어노테이션 대신 수동 등록)
 */
public class PlayerInteractionHandler {
    
    /**
     * 이벤트 핸들러 등록 (수동)
     */
    public static void register() {
        NeoForge.EVENT_BUS.register(PlayerInteractionHandler.class);
    }
    private static final Logger LOGGER = LoggerFactory.getLogger(PlayerInteractionHandler.class);
    
    /**
     * 플레이어가 아이템을 우클릭했을 때 처리
     * Bukkit의 PlayerInteractEvent.Action.RIGHT_CLICK_AIR/BLOCK과 유사
     */
    @SubscribeEvent
    public static void onPlayerRightClickItem(PlayerInteractEvent.RightClickItem event) {
        Player player = event.getEntity();
        ItemStack itemStack = event.getItemStack();
        InteractionHand hand = event.getHand();
        
        // 메인 핸드에서만 처리 (중복 방지)
        if (hand != InteractionHand.MAIN_HAND) {
            return;
        }
        
        // AI 아이템인지 확인
        if (isAIItem(itemStack)) {
            LOGGER.info("플레이어 {}가 AI 아이템 사용", player.getName().getString());
            
            if (player.level().isClientSide) {
                // 클라이언트 측: AI 채팅 GUI 열기
                handleClientSideAIItemUse(player, itemStack);
            } else {
                // 서버 측: 메시지 전송
                handleServerSideAIItemUse((ServerPlayer) player, itemStack);
            }
            
            event.setCancellationResult(InteractionResult.SUCCESS);
            event.setCanceled(true);
        }
    }
    
    /**
     * 플레이어가 블록을 우클릭했을 때 처리
     */
    @SubscribeEvent
    public static void onPlayerRightClickBlock(PlayerInteractEvent.RightClickBlock event) {
        Player player = event.getEntity();
        ItemStack itemStack = event.getItemStack();
        InteractionHand hand = event.getHand();
        
        // 메인 핸드에서만 처리
        if (hand != InteractionHand.MAIN_HAND) {
            return;
        }
        
        // AI 아이템으로 블록을 우클릭한 경우도 GUI 열기
        if (isAIItem(itemStack)) {
            LOGGER.info("플레이어 {}가 블록에 대해 AI 아이템 사용", player.getName().getString());
            
            if (player.level().isClientSide) {
                // 클라이언트 측: AI 채팅 GUI 열기
                handleClientSideAIItemUse(player, itemStack);
            } else {
                // 서버 측: 메시지 전송
                handleServerSideAIItemUse((ServerPlayer) player, itemStack);
            }
            
            event.setCancellationResult(InteractionResult.SUCCESS);
            event.setCanceled(true);
        }
    }
    
    /**
     * 아이템이 AI 아이템인지 확인 (다중 Java 버전 지원)
     */
    private static boolean isAIItem(ItemStack itemStack) {
        if (itemStack.isEmpty()) {
            return false;
        }
        
        try {
            // AI 아이템 타입 확인
            if (itemStack.getItem() != ModpackAIMod.getInstance().getConfig().getAIItemMaterial()) {
                return false;
            }
            
            // 아이템 이름 확인 (버전 호환성)
            Component displayName = itemStack.getHoverName();
            String expectedName = ModpackAIMod.getInstance().getConfig().getAIItemName();
            
            if (displayName != null) {
                String actualName = displayName.getString();
                // 색깔 코드 제거해서 비교
                String cleanActualName = actualName.replaceAll("§[0-9a-fA-F]", "");
                String cleanExpectedName = expectedName.replaceAll("§[0-9a-fA-F]", "");
                
                return cleanActualName.contains("모드팩 AI") || cleanExpectedName.equals(cleanActualName);
            }
            
        } catch (Exception e) {
            LOGGER.warn("AI 아이템 확인 중 오류 (버전 호환성): {}", e.getMessage());
        }
        
        return false;
    }
    
    /**
     * 클라이언트 측 AI 아이템 사용 처리
     */
    @OnlyIn(Dist.CLIENT)
    private static void handleClientSideAIItemUse(Player player, ItemStack itemStack) {
        // AI 채팅 GUI 열기
        Minecraft.getInstance().execute(() -> {
            try {
                AIChatScreen aiChatScreen = new AIChatScreen();
                Minecraft.getInstance().setScreen(aiChatScreen);
                LOGGER.info("AI 채팅 GUI 열기 완료");
            } catch (Exception e) {
                LOGGER.error("AI 채팅 GUI 열기 실패", e);
                player.sendSystemMessage(Component.literal("§c[ModpackAI] GUI를 열 수 없습니다: " + e.getMessage()));
            }
        });
    }
    
    /**
     * 서버 측 AI 아이템 사용 처리
     */
    private static void handleServerSideAIItemUse(ServerPlayer player, ItemStack itemStack) {
        // 서버에서는 GUI를 직접 열 수 없으므로 메시지로 안내
        player.sendSystemMessage(Component.literal("§6[ModpackAI] AI 아이템을 사용했습니다!"));
        player.sendSystemMessage(Component.literal("§7/ai <질문> 명령어로 AI에게 질문하거나"));
        player.sendSystemMessage(Component.literal("§7클라이언트에서 우클릭하면 채팅 GUI가 열립니다."));
    }
    
    /**
     * 플레이어가 공중을 우클릭했을 때 처리
     */
    @SubscribeEvent
    public static void onPlayerRightClickEmpty(PlayerInteractEvent.RightClickEmpty event) {
        Player player = event.getEntity();
        ItemStack itemStack = player.getItemInHand(event.getHand());
        
        // 메인 핸드에서만 처리
        if (event.getHand() != InteractionHand.MAIN_HAND) {
            return;
        }
        
        // AI 아이템인지 확인
        if (isAIItem(itemStack)) {
            LOGGER.info("플레이어 {}가 공중에서 AI 아이템 사용", player.getName().getString());
            
            // 클라이언트에서만 GUI 열기
            if (player.level().isClientSide) {
                handleClientSideAIItemUse(player, itemStack);
            }
        }
    }
}