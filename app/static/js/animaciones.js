document.addEventListener("DOMContentLoaded", () => {
    /* ---------- AOS (revelado al hacer scroll) ---------- */
    if (typeof AOS !== "undefined") {
        AOS.init({
            duration: 800,
            easing: "ease-out-cubic",
            once: true,
            offset: 80
        });
    }

    /* ---------- Carrusel: activa Ken Burns y textos ---------- */
    const hero = document.getElementById("hero-carousel");
    if (hero) {
        requestAnimationFrame(() => requestAnimationFrame(() => hero.classList.add("kb-ready")));
    }

    /* ---------- Contadores numéricos ---------- */
    const counters = document.querySelectorAll("[data-target]");
    if (!counters.length) return;

    const animateCounter = (el) => {
        const target = parseInt(el.dataset.target, 10);
        const suffix = el.dataset.suffix || "";
        const duration = 1800; // milisegundos
        const start = performance.now();

        const tick = (now) => {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // frena suave al final
            el.textContent = Math.round(target * eased) + suffix;

            if (progress < 1) {
                requestAnimationFrame(tick);
            } else {
                el.textContent = target + suffix; // valor exacto final
            }
        };
        requestAnimationFrame(tick);
    };

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                obs.unobserve(entry.target); // cuenta una sola vez
            }
        });
    }, { threshold: 0.3 });

    counters.forEach((c) => observer.observe(c));
}); // <-- cierre correcto

/* ---------- Newsletter del footer ---------- */
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("newsletter-form");
    if (!form) return;

    const input = form.querySelector('input[type="email"]');
    const msg = document.getElementById("newsletter-msg");

    form.addEventListener("submit", (e) => {
        e.preventDefault();

        if (!input.checkValidity()) {
            msg.textContent = "Ingresa un correo válido.";
            msg.classList.add("is-error");
            return;
        }

        // TODO: aquí irá el fetch POST a Flask cuando exista la ruta
        msg.classList.remove("is-error");
        msg.textContent = "¡Gracias por suscribirte!";
        form.reset();
    });
});

document.addEventListener("DOMContentLoaded", () => {
    /* ---------- AOS (revelado al hacer scroll) ---------- */
    if (typeof AOS !== "undefined") {
        AOS.init({
            duration: 800,
            easing: "ease-out-cubic",
            once: true,
            offset: 80
        });
    }

    /* ---------- Carrusel: activa Ken Burns y textos ---------- */
    const hero = document.getElementById("hero-carousel");
    if (hero) {
        requestAnimationFrame(() => requestAnimationFrame(() => hero.classList.add("kb-ready")));
    }

    /* ---------- Contadores numéricos ---------- */
    const counters = document.querySelectorAll("[data-target]");
    if (counters.length) {
        const animateCounter = (el) => {
            const target = parseInt(el.dataset.target, 10);
            const suffix = el.dataset.suffix || "";
            const duration = 1800; // milisegundos
            const start = performance.now();

            const tick = (now) => {
                const progress = Math.min((now - start) / duration, 1);
                const eased = 1 - Math.pow(1 - progress, 3); // frena suave al final
                el.textContent = Math.round(target * eased) + suffix;

                if (progress < 1) {
                    requestAnimationFrame(tick);
                } else {
                    el.textContent = target + suffix; // valor exacto final
                }
            };
            requestAnimationFrame(tick);
        };

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    animateCounter(entry.target);
                    obs.unobserve(entry.target); // cuenta una sola vez
                }
            });
        }, { threshold: 0.3 });

        counters.forEach((c) => observer.observe(c));
    }

    /* ---------- Newsletter del footer ---------- */
    const form = document.getElementById("newsletter-form");
    if (form) {
        const input = form.querySelector('input[type="email"]');
        const msg = document.getElementById("newsletter-msg");

        form.addEventListener("submit", (e) => {
            e.preventDefault();

            if (!input.checkValidity()) {
                msg.textContent = "Ingresa un correo válido.";
                msg.classList.add("is-error");
                return;
            }

            msg.classList.remove("is-error");
            msg.textContent = "¡Gracias por suscribirte!";
            form.reset();
        });
    }
});