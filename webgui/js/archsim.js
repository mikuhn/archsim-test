const output = document.getElementById("output");
const registers = document.getElementById("gui_registers_table_id");
const memory = document.getElementById("gui_memory_table_id");
const instructions = document.getElementById("gui_cmd_table_body_id");
const input = document.getElementById("input");

function addToOutput(s) {
    output.value += ">>>" + input.value + "\n" + s + "\n";
    output.scrollTop = output.scrollHeight;
}

// Object containing functions to be exported to python
const archsim_js = {
    update_register: function(reg, val) {
        tr = document.createElement("tr")
        empty_td0 = document.createElement("td");
        td1 = document.createElement("td")
        td1.innerText = "x"+reg
        td2 = document.createElement("td")
        td2.innerText = val
        td2.id = "val_x"+reg
        tr.appendChild(empty_td0)
        tr.appendChild(td1)
        tr.appendChild(td2)
        registers.appendChild(tr)
    },
    update_single_register: function(reg, val) {
        document.getElementById("val_x"+reg).innerText = val
    },
    update_memory: function(address, val) {
        tr = document.createElement("tr")
        empty_td0 = document.createElement("td");
        td1 = document.createElement("td")
        td1.innerText = address
        td2 = document.createElement("td")
        td2.innerText = val
        td2.id = "memory"+address
        tr.appendChild(empty_td0)
        tr.appendChild(td1)
        tr.appendChild(td2)
        memory.appendChild(tr)
    },
    update_single_memory_address: function(address, val) {
        try{
        document.getElementById("memory"+address).innerText = val
        }
        catch
        {
        tr = document.createElement("tr")
        td1 = document.createElement("td")
        td1.innerText = address
        td2 = document.createElement("td")
        td2.innerText = val
        td2.id = "memory"+address
        tr.appendChild(td1)
        tr.appendChild(td2)
        memory.appendChild(tr)
        }
    },
    clear_memory_table: function() {
        this.clear_a_table(memory);

    },
    clear_register_table: function() {
        this.clear_a_table(registers);
    },
    clear_instruction_table: function() {
        this.clear_a_table(instructions);
    },
    clear_a_table: function(table) {
        while (table.childNodes.length > 2) {
            table.removeChild(table.lastChild);
        }
    }
};

output.value = "Initializing... ";
// init Pyodide
async function main() {
    let pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install(window.location.origin+"/dist/architecture_simulator-0.1.0-py3-none-any.whl");
    pyodide.registerJsModule("archsim_js", archsim_js);
    await pyodide.runPython(`
from architecture_simulator.gui.webgui import *
sim_init()
    `);
    output.value += "Ready!\n";
    return pyodide;
}
let pyodideReadyPromise = main();

async function evaluatePython_step_sim() {
    let pyodide = await pyodideReadyPromise;
    //alert("step")
    //alert(input.value.split("\n"))
    //alert(simulation_json)
    input_str = input.value
    try {
        step_sim = pyodide.globals.get("step_sim");
        let output = step_sim(input_str);
        addToOutput(output);
    } catch (err) {
        addToOutput(err);
    }
    //alert(simulation_json)
}

async function evaluatePython_run_sim() {
    let pyodide = await pyodideReadyPromise;
    //alert("run")
    //alert(input.value.split("\n"))
    input_str = input.value
    try {
        run_sim = pyodide.globals.get("run_sim");
        let output = run_sim(input_str);
        addToOutput(output);
    } catch (err) {
        addToOutput(err);
    }
}

async function evaluatePython_reset_sim() {
    let pyodide = await pyodideReadyPromise;
    registers.innerHTML = ""
    memory.innerHTML = ""
    try {
        reset_sim = pyodide.globals.get("reset_sim");
        let output = reset_sim();
        addToOutput(output);
    } catch (err) {
        addToOutput(err);
    }
}
