package com.modpackai.gui;

import com.modpackai.ModpackAIMod;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.network.chat.Component;
import net.fabricmc.api.EnvType;
import net.fabricmc.api.Environment;

/**
 * Fabric용 AI 채팅 GUI 화면
 * 간단한 텍스트 입력과 응답 표시
 */
@Environment(EnvType.CLIENT)
public class AIChatScreen extends Screen {
    private EditBox messageInput;
    private Button sendButton;
    private String lastResponse = "AI에게 질문해보세요!";
    
    public AIChatScreen() {
        super(Component.literal("ModpackAI 채팅"));
    }
    
    @Override
    protected void init() {
        super.init();
        
        int centerX = this.width / 2;
        int centerY = this.height / 2;
        
        // 메시지 입력 필드
        this.messageInput = new EditBox(this.font, centerX - 150, centerY - 10, 300, 20, Component.literal("메시지 입력"));
        this.messageInput.setMaxLength(500);
        this.messageInput.setHint(Component.literal("AI에게 질문을 입력하세요..."));
        this.addRenderableWidget(this.messageInput);
        
        // 전송 버튼
        this.sendButton = Button.builder(Component.literal("전송"), this::onSendMessage)
                .bounds(centerX - 50, centerY + 20, 100, 20)
                .build();
        this.addRenderableWidget(this.sendButton);
        
        // 닫기 버튼
        Button closeButton = Button.builder(Component.literal("닫기"), (button) -> this.onClose())
                .bounds(centerX - 50, centerY + 50, 100, 20)
                .build();
        this.addRenderableWidget(closeButton);
        
        // 입력 필드에 포커스
        this.setInitialFocus(this.messageInput);
    }
    
    private void onSendMessage(Button button) {
        String message = this.messageInput.getValue().trim();
        if (message.isEmpty()) {
            return;
        }
        
        // 입력 필드 비우기
        this.messageInput.setValue("");
        this.lastResponse = "처리 중...";
        
        // AI에게 질문 (비동기)
        if (this.minecraft != null && this.minecraft.player != null) {
            ModpackAIMod.getInstance().getAIManager()
                    .askAIAsync(this.minecraft.player.getStringUUID(), message, "Unknown Modpack")
                    .thenAccept(response -> {
                        // 응답이 너무 길면 줄여서 표시
                        this.lastResponse = response.length() > 300 ? 
                                response.substring(0, 300) + "..." : response;
                    })
                    .exceptionally(throwable -> {
                        this.lastResponse = "AI 응답 처리 중 오류가 발생했습니다.";
                        return null;
                    });
        }
    }
    
    @Override
    public void render(GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        // 배경 그리기
        this.renderBackground(guiGraphics, mouseX, mouseY, partialTick);
        
        // 제목 표시
        guiGraphics.drawCenteredString(this.font, this.title, this.width / 2, 20, 0xFFFFFF);
        
        // AI 응답 표시 (여러 줄 지원)
        int responseY = this.height / 2 - 60;
        String[] lines = wrapText(this.lastResponse, 60); // 60자 기준으로 줄바꿈
        for (int i = 0; i < lines.length && i < 5; i++) { // 최대 5줄까지 표시
            guiGraphics.drawCenteredString(this.font, lines[i], this.width / 2, responseY + (i * 12), 0xCCCCCC);
        }
        
        super.render(guiGraphics, mouseX, mouseY, partialTick);
    }
    
    @Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        // Enter 키로 전송
        if (keyCode == 257 && this.messageInput.isFocused()) { // 257 = Enter
            this.onSendMessage(this.sendButton);
            return true;
        }
        return super.keyPressed(keyCode, scanCode, modifiers);
    }
    
    @Override
    public boolean isPauseScreen() {
        return false; // 게임을 일시정지하지 않음
    }
    
    /**
     * 텍스트를 지정된 길이로 줄바꿈
     */
    private String[] wrapText(String text, int maxLength) {
        if (text.length() <= maxLength) {
            return new String[]{text};
        }
        
        java.util.List<String> lines = new java.util.ArrayList<>();
        String[] words = text.split(" ");
        StringBuilder currentLine = new StringBuilder();
        
        for (String word : words) {
            if (currentLine.length() + word.length() + 1 > maxLength) {
                if (currentLine.length() > 0) {
                    lines.add(currentLine.toString());
                    currentLine = new StringBuilder(word);
                } else {
                    // 단어 자체가 너무 긴 경우
                    lines.add(word);
                }
            } else {
                if (currentLine.length() > 0) {
                    currentLine.append(" ");
                }
                currentLine.append(word);
            }
        }
        
        if (currentLine.length() > 0) {
            lines.add(currentLine.toString());
        }
        
        return lines.toArray(new String[0]);
    }
}