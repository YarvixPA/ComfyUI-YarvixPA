import { app } from "../../scripts/app.js";

const NODE_CLASS = "MultiReferenceLatent";
const INPUT_PREFIX = "image";
const WIDGET_NAME = "references";

/**
 * Return the numeric index from an input name like "image3" → 3.
 */
function getIndex(name) {
    if (!name?.startsWith(INPUT_PREFIX)) return NaN;
    return parseInt(name.slice(INPUT_PREFIX.length));
}

/**
 * Collect all image inputs currently on the node.
 */
function getImageInputs(node) {
    const res = [];
    if (!node.inputs) return res;

    for (let slot = 0; slot < node.inputs.length; slot++) {
        const input = node.inputs[slot];
        if (!input?.name) continue;

        const idx = getIndex(input.name);
        if (!isNaN(idx)) res.push({ idx, slot, input });
    }
    return res;
}

/**
 * Synchronise the number of image inputs with the `references` widget value.
 */
function syncInputs(node) {
    const widget = node.widgets?.find((w) => w.name === WIDGET_NAME);
    if (!widget) return;

    const desired = widget.value;
    if (!node.inputs) node.inputs = [];

    // Add missing image inputs
    for (let i = 1; i <= desired; i++) {
        if (!getImageInputs(node).some((e) => e.idx === i)) {
            node.addInput(`${INPUT_PREFIX}${i}`, "IMAGE");
        }
    }

    // Remove surplus inputs (from highest slot downward to keep indices stable)
    const surplus = getImageInputs(node)
        .filter((e) => e.idx > desired)
        .sort((a, b) => b.slot - a.slot);

    for (const { slot } of surplus) {
        node.removeInput(slot);
    }

    node.setDirtyCanvas(true, true);
}

app.registerExtension({
    name: "yarvix.MultiReferenceLatent",

    async nodeCreated(node) {
        if (node.comfyClass !== NODE_CLASS) return;

        // Listen to the `references` widget for changes
        const widget = node.widgets?.find((w) => w.name === WIDGET_NAME);
        if (widget) {
            const origCallback = widget.callback;
            widget.callback = function (...args) {
                origCallback?.apply(this, args);
                syncInputs(node);
            };
        }

        // Initial sync
        setTimeout(() => syncInputs(node), 0);
    },

    async loadedGraphNode(node) {
        if (node.comfyClass !== NODE_CLASS) return;
        setTimeout(() => syncInputs(node), 0);
    },
});
