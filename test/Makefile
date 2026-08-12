# Makefile
# See https://docs.cocotb.org/en/stable/quickstart.html for more info

# defaults
SIM ?= icarus
FST ?= -fst # Use more efficient FST format
TOPLEVEL_LANG ?= verilog
SRC_DIR = $(PWD)/../src
PROJECT_SOURCES  = tt_um_akankaan_bf16_fma.v
PROJECT_SOURCES += bf16-fma/rtl/bf16_fma.sv
PROJECT_SOURCES += bf16-fma/rtl/bf16_fma_io.sv
PROJECT_SOURCES += bf16-fma/rtl/bf16_loader.sv
PROJECT_SOURCES += bf16-fma/rtl/bf16_outputter.sv
PROJECT_SOURCES += bf16-fma/rtl/bf16_fma_core.sv
PROJECT_SOURCES += bf16-fma/rtl/bf16_decode_classify.sv
PROJECT_SOURCES += bf16-fma/rtl/bf16_multiplier.sv
PROJECT_SOURCES += bf16-fma/rtl/bf16_aligner.sv
PROJECT_SOURCES += bf16-fma/rtl/bf16_addsub.sv
PROJECT_SOURCES += bf16-fma/rtl/bf16_normalizer.sv
PROJECT_SOURCES += bf16-fma/rtl/bf16_rounder.sv

ifneq ($(GATES),yes)

# RTL simulation:
SIM_BUILD				= sim_build/rtl
VERILOG_SOURCES += $(addprefix $(SRC_DIR)/,$(PROJECT_SOURCES))

else

# Gate level simulation:
SIM_BUILD				= sim_build/gl
COMPILE_ARGS    += -DGL_TEST
COMPILE_ARGS    += -DFUNCTIONAL
COMPILE_ARGS    += -DUSE_POWER_PINS
COMPILE_ARGS    += -DSIM
COMPILE_ARGS    += -DUNIT_DELAY=\#1
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v

# this gets copied in by the GDS action workflow
VERILOG_SOURCES += $(PWD)/gate_level_netlist.v

endif

# Allow sharing configuration between design and testbench via `include`:
COMPILE_ARGS 		+= -I$(SRC_DIR)

# Include the testbench sources:
VERILOG_SOURCES += $(PWD)/tb.v
TOPLEVEL = tb

# List test modules to run, separated by commas and without the .py suffix:
COCOTB_TEST_MODULES = test

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
