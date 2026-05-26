let moduloActual = Object.keys(modelos)[0];
let varianteActual = obtenerPrimeraVariante(moduloActual);
let tipoActual = obtenerPrimerTipo(moduloActual, varianteActual);

const menuModulos = document.getElementById("menu-modulos");
const panelLateral = document.getElementById("panel-lateral");
const botonMenuMovil = document.getElementById("boton-menu-movil");
const selectorVariante = document.getElementById("selector-variante");
const selectorTipo = document.getElementById("selector-tipo");
const formulario = document.getElementById("formulario-modelo");
const resultadoContenedor = document.getElementById("resultado-contenedor");
const tarjetaFormulario = document.querySelector(".formulario-tarjeta");
const botonResolver = document.getElementById("resolver-btn");
const botonRestaurar = document.getElementById("restaurar-btn");
const botonAyudaModelo = document.getElementById("ayuda-modelo-btn");
const descripcionVariante = document.getElementById("descripcion-variante");
const modalAyuda = document.getElementById("modal-ayuda");
const modalAyudaCuerpo = document.getElementById("modal-ayuda-cuerpo");

generarMenu();
renderizarModulo();
configurarAvisoLegal();
configurarModalAyuda();
configurarMenuMovil();

selectorVariante.addEventListener("change", () => {
    varianteActual = selectorVariante.value;
    tipoActual = obtenerPrimerTipo(moduloActual, varianteActual);
    renderizarSelectorTipo();
    renderizarFormulario();
    actualizarDescripcionVariante();
    limpiarResultados();
});

selectorTipo.addEventListener("change", () => {
    tipoActual = selectorTipo.value;
    renderizarFormulario();
    limpiarResultados();
});

botonResolver.addEventListener("click", resolverModelo);
botonRestaurar.addEventListener("click", () => {
    renderizarFormulario();
    limpiarResultados();
});
botonAyudaModelo.addEventListener("click", mostrarAyudaModeloActual);

formulario.addEventListener("click", (evento) => {
    const boton = evento.target.closest("[data-ayuda-campo]");
    if (!boton) return;
    const campoId = boton.dataset.ayudaCampo;
    const variante = modelos[moduloActual].variantes[varianteActual];
    const campo = variante.campos.find(item => item.id === campoId);
    if (!campo) return;
    mostrarAyudaCampo(campo, variante);
});

resultadoContenedor.addEventListener("click", (evento) => {
    const boton = evento.target.closest("[data-doc-page-target]");
    if (!boton) return;
    const objetivo = boton.dataset.docPageTarget;
    resultadoContenedor.querySelectorAll("[data-doc-page-target]").forEach(item => item.classList.toggle("active", item === boton));
    resultadoContenedor.querySelectorAll("[data-doc-page]").forEach(pagina => pagina.classList.toggle("activa", pagina.dataset.docPage === objetivo));
    renderizarMathJax();
});

function obtenerPrimeraVariante(moduloClave) {
    const modulo = modelos[moduloClave];
    if (modulo.esDocumentacion) return "";
    return Object.keys(modulo.variantes)[0];
}

function obtenerPrimerTipo(moduloClave, varianteClave) {
    const modulo = modelos[moduloClave];
    if (modulo.esDocumentacion) return "";
    return Object.keys(modulo.variantes[varianteClave].tipos)[0];
}

function generarMenu() {
    menuModulos.innerHTML = Object.entries(modelos).map(([clave, modelo]) => `
        <button class="modulo-btn ${clave === moduloActual ? "active" : ""}" data-modulo="${clave}">
            <strong>${escaparHtml(modelo.titulo)}</strong>
            <span>${escaparHtml(modelo.etiquetaMenu || "∂ · modelo")}</span>
        </button>
    `).join("");

    document.querySelectorAll(".modulo-btn").forEach(boton => {
        boton.addEventListener("click", () => {
            moduloActual = boton.dataset.modulo;
            varianteActual = obtenerPrimeraVariante(moduloActual);
            tipoActual = obtenerPrimerTipo(moduloActual, varianteActual);
            document.querySelectorAll(".modulo-btn").forEach(item => item.classList.remove("active"));
            boton.classList.add("active");
            cerrarMenuMovil();
            renderizarModulo();
        });
    });
}

