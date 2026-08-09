document.addEventListener("DOMContentLoaded", () => {
  const track = document.querySelector(".ranking-track");

  if (!track) return;

  const speed = 0.6;

  let animationId;

  let paused = false;

  track.innerHTML += track.innerHTML;

  let x = 0;

  function animate() {
    if (!paused) {
      x -= speed;

      const width = track.scrollWidth / 2;

      if (Math.abs(x) >= width) {
        x = 0;
      }

      track.style.transform = `translateX(${x}px)`;
    }

    animationId = requestAnimationFrame(animate);
  }

  animate();

  track.addEventListener("mouseenter", () => {
    paused = true;
  });

  track.addEventListener("mouseleave", () => {
    paused = false;
  });

  window.addEventListener("blur", () => {
    paused = true;
  });

  window.addEventListener("focus", () => {
    paused = false;
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll(".counter");

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;

        const counter = entry.target;

        const target = Number(counter.dataset.target);

        let current = 0;

        const duration = 1800;

        const step = target / (duration / 16);

        function update() {
          current += step;

          if (current >= target) {
            current = target;
          }

          if (target >= 100) {
            counter.textContent = Math.round(current) + "%";
          } else {
            counter.textContent = Math.round(current) + "+";
          }

          if (current < target) {
            requestAnimationFrame(update);
          }
        }

        update();

        observer.unobserve(counter);
      });
    },
    {
      threshold: 0.5,
    },
  );

  counters.forEach((counter) => observer.observe(counter));
});

document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector(".sidebar");
  const navLinks = document.querySelectorAll(".side-nav a");
  const navGroups = document.querySelectorAll(".nav-group");

  /* ---------------------------------
       Restore Sidebar State
    --------------------------------- */

  if (localStorage.getItem("sidebar-collapsed") === "true") {
    sidebar.classList.add("collapsed");
  }

  /* ---------------------------------
       Sidebar Toggle
    --------------------------------- */

  const toggleBtn = document.querySelector(".sidebar-toggle");

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");

      localStorage.setItem(
        "sidebar-collapsed",
        sidebar.classList.contains("collapsed"),
      );
    });
  }

  /* ---------------------------------
       Active Menu
    --------------------------------- */

  const current = window.location.pathname.replace(/\/$/, "");

  let activeLink = null;
  let longestMatch = 0;

  document.querySelectorAll(".side-nav a").forEach((link) => {
    const href = new URL(link.href).pathname.replace(/\/$/, "");

    if (current === href && href.length > longestMatch) {
      longestMatch = href.length;
      activeLink = link;
    }
  });

  document.querySelectorAll(".side-nav a.active").forEach((link) => {
    link.classList.remove("active");
  });

  if (activeLink) {
    activeLink.classList.add("active");

    const group = activeLink.closest(".nav-group");

    if (group) {
      group.classList.remove("collapsed");
    }
  }

  /* ---------------------------------
       Collapsible Groups
    --------------------------------- */

  navGroups.forEach((group, index) => {
    const title = group.querySelector(".nav-title");

    if (!title) return;

    const storageKey = `sidebar-group-${index}`;

    if (localStorage.getItem(storageKey) === "collapsed") {
      group.classList.add("collapsed");
    }

    title.addEventListener("click", () => {
      group.classList.toggle("collapsed");

      localStorage.setItem(
        storageKey,

        group.classList.contains("collapsed") ? "collapsed" : "expanded",
      );
    });
  });

  /* ---------------------------------
       Tooltip
    --------------------------------- */

  navLinks.forEach((link) => {
    link.setAttribute("data-tooltip", link.innerText.trim());
  });

  /* ---------------------------------
       Ctrl + B
    --------------------------------- */

  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key.toLowerCase() === "b") {
      e.preventDefault();

      sidebar.classList.toggle("collapsed");

      localStorage.setItem(
        "sidebar-collapsed",

        sidebar.classList.contains("collapsed"),
      );
    }
  });

  /* ---------------------------------
       Loading Animation
    --------------------------------- */

  navLinks.forEach((link) => {
    link.addEventListener("click", function () {
      navLinks.forEach((item) => {
        item.classList.remove("loading");
      });

      this.classList.add("loading");
    });
  });

  /* ---------------------------------
       Hover Animation
    --------------------------------- */

  navLinks.forEach((link) => {
    link.addEventListener("mouseenter", () => {
      if (!sidebar.classList.contains("collapsed")) return;

      link.classList.add("hovering");
    });

    link.addEventListener("mouseleave", () => {
      link.classList.remove("hovering");
    });
  });
});

document.querySelectorAll("[data-table]").forEach((table) => {
  const input = document.querySelector(
    `[data-filter="${table.dataset.table}"]`,
  );
  const rows = Array.from(table.querySelectorAll("tbody tr"));
  const pageSize = Number(table.dataset.pageSize || 12);
  let page = 1;

  function visibleRows() {
    const term = (input?.value || "").toLowerCase();
    return rows.filter((row) => row.innerText.toLowerCase().includes(term));
  }

  function render() {
    const filtered = visibleRows();
    const total = Math.max(1, Math.ceil(filtered.length / pageSize));
    page = Math.min(page, total);

    rows.forEach((row) => (row.style.display = "none"));

    filtered
      .slice((page - 1) * pageSize, page * pageSize)
      .forEach((row) => (row.style.display = ""));

    const pager = document.querySelector(
      `[data-pager="${table.dataset.table}"]`,
    );

    if (pager) {
      pager.querySelector("[data-page]").textContent = `${page} / ${total}`;
      pager.querySelector("[data-prev]").disabled = page === 1;
      pager.querySelector("[data-next]").disabled = page === total;
    }
  }

  table.querySelectorAll("th[data-sort]").forEach((th, index) => {
    th.addEventListener("click", () => {
      rows.sort((a, b) =>
        a.children[index].innerText.localeCompare(b.children[index].innerText),
      );

      rows.forEach((row) => table.tBodies[0].appendChild(row));

      render();
    });
  });

  input?.addEventListener("input", () => {
    page = 1;
    render();
  });

  document
    .querySelector(`[data-pager="${table.dataset.table}"] [data-prev]`)
    ?.addEventListener("click", () => {
      page--;
      render();
    });

  document
    .querySelector(`[data-pager="${table.dataset.table}"] [data-next]`)
    ?.addEventListener("click", () => {
      page++;
      render();
    });

  render();
});
