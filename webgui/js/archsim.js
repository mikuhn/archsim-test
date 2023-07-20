const output = document.getElementById("output");
const registers = document.getElementById("gui_registers_table_body_id");
const memory = document.getElementById("gui_memory_table_body_id");
const instructions = document.getElementById("gui_cmd_table_body_id");
const input = document.getElementById("input");
const performance_metrics = document.getElementById("performance_metrics");

function addToOutput(s) {
    output.value += ">>>" + input.value + "\n" + s + "\n";
    output.scrollTop = output.scrollHeight;
}

// Object containing functions to be exported to python
const archsim_js = {
    update_register_table: function (reg, representations, abi_name) {
        tr = document.createElement("tr");
        td1 = document.createElement("td");
        td1.innerText = "x" + reg;
        td2 = document.createElement("td");
        td2.innerText = Array.from(representations)[reg_representation_mode];
        td2.id = "val_x" + reg;
        td3 = document.createElement("td");
        td3.innerText = abi_name;
        td3.id = abi_name;
        tr.appendChild(td3);
        tr.appendChild(td1);
        tr.appendChild(td2);
        registers.appendChild(tr);
    },
    // update_single_register: function(reg, val) {
    //     document.getElementById("val_x"+reg).innerText = val
    // },
    update_memory_table: function (address, representations) {
        tr = document.createElement("tr");
        td1 = document.createElement("td");
        td1.innerText = address;
        td2 = document.createElement("td");
        //alert(Array.from(representations))
        td2.innerText = Array.from(representations)[mem_representation_mode];
        td2.id = "memory" + address;
        tr.appendChild(td1);
        tr.appendChild(td2);
        memory.appendChild(tr);
    },
    // update_single_memory_address: function(address, val) {
    //     try{
    //     document.getElementById("memory"+address).innerText = val
    //     }
    //     catch
    //     {
    //     tr = document.createElement("tr")
    //     td1 = document.createElement("td")
    //     td1.innerText = address
    //     td2 = document.createElement("td")
    //     td2.innerText = val
    //     td2.id = "memory"+address
    //     tr.appendChild(td1)
    //     tr.appendChild(td2)
    //     memory.appendChild(tr)
    //     }
    // },
    //ids und inner texts have to be changed then delete this comment
    update_instruction_table: function (address, val, stage) {
        tr = document.createElement("tr");
        tr.id = address;
        td1 = document.createElement("td");
        td1.innerText = address;
        td2 = document.createElement("td");
        td2.innerText = val;
        td2.id = "instr" + address;
        td3 = document.createElement("td");
        td3.innerText = stage;
        if (stage == "Single") {
            td1.style.backgroundColor = "purple";
            td2.style.backgroundColor = "purple";
            td3.style.backgroundColor = "purple";
        } else if (stage == "IF") {
            td1.style.backgroundColor = "red";
            td2.style.backgroundColor = "red";
            td3.style.backgroundColor = "red";
        } else if (stage == "ID") {
            td1.style.backgroundColor = "yellow";
            td2.style.backgroundColor = "yellow";
            td3.style.backgroundColor = "yellow";
        } else if (stage == "EX") {
            td1.style.backgroundColor = "green";
            td2.style.backgroundColor = "green";
            td3.style.backgroundColor = "green";
        } else if (stage == "MA") {
            td1.style.backgroundColor = "aqua";
            td2.style.backgroundColor = "aqua";
            td3.style.backgroundColor = "aqua";
        } else if (stage == "WB") {
            td1.style.backgroundColor = "blue";
            td2.style.backgroundColor = "blue";
            td3.style.backgroundColor = "blue";
        }
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3);
        instructions.appendChild(tr);
    },
    clear_memory_table: function () {
        this.clear_a_table(memory);
    },
    clear_register_table: function () {
        this.clear_a_table(registers);
    },
    clear_instruction_table: function () {
        this.clear_a_table(instructions);
    },
    clear_a_table: function (table) {
        table.innerHTML = "";
    },
    set_output: function (str) {
        output.value = str;
    },
    highlight: function (position, str) {
        //editor.removeLineClass(position-1, "background", "highlight")
        editor.addLineClass(position - 1, "background", "highlight");
        editor.refresh();
        str.toString = function () {
            return this.str;
        };
        output_str = str.toString();
        var error_description = {
            hint: function () {
                return {
                    from: position,
                    to: position,
                    list: [output_str, ""],
                };
            },
            customKeys: {
                Up: function (cm, handle) {
                    CodeMirror.commands.goLineUp(cm);
                    handle.close();
                },
                Down: function (cm, handle) {
                    CodeMirror.commands.goLineDown(cm);
                    handle.close();
                },
            },
        };
        editor.showHint(error_description);
    },
    remove_all_highlights: function () {
        for (let i = 0; i < editor.lineCount(); i++) {
            editor.removeLineClass(i, "background", "highlight");
        }
        editor.refresh();
        editor.closeHint();
    },
    highlight_cmd_table: function (position) {
        table = document.getElementById("gui_cmd_table_id");
        table.rows[position + 1].cells[0].style.backgroundColor = "yellow";
        table.rows[position + 1].cells[1].style.backgroundColor = "yellow";
        console.log(table.innerHTML);
    },
    update_IF_Stage: function (instruction, address_of_instruction) {},
    update_ID_Stage: function (
        register_read_addr_1,
        register_read_addr_2,
        register_read_data_1,
        register_read_data_2,
        imm,
        control_unit_signals
    ) {},
    update_EX_Stage: function (
        alu_in_1,
        alu_in_2,
        register_read_data_2,
        imm,
        result,
        comparison,
        pc_plus_imm,
        control_unit_signals
    ) {},
    update_MA_Stage: function (
        memory_address,
        result,
        memory_write_data,
        memory_read_data,
        comparison,
        pc_src,
        pc_plus_imm,
        control_unit_signals
    ) {},
    update_WB_Stage: function (
        register_write_data,
        write_register,
        memory_read_data,
        alu_result,
        control_unit_signals
    ) {},
};