function renderizarModulo() {
    const modulo = modelos[moduloActual];
    document.getElementById("titulo-modulo").textContent = modulo.titulo;
    document.getElementById("descripcion-modulo").textContent = modulo.resumen;
    renderizarListaDinamica(modulo);

    if (modulo.esDocumentacion) {
        tarjetaFormulario.hidden = true;
        mostrarDocumentacion(modulo);
        return;
    }

    tarjetaFormulario.hidden = false;
    renderizarSelectorVariante();
    renderizarSelectorTipo();
    renderizarFormulario();
    actualizarDescripcionVariante();
    limpiarResultados();
}

function renderizarListaDinamica(modulo) {
    const lista = document.getElementById("lista-variantes");
    if (!lista) return;
    const elementos = Array.isArray(modulo.listaDinamica) ? modulo.listaDinamica : [];
    lista.innerHTML = elementos.map(item => `<li>${escaparHtml(item)}</li>`).join("");
}

function renderizarSelectorVariante() {
    const variantes = modelos[moduloActual].variantes;
    selectorVariante.innerHTML = Object.entries(variantes).map(([clave, variante]) => `
        <option value="${clave}" ${clave === varianteActual ? "selected" : ""}>${escaparHtml(variante.nombre)} · ${escaparHtml(variante.ecuacion || "")}</option>
    `).join("");
}

function renderizarSelectorTipo() {
    const tipos = modelos[moduloActual].variantes[varianteActual].tipos;
    selectorTipo.innerHTML = Object.entries(tipos).map(([clave, nombre]) => `
        <option value="${clave}" ${clave === tipoActual ? "selected" : ""}>${escaparHtml(nombre)}</option>
    `).join("");
}

function renderizarFormulario() {
    const variante = modelos[moduloActual].variantes[varianteActual];
    const campos = variante.campos.filter(campo => campo.tipos.length === 0 || campo.tipos.includes(tipoActual));
    const esFormulaSimbolica = tipoActual === "formula_simbolica";

    formulario.innerHTML = campos.map(campo => {
        const esOpcional = campo.opcional || esFormulaSimbolica;
        const valor = esFormulaSimbolica && campo.valor === "" ? "" : campo.valor;
        return `
            <label class="campo">
                <div class="campo-encabezado">
                    <span>${escaparHtml(campo.label)}${esOpcional ? " <em>(opcional)</em>" : ""}</span>
                    <button type="button" class="boton-ayuda boton-ayuda-campo" data-ayuda-campo="${escaparHtml(campo.id)}" aria-label="Ayuda sobre ${escaparHtml(campo.label)}">?</button>
                </div>
                <input id="${escaparHtml(campo.id)}" name="${escaparHtml(campo.id)}" value="${escaparHtml(valor)}">
            </label>
        `;
    }).join("");
}

function actualizarDescripcionVariante() {
    if (!descripcionVariante) return;
    descripcionVariante.textContent = "Ingresa los parámetros necesarios para resolver o construir simbólicamente el modelo. Las explicaciones completas de cada dato y de la fórmula están disponibles en los botones de ayuda.";
}

function construirDatos() {
    const datos = {
        variante: varianteActual,
        tipo_calculo: tipoActual
    };

    [...formulario.elements].forEach(elemento => {
        if (!elemento.name) return;
        datos[elemento.name] = elemento.value.trim();
    });

    return datos;
}

function validarDatos(datos) {
    // La validación fuerte vive en el backend.
    // El frontend permite datos incompletos para activar el modo simbólico con SymPy.
    return datos;
}

async function resolverModelo() {
    try {
        const datos = construirDatos();
        validarDatos(datos);
        limpiarResultados(tipoActual === "formula_simbolica" ? "Generando planteamiento simbólico con SymPy..." : "Construyendo expresión SymPy y evaluando modelo...");

        const respuesta = await fetch(modelos[moduloActual].ruta, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datos)
        });

        const resultado = await respuesta.json();
        if (!respuesta.ok || resultado.error) {
            mostrarError(resultado.mensaje || "No fue posible resolver el modelo.");
            return;
        }

        mostrarResultado(resultado);
    } catch (error) {
        mostrarError(error.message || "Error conectando con el servidor de cálculo.");
    }
}

