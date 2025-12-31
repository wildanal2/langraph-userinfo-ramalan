(function() {
    'use strict';

    class KreaChatWidget {
        constructor(config = {}) {
            this.apiUrl = config.apiUrl || 'http://localhost:8000';
            this.logoUrl = config.logoUrl || '/static/widget/images/iccn-ai.png';
            this.sessionId = localStorage.getItem('krea_session_id') || null;
            this.sessionState = null;
            this.init();
        }

        init() {
            this.injectStyles();
            this.createWidget();
            this.attachEventListeners();
            this.autoOpenForNewUser();
        }

        autoOpenForNewUser() {
            if (!this.sessionId) {
                setTimeout(() => {
                    document.getElementById('kreaChatWidget').classList.add('active');
                    this.initChat();
                }, 500);
            }
        }

        injectStyles() {
            if (!document.getElementById('krea-widget-styles')) {
                const link = document.createElement('link');
                link.id = 'krea-widget-styles';
                link.rel = 'stylesheet';
                link.href = '/static/widget/css/widget.css';
                document.head.appendChild(link);
            }
        }

        createWidget() {
            const widgetHTML = `
                <div id="kreaChatBubble" class="krea-chat-bubble">
                    <img src="/static/widget/images/iccn-ai.png" alt="Krea.ai" style="width: 52px; height: 52px; display: block;">
                </div>
                <div id="kreaChatWidget" class="krea-chat-widget">
                    <div class="krea-chat-header">
                        <div class="krea-chat-header-info">
                            <img src="${this.logoUrl}" alt="Krea.ai" class="krea-chat-logo">
                            <div>
                                <h3 class="krea-chat-title">ICCN AI</h3>
                                <p class="krea-chat-subtitle">Asisten Cerdas & Ramalan Digital Nusantara</p>
                            </div>
                        </div>
                        <button id="kreaChatClose" class="krea-chat-close">
                            <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                    <div id="kreaChatMessages" class="krea-chat-messages"></div>
                    <div class="krea-chat-input-area">
                        <div class="krea-chat-input-wrapper">
                            <input type="text" id="kreaChatInput" class="krea-chat-input" placeholder="Ketik pesan...">
                            <button id="kreaChatSend" class="krea-chat-send">Kirim</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', widgetHTML);
        }

        attachEventListeners() {
            document.getElementById('kreaChatBubble').addEventListener('click', () => this.toggleWidget());
            document.getElementById('kreaChatClose').addEventListener('click', () => this.toggleWidget());
            document.getElementById('kreaChatSend').addEventListener('click', () => this.sendMessage());
            document.getElementById('kreaChatInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.sendMessage();
            });
        }

        toggleWidget() {
            const widget = document.getElementById('kreaChatWidget');
            const isActive = widget.classList.toggle('active');
            if (isActive && document.getElementById('kreaChatMessages').children.length === 0) {
                this.initChat();
            }
        }

        async initChat() {
            const messagesContainer = document.getElementById('kreaChatMessages');
            messagesContainer.innerHTML = '';
            const botBubble = this.addMessage('<span class="krea-typing-dots"><span>.</span><span>.</span><span>.</span></span>', false);
            let fullResponse = '';

            try {
                const response = await fetch(`${this.apiUrl}/start-message`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ session_id: this.sessionId })
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = JSON.parse(line.slice(6));
                            
                            if (data.error) {
                                botBubble.innerHTML = `<span style="color: #fca5a5;">Error: ${data.error}</span>`;
                                break;
                            }
                            
                            if (!data.done) {
                                if (Array.isArray(data.content)) {
                                    fullResponse += data.content.map(c => c.text || '').join('');
                                } else if (typeof data.content === 'string') {
                                    fullResponse += data.content;
                                }
                                botBubble.innerHTML = this.parseBold(fullResponse);
                            } else {
                                if (data.session_id) {
                                    this.sessionId = data.session_id;
                                    localStorage.setItem('krea_session_id', this.sessionId);
                                }
                                if (data.interactive_options) {
                                    setTimeout(() => this.renderInteractiveOptions(data.interactive_options), 300);
                                }
                            }
                        }
                    }
                }
            } catch (error) {
                console.error('Init error:', error);
                botBubble.innerHTML = '<span style="color: #fca5a5;">Terjadi kesalahan</span>';
            }
        }

        addMessage(content, isUser = false) {
            const messagesContainer = document.getElementById('kreaChatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `krea-message ${isUser ? 'user' : 'bot'}`;
            
            if (!isUser) {
                const avatar = document.createElement('img');
                avatar.src = this.logoUrl;
                avatar.className = 'krea-bot-avatar';
                messageDiv.appendChild(avatar);
            }
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'krea-message-content';
            
            const bubble = document.createElement('div');
            bubble.className = 'krea-message-bubble';
            bubble.innerHTML = content;
            
            const time = document.createElement('div');
            time.className = 'krea-message-time';
            time.textContent = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
            
            contentDiv.appendChild(bubble);
            contentDiv.appendChild(time);
            
            messageDiv.appendChild(contentDiv);
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
            
            return bubble;
        }

        async sendMessage() {
            const input = document.getElementById('kreaChatInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            this.disableAllInteractiveButtons();
            
            this.addMessage(message, true);
            input.value = '';
            input.disabled = true;

            const botBubble = this.addMessage('<span class="krea-typing-dots"><span>.</span><span>.</span><span>.</span></span>', false);
            let fullResponse = '';
            let separatorRendered = false;

            try {
                const response = await fetch(`${this.apiUrl}/chat/stream`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        message, 
                        session_id: this.sessionId, 
                        session_state: this.sessionState 
                    })
                });

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;

                    const chunk = decoder.decode(value);
                    const lines = chunk.split('\n');

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = JSON.parse(line.slice(6));
                            
                            if (data.error) {
                                botBubble.innerHTML = `<span style="color: #fca5a5;">Error: ${data.error}</span>`;
                                break;
                            }
                            
                            if (!data.done) {
                                if (Array.isArray(data.content)) {
                                    fullResponse += data.content.map(c => c.text || '').join('');
                                } else if (typeof data.content === 'string') {
                                    fullResponse += data.content;
                                }
                                
                                const parsed = this.parseAndRenderSeparator(fullResponse);
                                
                                if (parsed.hasSeparator && !separatorRendered) {
                                    const messagesContainer = document.getElementById('kreaChatMessages');
                                    const separatorDiv = document.createElement('div');
                                    separatorDiv.className = 'krea-separator';
                                    separatorDiv.innerHTML = `<span>${parsed.separatorText}</span>`;
                                    messagesContainer.insertBefore(separatorDiv, botBubble.closest('.krea-message'));
                                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                                    separatorRendered = true;
                                    fullResponse = parsed.content;
                                }
                                
                                botBubble.innerHTML = this.parseBold(parsed.content);
                            } else {
                                this.sessionState = data.session_state;
                                if (data.session_id) {
                                    this.sessionId = data.session_id;
                                    localStorage.setItem('krea_session_id', this.sessionId);
                                }
                                
                                if (data.interactive_options) {
                                    setTimeout(() => this.renderInteractiveOptions(data.interactive_options, data.fortune_full), 300);
                                }
                            }
                        }
                    }
                }
            } catch (error) {
                botBubble.innerHTML = `<span style="color: #fca5a5;">Error: ${error.message}</span>`;
            } finally {
                input.disabled = false;
                input.focus();
            }
        }

        async resetChat() {
            try {
                if (this.sessionId) {
                    await fetch(`${this.apiUrl}/reset`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ session_id: this.sessionId })
                    });
                }
                this.sessionState = null;
                this.sessionId = null;
                localStorage.removeItem('krea_session_id');
                this.initChat();
            } catch (error) {
                console.error('Reset error:', error);
            }
        }

        parseBold(text) {
            return text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        }

        parseAndRenderSeparator(text) {
            const separatorMatch = text.match(/\[SEPARATOR:(.+?)\]/);
            if (separatorMatch) {
                const separatorText = separatorMatch[1];
                const contentAfter = text.replace(/\[SEPARATOR:.+?\]/, '');
                return { hasSeparator: true, separatorText, content: contentAfter };
            }
            return { hasSeparator: false, content: text };
        }

        disableAllInteractiveButtons() {
            const allOptions = document.querySelectorAll('.krea-options');
            allOptions.forEach(optionDiv => {
                const buttons = optionDiv.querySelectorAll('button');
                buttons.forEach(btn => {
                    btn.disabled = true;
                    btn.style.opacity = '0.5';
                    btn.style.cursor = 'not-allowed';
                });
            });
        }

        selectOption(value) {
            document.getElementById('kreaChatInput').value = value;
            this.sendMessage();
        }

        startFortune() {
            document.getElementById('kreaChatInput').value = 'Ramalan Karir';
            this.sendMessage();
        }

        renderInteractiveOptions(options, fortuneData) {
            const container = document.getElementById('kreaChatMessages');
            const optionsDiv = document.createElement('div');
            optionsDiv.className = 'krea-options';

            if (options.type === 'quick_reply') {
                optionsDiv.innerHTML = options.options.map(opt => 
                    `<button class="krea-option-btn" onclick="window.kreaWidget.selectOption('${opt}')">${opt}</button>`
                ).join('');
            } else if (options.type === 'fortune_trigger') {
                optionsDiv.innerHTML = `
                    <button class="krea-fortune-btn" onclick="window.kreaWidget.startFortune()">
                        ${options.text}
                    </button>
                `;
            } else if (options.type === 'sso_button') {
                optionsDiv.innerHTML = `
                    <a href="${options.url}" target="_blank" class="krea-sso-btn">
                        ${options.text}
                    </a>
                `;
            }

            container.appendChild(optionsDiv);
            container.scrollTop = container.scrollHeight;
        }
    }

    // Auto-initialize
    window.addEventListener('load', () => {
        window.kreaWidget = new KreaChatWidget({
            apiUrl: window.KREA_API_URL || 'http://localhost:8000'
        });
    });
})();