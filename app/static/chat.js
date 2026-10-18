const chat = document.querySelector('#chat');
const form = document.querySelector('#form');
let sessionId = localStorage.getItem('electoral_session') || '';

function append(text, type, citations = []) {
  const box = document.createElement('article'); box.className = `message ${type}`; box.textContent = text;
  if (citations.length) {
    const list = document.createElement('div'); list.className = 'citations';
    list.innerHTML = '<strong>Fuentes:</strong><br>' + citations.map((c, i) =>
      `[${i + 1}] ${c.document}, pág. ${c.page_start}${c.page_end !== c.page_start ? '-' + c.page_end : ''} — <a target="_blank" rel="noopener" href="${c.url}">abrir documento</a>`).join('<br>');
    box.appendChild(list);
  }
  chat.appendChild(box); chat.scrollTop = chat.scrollHeight;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = document.querySelector('#question').value.trim();
  append(question, 'user'); document.querySelector('#question').value = '';
  const button = form.querySelector('button'); button.disabled = true; button.textContent = 'Consultando…';
  try {
    const response = await fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({
      question, session_id: sessionId, dignity: document.querySelector('#dignity').value || null, canton: document.querySelector('#canton').value || null
    })});
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || 'No fue posible procesar la consulta.');
    sessionId = result.session_id; localStorage.setItem('electoral_session', sessionId);
    append(`${result.answer}\n\nVeredicto: ${result.verdict}. ${result.verdict_reason}`, 'assistant', result.citations);
  } catch (error) { append(`Error: ${error.message}`, 'assistant'); }
  finally { button.disabled = false; button.textContent = 'Enviar'; }
});