function limpiarResultados(texto = "Completa los datos del modelo y presiona resolver.") {
    resultadoContenedor.innerHTML = `
        <div class="placeholder">
            <h2>Esperando cálculo...</h2>
            <p>${escaparHtml(texto)}</p>
        </div>
    `;
}

function mostrarError(mensaje) {
    resultadoContenedor.innerHTML = `
        <div class="resultado-error">
            <h3>Revisa los datos ingresados</h3>
            <p>${escaparHtml(mensaje)}</p>
        </div>
    `;
}

function mostrarResultado(resultado) {
    const pasos = Array.isArray(resultado.pasos) ? resultado.pasos : [];
    const pasosHtml = pasos.map((paso, indice) => `
        <article class="paso">
            <h3>${indice + 1}. ${escaparHtml(paso.titulo)}</h3>
            <p>${escaparHtml(paso.descripcion)}</p>
            <div class="formula">\\[${paso.latex}\\]</div>
        </article>
    `).join("");

    const advertencias = Array.isArray(resultado.advertencias) ? resultado.advertencias : [];
    const advertenciasHtml = advertencias.map(advertencia => `
        <div class="advertencia">${escaparHtml(advertencia)}</div>
    `).join("");

    const resultadoLatex = resultado.resultado_latex
        ? `<div class="formula resultado-latex">\\[${resultado.resultado_latex}\\]</div>`
        : "";

    const esFormulaSimbolica = resultado.tipo === "formula_simbolica" || resultado.unidad === "fórmula simbólica";
    const resultadoPrincipal = esFormulaSimbolica
        ? `<div class="resultado-formula-nota">Fórmula renderizada en LaTeX:</div>`
        : `<h1>${escaparHtml(resultado.resultado)} <span class="unidad">${escaparHtml(resultado.unidad || "")}</span></h1>`;

    resultadoContenedor.innerHTML = `
        ${advertenciasHtml}
        ${pasosHtml}
        <section class="resultado-final">
            <p>${escaparHtml(resultado.modelo || "Modelo evaluado")}</p>
            <h2>Resultado final</h2>
            ${resultadoPrincipal}
            ${resultadoLatex}
            ${crearHtmlConstantes(resultado.constantes)}
            ${crearHtmlMetadatos(resultado.metadatos)}
        </section>
    `;

    renderizarMathJax();
}

function mostrarDocumentacion(modulo) {
    if (modulo.documentoHtml) {
        resultadoContenedor.innerHTML = `<section class="documentacion">${modulo.documentoHtml}</section>`;
        renderizarMathJax();
        return;
    }

    const secciones = Array.isArray(modulo.secciones) ? modulo.secciones : [];
    const htmlSecciones = secciones.map((seccion, indice) => `
        <article class="doc-bloque">
            <span class="doc-numero">${String(indice + 1).padStart(2, "0")}</span>
            <div>
                <h3>${escaparHtml(seccion.titulo)}</h3>
                <p>${escaparHtml(seccion.texto)}</p>
            </div>
        </article>
    `).join("");

    resultadoContenedor.innerHTML = `
        <section class="documentacion">
            <div class="doc-hero">
                <p class="eyebrow">Documentación técnica</p>
                <h2>${escaparHtml(modulo.titulo)}</h2>
                <p>${escaparHtml(modulo.resumen)}</p>
            </div>
            ${htmlSecciones}
        </section>
    `;
}

