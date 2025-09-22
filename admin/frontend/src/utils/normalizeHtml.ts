export function normalizeLineBreaksToDivBr(html: string): string {
  const wrapper = document.createElement('div');
  wrapper.innerHTML = html;

  const BLOCK_TAGS = new Set([
    'DIV','P','SECTION','ARTICLE','UL','OL','LI','H1','H2','H3','H4','H5','H6','TABLE','THEAD','TBODY','TFOOT','TR','TD','TH','BLOCKQUOTE','PRE'
  ]);

  const isBlock = (el: Element | null) => !!el && BLOCK_TAGS.has(el.tagName);

  const isVisuallyEmpty = (el: HTMLElement) => {
    // считаем пустыми: только пробелы/&nbsp;/брейки/пустые инлайны
    const clone = el.cloneNode(true) as HTMLElement;
    // убираем все инлайны-обёртки без текста
    clone.querySelectorAll('b,i,span,strong,em,a,small,u,s,mark,code').forEach(n => {
      if (n.textContent?.trim() === '' && n.querySelectorAll('img, svg, video, audio').length === 0) n.replaceWith();
    });
    const txt = clone.innerHTML
      .replace(/\u00A0/g, ' ')
      .replace(/<br\s*\/?>/gi, '\n')
      .replace(/[\s\n]+/g, '');
    return txt.length === 0;
  };

  // 1) P → DIV (и пустые P → <div><br></div>)
  wrapper.querySelectorAll('p').forEach((p) => {
    const hasOnlyBr =
      p.childNodes.length === 1 &&
      p.firstChild?.nodeName.toLowerCase() === 'br';

    if (hasOnlyBr || isVisuallyEmpty(p as HTMLElement)) {
      const div = document.createElement('div');
      div.appendChild(document.createElement('br'));
      p.replaceWith(div);
      return;
    }

    const div = document.createElement('div');
    while (p.firstChild) div.appendChild(p.firstChild);
    p.replaceWith(div);
  });

  // 2) Каждый <br> → отдельный <div><br></div>, вставляя у ближайшего блочного предка
  const allBr = Array.from(wrapper.querySelectorAll('br'));
  allBr.forEach((br) => {
    // уже корректный случай: <div><br></div>
    const parent = br.parentElement;
    if (
      parent &&
      parent.tagName === 'DIV' &&
      parent.childNodes.length === 1 &&
      parent.firstChild === br
    ) {
      return;
    }

    // найдём ближайшего блочного предка и позицию вставки
    let blockAncestor: HTMLElement | null = parent as HTMLElement | null;
    let anchor: Node = br; // куда относительно этого узла будем вставлять
    while (blockAncestor && !isBlock(blockAncestor)) {
      anchor = blockAncestor; // поднимаем «якорь»
      blockAncestor = blockAncestor.parentElement as HTMLElement | null;
    }
    if (!blockAncestor) {
      // на всякий случай — если вдруг нет блочного предка, вставим в корень
      blockAncestor = wrapper;
      anchor = br;
    }

    // соберём подряд идущие <br> (пачку)
    const brsInARow: HTMLBRElement[] = [br];
    let next = br.nextSibling;
    while (next && next.nodeName.toLowerCase() === 'br') {
      brsInARow.push(next as HTMLBRElement);
      next = next.nextSibling;
    }

    // на позицию ANCHOR передвинем пачку как набор блоков
    brsInARow.forEach((oneBr) => {
      const div = document.createElement('div');
      div.appendChild(document.createElement('br'));
      blockAncestor!.insertBefore(div, anchor);
      oneBr.remove();
    });

    // если исходный parent стал пустым инлайном — очистим
    if (parent && !isBlock(parent) && isVisuallyEmpty(parent)) {
      parent.remove();
    }
  });

  // 3) Удалить пустые контейнеры, кроме ровно <div><br></div>
  Array.from(wrapper.querySelectorAll('*')).forEach((el) => {
    if (!(el instanceof HTMLElement)) return;

    if (el.tagName === 'DIV') {
      const okDiv =
        el.childNodes.length === 1 &&
        el.firstChild?.nodeName.toLowerCase() === 'br';
      if (okDiv) return;
    }
    // пустые инлайны/блоки — убрать
    if (isVisuallyEmpty(el)) el.remove();
  });

  // 4) Нормализовать &nbsp; в текстовых узлах
  wrapper.querySelectorAll('*').forEach((el) => {
    el.childNodes.forEach((n) => {
      if (n.nodeType === Node.TEXT_NODE) {
        n.nodeValue = (n.nodeValue || '').replace(/\u00A0/g, ' ');
      }
    });
  });

  return wrapper.innerHTML;
}
