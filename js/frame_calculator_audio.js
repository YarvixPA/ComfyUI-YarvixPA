import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

const NODE_CLASS_NAME = "FrameCalculatorAudio";
const WIDGET_NAME = "frame_info_display";
const PLACEHOLDER_TEXT = "Waiting for frame calculation...";

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

    for (let i = 0; i < node.widgets.length; i++) {
        const w = node.widgets[i];
        const isOurs =
            w.name === WIDGET_NAME ||
            (w.type === "string" &&
                w.options &&
                w.options.placeholder === PLACEHOLDER_TEXT);

        if (isOurs) {
            if (firstIndex === -1) {
                firstIndex = i;
            } else {
                node.widgets.splice(i, 1);
                i--;
            }
        }
    }

    if (firstIndex !== -1) {
        node.frameInfoWidget = node.widgets[firstIndex];
    } else if (allowCreate) {
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

    const el = node.frameInfoWidget?.inputEl;
    if (el) {
        el.readOnly = true;
        el.style.fontSize = "12px";
        el.style.resize = "none";
        el.style.overflow = "hidden";
    }
}

/**
 * Auto-ajusta la altura del textarea para mostrar todo el contenido
 * y recalcula la altura del nodo.
 */
function autoResizeWidget(node) {
    const widget = node.frameInfoWidget;
    if (!widget) return;

    const el = widget.inputEl;
    if (!el) return;

    el.style.height = "auto";
    el.style.height = el.scrollHeight + "px";

    const lines = (widget.value || "").split("\n").length;
    widget.computedHeight = Math.max(lines * 18 + 16, 58);

    const currentWidth = node.size[0];
    const neededHeight = node.computeSize()[1];
    node.setSize([currentWidth, neededHeight]);
    node.setDirtyCanvas(true, true);
}

app.registerExtension({
    name: "custom.FrameCalculatorAudioDisplay",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== NODE_CLASS_NAME) return;

        //
        // 1. Nodo creado (nuevo o duplicado)
        //
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);
            setupFrameInfoWidget(this, app, true);
        };

        //
        // 2. Nodo configurado (cargado desde JSON / copy-paste)
        //
        const original_onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function (info) {
            if (original_onConfigure) original_onConfigure.apply(this, arguments);
            setupFrameInfoWidget(this, app, true);
        };

        //
        // 3. Ajustar ancho del widget cuando se redimensiona el nodo
        //
        const original_onResize = nodeType.prototype.onResize;
        nodeType.prototype.onResize = function (size) {
            if (original_onResize) original_onResize.apply(this, arguments);

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

            setupFrameInfoWidget(this, app, false);
            if (!this.frameInfoWidget) return;

            if (message?.text && message.text.length > 0) {
                this.frameInfoWidget.value = message.text;
            } else {
                this.frameInfoWidget.value = "No data received.";
            }

            autoResizeWidget(this);
        };
    }
});