function mostrarAyudaModeloActual() {
    const variante = modelos[moduloActual]?.variantes?.[varianteActual];
    if (!variante?.ayuda) return;
    const ayuda = variante.ayuda;
    const secuencia = ayuda.pasosLatex.map((paso, indice) => `\\text{${indice + 1}.}\\quad ${paso}`).join("\\\\[8px]");
    modalAyudaCuerpo.innerHTML = `
        <article class="modal-narrativa">
            <header class="modal-portada">
                <p class="eyebrow">Explicación matemática continua</p>
                <h2 id="modal-ayuda-titulo">${escaparHtml(ayuda.titulo)}</h2>
            </header>
            <p>${escaparHtml(ayuda.contexto)} En términos de modelado, esta variante se interpreta como una relación entre una variable dependiente y una variable independiente, normalmente el tiempo, aunque en algunos casos puede representar distancia. La idea central no es memorizar una fórmula aislada, sino reconocer qué hipótesis del fenómeno produce la ecuación diferencial y por qué esa ecuación conduce a una función exponencial, lineal o de equilibrio.</p>
            <p>La fórmula general usada por el sistema es la siguiente. Esta expresión aparece después de plantear la ecuación diferencial, separar variables o aplicar factor integrante, integrar ambos lados y usar la condición inicial para determinar la constante de integración.</p>
            <div class="formula formula-destacada">\\[${ayuda.formulaGeneral}\\]</div>
            <p>El proceso matemático previo se desarrolla de manera consecutiva. Primero se escribe la ecuación diferencial que representa la ley del fenómeno; después se transforma para poder integrar; luego aparece una constante de integración, usualmente representada como \\(C\\); finalmente, esa constante se reemplaza usando el dato inicial. Cuando el ejercicio entrega una medición posterior, el sistema despeja la constante del modelo, por ejemplo \\(k\\), y cuando no la entrega, SymPy conserva el parámetro simbólico en lugar de inventarlo.</p>
            <div class="formula formula-secuencia">\\[\\begin{gathered}${secuencia}\\end{gathered}\\]</div>
            <p>La comprobación consiste en derivar la fórmula obtenida y reemplazarla de nuevo en la ecuación diferencial original. Si la derivada reproduce exactamente la relación planteada al inicio, entonces la solución general es coherente. Para esta variante, la comprobación se resume así: ${escaparHtml(ayuda.comprobacion)}</p>
            <div class="formula">\\[${ayuda.comprobacionLatex}\\]</div>
            <h3>Ejemplo por defecto del sistema</h3>
            <p>${escaparHtml(ayuda.ejemplo)} Este caso permite observar cómo los datos concretos se sustituyen en la fórmula general, cómo se determina la constante del modelo cuando existe una medición adicional y cómo se obtiene el valor solicitado sin perder la relación con la ecuación diferencial original.</p>
        </article>
    `;
    abrirModalAyuda();
}

