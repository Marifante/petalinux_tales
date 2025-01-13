# Arty Z7


## Power

We should power the Arty A7 using an external power supply (not through the PC). That's because the PC might not have enough power to deliver.
We should use an 7 V to 15 V AC power adaptor.


If we check the reference manual, we can obtain the total power that should be delivered to the Arty in a worst case scenario:

| Voltage rail [V] | 3.3  | 1   | 1.5  | 1.8  | Total |
|------------------|------|-----|------|------|-------|
| Max Current [A]  | 1.5  | 2.1 | 1.2  | 0.6  |       |
| Max power [W]    | 4.95 | 2.1 | 1.8  | 1.08 | 9.93  |

So, our power AC adaptor should deliver at least 9.93 W. To put it safe, let's say 11 W.
AC power adaptors are being sold with the current and voltage rating, so we should compute if the current rating of the adaptor is enough.
For example, a 9 V AC adaptor should have a current rating bigger than: `11 W / 9 V = 1.2 A`.

## UART-USB

Arty Z7 has a FTDI FT2232HQ USB-UART bridge. The UART side of this controller is tied to Processing System (PS) (MIO) and can be used in combination to UART 0 controller.

## References

* Reference manual: https://digilent.com/reference/programmable-logic/arty-z7/reference-manual
* Schematic: https://digilent.com/reference/_media/reference/programmable-logic/arty-z7/arty_z7_sch.pdf?srsltid=AfmBOoqua3WAcdVJAR5xSSj9IAzbiFuIKLVl9Qt1xN1VmQnntC9gqjE2
* PS UART: https://xilinx-wiki.atlassian.net/wiki/spaces/A/pages/18842340/PS+UART
