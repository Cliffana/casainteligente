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
                if (!h.id) {
                    h.id = 's' + i;
                }
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
});
