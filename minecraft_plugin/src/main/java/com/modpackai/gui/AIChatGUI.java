package com.modpackai.gui;

import com.modpackai.ModpackAIPlugin;
import com.modpackai.managers.AIManager;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;

public class AIChatGUI {
    
    private final ModpackAIPlugin plugin;
    private final AIManager aiManager;
    private static final String GUI_TITLE = "§6§l모드팩 AI 어시스턴트";
    private static final int GUI_SIZE = 54; // 6줄
    
    public AIChatGUI(ModpackAIPlugin plugin) {
        this.plugin = plugin;
        this.aiManager = plugin.getAIManager();
    }
    
    public void openChatGUI(Player player) {
        Inventory inventory = Bukkit.createInventory(null, GUI_SIZE, GUI_TITLE);
        
        // 상단 제목 영역 (0-8)
        setupHeader(inventory, player);
        
        // 왼쪽 제작법 영역 (9-35, 3x3 그리드)
        setupRecipeArea(inventory);
        
        // 오른쪽 채팅 영역 (18-35)
        setupChatArea(inventory, player);
        
        // 하단 컨트롤 영역 (45-53)
        setupControlArea(inventory, player);
        
        player.openInventory(inventory);
    }
    
    private void setupHeader(Inventory inventory, Player player) {
        // 모드팩 정보 표시
        ItemStack modpackInfo = new ItemStack(Material.BOOK);
        ItemMeta meta = modpackInfo.getItemMeta();
        meta.setDisplayName("§e§l현재 모드팩 정보");
        
        List<String> lore = new ArrayList<>();
        lore.add("§7모드팩: §f" + getCurrentModpackName());
        lore.add("§7버전: §f" + getCurrentModpackVersion());
        lore.add("§7현재 AI: §f" + getCurrentAIModel());
        
        meta.setLore(lore);
        modpackInfo.setItemMeta(meta);
        inventory.setItem(4, modpackInfo);
    }
    
    private void setupRecipeArea(Inventory inventory) {
        // 3x3 제작법 그리드 (슬롯 9-17, 18-26, 27-35)
        for (int i = 9; i <= 35; i++) {
            if ((i % 9) >= 0 && (i % 9) <= 2) { // 왼쪽 3칸만
                inventory.setItem(i, createEmptySlot());
            }
        }
        
        // 제작법 제목
        ItemStack recipeTitle = new ItemStack(Material.CRAFTING_TABLE);
        ItemMeta meta = recipeTitle.getItemMeta();
        meta.setDisplayName("§6§l제작법");
        meta.setLore(Arrays.asList("§7여기에 제작법이 표시됩니다"));
        recipeTitle.setItemMeta(meta);
        inventory.setItem(9, recipeTitle);
    }
    
    private void setupChatArea(Inventory inventory, Player player) {
        // 채팅 기록 표시 (슬롯 18-35, 오른쪽 6칸)
        List<AIManager.ChatMessage> chatHistory = getChatHistory(player);
        
        int chatSlot = 18;
        for (AIManager.ChatMessage message : chatHistory) {
            if (chatSlot >= 36) break; // 채팅 영역을 벗어나면 중단
            
            ItemStack chatItem = createChatMessageItem(message);
            inventory.setItem(chatSlot, chatItem);
            chatSlot++;
        }
        
        // 새 메시지 입력 안내
        ItemStack newMessage = new ItemStack(Material.PAPER);
        ItemMeta meta = newMessage.getItemMeta();
        meta.setDisplayName("§a§l새 메시지 입력");
        meta.setLore(Arrays.asList(
            "§7채팅창에 §e/modpackai chat <메시지>§7를 입력하세요",
            "§7예: §e/modpackai chat 철 블록은 어떻게 만들어?"
        ));
        newMessage.setItemMeta(meta);
        inventory.setItem(chatSlot, newMessage);
    }
    
