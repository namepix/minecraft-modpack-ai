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
    private static final int CHAT_HEIGHT = 200;
    private static final int INPUT_HEIGHT = 20;
    private static final int BUTTON_WIDTH = 80;
    private static final int BUTTON_HEIGHT = 20;
    private static final int MARGIN = 10;
    
    private EditBox messageInput;
    private Button sendButton;
    private Button closeButton;
    private List<String> chatHistory;
    private int scrollPosition;
    
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
        int centerY = this.height / 2;
        
        // 메시지 입력 상자
        this.messageInput = new EditBox(
                this.font,
                centerX - 150,
                centerY + CHAT_HEIGHT / 2 + MARGIN,
                300 - BUTTON_WIDTH - 5,
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
                        centerX + 150 - BUTTON_WIDTH,
                        centerY + CHAT_HEIGHT / 2 + MARGIN,
                        BUTTON_WIDTH,
                        BUTTON_HEIGHT)
                .build();
        this.addRenderableWidget(this.sendButton);
        
        // 닫기 버튼
        this.closeButton = Button.builder(
                        Component.literal("닫기"),
                        button -> this.onClose())
                .bounds(
                        centerX - BUTTON_WIDTH / 2,
                        centerY + CHAT_HEIGHT / 2 + MARGIN + INPUT_HEIGHT + 5,
                        BUTTON_WIDTH,
                        BUTTON_HEIGHT)
                .build();
        this.addRenderableWidget(this.closeButton);
        
        // 초기 상태에서는 전송 버튼 비활성화
        updateSendButton();
    }
    
    @Override
    public void render(@NotNull GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        // 배경 렌더링
        this.renderBackground(guiGraphics, mouseX, mouseY, partialTick);
        
        // 제목 렌더링
        guiGraphics.drawCenteredString(
                this.font,
                this.title,
                this.width / 2,
                20,
                0xFFFFFF
        );
        
        // 채팅 영역 배경
        int chatX = this.width / 2 - 150;
        int chatY = this.height / 2 - CHAT_HEIGHT / 2;
        guiGraphics.fill(chatX, chatY, chatX + 300, chatY + CHAT_HEIGHT, 0x77000000);
        guiGraphics.fill(chatX, chatY, chatX + 300, chatY + 1, 0xFFAAAAAA); // 상단 테두리
        guiGraphics.fill(chatX, chatY + CHAT_HEIGHT - 1, chatX + 300, chatY + CHAT_HEIGHT, 0xFFAAAAAA); // 하단 테두리
        guiGraphics.fill(chatX, chatY, chatX + 1, chatY + CHAT_HEIGHT, 0xFFAAAAAA); // 좌측 테두리
        guiGraphics.fill(chatX + 299, chatY, chatX + 300, chatY + CHAT_HEIGHT, 0xFFAAAAAA); // 우측 테두리
        
        // 채팅 내용 렌더링
        renderChatMessages(guiGraphics, chatX + 5, chatY + 5, 290, CHAT_HEIGHT - 10);
        
        // 위젯들 렌더링
        super.render(guiGraphics, mouseX, mouseY, partialTick);
        
        // 상태 표시
        String status = getConnectionStatus();
        guiGraphics.drawString(
                this.font,
                status,
                10,
                this.height - 20,
                0xFFAAAAAA
        );
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