function obtenerDescripcionDatoEsperado(campo) {
    const clave = `${moduloActual}.${varianteActual}.${campo.id}`;
    const explicaciones = {
        "crecimiento.crecimiento_proporcional.cantidad_inicial": "Este valor es la cantidad que existe justo al comenzar el proceso, es decir, cuando el tiempo es igual a cero. En una población se interpreta como P(0): número inicial de habitantes, bacterias, usuarios o unidades antes de que pase el tiempo.",
        "crecimiento.crecimiento_proporcional.tiempo_transcurrido": "Este dato es el tiempo en el que ya se conoce una segunda medición. Por ejemplo, si se sabe que después de 4 años hay una población determinada, aquí se escribe 4. Sirve para relacionar el valor inicial con el valor conocido posterior.",
        "crecimiento.crecimiento_proporcional.cantidad_transcurrida": "Este valor es la cantidad observada después del tiempo conocido. Si inicialmente había 500 y después de 4 años hay 900, aquí se escribe 900 porque representa P(4).",
        "crecimiento.crecimiento_proporcional.constante_k": "Este dato representa la constante de crecimiento proporcional. Indica qué tan rápido aumenta la cantidad por unidad de tiempo. Si el problema ya entrega k, escríbela aquí; si no la entrega, deja el campo vacío y usa los datos de medición conocidos.",
        "crecimiento.crecimiento_proporcional.tiempo_objetivo": "Este es el tiempo en el que deseas conocer la cantidad final. Si quieres saber cuánta población habrá después de 8 años, aquí se escribe 8.",
        "crecimiento.crecimiento_proporcional.cantidad_objetivo": "Este dato es la cantidad que se desea alcanzar. Se usa cuando la pregunta no pide cuánto habrá en cierto tiempo, sino cuánto tiempo debe pasar para llegar a una cantidad específica.",
        "crecimiento.interes_continuo.capital_inicial": "Este valor es el dinero o capital invertido al inicio, cuando el tiempo es cero. En la fórmula se interpreta como S(0): monto inicial antes de acumular intereses.",
        "crecimiento.interes_continuo.tasa_porcentual": "Este dato es la tasa de interés expresada en porcentaje. Si la tasa anual es del 6%, escribe 6; no escribas 0.06 en este campo porque aquí se espera el porcentaje completo.",
        "crecimiento.interes_continuo.constante_k": "Este campo permite escribir directamente la tasa decimal del modelo. Por ejemplo, una tasa del 6% anual equivale a 0.06. Úsalo solo cuando el ejercicio entregue la tasa en forma decimal.",
        "crecimiento.interes_continuo.tiempo_objetivo": "Este valor es el tiempo durante el cual el capital permanece invertido. Si se quiere calcular el monto en 5 años, aquí se escribe 5.",
        "crecimiento.interes_continuo.monto_objetivo": "Este dato es el monto que se desea alcanzar. Se usa para calcular cuánto tiempo debe permanecer invertido el capital hasta llegar a ese valor.",
        "crecimiento.entrada_constante.cantidad_inicial": "Este valor es la población o cantidad inicial cuando t=0. Representa P(0), es decir, lo que ya existe antes de sumar la entrada externa constante.",
        "crecimiento.entrada_constante.constante_k": "Este dato mide el crecimiento proporcional propio de la población o cantidad. Si no aparece en el enunciado, puede dejarse vacío; lo importante es no inventar una constante que el problema no entrega.",
        "crecimiento.entrada_constante.entrada_constante": "Este valor representa la cantidad que entra de forma fija en cada unidad de tiempo. Por ejemplo, si llegan 50 individuos por año, aquí se escribe 50.",
        "crecimiento.entrada_constante.tiempo_objetivo": "Este campo indica el instante en el que quieres evaluar la población o cantidad total después de combinar crecimiento propio y entrada externa.",
        "crecimiento.caida_resistencia.velocidad_inicial": "Este valor es la velocidad del objeto al comenzar la caída, es decir, v(0). Si el objeto parte desde el reposo, se escribe 0.",
        "crecimiento.caida_resistencia.gravedad": "Este dato representa la aceleración causada por la gravedad. En el sistema internacional suele usarse 9.8 m/s², aunque puede cambiar si el ejercicio usa otras unidades.",
        "crecimiento.caida_resistencia.constante_k": "Este valor indica la intensidad de la resistencia del aire. Mientras mayor sea k, más rápido se frena el aumento de velocidad. Si el ejercicio no entrega k, déjalo vacío.",
        "crecimiento.caida_resistencia.tiempo_objetivo": "Este dato es el tiempo en el que deseas calcular la velocidad del objeto durante la caída.",
        "decaimiento.decaimiento_radiactivo.cantidad_inicial": "Este valor es la cantidad de sustancia radiactiva al inicio, cuando t=0. En la fórmula se interpreta como A(0), por ejemplo los gramos iniciales antes de que empiece la desintegración.",
        "decaimiento.decaimiento_radiactivo.tiempo_transcurrido": "Este dato es el tiempo después del cual se midió nuevamente la sustancia. Si se sabe que después de 5 horas queda cierta cantidad, aquí se escribe 5.",
        "decaimiento.decaimiento_radiactivo.cantidad_transcurrida": "Este valor es la cantidad que queda después del tiempo conocido. Por ejemplo, si de 100 g quedan 60 g después de 5 horas, aquí se escribe 60.",
        "decaimiento.decaimiento_radiactivo.constante_k": "Este dato es la constante de decaimiento. Indica qué tan rápido se desintegra la sustancia. Si el enunciado no la da directamente, déjala vacía y usa la medición posterior.",
        "decaimiento.decaimiento_radiactivo.tiempo_objetivo": "Este valor es el tiempo en el que deseas calcular cuánta sustancia queda.",
        "decaimiento.decaimiento_radiactivo.cantidad_objetivo": "Este dato es la cantidad final que quieres alcanzar. Se usa para calcular en qué momento quedará esa cantidad de sustancia.",
        "decaimiento.absorcion_medicamento.cantidad_inicial": "Este valor es la concentración o cantidad de medicamento al inicio, cuando t=0. Representa C(0), la dosis o concentración inicial antes de que el cuerpo la elimine.",
        "decaimiento.absorcion_medicamento.tiempo_transcurrido": "Este dato es el tiempo después del cual se conoce una nueva concentración del medicamento.",
        "decaimiento.absorcion_medicamento.cantidad_transcurrida": "Este valor es la concentración o cantidad restante del medicamento después del tiempo conocido.",
        "decaimiento.absorcion_medicamento.constante_k": "Este dato representa la rapidez de eliminación del medicamento. Si no aparece en el enunciado, déjalo vacío y usa la concentración conocida posterior.",
        "decaimiento.absorcion_medicamento.tiempo_objetivo": "Este valor indica el tiempo en el que quieres estimar cuánto medicamento queda.",
        "decaimiento.absorcion_medicamento.cantidad_objetivo": "Este dato es la cantidad o concentración final que se desea alcanzar, por ejemplo 20 mg.",
        "decaimiento.descarga_capacitor.cantidad_inicial": "Este valor es la carga eléctrica inicial almacenada en el capacitor cuando t=0. En la fórmula se representa como q(0).",
        "decaimiento.descarga_capacitor.constante_k": "Este dato es la constante de descarga si el problema ya la entrega directamente. En circuitos RC también puede obtenerse a partir de la resistencia y la capacitancia.",
        "decaimiento.descarga_capacitor.resistencia": "Este dato representa la resistencia eléctrica R del circuito. Se escribe en las unidades que use el ejercicio, normalmente ohmios.",
        "decaimiento.descarga_capacitor.capacitancia": "Este dato representa la capacitancia C del capacitor. Junto con la resistencia forma el producto RC, conocido como constante de tiempo del circuito.",
        "decaimiento.descarga_capacitor.tiempo_objetivo": "Este valor es el tiempo en el que deseas calcular la carga que queda en el capacitor.",
        "decaimiento.descarga_capacitor.cantidad_objetivo": "Este dato es la carga final que se desea alcanzar. Se usa para calcular cuánto tiempo tarda el capacitor en descargarse hasta ese valor.",
        "decaimiento.intensidad_luz.cantidad_inicial": "Este valor es la intensidad inicial del rayo antes de recorrer distancia dentro del medio. Si trabajas en porcentaje, puede usarse 100 para representar el 100% inicial.",
        "decaimiento.intensidad_luz.distancia_transcurrida": "Este dato es la distancia en la que ya se conoce una medición de intensidad. Por ejemplo, si a 5 metros se conoce la intensidad, aquí se escribe 5.",
        "decaimiento.intensidad_luz.cantidad_transcurrida": "Este valor es la intensidad observada en la distancia conocida. Si a 5 metros queda el 70% de intensidad, aquí se escribe 70.",
        "decaimiento.intensidad_luz.constante_k": "Este dato es la constante de atenuación de la luz. Indica qué tan rápido disminuye la intensidad por unidad de distancia. Si no se entrega, déjalo vacío.",
        "decaimiento.intensidad_luz.distancia_objetivo": "Este valor es la distancia en la que quieres estimar la intensidad del rayo.",
        "decaimiento.intensidad_luz.cantidad_objetivo": "Este dato es la intensidad que quieres alcanzar para calcular a qué distancia ocurre.",
        "enfriamiento.newton_constante.temperatura_inicial": "Este valor es la temperatura del objeto al inicio, cuando t=0. Representa T(0), antes de que el objeto se acerque a la temperatura ambiente.",
        "enfriamiento.newton_constante.temperatura_ambiente": "Este dato es la temperatura constante del ambiente que rodea al objeto. Es el valor hacia el cual tiende la temperatura con el paso del tiempo.",
        "enfriamiento.newton_constante.tiempo_transcurrido": "Este valor es el tiempo en el que ya se conoce una segunda temperatura del objeto.",
        "enfriamiento.newton_constante.temperatura_transcurrida": "Este dato es la temperatura medida después del tiempo conocido. Sirve para determinar qué tan rápido se enfría el objeto.",
        "enfriamiento.newton_constante.constante_k": "Este valor mide la rapidez del intercambio térmico. Si el enunciado no entrega k, déjalo vacío y usa la temperatura conocida posterior.",
        "enfriamiento.newton_constante.tiempo_objetivo": "Este dato es el tiempo en el que deseas calcular la temperatura del objeto.",
        "enfriamiento.newton_constante.temperatura_objetivo": "Este valor es la temperatura que deseas alcanzar para calcular cuánto tiempo tarda el objeto en llegar a ella.",
        "enfriamiento.calentamiento_newton.temperatura_inicial": "Este valor es la temperatura inicial del objeto cuando t=0. En calentamiento suele ser menor que la temperatura ambiente.",
        "enfriamiento.calentamiento_newton.temperatura_ambiente": "Este dato es la temperatura del entorno o fuente térmica hacia la cual se acerca el objeto.",
        "enfriamiento.calentamiento_newton.tiempo_transcurrido": "Este valor es el tiempo en el que se conoce una temperatura posterior durante el calentamiento.",
        "enfriamiento.calentamiento_newton.temperatura_transcurrida": "Este dato es la temperatura medida después del tiempo conocido.",
        "enfriamiento.calentamiento_newton.constante_k": "Este valor mide qué tan rápido el objeto se calienta hacia la temperatura ambiente. Si no aparece en el enunciado, déjalo vacío.",
        "enfriamiento.calentamiento_newton.tiempo_objetivo": "Este dato es el tiempo en el que quieres calcular la temperatura.",
        "enfriamiento.calentamiento_newton.temperatura_objetivo": "Este valor es la temperatura que deseas alcanzar para calcular el tiempo necesario.",
        "mezclas.volumen_constante.sal_inicial": "Este valor es la cantidad inicial de soluto dentro del tanque cuando t=0. Por ejemplo, kilogramos de sal disueltos antes de que empiece a entrar y salir líquido.",
        "mezclas.volumen_constante.volumen_inicial": "Este dato es el volumen total de líquido dentro del tanque. En esta variante permanece constante porque entra y sale líquido al mismo ritmo.",
        "mezclas.volumen_constante.concentracion_entrada": "Este valor indica cuánto soluto trae cada unidad de volumen que entra al tanque. Por ejemplo, 0.5 kg/L significa medio kilogramo por cada litro.",
        "mezclas.volumen_constante.concentracion_salida": "Este campo solo se usa si la salida tiene una concentración fija dada por el enunciado. Si la mezcla sale con la concentración interna del tanque, puede dejarse vacío.",
        "mezclas.volumen_constante.caudal_entrada": "Este dato es el volumen de líquido que entra al tanque por cada unidad de tiempo.",
        "mezclas.volumen_constante.caudal_salida": "Este dato es el volumen de líquido que sale del tanque por cada unidad de tiempo. Para volumen constante debe coincidir con el caudal de entrada.",
        "mezclas.volumen_constante.tiempo_objetivo": "Este valor es el tiempo en el que deseas calcular la cantidad de soluto o la concentración dentro del tanque.",
        "mezclas.volumen_variable.sal_inicial": "Este valor es la cantidad inicial de soluto dentro del tanque cuando t=0.",
        "mezclas.volumen_variable.volumen_inicial": "Este dato es el volumen inicial del tanque antes de que cambie por diferencia entre entrada y salida.",
        "mezclas.volumen_variable.concentracion_entrada": "Este valor indica la concentración del líquido que entra al tanque.",
        "mezclas.volumen_variable.concentracion_salida": "Este campo se usa solamente si el enunciado fija una concentración de salida diferente. Si la salida depende de la mezcla interna, puede dejarse vacío.",
        "mezclas.volumen_variable.caudal_entrada": "Este dato es el volumen de líquido que entra por unidad de tiempo.",
        "mezclas.volumen_variable.caudal_salida": "Este dato es el volumen de líquido que sale por unidad de tiempo. Si es distinto al de entrada, el volumen del tanque cambia.",
        "mezclas.volumen_variable.tiempo_objetivo": "Este valor es el tiempo en el que deseas calcular la cantidad de soluto o la concentración con volumen variable."
    };
    const comunes = {
        unidad: "Este campo no representa una cantidad matemática; solo indica cómo se nombrará la unidad del resultado, por ejemplo gramos, miligramos, litros, metros o pesos.",
        constante_k: "Este dato representa la constante de proporcionalidad del modelo. Úsala solo si el enunciado la entrega directamente; si no aparece, déjala vacía.",
        tiempo_objetivo: "Este dato indica el instante en el que deseas calcular el resultado del modelo.",
        cantidad_objetivo: "Este valor es la cantidad final que se quiere alcanzar para calcular el tiempo necesario.",
        tiempo_transcurrido: "Este dato es un tiempo donde ya se conoce una medición posterior.",
        cantidad_transcurrida: "Este valor es la medición conocida después de cierto tiempo."
    };
    return explicaciones[clave] || comunes[campo.id] || campo.ayuda || "Este dato corresponde a uno de los valores numéricos que pide el modelo seleccionado. Léelo desde el enunciado y escríbelo exactamente con las mismas unidades.";
}

