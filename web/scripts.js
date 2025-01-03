document.addEventListener('DOMContentLoaded', function() {
    const links = document.querySelectorAll('nav ul li a');

    function scrollToSection(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href').substring(1);
        const targetSection = document.getElementById(targetId);

        window.scrollTo({
            top: targetSection.offsetTop - 50,
            behavior: 'smooth'
        });
    }

    links.forEach(link => {
        link.addEventListener('click', scrollToSection);
    });

    function highlightActiveLink() {
        const scrollPosition = window.scrollY;
        links.forEach(link => {
            const targetId = link.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            const sectionTop = targetSection.offsetTop - 50;
            const sectionBottom = sectionTop + targetSection.offsetHeight;

            if (scrollPosition >= sectionTop && scrollPosition <= sectionBottom) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    window.addEventListener('scroll', highlightActiveLink);

    highlightActiveLink();
});