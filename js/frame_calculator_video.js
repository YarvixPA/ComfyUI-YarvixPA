import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

const NODE_CLASS_NAME = "FrameCalculatorVideo";
const WIDGET_NAME = "video_frame_info_display";
const PLACEHOLDER_TEXT = "Waiting for video frame calculation...";

/**
 * Normaliza el widget de info:
 *  - encuentra todos los widgets "nuestros" (mismo nombre o mismo placeholder),
 *  - mantiene solo el primero y borra duplicados,
 *  - opcionalmente crea uno si no existe.
 */
function setupFrameInfoWidget(node, app, allowCreate) {
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
        node.frameInfoWidget = node.widgets[firstIndex];
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

        node.frameInfoWidget = created;
    }

    // Estilos si tenemos widget
    const el = node.frameInfoWidget?.inputEl;
    if (el) {
        el.readOnly = true;
        el.style.fontSize = "12px";
        el.style.resize = "none";   // evitar redimensionar a mano
        el.style.overflow = "auto"; // scroll si hace falta
    }
}

app.registerExtension({
    name: "custom.FrameCalculatorVideoDisplay",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== NODE_CLASS_NAME) return;

        //
        // 1. Nodo creado (nuevo o duplicado)
        //
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);

            // Crear/normalizar el widget cuando el nodo se crea
            setupFrameInfoWidget(this, app, true);
        };

        //
        // 2. Nodo configurado (cargado desde JSON / copy-paste)
        //
        const original_onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function (info) {
            if (original_onConfigure) original_onConfigure.apply(this, arguments);

            // Widgets vienen del JSON: normalizar, enlazar, crear si falta
            setupFrameInfoWidget(this, app, true);
        };

        //
        // 3. Ajustar ancho del widget cuando se redimensiona el nodo
        //
        const original_onResize = nodeType.prototype.onResize;
        nodeType.prototype.onResize = function (size) {
            if (original_onResize) original_onResize.apply(this, arguments);

            // No crear nuevos aquí; solo reutilizar/limpiar duplicados
            setupFrameInfoWidget(this, app, false);
            if (!this.frameInfoWidget) return;

            const el = this.frameInfoWidget.inputEl;
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
            setupFrameInfoWidget(this, app, false);
            if (!this.frameInfoWidget) return;

            // Desde Python:
            // return { "ui": { "text": (display_text,) }, "result": (...) }
            // → message.text en el frontend
            if (message?.text && message.text.length > 0) {
                this.frameInfoWidget.value = message.text;
            } else {
                this.frameInfoWidget.value = "No data received.";
            }

            this.setDirtyCanvas(true, true);
        };
    }
});
