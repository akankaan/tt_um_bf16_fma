# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import sys

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge

# This testing mirrors the structure of my fma top file written
# for cocotb and with the fixed load and output cycles
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "src/bf16-fma/scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import reference_model
from vector_generation import fma_vectors


def generate_vectors(vector_generator):
    return [
        (a, b, c, reference_model.fma_bf16_ref(a, b, c))
        for a, b, c in vector_generator()
    ]


async def run_vectors(dut, name, vectors):
    operands = [operand for a, b, c, _ in vectors for operand in (a, b, c)]

    # Reset before each vector file
    dut.rst_n.value = 0
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    await ClockCycles(dut.clk, 2)
    await FallingEdge(dut.clk)
    dut.rst_n.value = 1

    errors = 0
    result_low_byte = 0

    # Inputs occupy cycles 1 through 3N. The last result high byte is on 3N + 8.
    for cycle in range(1, 3 * len(vectors) + 9):
        operand = operands[cycle - 1] if cycle <= len(operands) else 0
        dut.ui_in.value = operand & 0xFF
        dut.uio_in.value = operand >> 8

        await RisingEdge(dut.clk)
        await FallingEdge(dut.clk)

        if cycle >= 10:
            result_index, byte_index = divmod(cycle - 10, 3)
            if result_index < len(vectors):
                if byte_index == 0:
                    result_low_byte = int(dut.uo_out.value)
                elif byte_index == 1:
                    result = (int(dut.uo_out.value) << 8) | result_low_byte
                    a, b, c, expected = vectors[result_index]
                    if result != expected:
                        errors += 1
                        dut._log.error(
                            "MISS a=%04x b=%04x c=%04x | got=%04x want=%04x",
                            a,
                            b,
                            c,
                            result,
                            expected,
                        )

    dut._log.info("%s: %d vectors", name, len(vectors))
    return len(vectors), errors


@cocotb.test()
async def test_project(dut):
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1

    num_vectors = 0
    errors = 0

    vector_sets = (
        ("fma_special_vectors", fma_vectors.fma_special_vectors),
        ("fma_directed_vectors", fma_vectors.fma_directed_vectors),
    )

    for name, vector_generator in vector_sets:
        vectors = generate_vectors(vector_generator)
        vectors_run, vector_errors = await run_vectors(dut, name, vectors)
        num_vectors += vectors_run
        errors += vector_errors

    assert errors == 0, f"TT FMA: FAIL -- {num_vectors} vectors, {errors} errors"
    dut._log.info("TT FMA: PASS -- %d vectors, 0 errors", num_vectors)
