  const sidebar =
            document.getElementById("sidebar");

        const toggleSidebar =
            document.getElementById("toggleSidebar");

        const toggleTheme =
            document.getElementById("toggleTheme");

        /* Sidebar */

        if (localStorage.getItem("sidebar") === "collapsed") {
            sidebar.classList.add("collapsed");
        }

        toggleSidebar.addEventListener("click", () => {

            sidebar.classList.toggle("collapsed");

            localStorage.setItem(
                "sidebar",
                sidebar.classList.contains("collapsed")
                    ? "collapsed"
                    : "expanded"
            );

        });

        /* Theme */

        if (localStorage.getItem("theme") === "light") {
            document.body.classList.add("light");
        }

        toggleTheme.addEventListener("click", () => {

            document.body.classList.toggle("light");

            localStorage.setItem(
                "theme",
                document.body.classList.contains("light")
                    ? "light"
                    : "dark"
            );

        });

