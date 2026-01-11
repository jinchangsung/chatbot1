/**
 * chat.js
 * 실시간 대화 처리를 위한 프론트엔드 로직
 */

// 문서가 완전히 로드된 후 실행되도록 보장합니다.
$(document).ready(function() {

    // 메시지를 화면에 추가하는 함수
    function appendMessage(role, text) {
        let html = '';
        if (role === 'user') {
            // 사용자 메시지
            html = `<div class="msg-wrapper user-wrapper"><div class="message user">${text}</div></div>`;
        } else {
            // 봇 메시지: 줄바꿈 처리 및 아이콘 적용
            // index.html에서 정의한 BOT_ICON_URL 전역 변수를 사용합니다.
            html = `
                <div class="msg-wrapper bot-wrapper">
                    <img src="${BOT_ICON_URL}" class="chat-icon">
                    <div class="message bot">${text.replace(/\n/g, '<br>')}</div>
                </div>`;
        }
        // 채팅창에 메시지 추가 및 스크롤 하단 이동
        $('#chat-box').append(html);
        $('#chat-box').scrollTop($('#chat-box')[0].scrollHeight);
    }

    // 서버로 메시지를 전송하는 메인 함수
    function sendMessage() {
        const msgInput = $('#user-input');
        const msg = msgInput.val().trim();
        
        // 빈 메시지 방지
        if (!msg) return;

        // 1. 사용자 메시지를 먼저 화면에 표시
        appendMessage('user', msg);
        msgInput.val(''); // 입력창 초기화

        // 2. 서버에 AJAX 요청 전송
        $.ajax({
            url: '/chat',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ message: msg }),
            success: function(data) {
                // 성공 시 봇의 응답을 화면에 표시
                appendMessage('bot', data.reply);
            },
            error: function(xhr, status, error) {
                // 에러 처리
                console.error("Chat Error:", error);
                appendMessage('bot', '죄송합니다. 서버와 연결이 원활하지 않습니다. 잠시 후 다시 시도해 주세요.');
            }
        });
    }

    // --- 이벤트 리스너 등록 ---

    // 전송 버튼 클릭 시
    $('#send-btn').click(sendMessage);

    // 입력창에서 엔터 키 입력 시
    $('#user-input').keypress(function(e) {
        if(e.which == 13) { // Enter key code
            sendMessage();
            e.preventDefault(); // 폼 제출 기본 동작 방지
        }
    });
});
