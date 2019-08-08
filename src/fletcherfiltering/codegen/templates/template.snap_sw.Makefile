# Empty Makefile for SNAP
default_target: all

.PHONY : all

# Allow only one "make -f Makefile2" at a time, but pass parallelism.
all:
