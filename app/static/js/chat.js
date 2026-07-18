// ===== STATE MANAGEMENT FOR PRODUCT DISPLAY =====
let currentProductsInDisplay = [];
let selectedProductsForCompare = [];

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

// ===== OLD FUNCTION (kept for backward compatibility in chat) =====
function formatProductCards(products) {
    if (!products || products.length === 0) return '';
    let html = '<div class="products-section">';
    products.forEach(product => {
        const imageUrl = product.image_url || (product.immagini && product.immagini[0]) || 'https://via.placeholder.com/300x200/00A651/ffffff?text=STIGA';
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
                    <img src="${imageUrl}" alt="${product.nome}" onerror="this.src='https://via.placeholder.com/300x200/00A651/ffffff?text=STIGA'">
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

// ===== PHASE 2: NEW PRODUCT DISPLAY FUNCTIONS =====

function updateProductDisplay(products) {
    if (!products || products.length === 0) return;
    
    // Update state
    currentProductsInDisplay = products;
    
    // Get carousel container
    const carousel = document.getElementById('product-carousel');
    if (!carousel) {
        console.error('Product carousel not found');
        return;
    }
    
    // Render products in carousel
    carousel.innerHTML = formatProductCardsMinimal(products);
    
    // Reset compare selection
    selectedProductsForCompare = [];
    updateCompareButton();
}

function formatProductCardsMinimal(products) {
    if (!products || products.length === 0) {
        return '<p class="empty-state">I prodotti appariranno qui quando inizi a chattare</p>';
    }
    
    let html = '';
    products.forEach((product, index) => {
        const imageUrl = product.image_url || (product.immagini && product.immagini[0]) || 'https://via.placeholder.com/300x200/00A651/ffffff?text=STIGA';
        
        // Brief description (first 80 chars)
        let briefDesc = product.descrizione || '';
        if (briefDesc.length > 80) {
            briefDesc = briefDesc.substring(0, 80).trim() + '...';
        }
        
        html += `
            <div class="product-card" data-product-index="${index}" data-product-id="${product.id || ''}" onclick="handleProductCardClick(event, ${index})">
                <div class="product-image">
                    <img src="${imageUrl}" alt="${product.nome}" onerror="this.src='https://via.placeholder.com/300x200/00A651/ffffff?text=STIGA'">
                </div>
                <div class="product-info">
                    <h3>${product.nome}</h3>
                    ${product.categoria ? `<div class="product-category">${product.categoria}</div>` : ''}
                    <div class="product-description">${briefDesc}</div>
                    ${product.prezzo ? `<div class="product-price">${product.prezzo}</div>` : ''}
                    <a href="${product.url}" target="_blank" class="product-link" onclick="event.stopPropagation(); trackProductClick('${product.id || ''}', '${product.nome.replace(/'/g, "\\'")}', '${product.categoria || ''}'); return true;">
                        Vedi dettagli →
                    </a>
                </div>
            </div>
        `;
    });
    
    return html;
}

function toggleProductSelection(productIndex) {
    const product = currentProductsInDisplay[productIndex];
    if (!product) return;
    
    const index = selectedProductsForCompare.findIndex(p => p.id === product.id);
    
    if (index > -1) {
        // Deselect
        selectedProductsForCompare.splice(index, 1);
    } else {
        // Select (max 3)
        if (selectedProductsForCompare.length >= 3) {
            alert('Puoi confrontare massimo 3 prodotti alla volta');
            return;
        }
        selectedProductsForCompare.push(product);
    }
    
    updateCompareButton();
    updateSelectionUI();
}

function updateCompareButton() {
    const compareBtn = document.getElementById('compare-toggle');
    if (!compareBtn) return;
    
    const count = selectedProductsForCompare.length;
    
    if (count >= 2) {
        compareBtn.disabled = false;
        compareBtn.textContent = `Confronta (${count})`;
    } else {
        compareBtn.disabled = true;
        compareBtn.textContent = 'Confronta (0)';
    }
}

function updateSelectionUI() {
    // Update visual state of selected products
    const cards = document.querySelectorAll('.product-card');
    cards.forEach((card, index) => {
        const product = currentProductsInDisplay[index];
        if (!product) return;
        
        const isSelected = selectedProductsForCompare.some(p => p.id === product.id);
        
        if (isSelected) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });
}

// ===== PRODUCT CARD CLICK HANDLER =====
function handleProductCardClick(event, productIndex) {
    // Don't trigger if clicking on link
    if (event.target.closest('.product-link')) {
        return;
    }
    
    toggleProductSelection(productIndex);
}

// ===== CHAT FORM SUBMIT (MODIFIED FOR PHASE 2) =====

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = userInput.value.trim();
    if (!message) return;
    addMessage(message, true);
    userInput.value = '';
    sendButton.disabled = true;
    showTypingIndicator();
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });
        if (!response.ok) {
            throw new Error('Errore nella risposta del server');
        }
        const data = await response.json();
        console.log('📦 Response data:', data);
        removeTypingIndicator();
        addMessage(data.response, false);
        
        // Comparator (remains in chat)
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
        
        // ===== PHASE 2: Products go to display column (RIGHT) =====
        if (data.products && data.products.length > 0) {
            updateProductDisplay(data.products);
            renderShowAllButton(data);  // ← Show "Mostra tutti" button
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

document.getElementById('language-selector').addEventListener('change', (e) => {
    const newLang = e.target.value;
    localStorage.setItem('stiga-lang', newLang);
    updateWelcomeMessage(newLang);
});

// ===== COMPARATORE DETERMINISTICO (F-06b, senza AI) =====
// Legge le specifiche reali da /api/product/<id> e le mostra affiancate
// nel pannello #comparison-panel. Nessuna chiamata LLM: istantaneo e stabile.
const CMP_BLACKLIST = ['ean', 'upc', 'sku', 'gtin', 'codice', 'barcode'];
const CMP_HIGHER_BETTER = ['area di taglio', 'capacità batteria', 'capacita batteria', 'potenza', 'autonomia', 'tempo massimo di taglio', 'capacità sacco', 'capacita sacco', 'cilindrata'];
const CMP_LOWER_BETTER = ['peso', 'tempo di ricarica', 'livello', 'rumore', 'emission'];
const CMP_PREFERRED = {
  'Robot tagliaerba': ['Alimentazione', 'Area di taglio fino a', 'Capacità batteria', 'Tempo di ricarica', 'Tempo massimo di taglio per ciclo', 'Larghezza di taglio', 'Pendenza massima', 'GPS'],
  'Trattorini da giardino': ['Alimentazione', 'Area di taglio', 'Larghezza di taglio', 'Altezze di taglio', 'Capacità sacco raccolta', 'Potenza', 'Trasmissione', 'Peso'],
  'Tagliaerba': ['Alimentazione', 'Larghezza di taglio', 'Altezze di taglio', 'Capacità sacco raccolta', 'Area di taglio', 'Avanzamento', 'Potenza', 'Peso'],
  'Decespugliatori': ['Alimentazione', 'Cilindrata', 'Potenza', 'Diametro lama', 'Larghezza di taglio', 'Peso'],
  'Motoseghe': ['Alimentazione', 'Cilindrata', 'Potenza', 'Lunghezza barra', 'Capacità serbatoio olio catena', 'Freno catena', 'Peso'],
  'Tagliasiepi': ['Alimentazione', 'Capacità di taglio', 'Distanza tra i denti', 'Lunghezza lama', 'Peso']
};

function cmpNormLabel(raw) {
  return String(raw).replace(/^Specifiche tecniche\s*-\s*/i, '').replace(/info_outline/ig, '').replace(/\s+/g, ' ').trim();
}
function cmpNonEmpty(v) {
  const s = (v === null || v === undefined) ? '' : String(v).trim();
  return s !== '' && s !== '-' && s !== '—' && s.toLowerCase() !== 'n/a';
}
function cmpBlacklisted(label) {
  const l = label.toLowerCase();
  return CMP_BLACKLIST.some(b => l.includes(b));
}
function cmpNormSpecs(product) {
  const specs = product.specifiche_tecniche || {};
  const out = {};
  for (const k in specs) {
    if (!cmpNonEmpty(specs[k])) continue;
    const lab = cmpNormLabel(k);
    if (!lab || cmpBlacklisted(lab)) continue;
    if (!(lab in out)) out[lab] = String(specs[k]).trim();
  }
  return out;
}
function cmpBuildRows(specSets, categoria) {
  const avail = new Set();
  specSets.forEach(s => Object.keys(s).forEach(k => avail.add(k)));
  const rows = [], seen = new Set();
  const pref = CMP_PREFERRED[categoria] || [];
  const find = (p) => {
    for (const a of avail) if (a.toLowerCase() === p.toLowerCase()) return a;
    for (const a of avail) if (a.toLowerCase().startsWith(p.toLowerCase())) return a;
    return null;
  };
  pref.forEach(p => { const a = find(p); if (a && !seen.has(a)) { rows.push(a); seen.add(a); } });
  const freq = {};
  specSets.forEach(s => Object.keys(s).forEach(k => { freq[k] = (freq[k] || 0) + 1; }));
  Object.keys(freq).sort((a, b) => freq[b] - freq[a]).forEach(k => { if (!seen.has(k)) { rows.push(k); seen.add(k); } });
  return rows.slice(0, 14);
}
function cmpParseNum(v) {
  const m = String(v).match(/[-+]?\d+(?:[.,]\d+)?/);
  return m ? parseFloat(m[0].replace(',', '.')) : null;
}
function cmpRow(label, specSets) {
  const vals = specSets.map(s => (label in s) ? s[label] : '—');
  const diff = new Set(vals).size > 1;
  const l = label.toLowerCase();
  let dir = 0;
  if (CMP_HIGHER_BETTER.some(k => l.includes(k))) dir = 1;
  else if (CMP_LOWER_BETTER.some(k => l.includes(k))) dir = -1;
  let best = null;
  if (dir !== 0 && diff) {
    const nums = vals.map(cmpParseNum);
    if (nums.every(n => n !== null) && new Set(nums).size > 1) {
      const target = dir === 1 ? Math.max(...nums) : Math.min(...nums);
      best = nums.indexOf(target);
    }
  }
  return { vals, diff, best };
}

async function openDeterministicComparison(selected) {
  const panel = document.getElementById('comparison-panel');
  if (!panel) return;
  panel.classList.remove('hidden');
  panel.innerHTML = '<p style="padding:12px; color:#666; font-size:13px;">Preparo il confronto…</p>';
  panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  let full;
  try {
    full = await Promise.all(selected.map(p => fetch('/api/product/' + encodeURIComponent(p.id)).then(r => r.json())));
  } catch (e) {
    panel.innerHTML = '<p style="padding:12px; color:#b00; font-size:13px;">Errore nel recupero delle schede. Riprova.</p>';
    return;
  }
  const categoria = (full[0] && full[0].categoria) || '';
  const specSets = full.map(cmpNormSpecs);
  const rows = cmpBuildRows(specSets, categoria);
  cmpRenderPanel(panel, full, specSets, rows);
}

function cmpRenderPanel(panel, products, specSets, rows) {
  let onlyDiff = false;
  const render = () => {
    const head = ['<th style="text-align:left;padding:10px 8px;font-size:12px;color:#666;font-weight:500;">Caratteristica</th>']
      .concat(products.map(p => '<th style="padding:10px 8px;border-bottom:1px solid #e5e5e5;font-size:13px;font-weight:600;color:#111;">' +
        cmpEsc(p.nome) + '<div style="font-weight:600;color:#00843D;margin-top:2px;">' + cmpEsc(p.prezzo || '—') + '</div></th>')).join('');
    let bodyRows = '';
    rows.forEach(label => {
      const r = cmpRow(label, specSets);
      if (onlyDiff && !r.diff) return;
      const labColor = r.diff ? '#111' : '#999';
      let tds = '<td style="padding:9px 8px;border-bottom:1px solid #f0f0f0;font-size:12px;color:#666;">' + cmpEsc(label) +
        (r.diff ? ' <span style="color:#00843D;">•</span>' : '') + '</td>';
      r.vals.forEach((v, i) => {
        const win = r.best === i;
        tds += '<td style="padding:9px 8px;border-bottom:1px solid #f0f0f0;font-size:13px;color:' + labColor + ';' +
          (win ? 'background:#eaf6ee;font-weight:600;' : '') + '">' + cmpEsc(v) + (win ? ' ✓' : '') + '</td>';
      });
      bodyRows += '<tr>' + tds + '</tr>';
    });
    if (!bodyRows) bodyRows = '<tr><td colspan="' + (products.length + 1) + '" style="padding:12px;color:#999;font-size:13px;">Nessuna differenza tra i prodotti selezionati.</td></tr>';
    panel.innerHTML =
      '<div style="display:flex;align-items:center;justify-content:space-between;gap:8px;padding:10px 4px;">' +
      '<span style="font-size:14px;font-weight:600;color:#111;">Confronto (' + products.length + ')</span>' +
      '<span style="display:flex;align-items:center;gap:12px;">' +
      '<label style="font-size:12px;color:#666;cursor:pointer;display:flex;align-items:center;gap:5px;"><input type="checkbox" id="cmp-onlydiff"' + (onlyDiff ? ' checked' : '') + '> Solo differenze</label>' +
      '<button id="cmp-close" style="border:none;background:none;color:#999;cursor:pointer;font-size:18px;line-height:1;">×‍</button>' +
      '</span></div>' +
      '<table style="width:100%;border-collapse:collapse;table-layout:fixed;"><thead><tr>' + head + '</tr></thead><tbody>' + bodyRows + '</tbody></table>';
    const cb = document.getElementById('cmp-onlydiff');
    if (cb) cb.addEventListener('change', e => { onlyDiff = e.target.checked; render(); });
    const cl = document.getElementById('cmp-close');
    if (cl) cl.addEventListener('click', () => { panel.classList.add('hidden'); panel.innerHTML = ''; });
  };
  render();
}
function cmpEsc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}


// ===== COMPARE BUTTON CLICK HANDLER (F-06b: comparatore deterministico) =====
document.getElementById('compare-toggle')?.addEventListener('click', () => {
    if (selectedProductsForCompare.length < 2) return;
    openDeterministicComparison(selectedProductsForCompare.slice());
});

document.addEventListener('DOMContentLoaded', () => {
    const currentLang = initLanguage();
    trackSessionStart();
    userInput.focus();
});

// === SHOW ALL BUTTON LOGIC ===
function renderShowAllButton(data) {
    console.log('🔍 renderShowAllButton called:', {
        category: data.category,
        total_count: data.total_count,
        products_shown: data.products?.length,
        show_all: data.show_all
    });
    
    // Rimuovi bottone esistente solo se categoria diversa
    const existingBtn = document.querySelector('.show-all-btn');
    if (existingBtn) {
        const existingCategory = existingBtn.dataset.category;
        console.log('🔄 Existing button category:', existingCategory);
        if (existingCategory !== data.category) {
            console.log('❌ Removing old button (different category)');
            existingBtn.remove();
        } else {
            console.log('✅ Same category, keeping button');
            return; // Stessa categoria, mantieni bottone
        }
    }
    
    // Se total_count > prodotti mostrati, aggiungi bottone
    console.log('🔍 Check button creation:', {
        hasCount: !!data.total_count,
        countGreater: data.total_count > data.products?.length,
        hasCategory: !!data.category
    });
    
    if (data.total_count && data.total_count > data.products.length && data.category) {
        const productCarousel = document.getElementById('product-carousel');
        if (!productCarousel) return;
        
        const button = document.createElement('button');
        button.className = 'show-all-btn';
        button.dataset.category = data.category;
        button.innerHTML = `🔍 Mostra tutti i ${data.category} (${data.total_count})`;
        button.onclick = () => {
            // Helper function to submit message programmatically
            const message = `mostra tutti i ${data.category}`;
            userInput.value = message;
            chatForm.dispatchEvent(new Event('submit', { cancelable: true }));
        };
        
        productCarousel.insertAdjacentElement('afterend', button);
    }
}
