package com.modpackai.commands;

import com.modpackai.ModpackAIMod;
import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import net.minecraft.server.command.ServerCommandSource;
import net.minecraft.server.command.CommandManager;
import net.minecraft.text.Text;
import net.minecraft.server.network.ServerPlayerEntity;
import net.minecraft.item.ItemStack;

/**
 * Fabric 모드용 명령어 시스템
 * NeoForge Commands를 Fabric Command API로 변환
 */
public class ModpackAICommands {
    
    /**
     * 명령어 등록
     */
    public static void register(CommandDispatcher<ServerCommandSource> dispatcher) {
        // /ai <message> 명령어
        dispatcher.register(CommandManager.literal("ai")
                .then(CommandManager.argument("message", StringArgumentType.greedyString())
                        .executes(ModpackAICommands::handleAICommand))
                .executes(ModpackAICommands::handleAICommandNoArgs));
        
        // /modpackai 명령어
        dispatcher.register(CommandManager.literal("modpackai")
                .executes(ModpackAICommands::handleModpackAICommand)
                .then(CommandManager.literal("give")
                        .executes(ModpackAICommands::handleGiveAIItem))
                .then(CommandManager.literal("help")
                        .executes(ModpackAICommands::handleHelpCommand))
                .then(CommandManager.literal("recipe")
                        .then(CommandManager.argument("item", StringArgumentType.string())
                                .executes(ModpackAICommands::handleRecipeCommand)))
                .then(CommandManager.literal("models")
                        .executes(ModpackAICommands::handleModelsCommand))
                .then(CommandManager.literal("status")
                        .executes(ModpackAICommands::handleStatusCommand))
                .then(CommandManager.literal("rag")
                        .then(CommandManager.literal("status")
                                .executes(ModpackAICommands::handleRAGStatusCommand))
                        .then(CommandManager.literal("build")
                                .then(CommandManager.argument("modpack_path", StringArgumentType.string())
                                        .executes(ModpackAICommands::handleRAGBuildCommand)))
                        .then(CommandManager.literal("list")
                                .executes(ModpackAICommands::handleRAGListCommand))
                        .then(CommandManager.literal("test")
                                .then(CommandManager.argument("query", StringArgumentType.greedyString())
                                        .executes(ModpackAICommands::handleRAGTestCommand)))));
    }
    
    /**
     * /ai <message> 명령어 처리
     */
    private static int handleAICommand(CommandContext<ServerCommandSource> context) throws CommandSyntaxException {
        String message = StringArgumentType.getString(context, "message");
        ServerPlayerEntity player = context.getSource().getPlayerOrThrow();
        
        ModpackAIMod.LOGGER.info("플레이어 {}가 AI 질문: {}", player.getName().getString(), message);
        
        // AI 응답 처리 (비동기)
        ModpackAIMod.getInstance().getAIManager()
                .askAIAsync(player.getUuidAsString(), message, getModpackName())
                .thenAccept(response -> {
                    // 메인 스레드에서 응답 전송
                    player.sendMessage(Text.literal("§6[AI] §f" + response));
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("AI 응답 처리 실패", throwable);
                    player.sendMessage(Text.literal("§c[AI] AI 응답 처리 중 오류가 발생했습니다."));
                    return null;
                });
        
        return 1; // 성공
    }
    
    /**
     * /ai (인수 없음) 명령어 처리 - GUI 열기 안내 (클라이언트는 별도 처리)
     */
    private static int handleAICommandNoArgs(CommandContext<ServerCommandSource> context) throws CommandSyntaxException {
        ServerPlayerEntity player = context.getSource().getPlayerOrThrow();
        
        player.sendMessage(Text.literal("§6[ModpackAI] §fAI 채팅을 시작하려면:"));
        player.sendMessage(Text.literal("§f- /ai <질문> - AI에게 바로 질문하기"));
        player.sendMessage(Text.literal("§f- AI 아이템 우클릭 - GUI 채팅창 열기"));
        player.sendMessage(Text.literal("§f- G키 - AI 채팅 GUI 열기 (클라이언트)"));
        
        return 1; // 성공
    }
    
    /**
     * /modpackai 기본 명령어
     */
    private static int handleModpackAICommand(CommandContext<ServerCommandSource> context) throws CommandSyntaxException {
        ServerPlayerEntity player = context.getSource().getPlayerOrThrow();
        
        player.sendMessage(Text.literal("§6=== ModpackAI Fabric 모드 ==="));
        player.sendMessage(Text.literal("§f/ai <질문> - AI에게 질문하기"));
        player.sendMessage(Text.literal("§f/modpackai help - 도움말 보기"));
        player.sendMessage(Text.literal("§f/modpackai give - AI 아이템 받기"));
        player.sendMessage(Text.literal("§f/modpackai recipe <아이템> - 제작법 보기"));
        
        return 1;
    }
    
