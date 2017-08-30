Look-up tables
==============

This directory contains various look-up tables, based on simulated
spectra for various parameters.  We can then take an observed spectrum
and find the matching parameters (typically LFMC).

All you need to know:

- Use `merged_lookup.csv`

- For reasons below, we'll need to recreate the lookup tables and
  re-run everything later.

-------------------

The .npy format LUTs are derived from "LUT.xlsx", and the NDII column uses the correct bands.

Bugs: there are a variety of table lengths:

- LUT.xlsx mostly has 8607 rows of data, except the "LUTs" sheet
  (not "LUT"), which only has 7045
- LUT_withHeaders.txt has 8607 rows (direct copy of LUT.xlsx sheet "LUT")
- LUTs_continuo.xlsx has the table split over many sheets, with a total
  of 8370 rows
- LUT.txt, FMC.txt, and VEGTYPE.txt all have 8708 rows.
- The binary .npy format tables have 8708 rows

The table of 8708 values was derived from Marta's PhD research, but only
MODIS spectra were saved.  We'll use this one for now, and revisit the whole
thing when it's less urgent.

Full spectra were re-simulated more recently but have some replication
problems.  We will re-run the simulations with known parameters and regenerate
everything later.

**Why do some tables have 101 fewer rows and another 28 more?**


Note: according to the LUT.xlsx sheet "LUT", vegtype indices are as follows:
    1 = grass           (Spanish letter "p" for pasture)
    2 = shrub           (Spanish letter "m" for mattoral)
    3 = forest          (Spanish letter "a" for arbor)


