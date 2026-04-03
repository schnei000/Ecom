import { useEffect, useRef } from 'react';

/**
 * Attaches an IntersectionObserver to a container ref.
 * Also watches for newly-added children via MutationObserver,
 * so dynamically-rendered items (e.g. after a fetch) are detected.
 *
 * Usage:
 *   const ref = useScrollReveal();
 *   <section ref={ref}>
 *     <div className="reveal delay-200">…</div>
 *   </section>
 */
export default function useScrollReveal(threshold = 0.1) {
    const ref = useRef(null);

    useEffect(() => {
        const el = ref.current;
        if (!el) return;

        const SELECTOR = '.reveal, .reveal-left, .reveal-scale';

        const io = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                        io.unobserve(entry.target);
                    }
                });
            },
            { threshold }
        );

        /* Observe an element if not already visible */
        const observe = (node) => {
            if (!node.classList.contains('visible')) {
                io.observe(node);
            }
        };

        /* Observe existing children */
        el.querySelectorAll(SELECTOR).forEach(observe);

        /* Watch for children added later (e.g. after API fetch) */
        const mo = new MutationObserver((mutations) => {
            mutations.forEach((m) => {
                m.addedNodes.forEach((node) => {
                    if (node.nodeType !== 1) return;          // elements only
                    if (node.matches?.(SELECTOR)) observe(node);
                    node.querySelectorAll?.(SELECTOR).forEach(observe);
                });
            });
        });

        mo.observe(el, { childList: true, subtree: true });

        return () => {
            io.disconnect();
            mo.disconnect();
        };
    }, [threshold]);

    return ref;
}
