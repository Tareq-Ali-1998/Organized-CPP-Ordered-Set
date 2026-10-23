(function() {
    "use strict";
    const panel = document.getElementById("ordered-set-lab");
    if (!panel) {
        return;
    }
    const model = window.OrderedSetDemo;
    const status = document.getElementById("lab-status");
    const graph = document.getElementById("lab-tree");
    const traceList = document.getElementById("lab-trace");
    const nextButton = document.getElementById("lab-next");
    let tree;
    let trace;
    let progress = 0;
    let rendering = Promise.resolve();
    let revision = 0;

    function Render() {
        const code = model.Diagram(tree, trace ? trace.steps.slice(0, progress) : []);
        const request = ++revision;
        rendering = rendering.catch(() => {}).then(async () => {
            const output = await mermaid.render("lab-diagram-" + request, code);
            if (request === revision) {
                graph.innerHTML = output.svg;
                const svg = graph.querySelector('svg');
                if (svg && svg.viewBox.baseVal.width) {
                    svg.style.width = Math.max(380, svg.viewBox.baseVal.width) + 'px';
                }
                graph.setAttribute("data-rendered", "true");
                graph.setAttribute("data-render-revision", String(request));
            }
        }).catch(error => {
            status.textContent = "The diagram could not render. The text trace is still available.";
            graph.setAttribute("data-render-error", String(error));
        });
        traceList.replaceChildren();
        if (trace) {
            for (const step of trace.steps.slice(0, progress)) {
                const item = document.createElement("li");
                item.textContent = step.text;
                traceList.appendChild(item);
            }
            status.textContent = progress === trace.steps.length ? trace.message : `Step ${progress} of ${trace.steps.length}. Choose Next step.`;
        }
        nextButton.disabled = !trace || progress >= trace.steps.length;
    }

    function Build() {
        const values = model.ParseValues(document.getElementById("lab-values").value);
        const multi = document.getElementById("lab-mode").value === "multi";
        tree = model.BuildTree(values, multi);
        trace = null;
        progress = 0;
        document.getElementById("lab-sorted").textContent = "Sorted values: [" + tree.entries.map(entry => entry.value).join(", ") + "]";
        status.textContent = "Choose a query, then step through its decisions.";
        Render();
    }

    function Query() {
        Build();
        const input = document.getElementById("lab-query").value.trim();
        if (!/^-?\d+$/.test(input) || !Number.isSafeInteger(Number(input))) {
            throw new Error("Choose a whole-number rank or threshold.");
        }
        const value = Number(input);
        const operation = document.getElementById("lab-operation").value;
        trace = operation === "select" ? model.SelectTrace(tree, value) : model.RankTrace(tree, value, operation === "upper");
        progress = 0;
        Render();
    }

    function Safely(action) {
        return () => {
            try {
                action();
            }
            catch (error) {
                status.textContent = error.message;
            }
        };
    }

    if (!window.mermaid || !model) {
        status.textContent = "The interactive files could not load. The static diagrams and article remain readable.";
        panel.querySelectorAll("button").forEach(button => button.disabled = true);
        return;
    }
    mermaid.initialize({startOnLoad:false, securityLevel:"strict", theme:"base",
        themeVariables:{fontFamily:"Arial"}, flowchart:{htmlLabels:false}});
    document.getElementById("lab-run").addEventListener("click", Safely(Query));
    document.getElementById("lab-reset").addEventListener("click", Safely(Build));
    nextButton.addEventListener("click", Safely(() => {
        if (trace && progress < trace.steps.length) {
            progress++;
            Render();
        }
    }));
    document.getElementById("lab-all").addEventListener("click", Safely(() => {
        if (!trace) {
            Query();
        }
        progress = trace.steps.length;
        Render();
    }));
    Safely(Build)();
})();
