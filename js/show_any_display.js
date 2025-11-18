import { app } from "../../scripts/app.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

const NODE_CLASS_NAME = "ShowAnyDataType";
const WIDGET_NAME = "output_display";

// Visual bottom margin between the widget and the node border
const BOTTOM_MARGIN = 18;

app.registerExtension({
    name: "custom.ShowAnyDataTypeExtension",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {

        if (nodeData.name !== NODE_CLASS_NAME) return;

        //
        // 1. Create widget when the node is created
        //
        const onNodeCreated = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            if (onNodeCreated) onNodeCreated.apply(this, arguments);

            // Create multiline STRING widget
            this.showValueWidget = ComfyWidgets["STRING"](
                this,
                WIDGET_NAME,
                ["STRING", { multiline: true, default: "", placeholder: "Waiting for data..." }],
                app
            ).widget;

            const el = this.showValueWidget.inputEl;
            el.readOnly = true;
            el.style.fontSize = "12px";
            el.style.resize = "none";     // prevents manual resizing
            el.style.overflow = "auto";   // automatic scroll

            // Adjust immediately
            this.onResize(this.size);
        };


        //
        // 2. Dynamically adjust widget size when the node is resized
        //
        const original_onResize = nodeType.prototype.onResize;
        nodeType.prototype.onResize = function (size) {

            if (original_onResize) original_onResize.apply(this, arguments);
            if (!this.showValueWidget) return;

            const el = this.showValueWidget.inputEl;

            // Current node size
            const nodeWidth = this.size[0];
            const nodeHeight = this.size[1];

            // Adjust WIDTH
            el.style.width = (nodeWidth - 20) + "px";

            // Vertical position where the widget starts
            const widgetTop =
                (this.showValueWidget.y ?? this.widgets_start_y ?? 40);

            // Available space below the widget, leaving bottom margin
            const availableHeight = nodeHeight - widgetTop - BOTTOM_MARGIN;

            // Prevent textarea from overflowing outside the node
            if (availableHeight > 0) {
                el.style.height = availableHeight + "px";
            } else {
                el.style.height = "0px"; // prevents overflow at minimum node size
            }

            this.setDirtyCanvas(true, true);
        };


        //
        // 3. Update widget content when the node receives data
        //
        const onExecuted = nodeType.prototype.onExecuted;
        nodeType.prototype.onExecuted = function (message) {
            if (onExecuted) onExecuted.apply(this, arguments);

            if (!this.showValueWidget) return;

            if (message?.text?.length > 0) {
                this.showValueWidget.value = message.text;
            } else {
                this.showValueWidget.value = "No data received.";
            }

            this.setDirtyCanvas(true, true);
        };
    }
});
