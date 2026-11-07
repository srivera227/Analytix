const btnProbarConexion = document.getElementById("btnProbarConexion");
const dbStatus = document.getElementById("dbStatus");
const urlBase = "http://127.0.0.1:8000/synergy/conectarDataBase/"

btnProbarConexion.addEventListener("click", async () => {
    const datosConexion = {
        motor: document.getElementById("dbMotor").value,
        host: document.getElementById("dbHost").value.trim(),
        port: document.getElementById("dbPort").value,
        database: document.getElementById("dbDatabase").value.trim(),
        user: document.getElementById("dbUser").value.trim(),
        password: document.getElementById("dbPassword").value
    };

    btnProbarConexion.disabled = true;
    dbStatus.className = "db-status";
    dbStatus.textContent = "Probando conexión...";

    try {
        const response = await fetch("synergy/conectarDataBase/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify(datosConexion)
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "No fue posible conectar con la base de datos.");
        }

        dbStatus.className = "db-status success";
        dbStatus.textContent = `${data.mensaje} ${data.id_conexion}` || "Conexión establecida correctamente.";

    } catch (error) {
        console.error("Error al conectar la base de datos:", error);

        dbStatus.className = "db-status error";
        dbStatus.textContent = error.message || "Error al conectar con la base de datos.";

    } finally {
        btnProbarConexion.disabled = false;
    }
});

const btnBasesDatos = document.getElementById("btnBasesDatos");
const dbModal = document.getElementById("dbModal");

if (btnBasesDatos && dbModal) {

    btnBasesDatos.addEventListener("click", (e) => {
        e.preventDefault();
        dbModal.classList.add("active");
    });

}

const btnCerrarConexion =
    document.getElementById("btnCerrarConexion");

if (btnCerrarConexion) {
    btnCerrarConexion.addEventListener("click", () => {
        dbModal.classList.remove("active");
    });
}

function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies =
            document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {

                cookieValue =
                    decodeURIComponent(
                        cookie.substring(
                            name.length + 1
                        )
                    );

                break;
            }
        }
    }

    return cookieValue;
}

/*Funcionalidad del modal de administración de conexiones*/
const modalConexiones = document.getElementById(
    "modalAdministrarConexiones"
);

const listaConexiones = document.getElementById("listaConexiones");
const buscarConexion = document.getElementById("buscarConexion");
const mensajeConexiones = document.getElementById("mensajeConexiones");

let conexiones = [];
let conexionActivaId = null;

function abrirModalConexiones() {
    modalConexiones.hidden = false;
    document.body.classList.add("modal-abierto");
    cargarConexiones();
}

function cerrarModalConexiones() {
    modalConexiones.hidden = true;
    document.body.classList.remove("modal-abierto");
}

document.getElementById("btnAdministrarConexiones")
    .addEventListener("click", event => {
        event.preventDefault();
        abrirModalConexiones();
    });

document.getElementById("cerrarAdministrarConexiones")
    .addEventListener("click", cerrarModalConexiones);

document.getElementById("cancelarAdministrarConexiones")
    .addEventListener("click", cerrarModalConexiones);

modalConexiones.addEventListener("click", event => {
    if (event.target === modalConexiones) {
        cerrarModalConexiones();
    }
});

document.getElementById("btnNuevaConexion")
    .addEventListener("click", () => {
        // Reutiliza el modal de registro que ya creaste.
        document.getElementById("btnBasesDatos").click();
    });

buscarConexion.addEventListener("input", () => {
    renderizarConexiones(buscarConexion.value);
});

function mostrarMensaje(texto) {
    mensajeConexiones.textContent = texto;
    mensajeConexiones.hidden = false;
}

function ocultarMensaje() {
    mensajeConexiones.hidden = true;
    mensajeConexiones.textContent = "";
}


