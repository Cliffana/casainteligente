document.addEventListener('DOMContentLoaded', function() {
    var toggle = document.querySelector('.nav-toggle');
    var links = document.querySelector('.nav-links');
    if (toggle && links) {
        toggle.addEventListener('click', function() {
            links.classList.toggle('open');
        });
        document.addEventListener('click', function(e) {
            if (!toggle.contains(e.target) && !links.contains(e.target)) {
                links.classList.remove('open');
            }
        });
    }

    var toc = document.getElementById('toc');
    if (toc) {
        var headings = document.querySelectorAll('.article-content h2, .article-content h3');
        if (headings.length > 1) {
            var list = document.createElement('ul');
            var lastH2 = null;
            headings.forEach(function(h, i) {
                if (!h.id) { h.id = 's' + i; }
                var li = document.createElement('li');
                var a = document.createElement('a');
                a.href = '#' + h.id;
                a.textContent = h.textContent;
                if (h.tagName === 'H3') {
                    if (lastH2) {
                        var subUl = lastH2.querySelector('ul');
                        if (!subUl) {
                            subUl = document.createElement('ul');
                            lastH2.appendChild(subUl);
                        }
                        var subLi = document.createElement('li');
                        subLi.appendChild(a);
                        subUl.appendChild(subLi);
                    }
                } else {
                    li.appendChild(a);
                    list.appendChild(li);
                    lastH2 = li;
                }
            });
            if (list.children.length > 1 || (list.children.length === 1 && list.querySelector('ul'))) {
                toc.appendChild(list);
            } else {
                toc.style.display = 'none';
            }
        } else {
            toc.style.display = 'none';
        }
    }

    var langToggle = document.querySelector('.lang-toggle');
    var langDropdown = document.querySelector('.lang-dropdown');
    if (langToggle && langDropdown) {
        document.addEventListener('click', function(e) {
            if (!langToggle.contains(e.target) && !langDropdown.contains(e.target)) {
                langDropdown.classList.remove('open');
            }
        });
    }

    document.querySelectorAll('a.affiliate-link').forEach(function(link) {
        link.addEventListener('click', function(e) {
            try {
                var url = link.getAttribute('href');
                var label = link.textContent.trim().substring(0, 100);
                if (typeof window.goatcounter !== 'undefined' && window.goatcounter.count) {
                    window.goatcounter.count({
                        path: '/outbound/affiliate',
                        event: true,
                        title: label
                    });
                }
            } catch(err) {}
        });
    });

    // ---- Geo-aware affiliate links ----
    // US → amazon.com (casaintel0c20-20)
    // FR → amazon.fr / DE → amazon.de (mesmo tag ES: casainteli0e7-21)
    // Resto → amazon.es (casainteli0e7-21)
    var MARKETPLACES = {
        'US': { domain: 'amazon.com', tag: 'casaintel0c20-20' },
        'FR': { domain: 'amazon.fr', tag: 'casainteli0e7-21' },
        'DE': { domain: 'amazon.de', tag: 'casainteli0e7-21' },
        'default': { domain: 'amazon.es', tag: 'casainteli0e7-21' },
    };

    function getCountryFromLocale() {
        var lang = navigator.language || navigator.userLanguage || '';
        if (lang === 'fr' || lang.startsWith('fr-')) return 'FR';
        if (lang === 'de' || lang.startsWith('de-')) return 'DE';
        if (lang.endsWith('-US')) return 'US';
        if (lang === 'en' || lang.startsWith('en-')) return 'US';
        return null;
    }

    function getMarketplace(country) {
        return MARKETPLACES[country] || MARKETPLACES['default'];
    }

    function rewriteAffiliateLinks(mp) {
        var es_domain = 'amazon.es';
        var es_tag = 'casainteli0e7-21';
        document.querySelectorAll('a[href*="' + es_domain + '"]').forEach(function(a) {
            a.href = a.href
                .replace(es_domain, mp.domain)
                .replace(es_tag, mp.tag);
        });
    }

    function applyGeo() {
        var cached = localStorage.getItem('geo_marketplace');
        if (cached) {
            rewriteAffiliateLinks(getMarketplace(cached));
            return;
        }

        var fromLocale = getCountryFromLocale();
        if (fromLocale) {
            localStorage.setItem('geo_marketplace', fromLocale);
            rewriteAffiliateLinks(getMarketplace(fromLocale));
        }

        // Async IP check for accuracy
        fetch('https://ipapi.co/json/')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var country = data.country_code;
                if (!country) return;
                localStorage.setItem('geo_marketplace', country);
                rewriteAffiliateLinks(getMarketplace(country));
            })
            .catch(function() {});
    }

    applyGeo();
});
