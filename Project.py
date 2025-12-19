import re
import matplotlib.pyplot as plt


# ------------------------------------------------------------
# LOGIC GATES
# ------------------------------------------------------------

def gate_and(inputs):
    return int(all(inputs))


def gate_or(inputs):
    return int(any(inputs))


def gate_not(inputs):
    return int(not inputs[0])


def gate_xor(inputs):
    v = 0
    for x in inputs:
        v ^= x
    return v


GATE_FUNCS = {
    "AND": gate_and,
    "OR": gate_or,
    "INVERTOR": gate_not,  # kept original keyword for compatibility
    "XOR": gate_xor,
}


# ------------------------------------------------------------
# INPUT FILE PARSER
# ------------------------------------------------------------

def parse_file(filename):
    inputs = {}  # IN A { ... }
    wires = set()  # WIRE X
    outputs = set()  # OUT Z
    elements = []  # ELEMENT AND 3{A,B,C} 1{X}
    sim_time = 0

    with open(filename, "r") as f:
        lines = [x.strip() for x in f if x.strip()]

    for line in lines:
        if line.startswith("IN"):
            # IN A {0,1,1,0,1}
            m = re.match(r"IN\s+(\w+)\s*\{([^}]*)\}", line)
            name = m.group(1)
            arr = [int(x.strip()) for x in m.group(2).split(",")]
            inputs[name] = arr

        elif line.startswith("WIRE"):
            # WIRE X
            name = line.split()[1]
            wires.add(name)

        elif line.startswith("OUT"):
            # OUT Z
            name = line.split()[1]
            outputs.add(name)

        elif line.startswith("ELEMENT"):
            # ELEMENT AND 3{A,B,C} 1{X}
            m = re.match(r"ELEMENT\s+(\w+)\s+(\d+)\{([^}]*)\}\s+(\d+)\{([^}]*)\}", line)
            gate = m.group(1)
            in_count = int(m.group(2))
            ins = [x.strip() for x in m.group(3).split(",")]
            out_count = int(m.group(4))
            outs = [x.strip() for x in m.group(5).split(",")]
            elements.append((gate, ins, outs))

        elif line.startswith("TIME"):
            sim_time = int(line.split()[1])

    return inputs, wires, outputs, elements, sim_time


# ------------------------------------------------------------
# SIMULATION
# ------------------------------------------------------------

def simulate(inputs, wires, outputs, elements, sim_time):
    signal_traces = {name: [0] * sim_time for name in list(wires) + list(outputs)}

    for name, arr in inputs.items():
        full = arr + [arr[-1]] * (sim_time - len(arr))
        signal_traces[name] = full

    all_nets = set(signal_traces.keys())

    for t in range(sim_time):

        for gate, ins, outs in elements:
            func = GATE_FUNCS[gate]
            in_values = [signal_traces[x][t] for x in ins]
            out_value = func(in_values)
            for out in outs:
                signal_traces[out][t] = out_value

    return signal_traces


# ------------------------------------------------------------
# WAVEFORM RENDERING
# ------------------------------------------------------------

def draw_waveforms(signal_traces, sim_time, filename=None):
    """Draw timing waveforms for all nets."""
    plt.figure(figsize=(12, 0.6 * len(signal_traces)))
    names = list(signal_traces.keys())

    for i, name in enumerate(names):
        y = [v + 2 * i for v in signal_traces[name]]  # vertical offset per signal
        plt.step(range(sim_time), y, where='post')
        plt.text(-0.5, 2 * i + 0.5, name, fontsize=10, va='center')

    plt.yticks([])
    plt.xlabel("Time")
    plt.grid(True, axis='x')

    if filename:
        plt.savefig(filename)
    else:
        plt.show()


# ------------------------------------------------------------
# SCHEMATIC (auto-drawn from netlist)
# ------------------------------------------------------------

def _levelize(inputs, elements):
    net_level = {name: 0 for name in inputs.keys()}
    gate_level = [None] * len(elements)

    changed = True
    passes = 0
    while changed and passes < 1000:
        changed = False
        passes += 1
        for i, (_, ins, outs) in enumerate(elements):
            # pure combinational (no latches/loops)
            if all(n in net_level for n in ins):
                lvl = 1 + max(net_level[n] for n in ins) if ins else 1
                if gate_level[i] != lvl:
                    gate_level[i] = lvl
                    changed = True
                for out in outs:
                    if net_level.get(out) != lvl:
                        net_level[out] = lvl
                        changed = True

    return gate_level, net_level


def _build_connectivity(inputs, elements, outputs):
    net_driver = {}
    net_sinks = {}

    # Inputs drive their own nets
    for in_name in inputs.keys():
        net_driver[in_name] = ("INPUT", in_name)

    # Elements drive output nets; input nets are sinks
    for gi, (_, ins, outs) in enumerate(elements):
        gname = f"G{gi + 1}"
        for out in outs:
            if out in net_driver:
                net_driver[out] = ("CONFLICT", net_driver[out], ("GATE", gname))
            else:
                net_driver[out] = ("GATE", gname)
        for n in ins:
            net_sinks.setdefault(n, []).append(("GATE", gname))

    # Outputs consume their nets
    for out_name in outputs:
        net_sinks.setdefault(out_name, []).append(("OUTPUT", out_name))

    return net_driver, net_sinks


