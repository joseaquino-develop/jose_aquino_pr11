// JS principal del proyecto.
// Tailwind se usa por CDN (ver templates/base.html), así que este archivo
// es para pequeñas interacciones propias del sitio.
document.addEventListener("DOMContentLoaded", () => {
    console.log("Mi Proyecto listo.");

    const header = document.getElementById('site-header');
    if (!header) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 20) {
            header.classList.add('navbar--scrolled');
        } else {
            header.classList.remove('navbar--scrolled');
        }
    });
});

// ==========================================
// FUNCIONALIDAD: BOTÓN VOLVER ARRIBA
// ==========================================

document.addEventListener("DOMContentLoaded", () => {

    // Crear el botón
    const botonArriba = document.createElement("button");

    botonArriba.innerHTML = "↑";
    botonArriba.id = "btn-volver-arriba";
    botonArriba.title = "Volver arriba";
    botonArriba.setAttribute("aria-label", "Volver al inicio de la página");

    // Agregar el botón al body
    document.body.appendChild(botonArriba);

    // Mostrar u ocultar dependiendo del scroll
    window.addEventListener("scroll", () => {

        if (window.scrollY > 300) {
            botonArriba.classList.add("mostrar");
        } else {
            botonArriba.classList.remove("mostrar");
        }

    });

    // Volver arriba al hacer clic
    botonArriba.addEventListener("click", () => {

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    });

});

// ==========================================
// BLOQUEO DE AVANCE Y VALIDACIÓN ESTRICTA
// ==========================================
    const botonesNext = document.querySelectorAll('[data-next]');

    botonesNext.forEach(btn => {
        // Capturamos el clic en la fase inicial (Capture Phase) para interceptarlo ANTES de cualquier otro script
        btn.addEventListener('click', (e) => {
            const currentPanel = btn.closest('.step-panel') || btn.closest('fieldset') || btn.closest('form');

            if (!currentPanel) return;

            // Expresiones Regulares
            const regexLetras = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s.]+$/;
            const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            const regexNumeros = /^\d+$/;
            const regexTelefono = /^\d{9,15}$/;

            const inputs = currentPanel.querySelectorAll('input, select, textarea');

            for (const inp of inputs) {
                const value = inp.value.trim();
                const name = (inp.name || '').toLowerCase();
                const type = (inp.type || '').toLowerCase();

                // A) CAMPOS OBLIGATORIOS VACÍOS
                if (inp.hasAttribute('required') && !value) {
                    alert(`El campo "${(name || 'requerido').toUpperCase()}" es obligatorio.`);
                    inp.focus();
                    
                    // BLOQUEO TOTAL DEL AVANCE
                    e.preventDefault();
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                    return false;
                }

                if (!value) continue; // Si no es obligatorio y está vacío, salta al siguiente

                // B) VALIDAR CORREO ELECTRÓNICO (Formato usuario@dominio.com)
                if (type === 'email' || name.includes('correo') || name.includes('email')) {
                    if (!regexEmail.test(value)) {
                        alert('⚠️ CORREO INVÁLIDO: Ingresa un correo electrónico correcto (ejemplo: contacto@empresa.com).');
                        inp.focus();
                        
                        // BLOQUEO TOTAL DEL AVANCE
                        e.preventDefault();
                        e.stopPropagation();
                        e.stopImmediatePropagation();
                        return false;
                    }
                }

                // C) VALIDAR TELÉFONO (Solo números)
                if (type === 'tel' || name.includes('telefono') || name.includes('celular')) {
                    if (!regexTelefono.test(value)) {
                        alert('⚠️ TELÉFONO INVÁLIDO: Debe contener solo números y mínimo 9 dígitos.');
                        inp.focus();
                        
                        // BLOQUEO TOTAL DEL AVANCE
                        e.preventDefault();
                        e.stopPropagation();
                        e.stopImmediatePropagation();
                        return false;
                    }
                }

                // D) VALIDAR SOLO LETRAS (Empresa, Contacto, Cargo, País)
                if (['empresa', 'contacto', 'cargo', 'pais', 'destino', 'nota'].some(k => name.includes(k))) {
                    if (!regexLetras.test(value)) {
                        alert(`⚠️ TEXTO INVÁLIDO: El campo "${name.toUpperCase()}" solo debe contener letras y espacios.`);
                        inp.focus();
                        
                        // BLOQUEO TOTAL DEL AVANCE
                        e.preventDefault();
                        e.stopPropagation();
                        e.stopImmediatePropagation();
                        return false;
                    }
                }

                // E) VALIDAR CANTIDAD (Solo dígitos)
                if (name.includes('cantidad') || type === 'number') {
                    if (!regexNumeros.test(value)) {
                        alert('⚠️️ CANTIDAD INVÁLIDA: Solo se permiten números enteros.');
                        inp.focus();
                        
                        // BLOQUEO TOTAL DEL AVANCE
                        e.preventDefault();
                        e.stopPropagation();
                        e.stopImmediatePropagation();
                        return false;
                    }
                }

                // F) VALIDAR NOTAS ADICIONALES (Letras, números y puntuación básica)
                if (name.includes('nota') || name.includes('mensaje') || name.includes('comentario')) {
               // Permite letras, números, espacios y la puntuación: . , ; : ? ! ( ) -
                const regexNotas = /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s.,;:?!()\-\n\r]+$/;
    
                    if (!regexNotas.test(value)) {
                        alert('⚠️ NOTAS ADICIONALES: No se permiten caracteres especiales como < > { } [ ] / \\ # $ % ^ & *');
                        inp.focus();
        
                        // BLOQUEO TOTAL DEL AVANCE
                        e.preventDefault();
                        e.stopPropagation();
                        e.stopImmediatePropagation();
                        return false;
                   }
                }
            }

            // Si todo está correcto, permite pasar al siguiente paso
        }, true); // El 'true' activa el modo captura para ejecutarse ANTES de cualquier función inline en HTML
    });

