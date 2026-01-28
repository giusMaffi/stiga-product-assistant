// ===== POSTGRESQL ANALYTICS TRACKING =====
async function trackProductClick(productId, productName, productCategory) {
    try {
        await fetch('/api/track/click', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                product_name: productName,
                product_id: productId || '',
                product_category: productCategory || '',
                language: document.getElementById('language-selector').value
            })
        });
    } catch (error) {
        console.error('Track click error:', error);
    }
}

async function trackSessionStart() {
    try {
        await fetch('/api/track/session', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: sessionId,
                language: document.getElementById('language-selector').value
            })
        });
    } catch (error) {
        console.error('Track session error:', error);
    }
}

// ===== TRADUZIONI MULTILINGUA =====
const translations = {
    it: {
        welcomeTitle: "Ciao! 👋 Sono il tuo consulente STIGA, esperto di giardinaggio dal 1934.",
        welcomeSubtitle: "<strong>Cosa posso fare per te:</strong>",
        features: [
            "🔍 <strong>Trovare il prodotto perfetto</strong> — dimmi le tue esigenze e ti guido alla scelta migliore",
            "⚖️ <strong>Confrontare prodotti</strong> — \"Confronta l'A 6v con l'A 8v\" e ti mostro tutte le differenze",
            "💰 <strong>Rispettare il tuo budget</strong> — \"Ho 1000€, cosa mi consigli?\"",
            "📚 <strong>Darti consigli esperti</strong> — potatura, cura del prato, manutenzione stagionale",
            "❓ <strong>Rispondere ai tuoi dubbi</strong> — sicurezza, tecnologie, installazione"
        ],
        categories: "<strong>Categorie prodotti:</strong> Robot tagliaerba • Tagliaerba • Trattorini • Decespugliatori • Motoseghe • Tagliasiepi • Idropulitrici • Soffiatori • e molto altro!",
        languageNote: "Scrivi pure in qualsiasi lingua — risponderò nella tua! 🌍",
        startPrompt: "<em>Inizia descrivendomi il tuo giardino o cosa stai cercando...</em>",
        placeholder: "Scrivi qui la tua domanda...",
        sendButton: "Invia →"
    },
    en: {
        welcomeTitle: "Hello! 👋 I'm your STIGA consultant, gardening expert since 1934.",
        welcomeSubtitle: "<strong>What I can do for you:</strong>",
        features: [
            "🔍 <strong>Find the perfect product</strong> — tell me your needs and I'll guide you to the best choice",
            "⚖️ <strong>Compare products</strong> — \"Compare A 6v with A 8v\" and I'll show you all the differences",
            "💰 <strong>Respect your budget</strong> — \"I have €1000, what do you recommend?\"",
            "📚 <strong>Give expert advice</strong> — pruning, lawn care, seasonal maintenance",
            "❓ <strong>Answer your questions</strong> — safety, technologies, installation"
        ],
        categories: "<strong>Product categories:</strong> Robot mowers • Lawn mowers • Ride-on mowers • Brush cutters • Chainsaws • Hedge trimmers • Pressure washers • Blowers • and much more!",
        languageNote: "Write in any language — I'll respond in yours! 🌍",
        startPrompt: "<em>Start by describing your garden or what you're looking for...</em>",
        placeholder: "Type your question here...",
        sendButton: "Send →"
    },
    de: {
        welcomeTitle: "Hallo! 👋 Ich bin Ihr STIGA-Berater, Gartenexperte seit 1934.",
        welcomeSubtitle: "<strong>Was ich für Sie tun kann:</strong>",
        features: [
            "🔍 <strong>Das perfekte Produkt finden</strong> — teilen Sie mir Ihre Bedürfnisse mit und ich führe Sie zur besten Wahl",
            "⚖️ <strong>Produkte vergleichen</strong> — \"Vergleiche A 6v mit A 8v\" und ich zeige Ihnen alle Unterschiede",
            "💰 <strong>Ihr Budget respektieren</strong> — \"Ich habe 1000€, was empfehlen Sie?\"",
            "📚 <strong>Expertenrat geben</strong> — Beschneidung, Rasenpflege, saisonale Wartung",
            "❓ <strong>Ihre Fragen beantworten</strong> — Sicherheit, Technologien, Installation"
        ],
        categories: "<strong>Produktkategorien:</strong> Mähroboter • Rasenmäher • Rasentraktoren • Freischneider • Kettensägen • Heckenscheren • Hochdruckreiniger • Laubbläser • und vieles mehr!",
        languageNote: "Schreiben Sie in jeder Sprache — ich antworte in Ihrer! 🌍",
        startPrompt: "<em>Beschreiben Sie zunächst Ihren Garten oder wonach Sie suchen...</em>",
        placeholder: "Schreiben Sie hier Ihre Frage...",
        sendButton: "Senden →"
    },
    fr: {
        welcomeTitle: "Bonjour! 👋 Je suis votre conseiller STIGA, expert en jardinage depuis 1934.",
        welcomeSubtitle: "<strong>Ce que je peux faire pour vous:</strong>",
        features: [
            "🔍 <strong>Trouver le produit parfait</strong> — dites-moi vos besoins et je vous guide vers le meilleur choix",
            "⚖️ <strong>Comparer les produits</strong> — \"Compare A 6v avec A 8v\" et je vous montre toutes les différences",
            "💰 <strong>Respecter votre budget</strong> — \"J'ai 1000€, que me conseillez-vous?\"",
            "📚 <strong>Donner des conseils d'expert</strong> — taille, entretien de la pelouse, maintenance saisonnière",
            "❓ <strong>Répondre à vos questions</strong> — sécurité, technologies, installation"
        ],
        categories: "<strong>Catégories de produits:</strong> Robots tondeuses • Tondeuses • Tracteurs • Débroussailleuses • Tronçonneuses • Taille-haies • Nettoyeurs haute pression • Souffleurs • et bien plus!",
        languageNote: "Écrivez dans n'importe quelle langue — je répondrai dans la vôtre! 🌍",
        startPrompt: "<em>Commencez par décrire votre jardin ou ce que vous recherchez...</em>",
        placeholder: "Écrivez votre question ici...",
        sendButton: "Envoyer →"
    },
    es: {
        welcomeTitle: "¡Hola! 👋 Soy tu consultor STIGA, experto en jardinería desde 1934.",
        welcomeSubtitle: "<strong>Lo que puedo hacer por ti:</strong>",
        features: [
            "🔍 <strong>Encontrar el producto perfecto</strong> — cuéntame tus necesidades y te guío a la mejor elección",
            "⚖️ <strong>Comparar productos</strong> — \"Compara A 6v con A 8v\" y te muestro todas las diferencias",
            "💰 <strong>Respetar tu presupuesto</strong> — \"Tengo 1000€, ¿qué me recomiendas?\"",
            "📚 <strong>Dar consejos expertos</strong> — poda, cuidado del césped, mantenimiento estacional",
            "❓ <strong>Responder tus dudas</strong> — seguridad, tecnologías, instalación"
        ],
        categories: "<strong>Categorías de productos:</strong> Robots cortacésped • Cortacéspedes • Tractores • Desbrozadoras • Motosierras • Cortasetos • Hidrolimpiadoras • Sopladores • ¡y mucho más!",
        languageNote: "Escribe en cualquier idioma — ¡responderé en el tuyo! 🌍",
        startPrompt: "<em>Empieza describiendo tu jardín o lo que estás buscando...</em>",
        placeholder: "Escribe tu pregunta aquí...",
        sendButton: "Enviar →"
    }
};