function mostrarAyudaCampo(campo, variante) {
    const descripcionDato = obtenerDescripcionDatoEsperado(campo);
    const valorActual = campo.valor === "" || campo.valor === undefined || campo.valor === null ? "vacío" : campo.valor;
    const notaValor = valorActual === "vacío"
        ? "En este formulario aparece vacío porque no siempre se entrega en el enunciado. Si el problema no menciona este dato, es mejor dejarlo vacío que inventarlo."
        : `En este formulario aparece cargado el valor ${escaparHtml(valorActual)} como ejemplo editable. Cámbialo cuando tu ejercicio tenga otro dato.`;
    modalAyudaCuerpo.innerHTML = `
        <article class="modal-narrativa modal-dato">
            <header class="modal-portada mini">
                <p class="eyebrow">Guía del dato esperado</p>
                <h2 id="modal-ayuda-titulo">${escaparHtml(campo.label)}</h2>
            </header>
            <p>${escaparHtml(descripcionDato)}</p>
            <p>${notaValor}</p>
            <p>Escribe únicamente números en el campo. Cuando necesites decimales usa punto, por ejemplo <code>9.8</code>, <code>0.06</code> o <code>0.5</code>. Conserva las mismas unidades del problema para que el resultado tenga sentido.</p>
        </article>
    `;
    abrirModalAyuda();
}