async function cargarConexiones() {
    listaConexiones.innerHTML = `
        <div class="conexiones-vacio">
            <p>Cargando conexiones...</p>
        </div>
    `;

    ocultarMensaje();

    try {
        const response = await fetch("http://127.0.0.1:8000/synergy/listarDataBase/", {
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        if (!response.ok) {
            throw new Error("No se pudieron consultar las conexiones.");
        }

        const data = await response.json();
        conexiones = data.conexiones || [];

        // Identificar la conexión activa según su estado.
        const activa = conexiones.find(c => c.estado === true);

        conexionActivaId = activa ? activa.id : null;

        actualizarConexionActiva();
        renderizarConexiones(buscarConexion.value);

    } catch (error) {
        listaConexiones.innerHTML = "";
        mostrarMensaje(error.message);
    }
}


function actualizarConexionActiva() {
    const activa = conexiones.find(c => c.estado === true);

    document.getElementById("nombreConexionActiva").textContent =
        activa ? activa.nombre : "Ninguna seleccionada";

    document.getElementById("detalleConexionActiva").textContent =
        activa
            ? `${activa.motor || "Motor no especificado"} · ${activa.host}:${activa.puerto}`
            : "Selecciona una conexión para comenzar.";

    const estado = document.getElementById("estadoConexionActiva");

    estado.textContent = activa ? "Activa" : "Sin conexión";
    estado.classList.toggle("activa", Boolean(activa));

    conexionActivaId = activa ? activa.id : null;
}

function renderizarConexiones(filtro = "") {
    const termino = filtro.trim().toLowerCase();

    const filtradas = conexiones.filter(conexion =>
        `${conexion.nombre} ${conexion.motor} ${conexion.host}`
            .toLowerCase()
            .includes(termino)
    );

    document.getElementById("contadorConexiones").textContent =
        `${conexiones.length} conexión${conexiones.length !== 1 ? "es" : ""}`;

    if (!filtradas.length) {
        listaConexiones.innerHTML = `
            <div class="conexiones-vacio">
                <span class="material-symbols-outlined">database_off</span>
                <p>No se encontraron conexiones.</p>
            </div>
        `;
        return;
    }

    listaConexiones.innerHTML = filtradas.map(conexion => {
        const activa = conexion.estado === true;

        return `
            <article class="conexion-item ${activa ? "seleccionada" : ""}">
                <div class="conexion-icono">
                    <span class="material-symbols-outlined">database</span>
                </div>

                <div class="conexion-detalles">
                    <h3>${escaparHTML(conexion.nombre)}</h3>
                    <p>${escaparHTML(conexion.host)}:${escaparHTML(conexion.puerto)}</p>

                    <div class="conexion-badges">
                        <span class="conexion-badge">
                            ${escaparHTML(conexion.motor)}
                        </span>
                        ${activa
                ? '<span class="conexion-badge activa">En uso</span>'
                : ''}
                    </div>
                    ${conexion.estado
                ? '<span class="conexion-badge activa">Activa</span>'
                : '<span class="conexion-badge">Inactiva</span>'}
                </div>

                
                <button type="button"
                    class="btn-usar-conexion"
                    data-conexion-id="${escaparHTML(conexion.id)}"
                    data-accion="${conexion.estado ? "desactivar" : "activar"}">

                    <span class="material-symbols-outlined">
                        ${conexion.estado ? "power_settings_new" : "play_arrow"}
                    </span>

                    ${conexion.estado ? "Desactivar" : "Seleccionar"}
                </button>
            </article>
        `;
    }).join("");
}

function escaparHTML(valor) {
    return String(valor ?? "").replace(/[&<>"']/g, caracter => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[caracter]);
}


listaConexiones.addEventListener("click", async event => {
    const boton = event.target.closest("[data-conexion-id]");

    if (!boton || boton.disabled) return;

    const id = boton.dataset.conexionId;
    const accion = boton.dataset.accion;

    const url = accion === "desactivar"
        ? `synergy/controller_cnx/?id=${encodeURIComponent(id)}&accion=${encodeURIComponent("desactivar")}`
        : `synergy/controller_cnx/?id=${encodeURIComponent(id)}&accion=${encodeURIComponent("activar")}`;

    boton.disabled = true;
    boton.style.cursor = "default";
    console.log(url)
    try {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": obtenerCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
            }

        });

        const data = await response.json();

        if (!response.ok || !data.ok) {
            throw new Error(
                data.mensaje || "No se pudo actualizar la conexión."
            );
        }

        if (data.ok) {
            actualizarTablasDisponibles(data.schema);
            console.log("Tablas disponibles:", tablasDisponibles);
        }

        // Volver a consultar el estado real guardado en Django.
        await cargarConexiones();

        mostrarMensaje(
            accion === "desactivar"
                ? "Conexión desactivada correctamente."
                : "Conexión seleccionada correctamente."
        );

    } catch (error) {
        mostrarMensaje(error.message);
    } finally {
        // Si el botón todavía existe en el DOM, liberarlo.
        if (boton.isConnected) {
            boton.disabled = false;
        }
    }
});

function obtenerCSRFToken() {
    const cookie = document.cookie
        .split("; ")
        .find(fila => fila.startsWith("csrftoken="));

    return cookie ? decodeURIComponent(cookie.split("=")[1]) : "";
}



/* ==========================================
   MODAL: DASHBOARD ANALIZADO POR IA
=========================================== */

const modalDashboardIA = document.getElementById("modalDashboardIA");
const btnDashboards = document.getElementById("btnDashboards");

const dashboardNombreConexion = document.getElementById(
    "dashboardNombreConexion"
);
const dashboardDetalleConexion = document.getElementById(
    "dashboardDetalleConexion"
);
const dashboardEstadoConexion = document.getElementById(
    "dashboardEstadoConexion"
);

const dashboardBuscarTabla = document.getElementById(
    "dashboardBuscarTabla"
);
const dashboardListaTablas = document.getElementById(
    "dashboardListaTablas"
);
const dashboardContadorSeleccion = document.getElementById(
    "dashboardContadorSeleccion"
);
const dashboardSeleccionarTodas = document.getElementById(
    "dashboardSeleccionarTodas"
);
const dashboardMensaje = document.getElementById(
    "dashboardMensaje"
);
const dashboardAyudaFooter = document.getElementById(
    "dashboardAyudaFooter"
);
const btnGenerarDashboardIA = document.getElementById(
    "btnGenerarDashboardIA"
);

const dashboardTablasSeleccionadas = new Set();

let dashboardConexionActiva = null;


/* Abrir y cerrar */

function abrirModalDashboardIA() {
    modalDashboardIA.hidden = false;
    document.body.classList.add("dashboard-modal-open");

    dashboardBuscarTabla.value = "";
    dashboardMensaje.hidden = true;

    actualizarConexionDashboard();
    renderizarTablasDashboard();

    // Refrescar el estado de las conexiones desde Django.
    cargarConexiones().then(() => {
        actualizarConexionDashboard();
        renderizarTablasDashboard();
    });

    document.getElementById("cerrarDashboardIA").focus();
}

function cerrarModalDashboardIA() {
    modalDashboardIA.hidden = true;
    document.body.classList.remove("dashboard-modal-open");
}

btnDashboards.addEventListener("click", event => {
    event.preventDefault();
    abrirModalDashboardIA();
});

document.getElementById("cerrarDashboardIA")
    .addEventListener("click", cerrarModalDashboardIA);

document.getElementById("cancelarDashboardIA")
    .addEventListener("click", cerrarModalDashboardIA);

modalDashboardIA.addEventListener("click", event => {
    if (event.target === modalDashboardIA) {
        cerrarModalDashboardIA();
    }
});

document.addEventListener("keydown", event => {
    if (event.key === "Escape" && !modalDashboardIA.hidden) {
        cerrarModalDashboardIA();
    }
});


/* Conexión activa */

function actualizarConexionDashboard() {
    dashboardConexionActiva =
        conexiones.find(conexion => conexion.estado === true) || null;

    if (!dashboardConexionActiva) {
        dashboardNombreConexion.textContent = "Sin conexión activa";
        dashboardDetalleConexion.textContent =
            "Selecciona una conexión para analizar sus tablas.";

        dashboardEstadoConexion.textContent = "Desconectada";
        dashboardEstadoConexion.classList.remove("active");
        return;
    }

    dashboardNombreConexion.textContent =
        dashboardConexionActiva.nombre || "Base de datos";

    dashboardDetalleConexion.textContent =
        `${dashboardConexionActiva.motor || "Motor no especificado"} · ` +
        `${dashboardConexionActiva.host || ""}:` +
        `${dashboardConexionActiva.puerto || ""}`;

    dashboardEstadoConexion.textContent = "Activa";
    dashboardEstadoConexion.classList.add("active");
}


/* Mensajes del modal */

function mostrarMensajeDashboard(texto, tipo = "") {
    dashboardMensaje.textContent = texto;
    dashboardMensaje.classList.toggle("error", tipo === "error");
    dashboardMensaje.hidden = false;
}


/* Renderizado de tablas */

function renderizarTablasDashboard() {
    dashboardListaTablas.replaceChildren();

    const tablas = Array.isArray(tablasDisponibles)
        ? [...new Set(
            tablasDisponibles.filter(
                tabla => typeof tabla === "string" && tabla.trim()
            )
        )].sort((a, b) => a.localeCompare(b))
        : [];

    // Eliminar selecciones de tablas que ya no están disponibles.
    const tablasDisponiblesSet = new Set(tablas);

    for (const tabla of dashboardTablasSeleccionadas) {
        if (!tablasDisponiblesSet.has(tabla)) {
            dashboardTablasSeleccionadas.delete(tabla);
        }
    }

    if (!dashboardConexionActiva) {
        mostrarEstadoVacioDashboard(
            "database_off",
            "No hay una conexión activa. Selecciona una conexión antes de continuar."
        );
        actualizarControlesDashboard([]);
        return;
    }

    if (tablas.length === 0) {
        mostrarEstadoVacioDashboard(
            "database",
            "El esquema no está cargado en esta sesión. " +
            "Necesitamos obtener las tablas de la conexión activa para continuar."
        );
        actualizarControlesDashboard([]);
        return;
    }

    const termino = dashboardBuscarTabla.value.trim().toLowerCase();

    const filtradas = tablas.filter(tabla =>
        tabla.toLowerCase().includes(termino)
    );

    if (filtradas.length === 0) {
        mostrarEstadoVacioDashboard(
            "search_off",
            "No se encontraron tablas con ese nombre."
        );
        actualizarControlesDashboard([]);
        return;
    }

    filtradas.forEach(nombreTabla => {
        const seleccionada =
            dashboardTablasSeleccionadas.has(nombreTabla);

        const item = document.createElement("label");
        item.className =
            `dashboard-table-item${seleccionada ? " selected" : ""}`;

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.className = "dashboard-table-checkbox";
        checkbox.value = nombreTabla;
        checkbox.checked = seleccionada;
        checkbox.setAttribute(
            "aria-label",
            `Seleccionar tabla ${nombreTabla}`
        );

        const icono = document.createElement("span");
        icono.className =
            "material-symbols-outlined dashboard-table-icon";
        icono.textContent = "table";

        const info = document.createElement("span");
        info.className = "dashboard-table-info";

        const nombre = document.createElement("strong");
        nombre.textContent = nombreTabla;

        const detalle = document.createElement("small");
        detalle.textContent = seleccionada
            ? "Incluida en el análisis"
            : "Tabla disponible para analizar";

        info.append(nombre, detalle);
        item.append(checkbox, icono, info);

        checkbox.addEventListener("change", () => {
            if (checkbox.checked) {
                dashboardTablasSeleccionadas.add(nombreTabla);
            } else {
                dashboardTablasSeleccionadas.delete(nombreTabla);
            }

            renderizarTablasDashboard();
        });

        dashboardListaTablas.appendChild(item);
    });

    actualizarControlesDashboard(filtradas);
}

function mostrarEstadoVacioDashboard(icono, mensaje) {
    const contenedor = document.createElement("div");
    contenedor.className = "dashboard-table-empty";

    const simbolo = document.createElement("span");
    simbolo.className = "material-symbols-outlined";
    simbolo.textContent = icono;

    const texto = document.createElement("p");
    texto.textContent = mensaje;

    contenedor.append(simbolo, texto);
    dashboardListaTablas.appendChild(contenedor);
}


/* Contador y controles */

function actualizarControlesDashboard(tablasVisibles) {
    const cantidad = dashboardTablasSeleccionadas.size;

    dashboardContadorSeleccion.textContent =
        `${cantidad} seleccionada${cantidad !== 1 ? "s" : ""}`;

    const todasSeleccionadas =
        tablasVisibles.length > 0 &&
        tablasVisibles.every(tabla =>
            dashboardTablasSeleccionadas.has(tabla)
        );

    dashboardSeleccionarTodas.disabled =
        tablasVisibles.length === 0;

    dashboardSeleccionarTodas.textContent =
        todasSeleccionadas
            ? "Quitar selección"
            : "Seleccionar todas";

    btnGenerarDashboardIA.disabled =
        !dashboardConexionActiva || cantidad === 0;

    dashboardAyudaFooter.textContent =
        cantidad === 0
            ? "Selecciona al menos una tabla para continuar."
            : `${cantidad} tabla${cantidad !== 1 ? "s" : ""} preparada${cantidad !== 1 ? "s" : ""} para el análisis.`;
}


/* Búsqueda */

dashboardBuscarTabla.addEventListener("input", () => {
    renderizarTablasDashboard();
});


/* Seleccionar o deseleccionar las tablas visibles */

dashboardSeleccionarTodas.addEventListener("click", () => {
    const termino = dashboardBuscarTabla.value.trim().toLowerCase();

    const visibles = [...new Set(
        tablasDisponibles.filter(
            tabla =>
                typeof tabla === "string" &&
                tabla.trim() &&
                tabla.toLowerCase().includes(termino)
        )
    )];

    const todasSeleccionadas =
        visibles.length > 0 &&
        visibles.every(tabla =>
            dashboardTablasSeleccionadas.has(tabla)
        );

    if (todasSeleccionadas) {
        visibles.forEach(tabla =>
            dashboardTablasSeleccionadas.delete(tabla)
        );
    } else {
        visibles.forEach(tabla =>
            dashboardTablasSeleccionadas.add(tabla)
        );
    }

    renderizarTablasDashboard();
});


/* Preparar selección para la integración con bi_agent */

btnGenerarDashboardIA.addEventListener("click", async () => {
    if (!dashboardConexionActiva) {
        mostrarMensajeDashboard(
            "No hay una conexión activa.",
            "error"
        );
        return;
    }

    if (dashboardTablasSeleccionadas.size === 0) {
        mostrarMensajeDashboard(
            "Selecciona al menos una tabla.",
            "error"
        );
        return;
    }

    const seleccion = {
        conexionId: dashboardConexionActiva.id,
        tablas: [...dashboardTablasSeleccionadas]
    };

    // Construir los parámetros de la solicitud.
    const params = new URLSearchParams({
        conexionId: seleccion.conexionId,
        tablas: seleccion.tablas.join(",")
    });

    const url = `/synergy/dashboardBuilder/?${params.toString()}`;

    try {
        mostrarMensajeDashboard(
            "Analizando la estructura de las tablas..."
        );

        // Evitar múltiples solicitudes simultáneas.
        btnGenerarDashboardIA.disabled = true;

        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            },
            credentials: "same-origin"
        });

        // Leer la respuesta del backend.
        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.error ||
                data.mensaje ||
                `Error HTTP ${response.status}`
            );
        }

        console.log("Estructura analizada:", data);
        if (data.dashboard_id) {
            window.location.href =
                `/synergy/dashboard/${data.dashboard_id}/`;
        }

        mostrarMensajeDashboard(
            "Análisis de la estructura completado correctamente."
        );

        // Punto de integración:
        // Aquí utilizaremos la estructura analizada para
        // construir el contexto que recibirá la IA.
        //console.log("Configuración del dashboard:", seleccion);


    } catch (error) {
        console.error(
            "Error al analizar la estructura de las tablas:",
            error
        );

        mostrarMensajeDashboard(
            error.message ||
            "No fue posible analizar la estructura de las tablas.",
            "error"
        );
    } finally {
        btnGenerarDashboardIA.disabled = false;
    }
});