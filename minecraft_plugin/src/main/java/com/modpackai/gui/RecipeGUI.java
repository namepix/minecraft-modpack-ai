package com.modpackai.gui;

import com.modpackai.ModpackAIPlugin;
import com.modpackai.managers.RecipeManager;
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

public class RecipeGUI {
    
    private final ModpackAIPlugin plugin;
    private final RecipeManager recipeManager;
    private static final String GUI_TITLE = "§6§l제작법 - ";
    private static final int GUI_SIZE = 27; // 3줄
    
    public RecipeGUI(ModpackAIPlugin plugin) {
        this.plugin = plugin;
        this.recipeManager = plugin.getRecipeManager();
    }
    
    public void showRecipe(Player player, String itemName) {
        try {
            // 백엔드에서 제작법 정보 가져오기
            String recipeData = recipeManager.getRecipe(itemName);
            JSONObject recipe = new JSONObject(recipeData);
            
            if (recipe.has("error")) {
                player.sendMessage("§c제작법을 찾을 수 없습니다: " + itemName);
                return;
            }
            
            // GUI 생성
            String title = GUI_TITLE + recipe.getString("item_name");
            Inventory inventory = Bukkit.createInventory(null, GUI_SIZE, title);
            
            // 3x3 제작법 그리드 표시 (슬롯 10-12, 13-15, 16-18)
            displayCraftingGrid(inventory, recipe);
            
            // 결과 아이템 표시 (슬롯 22)
            displayResultItem(inventory, recipe);
            
            // 제작법 정보 표시 (슬롯 4)
            displayRecipeInfo(inventory, recipe);
            
            player.openInventory(inventory);
            
        } catch (Exception e) {
            player.sendMessage("§c제작법을 불러오는 중 오류가 발생했습니다: " + e.getMessage());
        }
    }
    
    private void displayCraftingGrid(Inventory inventory, JSONObject recipe) {
        JSONArray grid = recipe.getJSONArray("grid");
        
        // 3x3 그리드 슬롯 매핑
        int[] gridSlots = {10, 11, 12, 13, 14, 15, 16, 17, 18};
        
        for (int i = 0; i < Math.min(grid.length(), 9); i++) {
            JSONObject ingredient = grid.getJSONObject(i);
            String itemName = ingredient.getString("item");
            int amount = ingredient.optInt("amount", 1);
            
            ItemStack item = createIngredientItem(itemName, amount);
            inventory.setItem(gridSlots[i], item);
        }
        
        // 빈 슬롯은 투명 유리판으로 채우기
        for (int i = 0; i < 9; i++) {
            if (inventory.getItem(gridSlots[i]) == null) {
                inventory.setItem(gridSlots[i], createEmptySlot());
            }
        }
    }
    
    private void displayResultItem(Inventory inventory, JSONObject recipe) {
        JSONObject result = recipe.getJSONObject("result");
        String itemName = result.getString("item");
        int amount = result.optInt("amount", 1);
        
        ItemStack resultItem = createIngredientItem(itemName, amount);
        ItemMeta meta = resultItem.getItemMeta();
        meta.setDisplayName("§a§l결과: " + itemName);
        
        List<String> lore = new ArrayList<>();
        lore.add("§7수량: §f" + amount);
        lore.add("§7모드: §f" + recipe.optString("mod_name", "알 수 없음"));
        
        meta.setLore(lore);
        resultItem.setItemMeta(meta);
        
        inventory.setItem(22, resultItem);
    }
    
    private void displayRecipeInfo(Inventory inventory, JSONObject recipe) {
        ItemStack infoItem = new ItemStack(Material.BOOK);
        ItemMeta meta = infoItem.getItemMeta();
        meta.setDisplayName("§e§l제작법 정보");
        
        List<String> lore = new ArrayList<>();
        lore.add("§7아이템: §f" + recipe.getString("item_name"));
        lore.add("§7모드: §f" + recipe.optString("mod_name", "알 수 없음"));
        lore.add("§7타입: §f" + (recipe.optBoolean("shapeless", false) ? "무형태" : "형태"));
        lore.add("§7모드팩: §f" + recipe.optString("modpack_name", "알 수 없음"));
        lore.add("§7버전: §f" + recipe.optString("modpack_version", "1.0"));
        
        meta.setLore(lore);
        infoItem.setItemMeta(meta);
        
        inventory.setItem(4, infoItem);
    }
    
