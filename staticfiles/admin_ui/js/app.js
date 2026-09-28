(() => {
  const qs = (sel, root = document) => root.querySelector(sel);
  const qsa = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function initialsFrom(text) {
    const parts = String(text || "")
      .trim()
      .split(/\s+/)
      .filter(Boolean);
    if (!parts.length) return "U";
    if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }

  function setupAvatar() {
    qsa("[data-user-initial]").forEach((el) => {
      el.textContent = initialsFrom(el.textContent);
    });
  }

  function setupUserMenu() {
    const toggle = qs("#user-menu-toggle");
    const menu = qs("#user-menu");
    if (!toggle || !menu) return;
    const close = () => {
      menu.hidden = true;
      toggle.setAttribute("aria-expanded", "false");
    };
    toggle.addEventListener("click", (event) => {
      event.stopPropagation();
      const open = menu.hidden;
      menu.hidden = !open;
      toggle.setAttribute("aria-expanded", String(open));
    });
    document.addEventListener("click", close);
    menu.addEventListener("click", (event) => event.stopPropagation());
  }

  function collectCommands() {
    const items = [{ title: "Overview", href: qs(".sidebar-home")?.getAttribute("href") || "/admin/" }];
    qsa("#nav-sidebar th[scope=row] a").forEach((link) => {
      items.push({ title: link.textContent.trim(), href: link.getAttribute("href") });
    });
    qsa(".model-card h3").forEach((title, index) => {
      const href = title.parentElement.querySelector("a")?.getAttribute("href");
      if (href && !items.some((item) => item.href === href)) {
        items.push({ title: title.textContent.trim(), href });
      }
    });
    return items.filter((item) => item.href);
  }

  function setupCommandPalette() {
    const dialog = qs("#cmdk");
    const input = qs("#cmdk-input");
    const list = qs("#cmdk-results");
    const openBtn = qs("#cmdk-open");
    if (!dialog || !input || !list) return;

    let items = collectCommands();
    let index = 0;

    const render = (query = "") => {
      const q = query.trim().toLowerCase();
      const matches = items.filter((item) => item.title.toLowerCase().includes(q));
      list.innerHTML = matches
        .map(
          (item, i) =>
            `<li class="${i === index ? "is-active" : ""}"><a href="${item.href}">${item.title}</a></li>`,
        )
        .join("");
      if (!matches.length) {
        list.innerHTML = `<li><span style="padding:10px 12px;display:block;color:var(--text-muted)">No matches</span></li>`;
      }
    };

    const open = () => {
      items = collectCommands();
      index = 0;
      dialog.showModal();
      input.value = "";
      render();
      input.focus();
    };

    const close = () => dialog.open && dialog.close();

    openBtn?.addEventListener("click", open);
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) close();
    });

    input.addEventListener("input", () => {
      index = 0;
      render(input.value);
    });

    input.addEventListener("keydown", (event) => {
      const options = qsa("#cmdk-results a");
      if (event.key === "ArrowDown") {
        event.preventDefault();
        index = Math.min(options.length - 1, index + 1);
        render(input.value);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        index = Math.max(0, index - 1);
        render(input.value);
      } else if (event.key === "Enter") {
        event.preventDefault();
        options[index]?.click();
      }
    });

    document.addEventListener("keydown", (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        dialog.open ? close() : open();
      }
    });
  }

  function setupToasts() {
    qsa(".messagelist li").forEach((item) => {
      window.setTimeout(() => {
        item.style.opacity = "0";
        item.style.transform = "translateY(8px)";
        item.style.transition = "all 180ms ease";
        window.setTimeout(() => item.remove(), 200);
      }, 4200);
    });
  }

  setupAvatar();
  setupUserMenu();
  setupCommandPalette();
  setupToasts();
})();