    /**
     * AI 아이템 지급
     */
    private static int handleGiveAIItem(CommandContext<ServerCommandSource> context) throws CommandSyntaxException {
        ServerPlayerEntity player = context.getSource().getPlayerOrThrow();
        
        // AI 아이템 생성
        ItemStack aiItem = new ItemStack(ModpackAIMod.getInstance().getConfig().getAIItemMaterial());
        aiItem.setCustomName(Text.literal(ModpackAIMod.getInstance().getConfig().getAIItemName()));
        
        // 인벤토리에 추가
        if (player.getInventory().insertStack(aiItem)) {
            player.sendMessage(Text.literal("§a[ModpackAI] AI 아이템을 받았습니다!"));
            ModpackAIMod.LOGGER.info("플레이어 {}에게 AI 아이템 지급", player.getName().getString());
        } else {
            player.sendMessage(Text.literal("§c[ModpackAI] 인벤토리가 가득 차서 아이템을 받을 수 없습니다."));
        }
        
        return 1;
    }
    
    /**
     * 도움말 명령어
     */
    private static int handleHelpCommand(CommandContext<ServerCommandSource> context) throws CommandSyntaxException {
        ServerPlayerEntity player = context.getSource().getPlayerOrThrow();
        
        player.sendMessage(Text.literal("§6=== ModpackAI Fabric 도움말 ==="));
        player.sendMessage(Text.literal("§f"));
        player.sendMessage(Text.literal("§e기본 명령어:"));
        player.sendMessage(Text.literal("§f  /ai <질문> - AI에게 질문하기"));
        player.sendMessage(Text.literal("§f  /ai - AI 사용법 안내"));
        player.sendMessage(Text.literal("§f"));
        player.sendMessage(Text.literal("§e관리 명령어:"));
        player.sendMessage(Text.literal("§f  /modpackai give - AI 아이템 받기"));
        player.sendMessage(Text.literal("§f  /modpackai recipe <아이템> - 제작법 조회"));
        player.sendMessage(Text.literal("§f  /modpackai models - 사용 가능한 AI 모델 보기"));
        player.sendMessage(Text.literal("§f  /modpackai status - 시스템 상태 확인"));
        player.sendMessage(Text.literal("§f"));
        player.sendMessage(Text.literal("§6RAG 관리 명령어:"));
        player.sendMessage(Text.literal("§f  /modpackai rag status - RAG 시스템 상태"));
        player.sendMessage(Text.literal("§f  /modpackai rag build <경로> - 모드팩 분석"));
        player.sendMessage(Text.literal("§f  /modpackai rag list - 등록된 모드팩 목록"));
        player.sendMessage(Text.literal("§f  /modpackai rag test <검색어> - RAG 검색 테스트"));
        player.sendMessage(Text.literal("§f"));
        player.sendMessage(Text.literal("§7AI 아이템을 우클릭하거나 G키로 GUI를 열 수 있습니다!"));
        
        return 1;
    }
    
    /**
     * 제작법 조회 명령어
     */
    private static int handleRecipeCommand(CommandContext<ServerCommandSource> context) throws CommandSyntaxException {
        String itemName = StringArgumentType.getString(context, "item");
        ServerPlayerEntity player = context.getSource().getPlayerOrThrow();
        
        ModpackAIMod.LOGGER.info("플레이어 {}가 제작법 조회: {}", player.getName().getString(), itemName);
        
        player.sendMessage(Text.literal("§6[ModpackAI] §f" + itemName + "의 제작법을 검색 중..."));
        
        // 비동기 제작법 조회
        ModpackAIMod.getInstance().getAIManager()
                .getRecipeAsync(itemName)
                .thenAccept(recipeData -> {
                    if (recipeData.has("success") && recipeData.get("success").getAsBoolean()) {
                        // 제작법 정보 표시
                        player.sendMessage(Text.literal("§a[제작법] " + itemName));
                        if (recipeData.has("recipe")) {
                            player.sendMessage(Text.literal("§f" + recipeData.get("recipe").getAsString()));
                        }
                    } else {
                        String error = recipeData.has("error") ? recipeData.get("error").getAsString() : "제작법을 찾을 수 없습니다.";
                        player.sendMessage(Text.literal("§c[ModpackAI] " + error));
                    }
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("제작법 조회 실패", throwable);
                    player.sendMessage(Text.literal("§c[ModpackAI] 제작법 조회 중 오류가 발생했습니다."));
                    return null;
                });
        
        return 1;
    }
    
