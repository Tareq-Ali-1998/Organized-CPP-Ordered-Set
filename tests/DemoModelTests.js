"use strict";

const assert = require("node:assert/strict");
const model = require("../assets/demo-model.js");
let checks = 0;

function Check(actual, expected) {
    assert.deepEqual(actual, expected);
    checks++;
}

function Validate(values, multi) {
    const tree = model.BuildTree(values, multi);
    const expected = [...values].sort((a, b) => a - b).filter((value, idx, sorted) => multi || idx === 0 || value !== sorted[idx - 1]);
    Check(tree.entries.map(entry => entry.value), expected);
    Check(model.Size(tree.root), expected.length);
    for (let rank = -1; rank <= expected.length; rank++) {
        const trace = model.SelectTrace(tree, rank);
        Check(trace.result, rank >= 0 && rank < expected.length ? expected[rank] : null);
        for (const step of trace.steps) {
            Check(model.NodeIds(tree.root).includes(step.nodeId), true);
        }
    }
    for (const value of [-2, -1, 0, 1, 2, ...values]) {
        for (const upper of [false, true]) {
            const trace = model.RankTrace(tree, value, upper);
            Check(trace.result, expected.filter(current => upper ? current <= value : current < value).length);
            const counted = new Set(trace.steps.flatMap(step => step.skipped));
            Check(counted.size, trace.result);
        }
    }
    Check(model.Diagram(tree).startsWith("flowchart TD"), true);
}

let combinations = 1;
for (let length = 0; length <= 7; length++) {
    for (let mask = 0; mask < combinations; mask++) {
        const values = [];
        let current = mask;
        for (let i = 0; i < length; i++) {
            values.push(current % 3 - 1);
            current = Math.floor(current / 3);
        }
        Validate(values, true);
        Validate(values, false);
    }
    combinations *= 3;
}
Validate([7, 2, 7, 5], true);
Validate([-1000000, 0, 1000000, -1000000], true);
Check(model.ParseValues(""), []);
Check(model.ParseValues("7, 2  7,5"), [7, 2, 7, 5]);
for (const text of ["NaN", "1.5", "1e3", "1000001", "<script>", Array(16).fill("1").join(",")]) {
    assert.throws(() => model.ParseValues(text));
    checks++;
}
console.log(`Passed ${checks} walkthrough-model checks.`);