function abrirModalAyuda() {
    modalAyuda.hidden = false;
    modalAyuda.setAttribute("aria-hidden", "false");
    document.body.classList.add("modal-abierto");
    renderizarMathJax();
}

function cerrarModalAyuda() {
    modalAyuda.hidden = true;
    modalAyuda.setAttribute("aria-hidden", "true");
    document.body.classList.remove("modal-abierto");
}

function configurarModalAyuda() {
    modalAyuda.addEventListener("click", (evento) => {
        if (evento.target.matches("[data-cerrar-modal]")) cerrarModalAyuda();
    });
    document.addEventListener("keydown", (evento) => {
        if (evento.key === "Escape") {
            cerrarModalAyuda();
            cerrarMenuMovil();
        }
    });
}

function configurarMenuMovil() {
    if (!botonMenuMovil || !panelLateral) return;
    botonMenuMovil.addEventListener("click", () => {
        const abierto = panelLateral.classList.toggle("abierto");
        botonMenuMovil.setAttribute("aria-expanded", String(abierto));
        document.body.classList.toggle("menu-movil-abierto", abierto);
    });
}

function cerrarMenuMovil() {
    if (!botonMenuMovil || !panelLateral) return;
    panelLateral.classList.remove("abierto");
    botonMenuMovil.setAttribute("aria-expanded", "false");
    document.body.classList.remove("menu-movil-abierto");
}

