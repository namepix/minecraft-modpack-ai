package com.modpackai.gui;

import com.modpackai.ModpackAIMod;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.api.distmarker.OnlyIn;
import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;
import java.util.List;

/**
 * NeoForge 모드용 AI 채팅 GUI
 * Bukkit Inventory GUI를 NeoForge Screen API로 변환
 */
@OnlyIn(Dist.CLIENT)
public class AIChatScreen extends Screen {
    private static final int INPUT_HEIGHT = 20;
    private static final int BUTTON_WIDTH = 80;
    private static final int BUTTON_HEIGHT = 20;
    private static final int MARGIN = 10;
    private static final int LEFT_PANEL_WIDTH = 180;
    private static final int GRID_CELL_SIZE = 18;
    private static final int CHAT_WIDTH = 300;
    private static final int CHAT_HEIGHT = 180;

    // 오른쪽: 채팅 영역
    private EditBox messageInput;
    private Button sendButton;
    private Button closeButton;
    private List<String> chatHistory;
    private int scrollPosition;

    // 왼쪽: 레시피 영역
    private EditBox recipeItemInput;
    private Button recipeFetchButton;
    private String recipeTitle = "레시피 (3x3)";
    private String recipeText = "아이템명을 입력하고 레시피 조회를 누르세요";
    private String[][] recipeGrid = new String[3][3];

    // 하단: 모델 선택 버튼
    private Button geminiButton;
    private Button openaiButton;
    private Button claudeButton;
    
    public AIChatScreen() {
        super(Component.literal("ModpackAI 채팅"));
        this.chatHistory = new ArrayList<>();
        this.scrollPosition = 0;
        
        // 초기 환영 메시지
        addChatMessage("§6[AI] 안녕하세요! 모드팩에 대해 궁금한 것이 있으면 언제든 물어보세요!");
    }
    
    @Override
    protected void init() {
        super.init();
        
        int centerX = this.width / 2;
        int usableWidth = this.width - (MARGIN * 3) - LEFT_PANEL_WIDTH; // 좌측 패널 제외한 우측 영역 + 간격
        int rightX = MARGIN * 2 + LEFT_PANEL_WIDTH;
        int rightWidth = Math.max(300, usableWidth);
        int chatTop = 40;
        int chatBottom = this.height - (MARGIN * 4) - INPUT_HEIGHT - BUTTON_HEIGHT; // 하단 버튼 영역 제외
        int chatHeight = Math.max(160, chatBottom - chatTop);
        
        // 메시지 입력 상자
        this.messageInput = new EditBox(
                this.font,
                rightX,
                chatTop + chatHeight + MARGIN,
                rightWidth - BUTTON_WIDTH - 5,
                INPUT_HEIGHT,
                Component.literal("메시지를 입력하세요...")
        );
        this.messageInput.setMaxLength(500);
        this.messageInput.setResponder(this::onMessageChanged);
        this.addWidget(this.messageInput);
        this.setInitialFocus(this.messageInput);
        
        // 전송 버튼
        this.sendButton = Button.builder(
                        Component.literal("전송"),
                        button -> sendMessage())
                .bounds(
                        rightX + rightWidth - BUTTON_WIDTH,
                        chatTop + chatHeight + MARGIN,
                        BUTTON_WIDTH,
                        BUTTON_HEIGHT)
                .build();
        this.addRenderableWidget(this.sendButton);
        
        // 닫기 버튼
        this.closeButton = Button.builder(
                        Component.literal("닫기"),
                        button -> this.onClose())
                .bounds(
                        rightX + rightWidth/2 - BUTTON_WIDTH/2,
                        chatTop + chatHeight + MARGIN + INPUT_HEIGHT + 5,
                        BUTTON_WIDTH,
                        BUTTON_HEIGHT)
                .build();
        this.addRenderableWidget(this.closeButton);
        
        // 좌측: 레시피 아이템 입력
        this.recipeItemInput = new EditBox(
                this.font,
                MARGIN,
                chatTop,
                LEFT_PANEL_WIDTH,
                INPUT_HEIGHT,
                Component.literal("���이템명을 입력...")
        );
        this.recipeItemInput.setMaxLength(100);
        this.addWidget(this.recipeItemInput);

        // 레시피 조회 버튼
        this.recipeFetchButton = Button.builder(
                        Component.literal("레시피 조회"),
                        button -> fetchRecipe())
                .bounds(
                        MARGIN,
                        chatTop + INPUT_HEIGHT + 4,
                        LEFT_PANEL_WIDTH,
                        BUTTON_HEIGHT)
                .build();
        this.addRenderableWidget(this.recipeFetchButton);

        // 모델 선택 버튼 (하단 좌측)
        int footerY = this.height - 24;
        this.geminiButton = Button.builder(Component.literal("Gemini"), b -> switchModel("gemini"))
                .bounds(MARGIN, footerY, 70, 18).build();
        this.openaiButton = Button.builder(Component.literal("OpenAI"), b -> switchModel("openai"))
                .bounds(MARGIN + 75, footerY, 70, 18).build();
        this.claudeButton = Button.builder(Component.literal("Claude"), b -> switchModel("claude"))
                .bounds(MARGIN + 150, footerY, 70, 18).build();
        this.addRenderableWidget(this.geminiButton);
        this.addRenderableWidget(this.openaiButton);
        this.addRenderableWidget(this.claudeButton);

        // 초기 상태에서는 전송 버튼 비활성화
        updateSendButton();
    }
    
