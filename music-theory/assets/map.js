(() => {
  const {nodes, edges} = JSON.parse(document.getElementById('map-data').textContent);
  const select = document.getElementById('node-choice');
  const graph = document.getElementById('map-graph');
  const make = (tag, text, className) => {
    const item = document.createElement(tag);
    if (className) item.className = className;
    item.textContent = text;
    return item;
  };
  const bookLink = id => {
    const link = make('a', nodes[id].title);
    link.href = nodes[id].url;
    return link;
  };
  function draw() {
    const requested = new URLSearchParams(location.hash.slice(1)).get('focus') || new URLSearchParams(location.search).get('focus');
    const id = Object.hasOwn(nodes, requested) ? requested : 'phase-pairs';
    select.value = id;
    const label = make('h2', '');
    label.append(bookLink(id));
    const list = make('ul', '', 'map-connections');
    for (const edge of edges.filter(e => e.from === id || e.to === id)) {
      const next = edge.from === id ? edge.to : edge.from;
      const item = make('li', '');
      item.append(bookLink(next), make('p', edge.why));
      const follow = make('button', 'この章を起点にする');
      follow.type = 'button';
      follow.addEventListener('click', () => { change(next); select.focus(); });
      item.append(follow);
      list.append(item);
    }
    graph.replaceChildren(label, list);
  }
  function change(id) {
    const address = new URL(location.href);
    address.hash = 'focus=' + encodeURIComponent(id);
    history.pushState(null, '', address);
    draw();
  }
  select.addEventListener('change', () => change(select.value));
  window.addEventListener('popstate', draw);
  draw();
  document.getElementById('map-control').hidden = false;
})();
