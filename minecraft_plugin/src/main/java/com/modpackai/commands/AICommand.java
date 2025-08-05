package com.modpackai.commands;

import com.modpackai.ModpackAIPlugin;
import com.modpackai.managers.AIManager;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;

import java.util.Arrays;

public class AICommand implements CommandExecutor {
    private final ModpackAIPlugin plugin;
    private final AIManager aiManager;
    
    public AICommand(ModpackAIPlugin plugin) {
        this.plugin = plugin;
        this.aiManager = plugin.getAIManager();
    }
    
    @Override
    public boolean onCommand(CommandSender sender, Command command, String label, String[] args) {
        if (!(sender instanceof Player)) {
            sender.sendMessage("§c이 명령어는 플레이어만 사용할 수 있습니다.");
            return true;
        }
        
        Player player = (Player) sender;
        
        if (args.length == 0) {
            player.sendMessage("§c사용법: /ai <질문>");
            player.sendMessage("§7예: /ai 철 블록은 어떻게 만들어?");
            return true;
        }
        
        // 모든 인수를 하나의 질문으로 결합
        String question = String.join(" ", args);
        
        player.sendMessage("§a🤖 AI가 답변을 생성하고 있습니다...");
        
        // 비동기로 AI 응답 생성
        plugin.getServer().getScheduler().runTaskAsynchronously(plugin, () -> {
            try {
                String currentModpack = plugin.getConfigManager().getModpackName();
                String modpackVersion = plugin.getConfigManager().getModpackVersion();
                
                String response = aiManager.generateResponse(player, question, currentModpack, modpackVersion);
                
                // 메인 스레드에서 응답 전송
                plugin.getServer().getScheduler().runTask(plugin, () -> {
                    player.sendMessage("§6=== AI 응답 ===");
                    
                    // 긴 응답을 여러 줄로 나누기
                    String[] lines = response.split("\\n");
                    for (String line : lines) {
                        if (line.trim().isEmpty()) continue;
                        
                        // 줄이 너무 길면 자르기
                        if (line.length() > 50) {
                            String[] words = line.split(" ");
                            StringBuilder currentLine = new StringBuilder();
                            
                            for (String word : words) {
                                if (currentLine.length() + word.length() + 1 > 50) {
                                    if (currentLine.length() > 0) {
                                        player.sendMessage("§f" + currentLine.toString());
                                        currentLine = new StringBuilder();
                                    }
                                }
                                if (currentLine.length() > 0) {
                                    currentLine.append(" ");
                                }
                                currentLine.append(word);
                            }
                            
                            if (currentLine.length() > 0) {
                                player.sendMessage("§f" + currentLine.toString());
                            }
                        } else {
                            player.sendMessage("§f" + line);
                        }
                    }
                    
                    player.sendMessage("§6================");
                    player.sendMessage("§e💡 더 자세한 정보는 §f/modpackai chat§e을 이용하세요!");
                });
                
            } catch (Exception e) {
                plugin.getLogger().warning("AI 응답 생성 중 오류: " + e.getMessage());
                
                plugin.getServer().getScheduler().runTask(plugin, () -> {
                    player.sendMessage("§c죄송합니다. AI 응답 생성 중 오류가 발생했습니다.");
                    player.sendMessage("§7잠시 후 다시 시도해주세요.");
                });
            }
        });
        
        return true;
    }
}