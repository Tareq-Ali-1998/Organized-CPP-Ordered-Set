(function(root) {
    "use strict";

    function ParseValues(text) {
        if (!text.trim()) {
            return [];
        }
        const tokens = text.trim().split(/[\s,]+/);
        if (tokens.length > 15) {
            throw new Error("Use at most 15 values so the tree stays readable.");
        }
        return tokens.map(token => {
            if (!/^-?\d+$/.test(token)) {
                throw new Error("Use whole numbers separated by spaces or commas.");
            }
            const value = Number(token);
            if (!Number.isSafeInteger(value) || Math.abs(value) > 1000000) {
                throw new Error("Choose integers between -1000000 and 1000000.");
            }
            return value;
        });
    }

    function BuildTree(values, multi = true) {
        let entries = values.map((value, insertionId) => ({value, insertionId}));
        entries.sort((a, b) => a.value - b.value || a.insertionId - b.insertionId);
        if (!multi) {
            entries = entries.filter((entry, idx) => idx === 0 || entry.value !== entries[idx - 1].value);
        }
        function Build(left, right) {
            if (left >= right) {
                return null;
            }
            const mid = Math.floor((left + right) / 2);
            const node = {...entries[mid], id: "n" + mid, index: mid};
            node.left = Build(left, mid);
            node.right = Build(mid + 1, right);
            node.size = 1 + Size(node.left) + Size(node.right);
            return node;
        }
        return {root: Build(0, entries.length), entries, multi};
    }

    function Size(node) {
        return node ? node.size : 0;
    }

    function NodeIds(node) {
        return node ? [node.id, ...NodeIds(node.left), ...NodeIds(node.right)] : [];
    }

    function SelectTrace(tree, rank) {
        if (!Number.isInteger(rank) || rank < 0 || rank >= tree.entries.length) {
            return {steps: [], result: null, message: "No such rank: find_by_order returns end()."};
        }
        const steps = [];
        let node = tree.root;
        let remaining = rank;
        while (node) {
            const leftSize = Size(node.left);
            if (remaining < leftSize) {
                steps.push({nodeId: node.id, action: "left", skipped: [],
                    text: `At ${node.value}: rank ${remaining} is below left size ${leftSize}. Go left.`});
                node = node.left;
            }
            else if (remaining === leftSize) {
                steps.push({nodeId: node.id, action: "found", skipped: [],
                    text: `At ${node.value}: rank ${remaining} equals left size ${leftSize}. Found ${node.value}.`});
                return {steps, result: node.value, message: `Rank ${rank} contains ${node.value}.`};
            }
            else {
                const next = remaining - leftSize - 1;
                steps.push({nodeId: node.id, action: "right", skipped: [node.id, ...NodeIds(node.left)],
                    text: `At ${node.value}: skip ${leftSize} left entries and this node. Rank ${remaining} becomes ${next}; go right.`});
                remaining = next;
                node = node.right;
            }
        }
        throw new Error("Selection invariant failed.");
    }

    function RankTrace(tree, value, upper = false) {
        const steps = [];
        let node = tree.root;
        let result = 0;
        while (node) {
            const before = upper ? node.value <= value : node.value < value;
            if (before) {
                const added = Size(node.left) + 1;
                result += added;
                steps.push({nodeId: node.id, action: "right", skipped: [node.id, ...NodeIds(node.left)],
                    text: `At ${node.value}: count ${added} entries (left subtree + node). Total ${result}; go right.`});
                node = node.right;
            }
            else {
                steps.push({nodeId: node.id, action: "left", skipped: [],
                    text: `At ${node.value}: this node does not qualify. Total ${result}; go left.`});
                node = node.left;
            }
        }
        const relation = upper ? "before or equal to" : "strictly before";
        return {steps, result, message: `${result} entries are ${relation} ${value}.`};
    }

    function Diagram(tree, steps = []) {
        if (!tree.root) {
            return 'flowchart TD\n    Empty["Empty container | size = 0"]';
        }
        const lines = ["flowchart TD"];
        const skipped = new Set(steps.flatMap(step => step.skipped));
        const visited = new Set(steps.map(step => step.nodeId));
        const current = steps.length ? steps[steps.length - 1].nodeId : null;
        function Walk(node) {
            if (!node) {
                return;
            }
            const id = tree.multi ? ` | ID ${node.insertionId}` : "";
            lines.push(`    ${node.id}["${node.value}${id} | size ${node.size}"]`);
            for (const child of [node.left, node.right]) {
                if (child) {
                    lines.push(`    ${node.id} --> ${child.id}`);
                }
            }
            const color = node.id === current ? "current" : skipped.has(node.id) ? "counted" : visited.has(node.id) ? "visited" : "quiet";
            lines.push(`    class ${node.id} ${color};`);
            Walk(node.left);
            Walk(node.right);
        }
        Walk(tree.root);
        lines.push("    classDef current fill:#dbeafe,stroke:#1d4ed8,stroke-width:3px,color:#172554;");
        lines.push("    classDef counted fill:#dcfce7,stroke:#15803d,color:#14532d;");
        lines.push("    classDef visited fill:#fff1d6,stroke:#b45309,color:#78350f;");
        lines.push("    classDef quiet fill:#f1f5f9,stroke:#94a3b8,color:#334155;");
        return lines.join("\n");
    }

    const api = {ParseValues, BuildTree, Size, NodeIds, SelectTrace, RankTrace, Diagram};
    if (typeof module !== "undefined" && module.exports) {
        module.exports = api;
    }
    root.OrderedSetDemo = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
