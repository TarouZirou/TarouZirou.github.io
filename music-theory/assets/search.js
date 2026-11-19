'use strict';

const search = document.querySelector('#contents-search');
if (search) {
  const chapters = JSON.parse(document.querySelector('#heading-index').textContent);
  const output = document.querySelector('#search-results');
  const cards = document.querySelector('.part-grid');
  const empty = document.querySelector('#empty-result');
  const normalized = s => s.normalize('NFKC').toLowerCase();
  search.addEventListener('input', () => {
    const terms = normalized(search.value.trim()).split(/\s+/u).filter(Boolean);
    output.replaceChildren();
    cards.hidden = terms.length > 0;
    if (!terms.length) {
      empty.hidden = true;
      return;
    }
    let count = 0;
    for (const chapter of chapters) {
      const corpus = normalized([chapter.title, ...chapter.headings].join(' '));
      if (!terms.every(term => corpus.includes(term))) continue;
      const item = document.createElement('li');
      const link = document.createElement('a');
      link.href = chapter.url;
      link.textContent = chapter.title;
      const matches = chapter.headings.filter(heading => terms.some(term => normalized(heading).includes(term)));
      item.append(link);
      if (matches.length) {
        const detail = document.createElement('small');
        detail.textContent = matches.slice(0, 4).join('・');
        item.append(detail);
      }
      output.append(item);
      count++;
    }
    empty.hidden = count > 0;
  });
}

