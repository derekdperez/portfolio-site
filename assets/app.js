const root = document.documentElement;
const themeToggle = document.querySelector("[data-theme-toggle]");
const menuBtn = document.querySelector("[data-menu-toggle]");
const mobileMenu = document.getElementById("mobile-menu");
const backToTop = document.querySelector("[data-back-to-top]");
const toast = document.querySelector("[data-toast]");

const savedTheme = localStorage.getItem("avery-theme");
if (savedTheme) root.setAttribute("data-theme", savedTheme);

if (themeToggle) {
  themeToggle.addEventListener("click", () => {
    const next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
    root.setAttribute("data-theme", next);
    localStorage.setItem("avery-theme", next);
  });
}

if (menuBtn && mobileMenu) {
  menuBtn.addEventListener("click", () => {
    const expanded = menuBtn.getAttribute("aria-expanded") === "true";
    menuBtn.setAttribute("aria-expanded", String(!expanded));
    mobileMenu.hidden = expanded;
  });
}

const current = location.pathname.split("/").pop() || "index.html";
document.querySelectorAll(".desktop-nav a").forEach((a) => {
  const href = a.getAttribute("href");
  if (href === current) a.setAttribute("aria-current", "page");
});

document.querySelectorAll(".reveal").forEach((el) => {
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.16 });
  io.observe(el);
});

document.querySelectorAll("[data-counter]").forEach((el) => {
  const target = Number(el.dataset.counter);
  const suffix = el.dataset.suffix || "";
  let started = false;
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting || started) return;
      started = true;
      let value = 0;
      const step = Math.max(1, Math.ceil(target / 34));
      const tick = () => {
        value += step;
        if (value >= target) {
          el.textContent = target + suffix;
        } else {
          el.textContent = value + suffix;
          requestAnimationFrame(tick);
        }
      };
      tick();
      io.disconnect();
    });
  }, { threshold: 0.4 });
  io.observe(el);
});

document.querySelectorAll("[data-tabs]").forEach((group) => {
  const buttons = group.querySelectorAll("[data-tab-btn]");
  const panels = group.querySelectorAll("[data-tab-panel]");
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const name = btn.dataset.tabBtn;
      buttons.forEach((b) => b.classList.toggle("active", b === btn));
      panels.forEach((panel) => panel.classList.toggle("active", panel.dataset.tabPanel === name));
    });
  });
});

document.querySelectorAll(".accordion-item").forEach((item, index) => {
  const btn = item.querySelector(".accordion-btn");
  if (!btn) return;
  if (index === 0) item.classList.add("open");
  btn.addEventListener("click", () => item.classList.toggle("open"));
});

document.querySelectorAll("[data-filter-group]").forEach((wrap) => {
  const cards = document.querySelectorAll("[data-project-card]");
  const search = document.querySelector("[data-project-search]");
  const chips = wrap.querySelectorAll(".chip");
  let active = "all";

  const apply = () => {
    const q = (search?.value || "").toLowerCase().trim();
    let shown = 0;
    cards.forEach((card) => {
      const category = card.dataset.category;
      const text = card.textContent.toLowerCase();
      const matchesCategory = active === "all" || category === active;
      const matchesSearch = !q || text.includes(q);
      const show = matchesCategory && matchesSearch;
      card.hidden = !show;
      if (show) shown += 1;
    });
    const empty = document.querySelector("[data-empty-state]");
    if (empty) empty.hidden = shown !== 0;
  };

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chips.forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      active = chip.dataset.filter || "all";
      apply();
    });
  });

  search?.addEventListener("input", apply);
  apply();
});

document.querySelectorAll("[data-modal-trigger]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const card = btn.closest("[data-project-card]");
    const title = card?.querySelector("h3")?.textContent || "Project preview";
    const summary = card?.querySelector("p")?.textContent || "";
    alert(title + "\n\n" + summary + "\n\nThis is a static preview modal stand-in.");
    if (toast) {
      toast.hidden = false;
      setTimeout(() => (toast.hidden = true), 1200);
    }
  });
});

document.querySelectorAll("[data-carousel]").forEach((carousel) => {
  const track = carousel.querySelector(".carousel-track");
  const items = carousel.querySelectorAll(".testimonial");
  const next = carousel.querySelector("[data-next]");
  const prev = carousel.querySelector("[data-prev]");
  let index = 0;
  const render = () => track.style.transform = "translateX(-" + (index * 100) + "%)";
  next?.addEventListener("click", () => { index = (index + 1) % items.length; render(); });
  prev?.addEventListener("click", () => { index = (index - 1 + items.length) % items.length; render(); });
});

window.addEventListener("scroll", () => {
  if (!backToTop) return;
  backToTop.classList.toggle("show", window.scrollY > 700);
});

backToTop?.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

document.querySelectorAll("[data-toc] a").forEach((link) => {
  link.addEventListener("click", () => {
    document.querySelectorAll("[data-toc] a").forEach((a) => a.classList.remove("active"));
    link.classList.add("active");
  });
});
