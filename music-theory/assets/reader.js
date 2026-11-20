'use strict';

for (const button of document.querySelectorAll('[data-proofs]')) {
  button.addEventListener('click', () => {
    const open = button.dataset.proofs === 'open';
    for (const box of document.querySelectorAll('details.proof')) box.open = open;
  });
}

const target = location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
const holder = target && target.closest('details');
if (holder) holder.open = true;