    @Override
    public void render(@NotNull GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        // 배경 렌더링
        this.renderBackground(guiGraphics, mouseX, mouseY, partialTick);
        
        // 상단 바: 아이템 이름 + 모드팩명/버전 표시
        String header = "§6모드팩 AI 어시스턴트 - "
                + ModpackAIMod.getInstance().getConfig().getModpackName()
                + " v" + ModpackAIMod.getInstance().getConfig().getModpackVersion();
        guiGraphics.drawCenteredString(this.font, Component.literal(header), this.width / 2, 12, 0xFFFFFF);
        
        // 좌측 레시피 패널 렌더링
        int chatTop = 40;
        int leftX = MARGIN;
        int leftY = chatTop + INPUT_HEIGHT + 4 + BUTTON_HEIGHT + 6;
        int leftHeight = this.height - leftY - 40;
        guiGraphics.fill(leftX, leftY, leftX + LEFT_PANEL_WIDTH, leftY + leftHeight, 0x77000000);
        // 3x3 그리드 그리기 (텍스트 기반 슬롯 라벨)
        int gridStartX = leftX + (LEFT_PANEL_WIDTH - (GRID_CELL_SIZE * 3 + 4 * 2)) / 2;
        int gridStartY = leftY + 10;
        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 3; col++) {
                int cellX = gridStartX + col * (GRID_CELL_SIZE + 4);
                int cellY = gridStartY + row * (GRID_CELL_SIZE + 4);
                guiGraphics.fill(cellX, cellY, cellX + GRID_CELL_SIZE, cellY + GRID_CELL_SIZE, 0x55000000);
                guiGraphics.fill(cellX, cellY, cellX + GRID_CELL_SIZE, cellY + 1, 0xFFAAAAAA);
                guiGraphics.fill(cellX, cellY + GRID_CELL_SIZE - 1, cellX + GRID_CELL_SIZE, cellY + GRID_CELL_SIZE, 0xFFAAAAAA);
                guiGraphics.fill(cellX, cellY, cellX + 1, cellY + GRID_CELL_SIZE, 0xFFAAAAAA);
                guiGraphics.fill(cellX + GRID_CELL_SIZE - 1, cellY, cellX + GRID_CELL_SIZE, cellY + GRID_CELL_SIZE, 0xFFAAAAAA);
                // 슬롯 라벨(재료 약칭) 렌더링
                String label = recipeGrid[row][col];
                if (label != null && !label.isBlank()) {
                    int tx = cellX + 2;
                    int ty = cellY + 5;
                    guiGraphics.drawString(this.font, label.substring(0, Math.min(3, label.length())), tx, ty, 0xFFFFFF);
                }
            }
        }
        // 레시피 텍스트 표시
        guiGraphics.drawString(this.font, Component.literal(recipeTitle), leftX + 6, leftY + (GRID_CELL_SIZE * 3 + 4 * 2) + 20, 0xFFFFFF);
        renderWrappedText(guiGraphics, recipeText, leftX + 6, leftY + (GRID_CELL_SIZE * 3 + 4 * 2) + 36, LEFT_PANEL_WIDTH - 12);

        // 우측 채팅 패널 렌더링
        int rightX = MARGIN * 2 + LEFT_PANEL_WIDTH;
        int rightWidth = this.width - rightX - MARGIN;
        int chatY = chatTop;
        int chatHeight = this.height - chatY - (MARGIN * 4) - INPUT_HEIGHT - BUTTON_HEIGHT;
        guiGraphics.fill(rightX, chatY, rightX + rightWidth, chatY + chatHeight, 0x77000000);
        guiGraphics.fill(rightX, chatY, rightX + rightWidth, chatY + 1, 0xFFAAAAAA);
        guiGraphics.fill(rightX, chatY + chatHeight - 1, rightX + rightWidth, chatY + chatHeight, 0xFFAAAAAA);
        guiGraphics.fill(rightX, chatY, rightX + 1, chatY + chatHeight, 0xFFAAAAAA);
        guiGraphics.fill(rightX + rightWidth - 1, chatY, rightX + rightWidth, chatY + chatHeight, 0xFFAAAAAA);
        
        // 채팅 내용 렌더링
        renderChatMessages(guiGraphics, rightX + 5, chatY + 5, rightWidth - 10, chatHeight - 10);
        
        // 위젯들 렌더링
        super.render(guiGraphics, mouseX, mouseY, partialTick);
        
        // 하단 바: 현재 모델 및 연결 상태
        String status = getConnectionStatus();
        String model = "모델: " + ModpackAIMod.getInstance().getConfig().getPrimaryModel();
        String footer = status + "  |  " + model + "  |  Enter=전송, Esc=닫기";
        guiGraphics.drawString(this.font, footer, 10, this.height - 20, 0xFFAAAAAA);
    }
    
    /**
     * 채팅 메시지들 렌더링
     */
    private void renderChatMessages(GuiGraphics guiGraphics, int x, int y, int width, int height) {
        int lineHeight = this.font.lineHeight + 2;
        int maxLines = height / lineHeight;
        
        // 스크롤 위치 계산
        int startIndex = Math.max(0, chatHistory.size() - maxLines + scrollPosition);
        int endIndex = Math.min(chatHistory.size(), startIndex + maxLines);
        
        for (int i = startIndex; i < endIndex; i++) {
            String message = chatHistory.get(i);
            int yPos = y + (i - startIndex) * lineHeight;
            
            // 메시지가 너무 길면 줄바꿈
            List<String> wrappedLines = wrapText(message, width);
            for (int j = 0; j < wrappedLines.size() && yPos < y + height - lineHeight; j++) {
                guiGraphics.drawString(this.font, wrappedLines.get(j), x, yPos, 0xFFFFFFFF);
                yPos += lineHeight;
            }
        }
    }
    
    /**
     * 텍스트 줄바꿈 처리
     */
    private List<String> wrapText(String text, int maxWidth) {
        List<String> lines = new ArrayList<>();
        String[] words = text.split(" ");
        StringBuilder currentLine = new StringBuilder();
        
        for (String word : words) {
            String testLine = currentLine.length() == 0 ? word : currentLine + " " + word;
            if (this.font.width(testLine) <= maxWidth) {
                if (currentLine.length() > 0) {
                    currentLine.append(" ");
                }
                currentLine.append(word);
            } else {
                if (currentLine.length() > 0) {
                    lines.add(currentLine.toString());
                    currentLine = new StringBuilder(word);
                } else {
                    lines.add(word);
                }
            }
        }
        
        if (currentLine.length() > 0) {
            lines.add(currentLine.toString());
        }
        
        return lines;
    }

    /**
     * 좌측 패널 래핑 텍스트 렌더링
     */
    private void renderWrappedText(GuiGraphics guiGraphics, String text, int x, int y, int maxWidth) {
        List<String> lines = wrapText(text, maxWidth);
        int lineHeight = this.font.lineHeight + 2;
        int yPos = y;
        for (String line : lines) {
            guiGraphics.drawString(this.font, line, x, yPos, 0xFFFFFFFF);
            yPos += lineHeight;
        }
    }
    
    /**
     * 메시지 입력 변경 처리
     */
    private void onMessageChanged(String message) {
        updateSendButton();
    }
    
    /**
     * 전송 버튼 상태 업데이트
     */
    private void updateSendButton() {
        String message = this.messageInput.getValue().trim();
        this.sendButton.active = !message.isEmpty() && getConnectionStatus().contains("연결됨");
    }
    
    /**
     * 메시지 전송
     */
    private void sendMessage() {
        String message = this.messageInput.getValue().trim();
        if (message.isEmpty()) {
            return;
        }
        
        // 사용자 메시지 표시
        addChatMessage("§a[나] §f" + message);
        this.messageInput.setValue("");
        
        // 처리 중 메시지
        addChatMessage("§7[AI] 응답을 생성하는 중...");
        
        // AI에게 메시지 전송 (비동기)
        String playerUuid = "client-player"; // 클라이언트에서는 임시 UUID
        ModpackAIMod.getInstance().getAIManager()
                .askAIAsync(playerUuid, message, "Unknown Modpack")
                .thenAccept(response -> {
                    // 마지막 "처리 중" 메시지 제거
                    if (!chatHistory.isEmpty() && chatHistory.get(chatHistory.size() - 1).contains("응답을 생성하는 중")) {
                        chatHistory.remove(chatHistory.size() - 1);
                    }
                    
                    // AI 응답 표시
                    addChatMessage("§6[AI] §f" + response);
                })
                .exceptionally(throwable -> {
                    ModpackAIMod.LOGGER.error("AI 응답 처리 실패", throwable);
                    
                    // 마지막 "처리 중" 메시지 제거
                    if (!chatHistory.isEmpty() && chatHistory.get(chatHistory.size() - 1).contains("응답을 생성하는 중")) {
                        chatHistory.remove(chatHistory.size() - 1);
                    }
                    
                    addChatMessage("§c[AI] 응답 처리 중 오류가 발생했습니다.");
                    return null;
                });
        
        updateSendButton();
    }

    /**
     * 레시피 조회
     */
    private void fetchRecipe() {
        String item = this.recipeItemInput != null ? this.recipeItemInput.getValue().trim() : "";
        if (item.isEmpty()) {
            this.recipeText = "아이템명을 입력하세요";
            return;
        }
        this.recipeTitle = "레시피: " + item;
        this.recipeText = "조회 중...";
        ModpackAIMod.getInstance().getAIManager()
                .getRecipeAsync(item)
                .thenAccept(data -> {
                    try {
                        boolean ok = data.has("success") && data.get("success").getAsBoolean();
                        if (ok && data.has("recipe") && data.getAsJsonObject("recipe").has("recipe")) {
                            var recipeObj = data.getAsJsonObject("recipe");
                            this.recipeText = recipeObj.get("recipe").getAsString();
                            // grid가 있다면 표시용 라벨 업데이트
                            if (recipeObj.has("grid") && recipeObj.get("grid").isJsonArray()) {
                                var grid = recipeObj.getAsJsonArray("grid");
                                for (int r = 0; r < Math.min(3, grid.size()); r++) {
                                    var row = grid.get(r).getAsJsonArray();
                                    for (int c = 0; c < Math.min(3, row.size()); c++) {
                                        var cell = row.get(c);
                                        this.recipeGrid[r][c] = cell.isJsonNull() ? null : cell.getAsString();
                                    }
                                }
                            } else {
                                // 텍스트만 있을 경우 기존 그리드 초기화
                                this.recipeGrid = new String[3][3];
                            }
                        } else {
                            this.recipeText = "레시피를 찾을 수 없습니다";
                            this.recipeGrid = new String[3][3];
                        }
                    } catch (Exception e) {
                        this.recipeText = "레시피 처리 중 오류";
                        this.recipeGrid = new String[3][3];
                    }
                })
                .exceptionally(t -> {
                    this.recipeText = "레시피 조회 실패";
                    this.recipeGrid = new String[3][3];
                    return null;
                });
    }

    /**
     * 모델 전환
     */
    private void switchModel(String modelId) {
        ModpackAIMod.getInstance().getAIManager()
                .switchModelAsync(modelId)
                .thenAccept(resp -> {
                    boolean ok = resp.has("success") && resp.get("success").getAsBoolean();
                    if (ok) {
                        addChatMessage("§7[시스템] 모델 전환 완료: " + modelId);
                    } else {
                        addChatMessage("§c[시스템] 모델 전환 실패");
                    }
                    updateSendButton();
                })
                .exceptionally(t -> {
                    addChatMessage("§c[시스템] 모델 전환 중 오류");
                    return null;
                });
    }
    
    /**
     * 채팅에 메시지 추가
     */
    private void addChatMessage(String message) {
        chatHistory.add(message);
        
        // 최대 100개 메시지만 보관
        if (chatHistory.size() > 100) {
            chatHistory.remove(0);
        }
        
        // 자동 스크롤
        scrollPosition = 0;
    }
    
    /**
     * 연결 상태 문자열 반환
     */
    private String getConnectionStatus() {
        boolean healthy = ModpackAIMod.getInstance().getAIManager().isBackendHealthy();
        return healthy ? "§a백엔드: 연결됨" : "§c백엔드: 연결 실패";
    }
    
    @Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        // Enter 키로 메시지 전송
        if (keyCode == 257 && this.messageInput.isFocused()) { // Enter key
            if (this.sendButton.active) {
                sendMessage();
                return true;
            }
        }
        
        // Escape 키로 닫기
        if (keyCode == 256) { // Escape key
            this.onClose();
            return true;
        }
        
        return super.keyPressed(keyCode, scanCode, modifiers);
    }
    
    @Override
    public boolean mouseScrolled(double mouseX, double mouseY, double scrollX, double scrollY) {
        // 채팅 영역에서 스크롤
        int chatX = this.width / 2 - 150;
        int chatY = this.height / 2 - CHAT_HEIGHT / 2;
        
        if (mouseX >= chatX && mouseX <= chatX + 300 && mouseY >= chatY && mouseY <= chatY + CHAT_HEIGHT) {
            scrollPosition = Math.max(-10, Math.min(10, scrollPosition - (int) scrollY));
            return true;
        }
        
        return super.mouseScrolled(mouseX, mouseY, scrollX, scrollY);
    }
    
    @Override
    public boolean isPauseScreen() {
        // 게임을 일시정지하지 않음
        return false;
    }
}