function detectBrowserLanguage() {
    const browserLang = navigator.language || navigator.userLanguage;
    const langCode = browserLang.split('-')[0].toLowerCase();
    if (translations[langCode]) {
        return langCode;
    }
    return 'en';
}

function updateWelcomeMessage(lang) {
    const t = translations[lang];
    const welcomeContent = document.querySelector('#welcome-message .message-content');
    let featuresHtml = '<ul>';
    t.features.forEach(feature => {
        featuresHtml += `<li>${feature}</li>`;
    });
    featuresHtml += '</ul>';
    welcomeContent.innerHTML = `
        <p>${t.welcomeTitle}</p>
        <p>${t.welcomeSubtitle}</p>
        ${featuresHtml}
        <p>${t.categories}</p>
        <p>${t.languageNote}</p>
        <p>${t.startPrompt}</p>
    `;
    document.getElementById('user-input').placeholder = t.placeholder;
    document.getElementById('send-button').textContent = t.sendButton;
}

function initLanguage() {
    const savedLang = localStorage.getItem('stiga-lang');
    const lang = savedLang || detectBrowserLanguage();
    document.getElementById('language-selector').value = lang;
    updateWelcomeMessage(lang);
    return lang;
}

const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const sessionId = 'session_' + Date.now();

function formatMarkdown(text) {
    text = text.replace(/  +/g, ' ');
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/\*([^\*\|]+?)\*/g, '<em>$1</em>');
    text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
    const tableRegex = /\|(.+)\|[\r\n]+\|[-:\| ]+\|[\r\n]+((?:\|.+\|[\r\n]*)+)/g;
    text = text.replace(tableRegex, function(match, headerRow, bodyRows) {
        const headers = headerRow.split('|').map(h => h.trim()).filter(h => h);
        const rows = bodyRows.trim().split('\n').map(row => {
            return row.split('|').map(cell => cell.trim()).filter(cell => cell);
        });
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
    let blocks = text.split('\n\n');
    let html = '';
    for (let block of blocks) {
        block = block.trim();
        if (!block) continue;
        if (block.startsWith('<table')) {
            html += block;
            continue;
        }
        if (block.match(/^[•\-\*]/m) && !block.includes('|')) {
            let items = block.split('\n').filter(line => line.trim());
            html += '<ul>';
            for (let item of items) {
                item = item.replace(/^[•\-\*]\s*/, '');
                if (item.trim()) {
                    html += `<li>${item.trim()}</li>`;
                }
            }
            html += '</ul>';
        } else {
            block = block.replace(/\n/g, '<br>');
            html += `<p>${block}</p>`;
        }
    }
    return html;
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addMessage(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'assistant-message'}`;
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    if (!isUser) {
        contentDiv.innerHTML = formatMarkdown(content);
    } else {
        contentDiv.innerHTML = content;
    }
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    return messageDiv;
}

function showLoadingMessage(text) {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message assistant-message';
    loadingDiv.id = 'loading-indicator';
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content loading-text';
    contentDiv.innerHTML = `<div class="typing-indicator"><span></span><span></span><span></span></div> ${text}`;
    loadingDiv.appendChild(contentDiv);
    chatMessages.appendChild(loadingDiv);
    scrollToBottom();
}

function updateLoadingMessage(text) {
    const indicator = document.getElementById('loading-indicator');
    if (indicator) {
        const contentDiv = indicator.querySelector('.message-content');
        contentDiv.innerHTML = `<div class="typing-indicator"><span></span><span></span><span></span></div> ${text}`;
        scrollToBottom();
    }
}

function removeLoadingMessage() {
    const indicator = document.getElementById('loading-indicator');
    if (indicator) {
        indicator.remove();
    }
}

function formatComparisonTable(comparatorData) {
    if (!comparatorData || !comparatorData.prodotti) return '';
    const prodotti = comparatorData.prodotti;
    const attributi = comparatorData.attributi || [];
    const consiglio = comparatorData.consiglio || '';
    let html = '<div class="comparison-container">';
    html += '<table class="comparison-table">';
    html += '<thead><tr>';
    html += '<th>Caratteristica</th>';
    prodotti.forEach(p => {
        html += `<th>${p}</th>`;
    });
    html += '</tr></thead>';
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
    if (consiglio) {
        html += `<div class="comparison-verdict"><strong>💡 Il mio consiglio:</strong> ${consiglio}</div>`;
    }
    html += '</div>';
    return html;
}

function formatProductCards(products) {
    if (!products || products.length === 0) return '';
    let html = '<div class="products-section">';
    products.forEach(product => {
        const imageUrl = product.image_url || (product.immagini && product.immagini[0]) || '/static/images/stiga-robot.webp';
        let desc = product.descrizione || '';
        if (desc.length > 150) {
            let cutPoint = desc.indexOf('.', 150);
            if (cutPoint > 0 && cutPoint < 300) {
                desc = desc.substring(0, cutPoint + 1);
            } else {
                desc = desc.substring(0, 200).trim() + '...';
            }
        }
        html += `
            <div class="product-card">
                <div class="product-image">
                    <img src="${imageUrl}" alt="${product.nome}" onerror="this.src='/static/images/stiga-robot.webp'">
                </div>
                <div class="product-info">
                    <h3>${product.nome}</h3>
                    ${product.categoria ? `<div class="product-category">${product.categoria}</div>` : ''}
                    <div class="product-description">${desc}</div>
                    ${product.prezzo ? `<div class="product-price">${product.prezzo}</div>` : ''}
                    <a href="${product.url}" target="_blank" class="product-link" onclick="trackProductClick('${product.id || ''}', '${product.nome.replace(/'/g, "\\'")}', '${product.categoria || ''}'); return true;">
                        Scopri tutti i dettagli →
                    </a>
                </div>
            </div>
        `;
    });
    html += '</div>';
    return html;
}

// ===== STREAMING SSE CHAT =====
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;

    // Mostra messaggio utente
    addMessage(message, true);
    userInput.value = '';
    sendButton.disabled = true;

    // Mostra loading iniziale
    showLoadingMessage('Sto cercando nel catalogo STIGA...');

    try {
        // Setup streaming con fetch (POST body support)
        const response = await fetch('/api/chat/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                language: document.getElementById('language-selector').value
            })
        });

        if (!response.ok) {
            throw new Error('Errore nella risposta del server');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let streamingMessageDiv = null;
        let streamingContent = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (!line.trim() || !line.startsWith('data: ')) continue;

                const jsonStr = line.substring(6); // Remove "data: "
                try {
                    const data = JSON.parse(jsonStr);

                    if (data.type === 'loading') {
                        // Aggiorna messaggio loading
                        updateLoadingMessage(data.text);
                    } else if (data.type === 'chunk') {
                        // Rimuovi loading al primo chunk
                        if (!streamingMessageDiv) {
                            removeLoadingMessage();
                            streamingMessageDiv = addMessage('', false);
                        }

                        // Aggiungi chunk al contenuto
                        streamingContent += data.text;
                        
                        // Rimuovi tag XML che non devono essere mostrati
                        let cleanContent = streamingContent;
                        cleanContent = cleanContent.replace(/<prodotti>.*?<\/prodotti>/gs, '');
                        cleanContent = cleanContent.replace(/<comparatore>.*?<\/comparatore>/gs, '');
                        cleanContent = cleanContent.replace(/<risposta>/g, '').replace(/<\/risposta>/g, '');
                        
                        const contentDiv = streamingMessageDiv.querySelector('.message-content');
                        contentDiv.innerHTML = formatMarkdown(cleanContent.trim());
                        scrollToBottom();
                    } else if (data.type === 'products') {
                        // Mostra prodotti
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

                        // Mostra comparatore se presente
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
                    } else if (data.type === 'done') {
                        // Stream completato
                        console.log('✅ Stream completed');
                    } else if (data.type === 'error') {
                        // Errore server
                        throw new Error(data.message || 'Errore sconosciuto');
                    }
                } catch (parseError) {
                    console.error('Error parsing SSE data:', parseError, jsonStr);
                }
            }
        }
    } catch (error) {
        removeLoadingMessage();
        addMessage('Mi dispiace, si è verificato un errore. Riprova.', false);
        console.error('Errore streaming:', error);
    } finally {
        sendButton.disabled = false;
        userInput.focus();
    }
});

document.getElementById('language-selector').addEventListener('change', (e) => {
    const newLang = e.target.value;
    localStorage.setItem('stiga-lang', newLang);
    updateWelcomeMessage(newLang);
});

document.addEventListener('DOMContentLoaded', () => {
    const currentLang = initLanguage();
    trackSessionStart();
    userInput.focus();
});
