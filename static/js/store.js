(() => {
  const getCookie = (name) => {
    const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
    return match ? decodeURIComponent(match[1]) : "";
  };

  const toast = (message) => {
    const el = document.querySelector("[data-toast]");
    if (!el) return;
    el.textContent = message;
    el.hidden = false;
    el.classList.add("is-visible");
    window.clearTimeout(toast._timer);
    toast._timer = window.setTimeout(() => {
      el.classList.remove("is-visible");
      el.hidden = true;
    }, 2200);
  };

  const setBadge = (selector, count) => {
    const value = Number(count) || 0;
    document.querySelectorAll(selector).forEach((badge) => {
      badge.textContent = String(value);
      badge.hidden = value <= 0;
      badge.classList.toggle("is-empty", value <= 0);
    });
  };

  const copyText = async (value) => {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(value);
      return;
    }
    const input = document.createElement("input");
    input.value = value;
    document.body.appendChild(input);
    input.select();
    document.execCommand("copy");
    input.remove();
  };

  const trackShare = async (slug, channel) => {
    const response = await fetch(`/products/${slug}/share/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({ channel }),
    });
    if (!response.ok) {
      throw new Error("Share tracking failed");
    }
    return response.json();
  };

  const postForm = async (form) => {
    const response = await fetch(form.action, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        Accept: "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: new FormData(form),
    });
    if (!response.ok) {
      throw new Error("Request failed");
    }
    return response.json();
  };

  const nav = document.querySelector("[data-site-nav]");
  const toggle = document.querySelector("[data-nav-toggle]");
  const backdrop = document.querySelector("[data-nav-backdrop]");

  const setNavOpen = (open) => {
    document.body.classList.toggle("nav-open", open);
    if (toggle) toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (toggle) toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    if (backdrop) backdrop.hidden = !open;
  };

  toggle?.addEventListener("click", () => {
    setNavOpen(!document.body.classList.contains("nav-open"));
  });
  backdrop?.addEventListener("click", () => setNavOpen(false));
  nav?.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => setNavOpen(false));
  });
  window.addEventListener("keydown", (event) => {
    if (event.key === "Escape") setNavOpen(false);
  });

  document.addEventListener("submit", async (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;

    if (form.matches("[data-cart-add]")) {
      event.preventDefault();
      try {
        const data = await postForm(form);
        setBadge("[data-cart-count]", data.item_count);
        toast(data.message || "Added to cart");
      } catch {
        form.submit();
      }
      return;
    }

    if (form.matches("[data-favourite-toggle]")) {
      event.preventDefault();
      try {
        const data = await postForm(form);
        setBadge("[data-favourite-count]", data.favourite_count);
        const button = form.querySelector("button");
        if (button) {
          button.classList.toggle("is-active", Boolean(data.favourited));
          button.setAttribute("aria-pressed", data.favourited ? "true" : "false");
          button.textContent = data.favourited ? "Saved" : "Favourite";
          if (button.classList.contains("btn--ghost") && button.closest(".product-detail")) {
            button.textContent = data.favourited
              ? "Saved to favourites"
              : "Add to favourites";
          }
        }
        toast(data.message || "Favourites updated");
      } catch {
        form.submit();
      }
    }
  });

  document.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-share-product]");
    if (!button) return;

    const slug = button.dataset.shareProduct;
    const url = button.dataset.shareUrl || document.querySelector("[data-share-input]")?.value;
    const title = button.dataset.shareTitle || "ElectroMarket";
    const status = document.querySelector("[data-share-status]");
    if (!url) return;

    try {
      if (navigator.share) {
        await navigator.share({ title, text: title, url });
        await trackShare(slug, "native");
        if (status) status.textContent = "Shared via device share sheet.";
        return;
      }
      await copyText(url);
      await trackShare(slug, "copy");
      if (status) status.textContent = "Public link copied to clipboard.";
    } catch (error) {
      if (error?.name === "AbortError") return;
      try {
        await copyText(url);
        await trackShare(slug, "copy");
        if (status) status.textContent = "Public link copied to clipboard.";
      } catch {
        if (status) status.textContent = "Could not share. Copy the link manually.";
      }
    }
  });
})();