// ==========================================
// FUNCIONALIDAD: CHATBOT DE PREGUNTAS FRECUENTES
// ==========================================

document.addEventListener("DOMContentLoaded", () => {
    const toggleBtn = document.getElementById("chatbot-toggle-btn");
    const closeBtn = document.getElementById("chatbot-close-btn");
    const chatWindow = document.getElementById("chatbot-window");
    const sendBtn = document.getElementById("chatbot-send-btn");
    const inputField = document.getElementById("chatbot-input");
    const messagesContainer = document.getElementById("chatbot-messages");
    const faqChips = document.querySelectorAll(".faq-chip");

    if (!toggleBtn || !chatWindow) return;

    // Base de conocimiento estática (FAQs)
    const faqDatabase = [
        { keywords: ["horario", "hora", "atencion", "abren"], answer: "Nuestro horario de atención es de lunes a sábado de 8:00 a.m. a 6:00 p.m." },
        { keywords: ["producto", "hass", "palta", "venden"], answer: "Ofrecemos productos agrícolas de calidad, destacando nuestra palta Hass y derivados desde San José de los Molinos, Ica." },
        { keywords: ["contacto", "telefono", "correo", "comunicar", "llamar"], answer: "Puedes comunicarte mediante nuestra sección de Contacto o solicitando una cotización directamente en la web." },
        { keywords: ["ubicacion", "direccion", "donde", "san jose", "ica"], answer: "Nos encontramos ubicados en San José de los Molinos, Ica." }
    ];

    // Abrir y cerrar la ventana del chat
    toggleBtn.addEventListener("click", () => {
        chatWindow.classList.toggle("hidden");
        chatWindow.classList.toggle("flex");
    });

    closeBtn.addEventListener("click", () => {
        chatWindow.classList.add("hidden");
        chatWindow.classList.remove("flex");
    });

    // Función para agregar mensajes visuales en el chat
    function appendMessage(text, sender) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `p-2.5 rounded-lg max-w-[85%] text-xs ${sender === 'user' ? 'bg-amber-500 text-white self-end ml-auto' : 'bg-gray-200 text-gray-800 self-start'}`;
        msgDiv.textContent = text;
        messagesContainer.appendChild(msgDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Lógica de respuesta inteligente según palabras clave
    function handleUserMessage(query) {
        if (!query.trim()) return;
        appendMessage(query, "user");
        inputField.value = "";

        setTimeout(() => {
            const queryLower = query.toLowerCase();
            let matchedAnswer = "Disculpa, no entendí tu consulta. Prueba preguntando por 'horarios', 'productos' o 'contacto'.";

            for (let item of faqDatabase) {
                if (item.keywords.some(keyword => queryLower.includes(keyword))) {
                    matchedAnswer = item.answer;
                    break;
                }
            }
            appendMessage(matchedAnswer, "bot");
        }, 400);
    }

    // Eventos de envío (botón o tecla Enter)
    if (sendBtn && inputField) {
        sendBtn.addEventListener("click", () => handleUserMessage(inputField.value));
        inputField.addEventListener("keypress", (e) => {
            if (e.key === "Enter") handleUserMessage(inputField.value);
        });
    }

    // Eventos para los botones rápidos (chips)
    faqChips.forEach(chip => {
        chip.addEventListener("click", () => {
            handleUserMessage(chip.getAttribute("data-question"));
        });
    });
});

// ============================================================
// TRADUCTOR GLOBAL ES / EN
// Traduce automáticamente TODO el contenido visible
// de todas las páginas que carguen este main.js
// ============================================================

(function () {

    const IDIOMA_ORIGINAL = "es";
    const IDIOMAS = ["es", "en"];

    // ========================================================
    // INICIAR
    // ========================================================

    function iniciarTraductor() {

        crearContenedorGoogle();

        ocultarInterfazGoogle();

        cargarGoogleTranslate();

        configurarBotonesIdioma();

        observarContenidoNuevo();

    }


    // ========================================================
    // CREAR CONTENEDOR OCULTO
    // ========================================================

    function crearContenedorGoogle() {

        if (document.getElementById("google_translate_element")) {
            return;
        }

        const contenedor = document.createElement("div");

        contenedor.id = "google_translate_element";

        contenedor.style.position = "fixed";
        contenedor.style.left = "-9999px";
        contenedor.style.top = "-9999px";
        contenedor.style.width = "1px";
        contenedor.style.height = "1px";
        contenedor.style.overflow = "hidden";
        contenedor.style.opacity = "0";
        contenedor.style.pointerEvents = "none";

        document.body.appendChild(contenedor);

    }


    // ========================================================
    // INICIALIZAR GOOGLE TRANSLATE
    // ========================================================

    window.googleTranslateElementInit = function () {

        new google.translate.TranslateElement(
            {
                pageLanguage: "es",
                includedLanguages: "es,en",
                autoDisplay: false
            },
            "google_translate_element"
        );

        const idioma =
            localStorage.getItem("idiomaChavalina") || "es";

        actualizarBotones(idioma);

        if (idioma === "en") {

            setTimeout(function () {

                traducirConGoogle("en");

            }, 1000);

        }

    };


    // ========================================================
    // CARGAR SCRIPT DE GOOGLE
    // ========================================================

    function cargarGoogleTranslate() {

        if (
            document.getElementById(
                "google-translate-script"
            )
        ) {
            return;
        }

        const script =
            document.createElement("script");

        script.id =
            "google-translate-script";

        script.src =
            "https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit";

        script.async = true;

        document.body.appendChild(script);

    }


    // ========================================================
    // ESPERAR A QUE GOOGLE CARGUE
    // ========================================================

    function esperarSelectorGoogle(callback, intentos = 0) {

        const selector =
            document.querySelector(".goog-te-combo");

        if (selector) {

            callback(selector);

            return;

        }

        if (intentos >= 50) {

            console.error(
                "Google Translate no pudo cargarse."
            );

            return;

        }

        setTimeout(function () {

            esperarSelectorGoogle(
                callback,
                intentos + 1
            );

        }, 200);

    }


    // ========================================================
    // TRADUCIR PÁGINA COMPLETA
    // ========================================================

    function traducirConGoogle(idioma) {

        esperarSelectorGoogle(function (selector) {

            selector.value = idioma;

            selector.dispatchEvent(
                new Event(
                    "change",
                    {
                        bubbles: true
                    }
                )
            );

            document.documentElement.lang =
                idioma;

        });

    }


    // ========================================================
    // CAMBIAR IDIOMA
    // ========================================================

    window.cambiarIdioma = function (idioma) {

        if (!IDIOMAS.includes(idioma)) {
            return;
        }

        localStorage.setItem(
            "idiomaChavalina",
            idioma
        );

        actualizarBotones(idioma);


        // ====================================================
        // INGLÉS
        // ====================================================

        if (idioma === "en") {

            traducirConGoogle("en");

            return;

        }


        // ====================================================
        // ESPAÑOL
        // ====================================================

        if (idioma === "es") {

            eliminarCookieGoogle();

            document.documentElement.lang =
                IDIOMA_ORIGINAL;

            /*
             * Google modifica el DOM directamente.
             * Recargar recupera el HTML original en español.
             */

            window.location.reload();

        }

    };


    // ========================================================
    // ELIMINAR COOKIE DE GOOGLE
    // ========================================================

    function eliminarCookieGoogle() {

        const dominios = [
            "",
            location.hostname,
            "." + location.hostname
        ];

        dominios.forEach(function (dominio) {

            let cookie =
                "googtrans=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/;";

            if (dominio) {

                cookie +=
                    "domain=" +
                    dominio +
                    ";";

            }

            document.cookie = cookie;

        });

    }


    // ========================================================
    // DETECTAR BOTONES ES / EN
    // ========================================================

    function configurarBotonesIdioma() {

        document.addEventListener(
            "click",
            function (evento) {

                const boton =
                    evento.target.closest(
                        "[data-lang]"
                    );

                if (!boton) {
                    return;
                }

                const idioma =
                    boton.dataset.lang;

                if (!IDIOMAS.includes(idioma)) {
                    return;
                }

                evento.preventDefault();

                cambiarIdioma(idioma);

            }
        );

    }


    // ========================================================
    // MOSTRAR CUÁL IDIOMA ESTÁ ACTIVO
    // ========================================================

    function actualizarBotones(idioma) {

        document
            .querySelectorAll("[data-lang]")
            .forEach(function (boton) {

                const activo =
                    boton.dataset.lang === idioma;

                boton.classList.toggle(
                    "font-bold",
                    activo
                );

                boton.classList.toggle(
                    "opacity-100",
                    activo
                );

                boton.classList.toggle(
                    "opacity-60",
                    !activo
                );

            });

    }


    // ========================================================
    // OCULTAR INTERFAZ DE GOOGLE
    // ========================================================

   function ocultarInterfazGoogle() {

    if (document.getElementById("google-translate-hide")) {
        return;
    }

    const style = document.createElement("style");

    style.id = "google-translate-hide";

    style.textContent = `

        /* Ocultar contenedor del traductor */
        #google_translate_element {
            position: absolute !important;
            left: -9999px !important;
            top: -9999px !important;
            width: 0 !important;
            height: 0 !important;
            overflow: hidden !important;
            opacity: 0 !important;
            visibility: hidden !important;
            pointer-events: none !important;
        }

        /* Ocultar barra superior de Google Translate */
        .goog-te-banner-frame,
        iframe.goog-te-banner-frame,
        .skiptranslate iframe,
        iframe.skiptranslate {
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
        }

        /* Evitar que Google baje la página */
        html {
            margin-top: 0 !important;
        }

        body {
            top: 0 !important;
            position: static !important;
            margin-top: 0 !important;
        }

        /* Ocultar ventanas flotantes */
        #goog-gt-tt,
        .goog-te-balloon-frame,
        .goog-te-menu-frame {
            display: none !important;
            visibility: hidden !important;
        }

        /* Quitar resaltado de Google */
        .goog-text-highlight {
            background-color: transparent !important;
            box-shadow: none !important;
        }

    `;

    document.head.appendChild(style);


    // Google crea la barra después de cargar.
    // Por eso también la eliminamos dinámicamente.
    const ocultarBarra = () => {

        document.documentElement.style.marginTop = "0px";
        document.body.style.top = "0px";
        document.body.style.marginTop = "0px";

        document
            .querySelectorAll(
                ".goog-te-banner-frame, iframe.goog-te-banner-frame"
            )
            .forEach(elemento => {
                elemento.style.display = "none";
                elemento.style.visibility = "hidden";
                elemento.style.height = "0";
            });

        document
            .querySelectorAll("iframe")
            .forEach(iframe => {

                const src = iframe.src || "";

                if (
                    src.includes("translate.google") ||
                    src.includes("translate.googleapis")
                ) {
                    iframe.style.display = "none";
                    iframe.style.visibility = "hidden";
                    iframe.style.height = "0";
                }

            });
    };


    // Ejecutar inmediatamente
    ocultarBarra();


    // Google puede crear la barra unos segundos después
    setInterval(ocultarBarra, 300);

}


    // ========================================================
    // OBSERVAR CONTENIDO CREADO DESPUÉS
    // ========================================================

    /*
     * Esto ayuda con contenido dinámico:
     * modales
     * chatbot
     * tarjetas
     * mensajes
     * elementos creados por JavaScript
     */

    function observarContenidoNuevo() {

        let temporizador = null;

        const observer =
            new MutationObserver(function () {

                document.body.style.top =
                    "0px";

                const idioma =
                    localStorage.getItem(
                        "idiomaChavalina"
                    );

                if (idioma !== "en") {
                    return;
                }

                clearTimeout(temporizador);

                temporizador =
                    setTimeout(function () {

                        const selector =
                            document.querySelector(
                                ".goog-te-combo"
                            );

                        if (
                            selector &&
                            selector.value !== "en"
                        ) {

                            selector.value = "en";

                            selector.dispatchEvent(
                                new Event(
                                    "change",
                                    {
                                        bubbles: true
                                    }
                                )
                            );

                        }

                    }, 300);

            });

        observer.observe(
            document.body,
            {
                childList: true,
                subtree: true
            }
        );

    }


    // ========================================================
    // EJECUTAR
    // ========================================================

    if (
        document.readyState === "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            iniciarTraductor
        );

    } else {

        iniciarTraductor();

    }

})();

