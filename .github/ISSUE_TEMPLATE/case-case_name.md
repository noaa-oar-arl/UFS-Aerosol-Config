---
name: case/CASE_NAME
about: Briefly describe the general science question or use case for setting the model
  this way
title: CASE
labels: Case
assignees: ''

---

## Case Details: 

Please provide a brief description of the case or experiment 


## Model Configuration Details 
- Resolution: 
- Begin Date: 
- End Date:
- Cold Start: True or False
- Forecast length (FHMAX_GFS): 120 hours
- FV3 output: every 6 hours 

## Aerosol Model Configuration

- ANTHRO1 (surface emissions) : CEDS
- ANTHRO2 (elevated emissions) : CEDS
- SHIP :  CEDS
- Biomass Burning: QFED where GBBEPx isn't available 
- Aviation: HTAP 
- NH3 Emissions: CEDS
- Dust : Fengsha
   * alpha:  0.7
   * gamma: 1
   * input file: 
- Sea Salt: 3 
    * scaling factor: 1 
- AOD output: 3 hours 
- Column Mass output: 3 hours 
- Surface Concentrtation output: every 3 hours 

## Measurements/Models available for comparison