    /**
     * 모델 목록 조회
     */
    private static int handleModelsCommand(CommandContext<ServerCommandSource> context) throws CommandSyntaxException {
        ServerPlayerEntity player = context.getSource().getPlayerOrThrow();
        
        player.sendMessage(Text.literal("§6[ModpackAI] 사용 가능한 AI 모델 조회 중..."));
        
        // 비동기 모델 목록 조회
        ModpackAIMod.getInstance().getAIManager()
                .getAvailableModelsAsync()
                .thenAccept(modelsData -> {
                    if (modelsData.has("success") && modelsData.get("success").getAsBoolean()) {
                        player.sendMessage(Text.literal("§a=== 사용 가능한 AI 모델 ==="));
                        if (modelsData.has("models")) {
                            // 모델 목록 표시
                            modelsData.getAsJsonArray("models").forEach(modelElement -> {
                                player.sendMessage(Text.literal("§f- " + modelElement.getAsString()));
                            });
                        }
                    } else {
                        player.sendMessage(Text.literal("§c[ModpackAI] 모델 목록을 가져올 수 없습니다."));
                    }
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("모델 목록 조회 실패", throwable);
                    player.sendMessage(Text.literal("§c[ModpackAI] 모델 목록 조회 중 오류가 발생했습니다."));
                    return null;
                });
        
        return 1;
    }
    
    /**
     * 시스템 상태 확인
     */
    private static int handleStatusCommand(CommandContext<ServerCommandSource> context) throws CommandSyntaxException {
        ServerPlayerEntity player = context.getSource().getPlayerOrThrow();
        
        player.sendMessage(Text.literal("§6=== ModpackAI Fabric 시스템 상태 ==="));
        player.sendMessage(Text.literal("§f모드 버전: 1.0.0"));
        player.sendMessage(Text.literal("§f모드팩: " + getModpackName() + " v" + ModpackAIMod.getInstance().getConfig().getModpackVersion()));
        player.sendMessage(Text.literal("§f백엔드 URL: " + ModpackAIMod.getInstance().getConfig().getBackendUrl()));
        
        // 백엔드 상태 확인
        boolean healthy = ModpackAIMod.getInstance().getAIManager().isBackendHealthy();
        if (healthy) {
            player.sendMessage(Text.literal("§a백엔드 상태: 정상"));
        } else {
            player.sendMessage(Text.literal("§c백엔드 상태: 연결 실패"));
        }
        
        return 1;
    }
    
    private static int handleRAGStatusCommand(CommandContext<ServerCommandSource> context) throws CommandSyntaxException {
        ServerPlayerEntity player = context.getSource().getPlayerOrThrow();
        
        player.sendMessage(Text.literal("§6[ModpackAI] RAG 시스템 상태 조회 중..."));
        
        // 비동기 RAG 상태 조회
        ModpackAIMod.getInstance().getAIManager()
                .getRAGStatusAsync()
                .thenAccept(statusData -> {
                    if (statusData.has("success") && statusData.get("success").getAsBoolean()) {
                        player.sendMessage(Text.literal("§a=== RAG 시스템 상태 ==="));
                        
                        boolean gcpAvailable = statusData.has("gcp_rag_available") && statusData.get("gcp_rag_available").getAsBoolean();
                        boolean localEnabled = statusData.has("local_rag_enabled") && statusData.get("local_rag_enabled").getAsBoolean();
                        
                        player.sendMessage(Text.literal("§f- GCP RAG: " + (gcpAvailable ? "§a활성화됨" : "§c비활성화됨")));
                        player.sendMessage(Text.literal("§f- 로컬 RAG: " + (localEnabled ? "§a활성화됨" : "§c비활성화됨")));
                        
                    } else {
                        player.sendMessage(Text.literal("§c[ModpackAI] RAG 상태 조회 실패"));
                    }
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("RAG 상태 조회 실패", throwable);
                    player.sendMessage(Text.literal("§c[ModpackAI] RAG 상태 조회 중 오류 발생"));
                    return null;
                });
        
        return 1;
    }
    
    private static int handleRAGBuildCommand(CommandContext<ServerCommandSource> context) throws CommandSyntaxException {
        String modpackPath = StringArgumentType.getString(context, "modpack_path");
        ServerPlayerEntity player = context.getSource().getPlayerOrThrow();
        
        player.sendMessage(Text.literal("§6[ModpackAI] §f모드팩 분석 시작: " + modpackPath));
        player.sendMessage(Text.literal("§e⚠️ 이 작업은 시간이 오래 걸리고 GCP 비용이 발생할 수 있습니다."));
        
        // 비동기 인덱스 구축
        ModpackAIMod.getInstance().getAIManager()
                .buildRAGIndexAsync(getModpackName(), "1.0.0", modpackPath)
                .thenAccept(result -> {
                    if (result.has("success") && result.get("success").getAsBoolean()) {
                        int docCount = result.has("document_count") ? result.get("document_count").getAsInt() : 0;
                        player.sendMessage(Text.literal("§a[ModpackAI] ✅ RAG 인덱스 구축 완료!"));
                        player.sendMessage(Text.literal("§f📊 처리된 문서 수: " + docCount));
                    } else {
                        String error = result.has("error") ? result.get("error").getAsString() : "알 수 없는 오류";
                        player.sendMessage(Text.literal("§c[ModpackAI] ❌ RAG 인덱스 구축 실패: " + error));
                    }
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("RAG 인덱스 구축 실패", throwable);
                    player.sendMessage(Text.literal("§c[ModpackAI] RAG 인덱스 구축 중 심각한 오류 발생"));
                    return null;
                });
        
        return 1;
    }
    