//VALIDACIONES DE CONTACTO//

document.addEventListener('DOMContentLoaded', () => {
    // 1. Escuchar el evento submit del formulario de contacto
    const contactForm = document.getElementById('contactForm');

    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            // Expresiones Regulares
            const regexLetras = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s.]+$/;
            const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            const regexNotas = /^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s.,;:?!()\-\n\r]+$/;

            const inputs = contactForm.querySelectorAll('input, select, textarea');

            for (const inp of inputs) {
                const value = inp.value.trim();
                const name = (inp.name || '').toLowerCase();
                const type = (inp.type || '').toLowerCase();

                // A) CAMPOS OBLIGATORIOS VACÍOS
                if (inp.hasAttribute('required') && !value) {
                    alert(`⚠️ El campo "${(name || 'requerido').toUpperCase()}" es obligatorio.`);
                    inp.focus();

                    // BLOQUEO DE ENVÍO
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                }

                if (!value) continue; // Si el campo no es obligatorio y está vacío, salta al siguiente

                // B) VALIDAR NOMBRE / TEXTO (Solo letras y espacios)
                if (name.includes('nombre') || name.includes('asunto')) {
                    if (!regexLetras.test(value)) {
                        alert(`⚠️ TEXTO INVÁLIDO: El campo "${name.toUpperCase()}" solo debe contener letras y espacios.`);
                        inp.focus();

                        // BLOQUEO DE ENVÍO
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }
                }

                // C) VALIDAR CORREO ELECTRÓNICO (Formato usuario@dominio.com)
                if (type === 'email' || name.includes('correo') || name.includes('email')) {
                    if (!regexEmail.test(value)) {
                        alert('⚠️ CORREO INVÁLIDO: Ingresa un correo electrónico correcto (ejemplo: contacto@empresa.com).');
                        inp.focus();

                        // BLOQUEO DE ENVÍO
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }
                }

                // D) VALIDAR MENSAJE (Sin caracteres especiales peligrosos como < > { } etc.)
                if (name.includes('mensaje')) {
                    if (!regexNotas.test(value)) {
                        alert('⚠️ MENSAJE INVÁLIDO: No se permiten caracteres especiales como < > { } [ ] / \\ # $ % ^ & *');
                        inp.focus();

                        // BLOQUEO DE ENVÍO
                        e.preventDefault();
                        e.stopPropagation();
                        return false;
                    }
                }
            }

            // Si pasa todas las validaciones, se envía a Flask correctamente
        });
    }
});