output.value = "Output \n\nInitializing... ";
input.value = "add x1, x2, x3 \nlui x1, 1";
performance_metrics.value = "Performance Metrics";
// init Pyodide
async function main() {
    start_loading_visuals();
    let pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    console.log(window.location.protocol);
    console.log(window.location.href);
    console.log(window.location.origin);
    console.log(window.location.hash);
    console.log(window.location.host);
    console.log(window.location.hostname);
    console.log(window.location.pathname);
    console.log(window.location.port);
    if (window.location.href == "https://atreus.cs.uni-tuebingen.de/archsim/") {
        await micropip.install(
            window.location.href +
                "/dist/architecture_simulator-0.1.0-py3-none-any.whl"
        );
    } else {
        await micropip.install(
            window.location.origin +
                "/dist/architecture_simulator-0.1.0-py3-none-any.whl"
        );
    }

    pyodide.registerJsModule("archsim_js", archsim_js);
    await pyodide.runPython(`
from architecture_simulator.gui.webgui import *
sim_init()
    `);
    output.value += "Ready!\n";
    performance_metrics.value += "...";
    stop_loading_visuals();
    return pyodide;
}
let pyodideReadyPromise = main();

async function evaluatePython_step_sim() {
    let pyodide = await pyodideReadyPromise;
    input_str = input.value;
    try {
        step_sim = pyodide.globals.get("step_sim");
        let output_repr = Array.from(step_sim(input_str));
        if (output_repr[1] == false) {
            stop_timer();
            stop_loading_animation();
            disable_pause();
            disable_step();
            disable_run();
            clearInterval(run);
        }
        update_performance_metrics();
    } catch (err) {
        output.value = err;
        stop_loading_animation();
        disable_pause();
        disable_step();
        disable_run();
        clearInterval(run);
    }
}

async function resume_timer() {
    let pyodide = await pyodideReadyPromise;
    resume_timer = pyodide.globals.get("resume_timer");
    resume_timer();
}

async function stop_timer() {
    let pyodide = await pyodideReadyPromise;
    stop_timer = pyodide.globals.get("stop_timer");
    stop_timer();
}

async function update_performance_metrics() {
    let pyodide = await pyodideReadyPromise;
    get_performance_metrics = pyodide.globals.get("get_performance_metrics");
    //output.value = get_performance_metrics();
    performance_metrics.value = get_performance_metrics();
}

// async function evaluatePython_run_sim() {
//     start_loading_animation();
//     let pyodide = await pyodideReadyPromise;
//     stop_loading_animation();
//     input_str = input.value
//     let output;
//     try {
//         // reset the sim before executing run
//         reset_sim = pyodide.globals.get("reset_sim");
//         reset_sim();

//         run_sim = pyodide.globals.get("run_sim");
//         let output = run_sim(input_str);
//         addToOutput(output);
//     } catch (err) {
//         addToOutput(err);
//     }
// }

async function evaluatePython_reset_sim(pipeline_mode) {
    start_loading_animation();
    let pyodide = await pyodideReadyPromise;
    stop_loading_animation();
    try {
        reset_sim = pyodide.globals.get("reset_sim");
        reset_sim(pipeline_mode);
        output.value = "";
        performance_metrics.value = "";
    } catch (err) {
        addToOutput(err);
    }
}

async function evaluatePython_update_tables() {
    let pyodide = await pyodideReadyPromise;
    try {
        update_tables = pyodide.globals.get("update_tables");
        let output = update_tables();
        var table = document.getElementById("gui_cmd_table_id");
        var rows = table.rows;
        rows[0].classList.add("highlight");
        console.log(rows[2].classList);
        console.log(table.innerHTML);
    } catch (err) {
        addToOutput(err);
    }
}

async function evaluatePython_parse_input() {
    let pyodide = await pyodideReadyPromise;
    input_str = input.value;
    try {
        parse_input = pyodide.globals.get("parse_input");
        parse_input(input_str);
    } catch (err) {
        addToOutput(err);
    }
}

//function update_output(output_string) {
//    output.value = output_string;
//}
