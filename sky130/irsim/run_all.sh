#!/bin/sh

# -40C vdd=1.62V
/usr/local/bin/ngspice -b -r spi_1v62_n40.out ckt_1v62_n40.spi
./findr -c 10 -n 0.8,0.18 -p 1.0,0.18 spi_1v62_n40.out |& tee sky130_1v62_n40.prm

# -40C vdd=1.80V
/usr/local/bin/ngspice -b -r spi_1v80_n40.out ckt_1v80_n40.spi
./findr -c 50 -n 0.8,0.18 -p 1.0,0.18 spi_1v80_n40.out |& tee sky130_1v80_n40.prm

# -40C vdd=1.98V
/usr/local/bin/ngspice -b -r spi_1v98_n40.out ckt_1v98_n40.spi
./findr -c 50 -n 0.8,0.18 -p 1.0,0.18 spi_1v98_n40.out |& tee sky130_1v98_n40.prm

# -5C vdd=1.62V
/usr/local/bin/ngspice -b -r spi_1v62_n5.out ckt_1v62_n5.spi
./findr -c 10 -n 0.8,0.18 -p 1.0,0.18 spi_1v62_n5.out |& tee sky130_1v62_n5.prm

# -5C vdd=1.80V
/usr/local/bin/ngspice -b -r spi_1v80_n5.out ckt_1v80_n5.spi
./findr -c 50 -n 0.8,0.18 -p 1.0,0.18 spi_1v80_n5.out |& tee sky130_1v80_n5.prm

# -5C vdd=1.98V
/usr/local/bin/ngspice -b -r spi_1v98_n5.out ckt_1v98_n5.spi
./findr -c 50 -n 0.8,0.18 -p 1.0,0.18 spi_1v98_n5.out |& tee sky130_1v98_n5.prm

# 27C vdd=1.62V
/usr/local/bin/ngspice -b -r spi_1v62_27.out ckt_1v62_27.spi
./findr -c 50 -n 0.8,0.18 -p 1.0,0.18 spi_1v62_27.out |& tee sky130_1v62_27.prm

# 27C vdd=1.8V
/usr/local/bin/ngspice -b -r spi_1v80_27.out ckt_1v80_27.spi
./findr -c 50 -n 0.8,0.18 -p 1.0,0.18 spi_1v80_27.out |& tee sky130_1v80_27.prm

# 27C vdd=1.98V
/usr/local/bin/ngspice -b -r spi_1v98_27.out ckt_1v98_27.spi
./findr -c 50 -n 0.8,0.18 -p 1.0,0.18 spi_1v98_27.out |& tee sky130_1v98_27.prm

# 125C vdd=1.62V
/usr/local/bin/ngspice -b -r spi_1v62_125.out ckt_1v62_125.spi
./findr -c 50 -n 0.8,0.18 -p 1.0,0.18 spi_1v62_125.out |& tee sky130_1v62_125.prm

# 125C vdd=1.8V
/usr/local/bin/ngspice -b -r spi_1v80_125.out ckt_1v80_125.spi
./findr -c 50 -n 0.8,0.18 -p 1.0,0.18 spi_1v80_125.out |& tee sky130_1v80_125.prm

# 125C vdd=1.98V
/usr/local/bin/ngspice -b -r spi_1v98_125.out ckt_1v98_125.spi
./findr -c 50 -n 0.8,0.18 -p 1.0,0.18 spi_1v98_125.out |& tee sky130_1v98_125.prm

