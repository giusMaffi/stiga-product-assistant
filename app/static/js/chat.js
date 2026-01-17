const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

// Genera session ID unico
const sessionId = 'session_' + Date.now();

// Formatta markdown in HTML
function formatMarkdown(text) {
    // Converti markdown in HTML con formattazione bella
    
    // 1. Rimuovi spazi multipli
    text = text.replace(/  +/g, ' ');
    
    // 2. Bold: **testo** 
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    // 3. Italic: *testo*
    text = text.replace(/\*([^\*\|]+?)\*/g, '<em>$1</em>');
    
    // 4. Links: [testo](url)
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

    // 5. Parsing tabelle Markdown
    const tableRegex = /\|(.+)\|[\r\n]+\|[-:\| ]+\|[\r\n]+((?:\|.+\|[\r\n]*)+)/g;
    text = text.replace(tableRegex, function(match, headerRow, bodyRows) {
        // Parse header
        const headers = headerRow.split('|').map(h => h.trim()).filter(h => h);
        
        // Parse body rows
        const rows = bodyRows.trim().split('\n').map(row => {
            return row.split('|').map(cell => cell.trim()).filter(cell => cell);
        });
        
        // Build HTML table
        let table = '<table class="comparison-table"><thead><tr>';
        headers.forEach(h => {
            table += `<th>${h}</th>`;
        });
        table += '</tr></thead><tbody>';
        
        rows.forEach(row => {
            table += '<tr>';
            row.forEach((cell, idx) => {
                table += `<td>${cell}</td>`;
            });
            table += '</tr>';
        });
        
        table += '</tbody></table>';
        return table;
    });
    
    // 5. Separa i blocchi principali (doppio a capo)
    let blocks = text.split('\n\n');
    
    let html = '';
    
    for (let block of blocks) {
        block = block.trim();
        if (!block) continue;
        
        // Già una tabella HTML? Lasciala così
        if (block.startsWith('<table')) {
            html += block;
            continue;
        }
        
        // È una lista con bullet points (•, -, *)?
        if (block.match(/^[•\-\*]/m) && !block.includes('|')) {
            let items = block.split('\n').filter(line => line.trim());
            html += '<ul>';
            for (let item of items) {
                // Rimuovi il bullet point
                item = item.replace(/^[•\-\*]\s*/, '');
                if (item.trim()) {
                    html += `<li>${item.trim()}</li>`;
                }
            }
            html += '</ul>';
        }
        // È un paragrafo normale
        else {
            // Sostituisci singoli a capo con <br>
            block = block.replace(/\n/g, '<br>');
            html += `<p>${block}</p>`;
        }
    }
    
    return html;
}

// Auto-scroll al fondo
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Aggiungi messaggio alla chat
function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Formatta markdown solo per messaggi assistente
    if (!isUser) {
        contentDiv.innerHTML = formatMarkdown(content);
    } else {
        contentDiv.innerHTML = content;
    }
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Mostra indicatore "typing..."
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant-message';
    typingDiv.id = 'typing-indicator';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
    
    typingDiv.appendChild(contentDiv);
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Formatta tabella comparativa
function formatComparisonTable(comparatorData) {
    if (!comparatorData || !comparatorData.prodotti) return '';
    
    const prodotti = comparatorData.prodotti;
    const attributi = comparatorData.attributi || [];
    const consiglio = comparatorData.consiglio || '';
    
    let html = '<div class="comparison-container">';
    
    // Tabella
    html += '<table class="comparison-table">';
    
    // Header con nomi prodotti
    html += '<thead><tr>';
    html += '<th>Caratteristica</th>';
    prodotti.forEach(p => {
        html += `<th>${p}</th>`;
    });
    html += '</tr></thead>';
    
    // Righe attributi
    html += '<tbody>';
    attributi.forEach(attr => {
        html += '<tr>';
        html += `<td>${attr.nome}</td>`;
        attr.valori.forEach((val, idx) => {
            const isWinner = attr.migliore === idx;
            const cellClass = isWinner ? 'winner-cell' : '';
            html += `<td class="${cellClass}">${val}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    
    // Verdetto finale
    if (consiglio) {
        html += `<div class="comparison-verdict"><strong>💡 Il mio consiglio:</strong> ${consiglio}</div>`;
    }
    
    html += '</div>';
    return html;
}

// Formatta prodotti come card HTML con immagini
function formatProductCards(products) {
    if (!products || products.length === 0) return '';
    
    let html = '<div class="products-section">';
    
    products.forEach(product => {
        // Immagine con fallback
        const imageUrl = product.image_url || 
                        (product.immagini && product.immagini[0]) || 
                        'https://via.placeholder.com/300x200/00A651/ffffff?text=STIGA';
        
        // Descrizione: taglia al primo punto dopo 150 caratteri
        let desc = product.descrizione || '';
        if (desc.length > 150) {
            // Trova il primo punto dopo posizione 150
            let cutPoint = desc.indexOf('.', 150);
            if (cutPoint > 0 && cutPoint < 300) {
                desc = desc.substring(0, cutPoint + 1);
            } else {
                // Se non trova punto, taglia a 200 e aggiungi ...
                desc = desc.substring(0, 200).trim() + '...';
            }
        }
        
        html += `
            <div class="product-card">
                <div class="product-image">
                    <img src="${imageUrl}" alt="${product.nome}" 
                         onerror="this.src='https://via.placeholder.com/300x200/00A651/ffffff?text=STIGA'">
                </div>
                <div class="product-info">
                    <h3>${product.nome}</h3>
                    ${product.categoria ? `<div class="product-category">${product.categoria}</div>` : ''}
                    <div class="product-description">${desc}</div>
                    ${product.prezzo ? `<div class="product-price">${product.prezzo}</div>` : ''}
                    <a href="${product.url}" target="_blank" class="product-link">
                        Scopri tutti i dettagli →
                    </a>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

// Gestisci invio messaggio
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = userInput.value.trim();
    if (!message) return;
    
    // Aggiungi messaggio utente
    addMessage(message, true);
    userInput.value = '';
    sendButton.disabled = true;
    
    // Mostra typing indicator
    showTypingIndicator();
    
    try {
        // Chiamata API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        
        if (!response.ok) {
            throw new Error('Errore nella risposta del server');
        }
        
        const data = await response.json();
        
        // Rimuovi typing indicator
        removeTypingIndicator();
        
        // Aggiungi risposta assistente (solo testo, formattato con markdown)
        addMessage(data.response, false);
        
        // Se c'è un comparatore, mostralo
        if (data.comparator) {
            const compDiv = document.createElement('div');
            compDiv.className = 'message assistant-message';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.innerHTML = formatComparisonTable(data.comparator);
            
            compDiv.appendChild(contentDiv);
            chatMessages.appendChild(compDiv);
            scrollToBottom();
        }
        
        // Aggiungi card prodotti SEPARATAMENTE come HTML grezzo
        if (data.products && data.products.length > 0) {
            const productsDiv = document.createElement('div');
            productsDiv.className = 'message assistant-message';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.innerHTML = formatProductCards(data.products);
            
            productsDiv.appendChild(contentDiv);
            chatMessages.appendChild(productsDiv);
            scrollToBottom();
        }
        
    } catch (error) {
        removeTypingIndicator();
        addMessage('Mi dispiace, si è verificato un errore. Riprova.', false);
        console.error('Errore:', error);
    } finally {
        sendButton.disabled = false;
        userInput.focus();
    }
});

// Focus automatico sull'input
userInput.focus();