    private static int handleRAGListCommand(CommandContext<ServerCommandSource> context) throws CommandSyntaxException {
        ServerPlayerEntity player = context.getSource().getPlayerOrThrow();
        
        player.sendMessage(Text.literal("§6[ModpackAI] 등록된 모드팩 목록 조회 중..."));
        
        // 비동기 모드팩 목록 조회
        ModpackAIMod.getInstance().getAIManager()
                .getRAGModpacksAsync()
                .thenAccept(listData -> {
                    if (listData.has("success") && listData.get("success").getAsBoolean()) {
                        var modpacks = listData.getAsJsonArray("modpacks");
                        int count = listData.has("count") ? listData.get("count").getAsInt() : 0;
                        
                        player.sendMessage(Text.literal("§a=== 등록된 모드팩 목록 (" + count + "개) ==="));
                        
                        if (count == 0) {
                            player.sendMessage(Text.literal("§e등록된 모드팩이 없습니다."));
                        } else {
                            for (int i = 0; i < modpacks.size(); i++) {
                                var modpack = modpacks.get(i).getAsJsonObject();
                                String name = modpack.has("modpack_name") ? modpack.get("modpack_name").getAsString() : "Unknown";
                                String version = modpack.has("modpack_version") ? modpack.get("modpack_version").getAsString() : "1.0.0";
                                int docCount = modpack.has("document_count") ? modpack.get("document_count").getAsInt() : 0;
                                
                                player.sendMessage(Text.literal("§f" + (i + 1) + ". " + name + " v" + version + " (" + docCount + "개 문서)"));
                            }
                        }
                    } else {
                        player.sendMessage(Text.literal("§c[ModpackAI] 모드팩 목록 조회 실패"));
                    }
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("RAG 모드팩 목록 조회 실패", throwable);
                    player.sendMessage(Text.literal("§c[ModpackAI] 모드팩 목록 조회 중 오류 발생"));
                    return null;
                });
        
        return 1;
    }
    
    private static int handleRAGTestCommand(CommandContext<ServerCommandSource> context) throws CommandSyntaxException {
        String query = StringArgumentType.getString(context, "query");
        ServerPlayerEntity player = context.getSource().getPlayerOrThrow();
        
        player.sendMessage(Text.literal("§6[ModpackAI] §fRAG 검색 테스트: \"" + query + "\""));
        
        // 비동기 RAG 테스트
        ModpackAIMod.getInstance().getAIManager()
                .testRAGSearchAsync(query, getModpackName(), "1.0.0")
                .thenAccept(testData -> {
                    if (testData.has("success") && testData.get("success").getAsBoolean()) {
                        int resultCount = testData.has("results_count") ? testData.get("results_count").getAsInt() : 0;
                        player.sendMessage(Text.literal("§a✅ RAG 검색 결과: " + resultCount + "개"));
                        
                        if (resultCount > 0 && testData.has("results")) {
                            var results = testData.getAsJsonArray("results");
                            for (int i = 0; i < Math.min(3, results.size()); i++) {
                                var result = results.get(i).getAsJsonObject();
                                double similarity = result.has("similarity") ? result.get("similarity").getAsDouble() : 0.0;
                                String docType = result.has("doc_type") ? result.get("doc_type").getAsString() : "unknown";
                                String text = result.has("text") ? result.get("text").getAsString() : "";
                                
                                if (text.length() > 100) text = text.substring(0, 100) + "...";
                                player.sendMessage(Text.literal("§f" + (i + 1) + ". [" + String.format("%.2f", similarity) + "] (" + docType + ") " + text));
                            }
                        } else {
                            player.sendMessage(Text.literal("§e관련 문서를 찾을 수 없습니다."));
                        }
                    } else {
                        String error = testData.has("error") ? testData.get("error").getAsString() : "알 수 없는 오류";
                        player.sendMessage(Text.literal("§c[ModpackAI] RAG 테스트 실패: " + error));
                    }
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("RAG 테스트 실패", throwable);
                    player.sendMessage(Text.literal("§c[ModpackAI] RAG 테스트 중 오류 발생"));
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