document.addEventListener("DOMContentLoaded", () => {
    /* ---------- Revelado sutil del contenido al desplazarse ---------- */
    const main = document.querySelector("main");
    const revealTargets = main
        ? main.querySelectorAll(
            ":scope > section:not([data-aos]), " +
            ":scope > div:not([data-aos]), " +
            ".grid > *:not([data-aos]), " +
            "article:not([data-aos])"
        )
        : [];

    if (
        revealTargets.length &&
        !window.matchMedia("(prefers-reduced-motion: reduce)").matches &&
        "IntersectionObserver" in window
    ) {
        revealTargets.forEach((element) => {
            const siblingIndex = Array.prototype.indexOf.call(
                element.parentElement.children,
                element
            );
            element.style.setProperty(
                "--reveal-delay",
                `${Math.min(siblingIndex, 4) * 35}ms`
            );
            element.dataset.reveal = "";
        });

        document.body.classList.add("motion-ready");

        const revealObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.08, rootMargin: "0px 0px -32px 0px" });

        revealTargets.forEach((element) => revealObserver.observe(element));
    }

    /* ---------- AOS (revelado al hacer scroll) ---------- */
    if (typeof AOS !== "undefined") {
        AOS.init({
            duration: 550,
            easing: "ease-out-cubic",
            once: true,
            offset: 50
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

        if ("IntersectionObserver" in window) {
            const observer = new IntersectionObserver((entries, obs) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        animateCounter(entry.target);
                        obs.unobserve(entry.target); // cuenta una sola vez
                    }
                });
            }, { threshold: 0.3 });

            counters.forEach((counter) => observer.observe(counter));
        } else {
            counters.forEach((counter) => {
                counter.textContent =
                    counter.dataset.target + (counter.dataset.suffix || "");
            });
        }
    }
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