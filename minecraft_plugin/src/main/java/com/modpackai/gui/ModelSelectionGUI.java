package com.modpackai.gui;

import com.modpackai.ModpackAIPlugin;
import com.modpackai.managers.AIManager;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

import java.util.ArrayList;
import java.util.List;

public class ModelSelectionGUI {
    private final ModpackAIPlugin plugin;
    private final AIManager aiManager;
    
    public ModelSelectionGUI(ModpackAIPlugin plugin) {
        this.plugin = plugin;
        this.aiManager = plugin.getAIManager();
    }
    
    /**
     * AI 모델 선택 GUI를 열습니다.
     */
    public void openModelSelection(Player player) {
        List<AIManager.AIModelInfo> models = aiManager.getAvailableModels();
        
        // GUI 크기 계산 (9개씩 행으로 배치)
        int size = Math.max(9, ((models.size() - 1) / 9 + 1) * 9);
        Inventory gui = Bukkit.createInventory(null, size, "§6AI 모델 선택");
        
        // 현재 모델 정보 가져오기
        AIManager.AIModelInfo currentModel = aiManager.getCurrentModel();
        
        for (int i = 0; i < models.size(); i++) {
            AIManager.AIModelInfo model = models.get(i);
            ItemStack item = createModelItem(model, currentModel);
            gui.setItem(i, item);
        }
        
        player.openInventory(gui);
    }
    
    /**
     * 모델 정보를 아이템으로 생성합니다.
     */
    private ItemStack createModelItem(AIManager.AIModelInfo model, AIManager.AIModelInfo currentModel) {
        Material material;
        String displayName;
        List<String> lore = new ArrayList<>();
        
        // 모델 상태에 따른 아이템 설정
        if (!model.isAvailable()) {
            material = Material.BARRIER;
            displayName = "§c" + model.getName() + " (사용 불가)";
            lore.add("§7이 모델을 사용할 수 없습니다.");
            lore.add("§7API 키가 설정되지 않았습니다.");
        } else if (model.isCurrent()) {
            material = Material.EMERALD;
            displayName = "§a" + model.getName() + " (현재 사용 중)";
            lore.add("§7현재 선택된 모델입니다.");
        } else {
            material = Material.BOOK;
            displayName = "§e" + model.getName();
            lore.add("§7클릭하여 이 모델로 전환하세요.");
        }
        
        // 모델 정보 추가
        lore.add("");
        lore.add("§6제공자: §f" + model.getProvider());
        lore.add("§6요금제: §f" + (model.isFreeTier() ? "무료" : "유료"));
        lore.add("§6설명: §f" + model.getDescription());
        
        // 아이템 생성
        ItemStack item = new ItemStack(material);
        ItemMeta meta = item.getItemMeta();
        meta.setDisplayName(displayName);
        meta.setLore(lore);
        item.setItemMeta(meta);
        
        return item;
    }
    
    /**
     * GUI 클릭 이벤트를 처리합니다.
     */
    public void handleClick(Player player, int slot, Inventory inventory) {
        List<AIManager.AIModelInfo> models = aiManager.getAvailableModels();
        
        if (slot >= 0 && slot < models.size()) {
            AIManager.AIModelInfo selectedModel = models.get(slot);
            
            if (!selectedModel.isAvailable()) {
                player.sendMessage("§c이 모델을 사용할 수 없습니다. API 키를 확인해주세요.");
                return;
            }
            
            if (selectedModel.isCurrent()) {
                player.sendMessage("§a이미 선택된 모델입니다.");
                return;
            }
            
            // 모델 전환
            boolean success = aiManager.switchModel(selectedModel.getId());
            if (success) {
                player.sendMessage("§aAI 모델이 " + selectedModel.getName() + "로 전환되었습니다.");
                player.closeInventory();
                
                // GUI 새로고침
                openModelSelection(player);
            } else {
                player.sendMessage("§c모델 전환에 실패했습니다.");
            }
        }
    }
} 