function crearHtmlConstantes(constantes) {
    if (!constantes || Object.keys(constantes).length === 0) return "";
    return `<div class="constantes-grid">${Object.entries(constantes).map(([clave, valor]) => `
        <span><strong>${escaparHtml(clave)}:</strong> ${escaparHtml(valor)}</span>
    `).join("")}</div>`;
}

function crearHtmlMetadatos(metadatos) {
    if (!metadatos || Object.keys(metadatos).length === 0) return "";
    return `<div class="constantes-grid">${Object.entries(metadatos).map(([clave, valor]) => `
        <span><strong>${escaparHtml(clave)}:</strong> ${escaparHtml(valor)}</span>
    `).join("")}</div>`;
}

function configurarAvisoLegal() {
    const aviso = document.getElementById("aviso-legal");
    const boton = document.getElementById("aceptar-aviso-legal");
    if (!aviso || !boton) return;
    if (localStorage.getItem("avisoLegalEdoAceptado") === "1") {
        aviso.hidden = true;
        return;
    }
    aviso.hidden = false;
    boton.addEventListener("click", () => {
        localStorage.setItem("avisoLegalEdoAceptado", "1");
        aviso.hidden = true;
    });
}

function resumenAyuda(texto) {
    const limpio = String(texto || "");
    return limpio.length > 112 ? `${limpio.slice(0, 109)}...` : limpio;
}

function renderizarMathJax() {
    if (window.MathJax) MathJax.typesetPromise();
}

function escaparHtml(valor) {
    return String(valor ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