    private ItemStack createIngredientItem(String itemName, int amount) {
        // 아이템 이름을 Material로 변환
        Material material = parseItemNameToMaterial(itemName);
        ItemStack item = new ItemStack(material, amount);
        
        ItemMeta meta = item.getItemMeta();
        meta.setDisplayName("§f" + itemName);
        
        List<String> lore = new ArrayList<>();
        lore.add("§7수량: §f" + amount);
        lore.add("§7재료");
        
        meta.setLore(lore);
        item.setItemMeta(meta);
        
        return item;
    }
    
    private Material parseItemNameToMaterial(String itemName) {
        // 일반적인 마인크래프트 아이템들을 Material로 매핑
        String lowerName = itemName.toLowerCase();
        
        // 블록들
        if (lowerName.contains("stone")) return Material.STONE;
        if (lowerName.contains("dirt")) return Material.DIRT;
        if (lowerName.contains("grass")) return Material.GRASS_BLOCK;
        if (lowerName.contains("wood") || lowerName.contains("log")) return Material.OAK_LOG;
        if (lowerName.contains("planks")) return Material.OAK_PLANKS;
        if (lowerName.contains("iron")) return Material.IRON_INGOT;
        if (lowerName.contains("gold")) return Material.GOLD_INGOT;
        if (lowerName.contains("diamond")) return Material.DIAMOND;
        if (lowerName.contains("coal")) return Material.COAL;
        if (lowerName.contains("redstone")) return Material.REDSTONE;
        if (lowerName.contains("lapis") || lowerName.contains("lazuli")) return Material.LAPIS_LAZULI;
        if (lowerName.contains("emerald")) return Material.EMERALD;
        if (lowerName.contains("quartz")) return Material.QUARTZ;
        if (lowerName.contains("obsidian")) return Material.OBSIDIAN;
        if (lowerName.contains("glass")) return Material.GLASS;
        if (lowerName.contains("sand")) return Material.SAND;
        if (lowerName.contains("gravel")) return Material.GRAVEL;
        if (lowerName.contains("clay")) return Material.CLAY;
        if (lowerName.contains("brick")) return Material.BRICK;
        if (lowerName.contains("stick")) return Material.STICK;
        if (lowerName.contains("string")) return Material.STRING;
        if (lowerName.contains("leather")) return Material.LEATHER;
        if (lowerName.contains("feather")) return Material.FEATHER;
        if (lowerName.contains("flint")) return Material.FLINT;
        if (lowerName.contains("gunpowder")) return Material.GUNPOWDER;
        if (lowerName.contains("bone")) return Material.BONE;
        if (lowerName.contains("blaze")) return Material.BLAZE_ROD;
        if (lowerName.contains("ender")) return Material.ENDER_PEARL;
        if (lowerName.contains("slime")) return Material.SLIME_BALL;
        if (lowerName.contains("glowstone")) return Material.GLOWSTONE_DUST;
        if (lowerName.contains("nether")) return Material.NETHERRACK;
        if (lowerName.contains("soul")) return Material.SOUL_SAND;
        
        // 기본값
        return Material.PAPER;
    }
    
    private ItemStack createEmptySlot() {
        ItemStack item = new ItemStack(Material.LIGHT_GRAY_STAINED_GLASS_PANE);
        ItemMeta meta = item.getItemMeta();
        meta.setDisplayName(" ");
        item.setItemMeta(meta);
        return item;
    }
    
    public void displayRecipeInChatGUI(Player player, String itemName, JSONObject recipeData) {
        // AIChatGUI에서 호출되어 채팅 GUI의 제작법 영역에 표시
        try {
            // 현재 열린 GUI가 채팅 GUI인지 확인
            if (player.getOpenInventory().getTitle().contains("모드팩 AI 어시스턴트")) {
                Inventory inventory = player.getOpenInventory().getTopInventory();
                
                // 제작법 영역에 표시
                displayCraftingGrid(inventory, recipeData);
                displayResultItem(inventory, recipeData);
                
                player.sendMessage("§a제작법이 GUI에 표시되었습니다!");
            }
        } catch (Exception e) {
            player.sendMessage("§c제작법 표시 중 오류가 발생했습니다.");
        }
    }
} 