    private void setupControlArea(Inventory inventory, Player player) {
        // AI 모델 변경 버튼
        ItemStack modelButton = new ItemStack(Material.ENDER_EYE);
        ItemMeta meta = modelButton.getItemMeta();
        meta.setDisplayName("§b§lAI 모델 변경");
        meta.setLore(Arrays.asList(
            "§7현재: §f" + getCurrentAIModel(),
            "§7클릭하여 다른 AI 모델을 선택하세요"
        ));
        modelButton.setItemMeta(meta);
        inventory.setItem(45, modelButton);
        
        // 도움말 버튼
        ItemStack helpButton = new ItemStack(Material.HELP);
        meta = helpButton.getItemMeta();
        meta.setDisplayName("§e§l도움말");
        meta.setLore(Arrays.asList(
            "§7사용법:",
            "§7• 채팅: §e/modpackai chat <메시지>",
            "§7• 제작법: §e/modpackai recipe <아이템명>",
            "§7• 모델 변경: §e/modpackai models"
        ));
        helpButton.setItemMeta(meta);
        inventory.setItem(49, helpButton);
        
        // 닫기 버튼
        ItemStack closeButton = new ItemStack(Material.BARRIER);
        meta = closeButton.getItemMeta();
        meta.setDisplayName("§c§l닫기");
        closeButton.setItemMeta(meta);
        inventory.setItem(53, closeButton);
    }
    
    private ItemStack createEmptySlot() {
        ItemStack item = new ItemStack(Material.GRAY_STAINED_GLASS_PANE);
        ItemMeta meta = item.getItemMeta();
        meta.setDisplayName(" ");
        item.setItemMeta(meta);
        return item;
    }
    
    private ItemStack createChatMessageItem(AIManager.ChatMessage message) {
        ItemStack item = new ItemStack(Material.PAPER);
        ItemMeta meta = item.getItemMeta();
        
        // 메시지 타입에 따라 다른 색상
        if (message.isUserMessage()) {
            meta.setDisplayName("§a§l사용자: §f" + truncateMessage(message.getMessage(), 20));
            item.setType(Material.LIGHT_BLUE_DYE);
        } else {
            meta.setDisplayName("§6§lAI: §f" + truncateMessage(message.getMessage(), 20));
            item.setType(Material.ORANGE_DYE);
        }
        
        List<String> lore = new ArrayList<>();
        lore.add("§7시간: §f" + message.getTimestamp());
        lore.add("§7내용: §f" + truncateMessage(message.getMessage(), 50));
        
        meta.setLore(lore);
        item.setItemMeta(meta);
        return item;
    }
    
    private String truncateMessage(String message, int maxLength) {
        if (message.length() <= maxLength) {
            return message;
        }
        return message.substring(0, maxLength - 3) + "...";
    }
    
    private List<AIManager.ChatMessage> getChatHistory(Player player) {
        try {
            String response = aiManager.getChatHistory(player.getUniqueId().toString());
            JSONObject jsonResponse = new JSONObject(response);
            JSONArray historyArray = jsonResponse.getJSONArray("history");
            
            List<AIManager.ChatMessage> messages = new ArrayList<>();
            for (int i = 0; i < Math.min(historyArray.length(), 10); i++) {
                JSONObject msg = historyArray.getJSONObject(i);
                messages.add(new AIManager.ChatMessage(
                    msg.getString("user_message"),
                    msg.getString("ai_response"),
                    msg.getString("timestamp")
                ));
            }
            return messages;
        } catch (Exception e) {
            return new ArrayList<>();
        }
    }
    
    private String getCurrentModpackName() {
        try {
            return plugin.getConfigManager().getModpackName();
        } catch (Exception e) {
            return "알 수 없음";
        }
    }
    
    private String getCurrentModpackVersion() {
        try {
            return plugin.getConfigManager().getModpackVersion();
        } catch (Exception e) {
            return "1.0";
        }
    }
    
    private String getCurrentAIModel() {
        try {
            String response = aiManager.getCurrentModel();
            JSONObject jsonResponse = new JSONObject(response);
            return jsonResponse.getString("name");
        } catch (Exception e) {
            return "알 수 없음";
        }
    }
    
    public void displayRecipe(Player player, String itemName, JSONObject recipeData) {
        // 제작법을 GUI에 표시하는 로직
        // 이 메서드는 RecipeGUI에서 호출될 수 있습니다
    }
} 