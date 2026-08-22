/*
 * SPDX-FileCopyrightText: 2026 Kaan Akan
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_akankaan_bf16_fma (
    input  wire [7:0] ui_in,    // dedicated input
    output wire [7:0] uo_out,   // dedicated output
    input  wire [7:0] uio_in,   // bidirectional input  pins
    output wire [7:0] uio_out,  // bidirectional output pins
    output wire [7:0] uio_oe,   // bidirectional output pins enable
    input  wire       ena,      // design active indication
    input  wire       clk,      // clock
    input  wire       rst_n     // active-low reset
);

    // uio is input only for a 16-bit load bus {uio_in, ui_in},
    // so uio never drives
    assign uio_out = 8'h00;
    assign uio_oe  = 8'h00;

    // The tapeout interface has no spare pins for valid signals.
    // Input words are therefore treated as valid every cycle,
    // while output bytes use the documented fixed timing.
        
    wire result_valid;

    bf16_fma fma (
        .clk          (clk),
        .rst_n        (rst_n),
        .in_valid     (1'b1),
        .in_data      ({uio_in, ui_in}), // uio = high, ui_in = low byte
        .out_data     (uo_out),
        .result_valid (result_valid)
    );

    // silence unused warnings
    wire unused_logic = ena & result_valid & 1'b0;

endmodule
