package com.modpackai.listeners;

import com.modpackai.ModpackAIPlugin;
import com.modpackai.gui.ModelSelectionGUI;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.inventory.Inventory;

public class InventoryListener implements Listener {
    private final ModpackAIPlugin plugin;
    private final ModelSelectionGUI modelSelectionGUI;
    
    public InventoryListener(ModpackAIPlugin plugin) {
        this.plugin = plugin;
        this.modelSelectionGUI = new ModelSelectionGUI(plugin);
    }
    
    @EventHandler
    public void onInventoryClick(InventoryClickEvent event) {
        if (!(event.getWhoClicked() instanceof Player)) {
            return;
        }
        
        Player player = (Player) event.getWhoClicked();
        Inventory inventory = event.getInventory();
        String title = inventory.getTitle();
        
        // AI 모델 선택 GUI 처리
        if (title.equals("§6AI 모델 선택")) {
            event.setCancelled(true);
            
            if (event.getCurrentItem() != null) {
                modelSelectionGUI.handleClick(player, event.getRawSlot(), inventory);
            }
        }
    }
} 