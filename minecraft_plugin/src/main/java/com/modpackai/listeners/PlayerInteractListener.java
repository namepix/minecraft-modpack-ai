package com.modpackai.listeners;

import com.modpackai.ModpackAIPlugin;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.inventory.ItemStack;

public class PlayerInteractListener implements Listener {
    
    private final ModpackAIPlugin plugin;
    
    public PlayerInteractListener(ModpackAIPlugin plugin) {
        this.plugin = plugin;
    }
    
    @EventHandler
    public void onPlayerInteract(PlayerInteractEvent event) {
        Player player = event.getPlayer();
        ItemStack item = event.getItem();
        
        // 아이템이 없거나 우클릭이 아니면 무시
        if (item == null || event.getAction() != Action.RIGHT_CLICK_AIR && event.getAction() != Action.RIGHT_CLICK_BLOCK) {
            return;
        }
        
        // AI 어시스턴트 아이템인지 확인
        if (isAIAssistantItem(item)) {
            event.setCancelled(true); // 기본 동작 취소
            
            // GUI 열기
            plugin.getAIChatGUI().openChatGUI(player);
            
            // 사용자에게 알림
            player.sendMessage("§a§l모드팩 AI 어시스턴트가 열렸습니다!");
        }
    }
    
    private boolean isAIAssistantItem(ItemStack item) {
        if (item == null || !item.hasItemMeta()) {
            return false;
        }
        
        // 설정에서 AI 어시스턴트 아이템 타입 가져오기
        String configuredItem = plugin.getConfigManager().getAIAssistantItem();
        
        // 기본값: BOOK
        Material targetMaterial = Material.BOOK;
        try {
            targetMaterial = Material.valueOf(configuredItem.toUpperCase());
        } catch (IllegalArgumentException e) {
            // 설정된 아이템이 유효하지 않으면 기본값 사용
        }
        
        // 아이템 타입 확인
        if (item.getType() != targetMaterial) {
            return false;
        }
        
        // 아이템 메타데이터 확인 (이름, 로어 등)
        if (item.getItemMeta().hasDisplayName()) {
            String displayName = item.getItemMeta().getDisplayName();
            return displayName.contains("AI") || displayName.contains("어시스턴트") || 
                   displayName.contains("모드팩") || displayName.contains("도움말");
        }
        
        // 기본값: BOOK 타입이면 AI 어시스턴트로 간주
        return item.getType() == Material.BOOK;
    }
} 