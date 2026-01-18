// ===== UMAMI ANALYTICS HELPER =====
function trackEvent(eventName, eventData = {}) {
    if (typeof umami !== 'undefined') {
        umami.track(eventName, eventData);
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

// Rileva lingua browser
function detectBrowserLanguage() {
    const browserLang = navigator.language || navigator.userLanguage;
    const langCode = browserLang.split('-')[0].toLowerCase();
    
    if (translations[langCode]) {
        return langCode;
    }
    return 'en';
}

// Aggiorna messaggio di benvenuto
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

// Inizializza lingua
function initLanguage() {
    const savedLang = localStorage.getItem('stiga-lang');
    const lang = savedLang || detectBrowserLanguage();
    
    document.getElementById('language-selector').value = lang;
    updateWelcomeMessage(lang);
    
    return lang;
}

// ===== ELEMENTI DOM =====
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

// Genera session ID unico
const sessionId = 'session_' + Date.now();

// Track session start
let sessionStartTime = Date.now();
let messageCount = 0;

// ===== FORMATTAZIONE MARKDOWN =====
function formatMarkdown(text) {
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
    
    // 6. Separa i blocchi principali (doppio a capo)
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

// ===== FUNZIONI CHAT =====
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
}

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

function formatComparisonTable(comparatorData) {
    if (!comparatorData || !comparatorData.prodotti) return '';
    
    const prodotti = comparatorData.prodotti;
    const attributi = comparatorData.attributi || [];
    const consiglio = comparatorData.consiglio || '';
    
    // Track comparison usage
    trackEvent('comparison_used', {
        products_count: prodotti.length,
        language: document.getElementById('language-selector').value
    });
    
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
        const imageUrl = product.image_url || 
                        (product.immagini && product.immagini[0]) || 
                        'https://via.placeholder.com/300x200/00A651/ffffff?text=STIGA';
        
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
                    <img src="${imageUrl}" alt="${product.nome}" 
                         onerror="this.src='https://via.placeholder.com/300x200/00A651/ffffff?text=STIGA'">
                </div>
                <div class="product-info">
                    <h3>${product.nome}</h3>
                    ${product.categoria ? `<div class="product-category">${product.categoria}</div>` : ''}
                    <div class="product-description">${desc}</div>
                    ${product.prezzo ? `<div class="product-price">${product.prezzo}</div>` : ''}
                    <a href="${product.url}" target="_blank" class="product-link" onclick="trackProductClick('${product.nome}', '${product.categoria || 'unknown'}')">
                        Scopri tutti i dettagli →
                    </a>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

// Track product clicks
function trackProductClick(productName, productCategory) {
    trackEvent('product_clicked', {
        product_name: productName,
        product_category: productCategory,
        language: document.getElementById('language-selector').value
    });
}

// ===== EVENT LISTENERS =====
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = userInput.value.trim();
    if (!message) return;
    
    messageCount++;
    
    // Track message sent
    trackEvent('message_sent', {
        message_length: message.length,
        message_count: messageCount,
        language: document.getElementById('language-selector').value
    });
    
    addMessage(message, true);
    userInput.value = '';
    sendButton.disabled = true;
    
    showTypingIndicator();
    
    try {
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
        
        removeTypingIndicator();
        addMessage(data.response, false);
        
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
        
        if (data.products && data.products.length > 0) {
            const productsDiv = document.createElement('div');
            productsDiv.className = 'message assistant-message';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.innerHTML = formatProductCards(data.products);
            
            productsDiv.appendChild(contentDiv);
            chatMessages.appendChild(productsDiv);
            scrollToBottom();
            
            // Track products shown
            trackEvent('products_shown', {
                products_count: data.products.length,
                language: document.getElementById('language-selector').value
            });
        }
        
    } catch (error) {
        removeTypingIndicator();
        addMessage('Mi dispiace, si è verificato un errore. Riprova.', false);
        console.error('Errore:', error);
        
        // Track error
        trackEvent('chat_error', {
            error_message: error.message
        });
    } finally {
        sendButton.disabled = false;
        userInput.focus();
    }
});

// Event listener per cambio lingua
document.getElementById('language-selector').addEventListener('change', (e) => {
    const oldLang = localStorage.getItem('stiga-lang') || 'it';
    const newLang = e.target.value;
    
    localStorage.setItem('stiga-lang', newLang);
    updateWelcomeMessage(newLang);
    
    // Track language change
    trackEvent('language_changed', {
        from: oldLang,
        to: newLang
    });
});

// Track session end on page unload
window.addEventListener('beforeunload', () => {
    const sessionDuration = Math.floor((Date.now() - sessionStartTime) / 1000);
    
    trackEvent('session_end', {
        duration_seconds: sessionDuration,
        message_count: messageCount,
        language: document.getElementById('language-selector').value
    });
});

// ===== INIZIALIZZAZIONE =====
document.addEventListener('DOMContentLoaded', () => {
    const currentLang = initLanguage();
    
    // Determine if widget or main version
    const isWidget = window.location.pathname.includes('widget');
    
    // Track chat opened
    trackEvent('chat_opened', {
        version: isWidget ? 'widget' : 'main',
        language: currentLang
    });
});

userInput.focus();