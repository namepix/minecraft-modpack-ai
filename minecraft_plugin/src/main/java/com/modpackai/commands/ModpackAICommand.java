package com.modpackai.commands;

import com.modpackai.ModpackAIPlugin;
import com.modpackai.gui.ModelSelectionGUI;
import com.modpackai.managers.AIManager;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;

import java.util.Arrays;

public class ModpackAICommand implements CommandExecutor {
    private final ModpackAIPlugin plugin;
    private final ModelSelectionGUI modelSelectionGUI;
    
    public ModpackAICommand(ModpackAIPlugin plugin) {
        this.plugin = plugin;
        this.modelSelectionGUI = new ModelSelectionGUI(plugin);
    }
    
    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!(sender instanceof Player)) {
            sender.sendMessage("§c이 명령어는 플레이어만 사용할 수 있습니다.");
            return true;
        }
        
        Player player = (Player) sender;
        
        if (args.length == 0) {
            showHelp(player);
            return true;
        }
        
        switch (args[0].toLowerCase()) {
            case "chat":
                plugin.getAIChatGUI().openChatGUI(player);
                break;
            case "recipe":
                if (args.length < 2) {
                    player.sendMessage("§c사용법: /modpackai recipe <아이템명>");
                    return true;
                }
                String itemName = String.join(" ", Arrays.copyOfRange(args, 1, args.length));
                plugin.getRecipeGUI().showRecipe(player, itemName);
                break;
            case "models":
                modelSelectionGUI.openModelSelection(player);
                break;
            case "current":
                showCurrentModel(player);
                break;
            case "switch":
                if (args.length < 2) {
                    player.sendMessage("§c사용법: /modpackai switch <모드팩명> [버전]");
                    return true;
                }
                String modpackName = args[1];
                String version = args.length > 2 ? args[2] : "1.0";
                switchModpack(player, modpackName, version);
                break;
            case "help":
                showHelp(player);
                break;
            default:
                player.sendMessage("§c알 수 없는 명령어입니다. /modpackai help를 입력하세요.");
                break;
        }
        
        return true;
    }
    
    private void showHelp(Player player) {
        player.sendMessage("§6=== ModpackAI 도움말 ===");
        player.sendMessage("§e/modpackai chat §7- AI 채팅 GUI 열기");
        player.sendMessage("§e/modpackai recipe <아이템명> §7- 제작법 보기");
        player.sendMessage("§e/modpackai models §7- AI 모델 선택");
        player.sendMessage("§e/modpackai current §7- 현재 AI 모델 정보");
        player.sendMessage("§e/modpackai switch <모드팩명> [버전] §7- 모드팩 변경");
        player.sendMessage("§e/modpackai help §7- 도움말 보기");
    }
    
    private void switchModpack(Player player, String modpackName, String version) {
        // 관리자 권한 확인
        if (!player.hasPermission("modpackai.admin")) {
            player.sendMessage("§c모드팩 변경은 관리자만 가능합니다.");
            return;
        }
        
        player.sendMessage("§a모드팩 변경을 시작합니다...");
        
        // 백엔드에 모드팩 변경 요청
        try {
            // 실제 구현에서는 백엔드 API 호출
            player.sendMessage("§a모드팩 변경이 완료되었습니다: " + modpackName + " v" + version);
        } catch (Exception e) {
            player.sendMessage("§c모드팩 변경 중 오류가 발생했습니다: " + e.getMessage());
        }
    }
    
    private void showCurrentModel(Player player) {
        AIManager.AIModelInfo currentModel = plugin.getAIManager().getCurrentModel();
        if (currentModel != null) {
            player.sendMessage("§6=== 현재 AI 모델 ===");
            player.sendMessage("§e모델: §f" + currentModel.getName());
            player.sendMessage("§e제공자: §f" + currentModel.getProvider());
            player.sendMessage("§e요금제: §f" + (currentModel.isFreeTier() ? "무료" : "유료"));
            player.sendMessage("§e설명: §f" + currentModel.getDescription());
        } else {
            player.sendMessage("§c현재 AI 모델 정보를 가져올 수 없습니다.");
        }
    }
} 