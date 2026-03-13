import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

const NODE_CLASS_NAME = "ShowAnyDataType";
const WIDGET_NAME = "output_display";
const PLACEHOLDER_TEXT = "Waiting for data...";

/**
 * Normaliza el widget de info:
 *  - encuentra todos los widgets "nuestros" (mismo nombre o mismo placeholder),
 *  - mantiene solo el primero y borra duplicados,
 *  - opcionalmente crea uno si no existe.
 */
function setupShowWidget(node, app, allowCreate) {
    if (!node.widgets) {
        node.widgets = [];
    }

    let firstIndex = -1;

    // Detectar nuestros widgets y eliminar duplicados
    for (let i = 0; i < node.widgets.length; i++) {
        const w = node.widgets[i];
        const isOurs =
            w.name === WIDGET_NAME ||
            (w.type === "string" &&
                w.options &&
                w.options.placeholder === PLACEHOLDER_TEXT);

        if (isOurs) {
            if (firstIndex === -1) {
                firstIndex = i; // este se queda
            } else {
                // borrar duplicados
                node.widgets.splice(i, 1);
                i--;
            }
        }
    }

    // Si encontramos uno existente, lo usamos
    if (firstIndex !== -1) {
        node.showValueWidget = node.widgets[firstIndex];
    } else if (allowCreate) {
        // Crear uno nuevo al final (debajo de los inputs)
        const created = ComfyWidgets["STRING"](
            node,
            WIDGET_NAME,
            [
                "STRING",
                {
                    multiline: true,
                    default: "",
                    placeholder: PLACEHOLDER_TEXT,
                },
            ],
            app
        ).widget;

        node.showValueWidget = created;
    }

    // Estilos si tenemos widget
    const el = node.showValueWidget?.inputEl;
    if (el) {
        el.readOnly = true;
        el.style.fontSize = "12px";
        el.style.resize = "none";
        el.style.overflow = "hidden";
    }
}

/**
 * Auto-ajusta la altura del textarea para mostrar todo el contenido
 * y recalcula el tamaño del nodo.
 */
function autoResizeWidget(node) {
    const widget = node.showValueWidget;
    if (!widget) return;

    const el = widget.inputEl;
    if (!el) return;

    // Reset height para obtener scrollHeight real
    el.style.height = "auto";
    el.style.height = el.scrollHeight + "px";

    // Ajustar el computedHeight del widget para que LiteGraph reserve espacio
    const lines = (widget.value || "").split("\n").length;
    widget.computedHeight = Math.max(lines * 18 + 16, 58);

    // Solo ajustar la altura del nodo, mantener el ancho actual
    const currentWidth = node.size[0];
    const neededHeight = node.computeSize()[1];
    node.setSize([currentWidth, neededHeight]);
    node.setDirtyCanvas(true, true);
}

app.registerExtension({
    name: "custom.ShowAnyDataTypeExtension",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== NODE_CLASS_NAME) return;

        //
        // 1. Nodo creado (nuevo o duplicado)
        //
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);

            // Crear/normalizar el widget de info
            setupShowWidget(this, app, true);
        };

        //
        // 2. Nodo configurado (cargado desde JSON / copy-paste)
        //
        const original_onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function (info) {
            if (original_onConfigure) original_onConfigure.apply(this, arguments);

            // Widgets vienen del JSON: normalizar, enlazar, crear si falta
            setupShowWidget(this, app, true);
        };

        //
        // 3. Ajustar ancho del widget cuando se redimensiona el nodo
        //
        const original_onResize = nodeType.prototype.onResize;
        nodeType.prototype.onResize = function (size) {
            if (original_onResize) original_onResize.apply(this, arguments);

            // No crear nuevos aquí; solo reutilizar/limpiar duplicados
            setupShowWidget(this, app, false);
            if (!this.showValueWidget) return;

            const el = this.showValueWidget.inputEl;
            if (!el) return;

            const nodeWidth = this.size[0];
            el.style.width = (nodeWidth - 20) + "px";

            this.setDirtyCanvas(true, true);
        };

        //
        // 4. Actualizar el contenido del widget cuando el nodo recibe datos
        //
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            if (onExecuted) onExecuted.apply(this, arguments);

            // Reutilizar widget existente y limpiar duplicados
            setupShowWidget(this, app, false);
            if (!this.showValueWidget) return;

            if (message?.text?.length > 0) {
                this.showValueWidget.value = message.text;
            } else {
                this.showValueWidget.value = "No data received.";
            }

            // Auto-ajustar altura del widget al contenido
            autoResizeWidget(this);
        };
    }
});
