package com.modpackai.commands;

import com.modpackai.ModpackAIMod;
import com.modpackai.gui.AIChatScreen;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import net.minecraft.client.Minecraft;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.component.DataComponents;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;

/**
 * NeoForge 모드용 명령어 시스템
 * Bukkit CommandExecutor를 NeoForge Commands로 변환
 */
public class ModpackAICommands {
    
    /**
     * 명령어 등록
     */
    public static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        // /ai <message> 명령어
        dispatcher.register(Commands.literal("ai")
                .then(Commands.argument("message", StringArgumentType.greedyString())
                        .executes(ModpackAICommands::handleAICommand))
                .executes(ModpackAICommands::handleAICommandNoArgs));
        
        // /modpackai 명령어
        dispatcher.register(Commands.literal("modpackai")
                .executes(ModpackAICommands::handleModpackAICommand)
                .then(Commands.literal("give")
                        .executes(ModpackAICommands::handleGiveAIItem))
                .then(Commands.literal("help")
                        .executes(ModpackAICommands::handleHelpCommand))
                .then(Commands.literal("recipe")
                        .then(Commands.argument("item", StringArgumentType.string())
                                .executes(ModpackAICommands::handleRecipeCommand)))
                .then(Commands.literal("models")
                        .executes(ModpackAICommands::handleModelsCommand))
                .then(Commands.literal("status")
                        .executes(ModpackAICommands::handleStatusCommand))
                .then(Commands.literal("rag")
                        .then(Commands.literal("status")
                                .executes(ModpackAICommands::handleRAGStatusCommand))
                        .then(Commands.literal("build")
                                .then(Commands.argument("modpack_path", StringArgumentType.string())
                                        .executes(ModpackAICommands::handleRAGBuildCommand)))
                        .then(Commands.literal("list")
                                .executes(ModpackAICommands::handleRAGListCommand))
                        .then(Commands.literal("test")
                                .then(Commands.argument("query", StringArgumentType.greedyString())
                                        .executes(ModpackAICommands::handleRAGTestCommand)))));
    }
    
    /**
     * /ai <message> 명령어 처리
     */
    private static int handleAICommand(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        String message = StringArgumentType.getString(context, "message");
        ServerPlayer player = context.getSource().getPlayerOrException();
        
        ModpackAIMod.LOGGER.info("플레이어 {}가 AI 질문: {}", player.getName().getString(), message);
        
        // AI 응답 처리 (비동기)
        ModpackAIMod.getInstance().getAIManager()
                .askAIAsync(player.getStringUUID(), message, getModpackName())
                .thenAccept(response -> {
                    // 메인 스레드에서 응답 전송
                    player.sendSystemMessage(Component.literal("§6[AI] §f" + response));
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("AI 응답 처리 실패", throwable);
                    player.sendSystemMessage(Component.literal("§c[AI] AI 응답 처리 중 오류가 발생했습니다."));
                    return null;
                });
        
        return 1; // 성공
    }
    
    /**
     * /ai (인수 없음) 명령어 처리 - GUI 열기
     */
    @OnlyIn(Dist.CLIENT)
    private static int handleAICommandNoArgs(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        // 클라이언트에서만 실행되는 GUI 열기
        Minecraft.getInstance().execute(() -> {
            Minecraft.getInstance().setScreen(new AIChatScreen());
        });
        
        return 1; // 성공
    }
    
    /**
     * /modpackai 기본 명령어
     */
    private static int handleModpackAICommand(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        ServerPlayer player = context.getSource().getPlayerOrException();
        
        player.sendSystemMessage(Component.literal("§6=== ModpackAI 모드 ==="));
        player.sendSystemMessage(Component.literal("§f/ai <질문> - AI에게 질문하기"));
        player.sendSystemMessage(Component.literal("§f/modpackai help - 도움말 보기"));
        player.sendSystemMessage(Component.literal("§f/modpackai give - AI 아이템 받기"));
        player.sendSystemMessage(Component.literal("§f/modpackai recipe <아이템> - 제작법 보기"));
        
        return 1;
    }
    
    /**
     * AI 아이템 지급
     */
    private static int handleGiveAIItem(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        ServerPlayer player = context.getSource().getPlayerOrException();
        
        // AI 아이템 생성
        ItemStack aiItem = new ItemStack(ModpackAIMod.getInstance().getConfig().getAIItemMaterial());
        aiItem.set(DataComponents.CUSTOM_NAME, Component.literal(ModpackAIMod.getInstance().getConfig().getAIItemName()));
        
        // 인벤토리에 추가
        if (player.getInventory().add(aiItem)) {
            player.sendSystemMessage(Component.literal("§a[ModpackAI] AI 아이템을 받았습니다!"));
            ModpackAIMod.LOGGER.info("플레이어 {}에게 AI 아이템 지급", player.getName().getString());
        } else {
            player.sendSystemMessage(Component.literal("§c[ModpackAI] 인벤토리가 가득 차서 아이템을 받을 수 없습니다."));
        }
        
        return 1;
    }
    
    /**
     * 도움말 명령어
     */
    private static int handleHelpCommand(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        ServerPlayer player = context.getSource().getPlayerOrException();
        
        player.sendSystemMessage(Component.literal("§6=== ModpackAI 도움말 ==="));
        player.sendSystemMessage(Component.literal("§f"));
        player.sendSystemMessage(Component.literal("§e기본 명령어:"));
        player.sendSystemMessage(Component.literal("§f  /ai <질문> - AI에게 질문하기"));
        player.sendSystemMessage(Component.literal("§f  /ai - AI 채팅 GUI 열기"));
        player.sendSystemMessage(Component.literal("§f"));
        player.sendSystemMessage(Component.literal("§e관리 명령어:"));
        player.sendSystemMessage(Component.literal("§f  /modpackai give - AI 아이템 받기"));
        player.sendSystemMessage(Component.literal("§f  /modpackai recipe <아이템> - 제작법 조회"));
        player.sendSystemMessage(Component.literal("§f  /modpackai models - 사용 가능한 AI 모델 보기"));
        player.sendSystemMessage(Component.literal("§f  /modpackai status - 시스템 상태 확인"));
        player.sendSystemMessage(Component.literal("§f"));
        player.sendSystemMessage(Component.literal("§6RAG 관리 명령어:"));
        player.sendSystemMessage(Component.literal("§f  /modpackai rag status - RAG 시스템 상태"));
        player.sendSystemMessage(Component.literal("§f  /modpackai rag build <경로> - 모드팩 분석"));
        player.sendSystemMessage(Component.literal("§f  /modpackai rag list - 등록된 모드팩 목록"));
        player.sendSystemMessage(Component.literal("§f  /modpackai rag test <검색어> - RAG 검색 테스트"));
        player.sendSystemMessage(Component.literal("§f"));
        player.sendSystemMessage(Component.literal("§7AI 아이템을 우클릭해서 GUI를 열 수도 있습니다!"));
        
        return 1;
    }
    
    /**
     * 제작법 조회 명령어
     */
    private static int handleRecipeCommand(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        String itemName = StringArgumentType.getString(context, "item");
        ServerPlayer player = context.getSource().getPlayerOrException();
        
        ModpackAIMod.LOGGER.info("플레이어 {}가 제작법 조회: {}", player.getName().getString(), itemName);
        
        player.sendSystemMessage(Component.literal("§6[ModpackAI] §f" + itemName + "의 제작법을 검색 중..."));
        
        // 비동기 제작법 조회
        ModpackAIMod.getInstance().getAIManager()
                .getRecipeAsync(itemName)
                .thenAccept(recipeData -> {
                    if (recipeData.has("success") && recipeData.get("success").getAsBoolean()) {
                        // 제작법 정보 표시
                        player.sendSystemMessage(Component.literal("§a[제작법] " + itemName));
                        if (recipeData.has("recipe")) {
                            player.sendSystemMessage(Component.literal("§f" + recipeData.get("recipe").getAsString()));
                        }
                    } else {
                        String error = recipeData.has("error") ? recipeData.get("error").getAsString() : "제작법을 찾을 수 없습니다.";
                        player.sendSystemMessage(Component.literal("§c[ModpackAI] " + error));
                    }
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("제작법 조회 실패", throwable);
                    player.sendSystemMessage(Component.literal("§c[ModpackAI] 제작법 조회 중 오류가 발생했습니다."));
                    return null;
                });
        
        return 1;
    }
    
    /**
     * 모델 목록 조회
     */
    private static int handleModelsCommand(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        ServerPlayer player = context.getSource().getPlayerOrException();
        
        player.sendSystemMessage(Component.literal("§6[ModpackAI] 사용 가능한 AI 모델 조회 중..."));
        
        // 비동기 모델 목록 조회
        ModpackAIMod.getInstance().getAIManager()
                .getAvailableModelsAsync()
                .thenAccept(modelsData -> {
                    if (modelsData.has("success") && modelsData.get("success").getAsBoolean()) {
                        player.sendSystemMessage(Component.literal("§a=== 사용 가능한 AI 모델 ==="));
                        if (modelsData.has("models")) {
                            // 모델 목록 표시
                            modelsData.getAsJsonArray("models").forEach(modelElement -> {
                                player.sendSystemMessage(Component.literal("§f- " + modelElement.getAsString()));
                            });
                        }
                    } else {
                        player.sendSystemMessage(Component.literal("§c[ModpackAI] 모델 목록을 가져올 수 없습니다."));
                    }
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("모델 목록 조회 실패", throwable);
                    player.sendSystemMessage(Component.literal("§c[ModpackAI] 모델 목록 조회 중 오류가 발생했습니다."));
                    return null;
                });
        
        return 1;
    }
    
    /**
     * 시스템 상태 확인
     */
    private static int handleStatusCommand(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        ServerPlayer player = context.getSource().getPlayerOrException();
        
        player.sendSystemMessage(Component.literal("§6=== ModpackAI 시스템 ��태 ==="));
        player.sendSystemMessage(Component.literal("§f모드 버전: 1.0.0"));
        player.sendSystemMessage(Component.literal("§f모드팩: " + getModpackName() + " v" + ModpackAIMod.getInstance().getConfig().getModpackVersion()));
        player.sendSystemMessage(Component.literal("§f백엔드 URL: " + ModpackAIMod.getInstance().getConfig().getBackendUrl()));
        
        // 백엔드 상태 확인
        boolean healthy = ModpackAIMod.getInstance().getAIManager().isBackendHealthy();
        if (healthy) {
            player.sendSystemMessage(Component.literal("§a백엔드 상태: 정상"));
        } else {
            player.sendSystemMessage(Component.literal("§c백엔드 상태: 연결 실패"));
        }
        
        return 1;
    }
    
    /**
     * RAG 시스템 상태 확인
     */
    private static int handleRAGStatusCommand(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        ServerPlayer player = context.getSource().getPlayerOrException();
        
        player.sendSystemMessage(Component.literal("§6[ModpackAI] RAG 시스템 상태 조회 중..."));
        
        // 비동기 RAG 상태 조회
        ModpackAIMod.getInstance().getAIManager()
                .getRAGStatusAsync()
                .thenAccept(statusData -> {
                    if (statusData.has("success") && statusData.get("success").getAsBoolean()) {
                        player.sendSystemMessage(Component.literal("§a=== RAG 시스템 상태 ==="));
                        
                        boolean gcpEnabled = statusData.has("gcp_rag_enabled") && statusData.get("gcp_rag_enabled").getAsBoolean();
                        boolean gcpAvailable = statusData.has("gcp_rag_available") && statusData.get("gcp_rag_available").getAsBoolean();
                        boolean localEnabled = statusData.has("local_rag_enabled") && statusData.get("local_rag_enabled").getAsBoolean();
                        
                        player.sendSystemMessage(Component.literal("§f- GCP RAG: " + (gcpAvailable ? "§a활성화됨" : "§c비활성화됨")));
                        player.sendSystemMessage(Component.literal("§f- 로컬 RAG: " + (localEnabled ? "§a활성화됨" : "§c비활성화됨")));
                        
                        if (statusData.has("project_id")) {
                            String projectId = statusData.get("project_id").getAsString();
                            player.sendSystemMessage(Component.literal("§f- GCP 프로젝트: " + projectId));
                        }
                        
                    } else {
                        player.sendSystemMessage(Component.literal("§c[ModpackAI] RAG 상태 조회 실패"));
                    }
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("RAG 상태 조회 실패", throwable);
                    player.sendSystemMessage(Component.literal("§c[ModpackAI] RAG 상태 조회 중 오류 발생"));
                    return null;
                });
        
        return 1;
    }
    
    /**
     * RAG 인덱스 구축
     */
    private static int handleRAGBuildCommand(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        String modpackPath = StringArgumentType.getString(context, "modpack_path");
        ServerPlayer player = context.getSource().getPlayerOrException();
        
        ModpackAIMod.LOGGER.info("플레이어 {}가 RAG 인덱스 구축 요청: {}", player.getName().getString(), modpackPath);
        
        player.sendSystemMessage(Component.literal("§6[ModpackAI] §f모드팩 분석 시작: " + modpackPath));
        player.sendSystemMessage(Component.literal("§e⚠️ 이 작업은 시간이 오래 걸리고 GCP 비용이 발생할 수 있습니다."));
        
        // 비동기 인덱스 구축
        ModpackAIMod.getInstance().getAIManager()
                .buildRAGIndexAsync(getModpackName(), "1.0.0", modpackPath)
                .thenAccept(result -> {
                    if (result.has("success") && result.get("success").getAsBoolean()) {
                        int docCount = result.has("document_count") ? result.get("document_count").getAsInt() : 0;
                        player.sendSystemMessage(Component.literal("§a[ModpackAI] ✅ RAG 인덱스 구축 완료!"));
                        player.sendSystemMessage(Component.literal("§f📊 처리된 문서 수: " + docCount));
                        
                        // 통계 정보
                        if (result.has("stats")) {
                            var stats = result.getAsJsonObject("stats");
                            int recipes = stats.has("recipes") ? stats.get("recipes").getAsInt() : 0;
                            int mods = stats.has("mods") ? stats.get("mods").getAsInt() : 0;
                            int kubejs = stats.has("kubejs") ? stats.get("kubejs").getAsInt() : 0;
                            
                            player.sendSystemMessage(Component.literal("§f📈 레시피: " + recipes + ", 모드: " + mods + ", KubeJS: " + kubejs));
                        }
                        
                    } else {
                        String error = result.has("error") ? result.get("error").getAsString() : "알 수 없는 오류";
                        player.sendSystemMessage(Component.literal("§c[ModpackAI] ❌ RAG 인덱스 구축 실패"));
                        player.sendSystemMessage(Component.literal("§c오류: " + error));
                    }
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("RAG 인덱스 구축 실패", throwable);
                    player.sendSystemMessage(Component.literal("§c[ModpackAI] RAG 인덱스 구축 중 심각한 오류 발생"));
                    return null;
                });
        
        return 1;
    }
    
    /**
     * 등록된 모드팩 목록 조회
     */
    private static int handleRAGListCommand(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        ServerPlayer player = context.getSource().getPlayerOrException();
        
        player.sendSystemMessage(Component.literal("§6[ModpackAI] 등록된 모드팩 목록 조회 중..."));
        
        // 비동기 모드팩 목록 조회
        ModpackAIMod.getInstance().getAIManager()
                .getRAGModpacksAsync()
                .thenAccept(listData -> {
                    if (listData.has("success") && listData.get("success").getAsBoolean()) {
                        var modpacks = listData.getAsJsonArray("modpacks");
                        int count = listData.has("count") ? listData.get("count").getAsInt() : 0;
                        
                        player.sendSystemMessage(Component.literal("§a=== 등록된 모드팩 목록 (" + count + "개) ==="));
                        
                        if (count == 0) {
                            player.sendSystemMessage(Component.literal("§e등록된 모드팩이 없습니다."));
                            player.sendSystemMessage(Component.literal("§f사용법: /modpackai rag build <모드팩_경로>"));
                        } else {
                            for (int i = 0; i < modpacks.size(); i++) {
                                var modpack = modpacks.get(i).getAsJsonObject();
                                String name = modpack.has("modpack_name") ? modpack.get("modpack_name").getAsString() : "Unknown";
                                String version = modpack.has("modpack_version") ? modpack.get("modpack_version").getAsString() : "1.0.0";
                                int docCount = modpack.has("document_count") ? modpack.get("document_count").getAsInt() : 0;
                                
                                player.sendSystemMessage(Component.literal("§f" + (i + 1) + ". " + name + " v" + version + " (" + docCount + "개 문서)"));
                            }
                        }
                        
                    } else {
                        player.sendSystemMessage(Component.literal("§c[ModpackAI] 모드팩 목록 조회 실패"));
                    }
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("RAG 모드팩 목록 조회 실패", throwable);
                    player.sendSystemMessage(Component.literal("§c[ModpackAI] 모드팩 목록 조회 중 오류 발생"));
                    return null;
                });
        
        return 1;
    }
    
    /**
     * RAG 검색 테스트 (개발자용)
     */
    private static int handleRAGTestCommand(CommandContext<CommandSourceStack> context) throws CommandSyntaxException {
        String query = StringArgumentType.getString(context, "query");
        ServerPlayer player = context.getSource().getPlayerOrException();
        
        ModpackAIMod.LOGGER.info("플레이어 {}가 RAG 테스트: {}", player.getName().getString(), query);
        
        player.sendSystemMessage(Component.literal("§6[ModpackAI] §fRAG 검색 테스트: \"" + query + "\""));
        
        // 비동기 RAG 테스트
        ModpackAIMod.getInstance().getAIManager()
                .testRAGSearchAsync(query, getModpackName(), "1.0.0")
                .thenAccept(testData -> {
                    if (testData.has("success") && testData.get("success").getAsBoolean()) {
                        int resultCount = testData.has("results_count") ? testData.get("results_count").getAsInt() : 0;
                        
                        player.sendSystemMessage(Component.literal("§a✅ RAG 검색 결과: " + resultCount + "개"));
                        
                        if (resultCount > 0 && testData.has("results")) {
                            var results = testData.getAsJsonArray("results");
                            
                            for (int i = 0; i < Math.min(3, results.size()); i++) { // 상위 3개만 표시
                                var result = results.get(i).getAsJsonObject();
                                
                                double similarity = result.has("similarity") ? result.get("similarity").getAsDouble() : 0.0;
                                String docType = result.has("doc_type") ? result.get("doc_type").getAsString() : "unknown";
                                String text = result.has("text") ? result.get("text").getAsString() : "";
                                
                                // 텍스트 길이 제한
                                if (text.length() > 100) {
                                    text = text.substring(0, 100) + "...";
                                }
                                
                                player.sendSystemMessage(Component.literal("§f" + (i + 1) + ". [" + String.format("%.2f", similarity) + "] (" + docType + ") " + text));
                            }
                            
                        } else {
                            player.sendSystemMessage(Component.literal("§e관련 문서를 찾을 수 없습니다."));
                            player.sendSystemMessage(Component.literal("§7모드팩이 인덱싱되지 않았거나 검색어와 관련성이 낮을 수 있습니다."));
                        }
                        
                    } else {
                        String error = testData.has("error") ? testData.get("error").getAsString() : "알 수 없는 오류";
                        player.sendSystemMessage(Component.literal("§c[ModpackAI] RAG 테스트 실패: " + error));
                    }
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("RAG 테스트 실패", throwable);
                    player.sendSystemMessage(Component.literal("§c[ModpackAI] RAG 테스트 중 오류 발생"));
                    return null;
                });
        
        return 1;
    }

    /**
     * 현재 모드팩 이름 가져오기 (임시 구현)
     */
    private static String getModpackName() {
        return ModpackAIMod.getInstance().getConfig().getModpackName();
    }
}