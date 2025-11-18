import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

const NODE_CLASS_NAME = "GetResolutionImage";
const WIDGET_NAME = "resolution_display";
const PLACEHOLDER_TEXT = "Waiting for image resolution...";

/**
 * Normalizes the info widget:
 *  - Finds widgets that belong to us (same name or same placeholder),
 *  - Keeps only the first one and removes duplicates,
 *  - Optionally creates one if none exists.
 */
function setupResolutionWidget(node, app, allowCreate) {
    if (!node.widgets) {
        node.widgets = [];
    }

    let firstIndex = -1;

    // Detect candidate widgets and remove duplicates
    for (let i = 0; i < node.widgets.length; i++) {
        const w = node.widgets[i];
        const isOurs =
            w.name === WIDGET_NAME ||
            (w.type === "string" &&
                w.options &&
                w.options.placeholder === PLACEHOLDER_TEXT);

        if (isOurs) {
            if (firstIndex === -1) {
                firstIndex = i; // Keep this one
            } else {
                // Remove duplicate
                node.widgets.splice(i, 1);
                i--;
            }
        }
    }

    // Use existing widget
    if (firstIndex !== -1) {
        node.resolutionWidget = node.widgets[firstIndex];
    } else if (allowCreate) {
        // Create new widget at end of node
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

        node.resolutionWidget = created;
    }

    // Apply styling if widget exists
    const el = node.resolutionWidget?.inputEl;
    if (el) {
        el.readOnly = true;
        el.style.fontSize = "12px";
        el.style.resize = "none";   
        el.style.overflow = "auto";
    }
}

app.registerExtension({
    name: "custom.GetResolutionImageDisplay",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name !== NODE_CLASS_NAME) return;

        //
        // 1. Node created (new or duplicated)
        //
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);
            setupResolutionWidget(this, app, true);
        };

        //
        // 2. Node configured (loaded from JSON / copy-paste)
        //
        const original_onConfigure = nodeType.prototype.onConfigure;
        nodeType.prototype.onConfigure = function (info) {
            if (original_onConfigure) original_onConfigure.apply(this, arguments);
            setupResolutionWidget(this, app, true);
        };

        //
        // 3. Resize handling
        //
        const original_onResize = nodeType.prototype.onResize;
        nodeType.prototype.onResize = function (size) {
            if (original_onResize) original_onResize.apply(this, arguments);

            setupResolutionWidget(this, app, false);
            if (!this.resolutionWidget) return;

            const el = this.resolutionWidget.inputEl;
            if (!el) return;

            const nodeWidth = this.size[0];
            el.style.width = (nodeWidth - 20) + "px";

            this.setDirtyCanvas(true, true);
        };

        //
        // 4. Update widget after execution
        //
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            if (onExecuted) onExecuted.apply(this, arguments);

            setupResolutionWidget(this, app, false);
            if (!this.resolutionWidget) return;

            // From Python:
            // return { "ui": { "text": (display_text,) } }
            if (message?.text && message.text.length > 0) {
                this.resolutionWidget.value = message.text;
            } else {
                this.resolutionWidget.value = "No resolution data.";
            }

            this.setDirtyCanvas(true, true);
        };
    }
});
