import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

const NODE_CLASS_NAME = "FrameCalculatorAudio";
const WIDGET_NAME = "frame_info_display";
const PLACEHOLDER_TEXT = "Waiting for frame calculation...";

/**
 * Normalizes the info widget:
 *  - finds all widgets that are "ours" (same name or same placeholder),
 *  - keeps only the first one, removes duplicates,
 *  - optionally creates one if none exists.
 */
function setupFrameInfoWidget(node, app, allowCreate) {
    if (!node.widgets) {
        node.widgets = [];
    }

    let firstIndex = -1;

    // Detect all our candidate widgets and remove duplicates
    for (let i = 0; i < node.widgets.length; i++) {
        const w = node.widgets[i];
        const isOurs =
            w.name === WIDGET_NAME ||
            (w.type === "string" &&
                w.options &&
                w.options.placeholder === PLACEHOLDER_TEXT);

        if (isOurs) {
            if (firstIndex === -1) {
                firstIndex = i; // keep this one
            } else {
                // Remove duplicates
                node.widgets.splice(i, 1);
                i--;
            }
        }
    }

    // If we found an existing widget, bind to it
    if (firstIndex !== -1) {
        node.frameInfoWidget = node.widgets[firstIndex];
    } else if (allowCreate) {
        // Create a new widget at the end (below fps)
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

    // Apply styles if we have a widget
    const el = node.frameInfoWidget?.inputEl;
    if (el) {
        el.readOnly = true;
        el.style.fontSize = "12px";
        el.style.resize = "none";   // prevent manual resize
        el.style.overflow = "auto"; // scroll if needed
        // Height is controlled by Comfy/LiteGraph; we only tweak width in onResize
    }
}

app.registerExtension({
    name: "custom.FrameCalculatorAudioDisplay",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== NODE_CLASS_NAME) return;

        //
        // 1. Node created (new or duplicated)
        //
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);

            // Allow creation (new node) and also normalize any leftover widgets
            setupFrameInfoWidget(this, app, true);
        };

        //
        // 2. Node configured (loaded from JSON / copy-paste)
        //
        const original_onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function (info) {
            if (original_onConfigure) original_onConfigure.apply(this, arguments);

            // Widgets come from JSON: normalize & bind, create if missing
            setupFrameInfoWidget(this, app, true);
        };

        //
        // 3. Adjust widget width when the node is resized
        //
        const original_onResize = nodeType.prototype.onResize;
        nodeType.prototype.onResize = function (size) {
            if (original_onResize) original_onResize.apply(this, arguments);

            // Do not create new widgets here; only reuse & clean duplicates
            setupFrameInfoWidget(this, app, false);
            if (!this.frameInfoWidget) return;

            const el = this.frameInfoWidget.inputEl;
            if (!el) return;

            const nodeWidth = this.size[0];
            el.style.width = (nodeWidth - 20) + "px";

            this.setDirtyCanvas(true, true);
        };

        //
        // 4. Update widget content when the node receives data
        //
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            if (onExecuted) onExecuted.apply(this, arguments);

            // Reuse existing widget and clean duplicates if any
            setupFrameInfoWidget(this, app, false);
            if (!this.frameInfoWidget) return;

            // From Python:
            // return { "ui": { "text": (display_text,) }, "result": (...) }
            // → message.text in the frontend
            if (message?.text && message.text.length > 0) {
                this.frameInfoWidget.value = message.text;
            } else {
                this.frameInfoWidget.value = "No data received.";
            }

            this.setDirtyCanvas(true, true);
        };
    }
});
