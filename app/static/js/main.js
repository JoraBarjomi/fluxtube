document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('comment-form');
  if (!form) return;

  const videoId = form.dataset.videoId;
  const csrfToken = window.CSRF_TOKEN;

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const textarea = form.querySelector('textarea[name="text"], textarea');
    const text = textarea.value.trim();
    if (!text) return;

    try {
      const resp = await fetch(`/comment/${videoId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ text })
      });

      if (!resp.ok) {
        console.error('Ошибка при добавлении комментария:', resp.status);
        return;
      }

      const data = await resp.json();

      const avatarUrl = data.avatar
        ? `${window.STATIC_URL}uploads/${data.avatar}`
        : `${window.STATIC_URL}images/avatar.png`;

      const tpl = `
        <div class="comment">
          <img class="comment-avatar" src="${avatarUrl}" alt="Аватар">
          <div class="comment-body">
            <div class="comment-header">
              <a href="/user/${data.author}" class="comment-author">${data.author}</a>
              <span class="comment-date">Только что</span>
            </div>
            <p class="comment-text">${data.text}</p>
          </div>
        </div>`;

      const list = document.querySelector('.comment-list');
      const placeholder = list.querySelector('.no-comments');
      if (placeholder) placeholder.remove();

      list.insertAdjacentHTML('afterbegin', tpl);
      textarea.value = '';

      const counter = document.querySelector('.video-comments h3');
      const current = parseInt(counter.textContent.match(/\d+/)[0], 10) || 0;
      counter.textContent = `Комментарии (${current + 1})`;

    } catch (err) {
      console.error('Network error:', err);
    }
  });
});

document.querySelector('.delete-btn').addEventListener('click', (e) => {
    if (!confirm('Удалить видео навсегда?')) {
        e.preventDefault();
    }
});
