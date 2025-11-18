import { app } from "../../scripts/app.js";

const NODE_CLASS = "BatchImagesNode";
const INPUT_PREFIX = "image";

function getIndex(name) {
    if (!name?.startsWith(INPUT_PREFIX)) return NaN;
    return parseInt(name.slice(INPUT_PREFIX.length));
}

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

function updateInputs(node) {
    if (!node.inputs) node.inputs = [];

    let imgInputs = getImageInputs(node);

    // Ensure image1 exists
    if (!imgInputs.some(e => e.idx === 1)) {
        node.addInput(`${INPUT_PREFIX}1`, "IMAGE");
        imgInputs = getImageInputs(node);
    }

    // Highest connected index
    let highest = 0;
    for (const { idx, input } of imgInputs) {
        if (input.link != null && idx > highest) highest = idx;
    }

    // Desired count = highest + 1 (or 1 if none connected)
    const desired = highest === 0 ? 1 : highest + 1;

    // Add missing inputs
    for (let i = 1; i <= desired; i++) {
        if (!getImageInputs(node).some(e => e.idx === i)) {
            node.addInput(`${INPUT_PREFIX}${i}`, "IMAGE");
        }
    }

    // Remove unused inputs > desired
    const final = getImageInputs(node)
        .filter(e => e.idx > desired && e.input.link == null)
        .sort((a, b) => b.slot - a.slot);

    for (const { slot } of final) {
        node.removeInput(slot);
    }

    node.setDirtyCanvas(true, true);
}

function schedule(node) {
    setTimeout(() => updateInputs(node), 0);
}

app.registerExtension({
    name: "yarvix.BatchImagesNode",

    // New node created
    async nodeCreated(node) {
        if (node.comfyClass !== NODE_CLASS) return;

        const orig = node.onConnectionsChange;
        node.onConnectionsChange = function (...args) {
            orig?.apply(this, args);
            if (args[0] === LiteGraph.INPUT) schedule(this);
        };

        schedule(node);
    },

    // Loaded from JSON
    async loadedGraphNode(node) {
        if (node.comfyClass !== NODE_CLASS) return;
        schedule(node);
    },
});