def draw_schematic(inputs, elements, outputs, filename=None):
    gate_levels, _ = _levelize(inputs, elements)
    net_driver, net_sinks = _build_connectivity(inputs, elements, outputs)

    # Group elements by level
    level_to_gate_indices = {}
    for i, lvl in enumerate(gate_levels):
        level_to_gate_indices.setdefault(lvl if lvl is not None else 1, []).append(i)

    max_gate_level = max([lvl for lvl in gate_levels if lvl is not None], default=1)

    # Node positions
    pos_inputs = {}
    pos_gates = {}
    pos_outputs = {}

    x_spacing = 4.0
    y_spacing = 2.0

    # Inputs at level 0
    for idx, in_name in enumerate(sorted(inputs.keys())):
        pos_inputs[in_name] = (0, -idx * y_spacing)

    # Gates by levels (1..max)
    for lvl in range(1, max_gate_level + 1):
        for j, gi in enumerate(level_to_gate_indices.get(lvl, [])):
            gname = f"G{gi + 1}"
            pos_gates[gname] = (lvl * x_spacing, -j * y_spacing)

    # Outputs on the right (max+1)
    for k, out_name in enumerate(sorted(outputs)):
        pos_outputs[out_name] = ((max_gate_level + 1) * x_spacing, -k * y_spacing)

    # Drawing
    fig_w = max(10, (max_gate_level + 2) * 2.5)
    fig, ax = plt.subplots(figsize=(fig_w, 8))

    # Inputs (circles)
    for name, (x, y) in pos_inputs.items():
        ax.add_patch(plt.Circle((x, y), 0.4, color='#1f77b4', fill=False, linewidth=2))
        ax.text(x - 0.9, y, name, va='center', ha='right', fontsize=11)

    # Gates (rectangles)
    for gi, (gate, ins, outs) in enumerate(elements):
        gname = f"G{gi + 1}"
        x, y = pos_gates.get(gname, (x_spacing, -gi * y_spacing))
        w, h = 2.8, 1.4
        ax.add_patch(plt.Rectangle((x - w / 2, y - h / 2), w, h, fill=False, linewidth=2, edgecolor='#2ca02c'))
        ax.text(x, y, f"{gate}\n{gname}", ha='center', va='center', fontsize=10)

    # Outputs (circles)
    for name, (x, y) in pos_outputs.items():
        ax.add_patch(plt.Circle((x, y), 0.4, color='#d62728', fill=False, linewidth=2))
        ax.text(x + 0.9, y, name, va='center', ha='left', fontsize=11)

    # Helpers for connections
    def _src_pos(net):
        drv = net_driver.get(net)
        if drv is None:
            return None
        if drv[0] == "INPUT":
            return pos_inputs.get(drv[1])
        if drv[0] == "GATE":
            return pos_gates.get(drv[1])
        if drv[0] == "CONFLICT":
            # choose the last gate for drawing
            _, _, gate = drv
            return pos_gates.get(gate[1])
        return None

    def _dst_pos(dst):
        if dst[0] == "GATE":
            return pos_gates.get(dst[1])
        if dst[0] == "OUTPUT":
            return pos_outputs.get(dst[1])
        return None

    # Connections (polyline + arrow)
    for net, sinks in net_sinks.items():
        sp = _src_pos(net)
        if sp is None:
            continue
        sx, sy = sp
        for dst in sinks:
            dp = _dst_pos(dst)
            if dp is None:
                continue
            dx, dy = dp
            mx = (sx + dx) / 2.0
            # horizontal → mid → vertical → horizontal
            ax.plot([sx + 1.3, mx, dx - 1.3], [sy, sy, dy], color='black')
            ax.annotate('', xy=(dx - 1.3, dy), xytext=(dx - 1.6, dy),
                        arrowprops=dict(arrowstyle='->', lw=1.5))
            ax.text(mx, sy + 0.35, net, fontsize=9, ha='center', va='bottom', color='#555')

    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()

    if filename:
        plt.savefig(filename)
        plt.close()
    else:
        plt.show()
        plt.close()


# ------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------

def run(filename):
    inputs, wires, outputs, elements, sim_time = parse_file(filename)
    signal_traces = simulate(inputs, wires, outputs, elements, sim_time)

    # Waveforms: save to file
    draw_waveforms(signal_traces, sim_time, filename="waveforms.png")

    # Schematic: save to file
    draw_schematic(inputs, elements, outputs, filename="schematic.png")

    print("Saved: waveforms.png and schematic.png")


if __name__ == "__main__":
    run("circuit.txt")
