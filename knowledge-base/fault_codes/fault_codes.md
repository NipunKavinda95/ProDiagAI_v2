# Industrial Fault Code and Symptom Reference

## Purpose

This document provides a simulated engineering reference for common faults
observed in industrial rotating equipment.

The information is intended to support ProDiag AI V2's retrieval-augmented
maintenance diagnosis and should be treated as decision-support information,
not as a replacement for machine-specific OEM documentation.

---

## F001 — Bearing Wear

### Equipment

Motors, pumps, fans, compressors, gearboxes

### Typical Symptoms

- Increasing vibration
- Gradually increasing temperature
- Abnormal mechanical noise
- Increasing vibration trend
- Possible reduction in operating efficiency

### Common Causes

- Normal bearing wear
- Poor lubrication
- Contamination
- Misalignment
- Excessive mechanical loading

### Recommended Inspection

- Check vibration trend
- Inspect bearing condition
- Check lubrication
- Inspect shaft and coupling alignment
- Check bearing housing

### Typical Severity

WARNING to CRITICAL depending on degradation level.

---

## F002 — Motor Overload

### Equipment

Motors, pumps, compressors, conveyors

### Typical Symptoms

- High motor current
- Reduced RPM
- Increasing temperature
- Increased mechanical load
- Possible protective trip

### Common Causes

- Excessive mechanical load
- Mechanical resistance
- Jammed equipment
- Incorrect operating conditions
- Bearing or gearbox problems

### Recommended Inspection

- Check motor current
- Check RPM
- Inspect mechanical load
- Inspect bearings and coupling
- Check for mechanical obstruction

### Typical Severity

WARNING to CRITICAL.

---

## F003 — Pump Cavitation

### Equipment

Centrifugal pumps

### Typical Symptoms

- Increased vibration
- Unstable operation
- Abnormal noise
- Reduced pump performance
- Fluctuating operating conditions

### Common Causes

- Insufficient suction pressure
- Restricted suction line
- Incorrect operating conditions
- Excessive pump demand
- Fluid supply problems

### Recommended Inspection

- Check suction pressure
- Inspect suction line
- Check fluid level
- Verify pump operating conditions
- Inspect impeller condition

### Typical Severity

WARNING to CRITICAL.

---

## F004 — Belt Misalignment

### Equipment

Conveyors, fans, belt-driven machines

### Typical Symptoms

- Increasing vibration
- Abnormal noise
- Temperature increase
- Belt wear
- Uneven mechanical operation

### Common Causes

- Pulley misalignment
- Incorrect belt tension
- Worn belt
- Incorrect installation
- Shaft alignment problem

### Recommended Inspection

- Inspect belt alignment
- Check belt tension
- Inspect pulleys
- Check shaft alignment
- Inspect belt condition

### Typical Severity

DEGRADING to WARNING.

---

## F005 — Fan Imbalance

### Equipment

Industrial fans and rotating equipment

### Typical Symptoms

- Elevated vibration
- Vibration increasing with RPM
- Abnormal noise
- Increased bearing loading

### Common Causes

- Uneven fan blade loading
- Damaged blades
- Dirt accumulation
- Shaft imbalance
- Mechanical damage

### Recommended Inspection

- Inspect fan blades
- Check for material accumulation
- Check shaft condition
- Measure vibration
- Check mechanical balance

### Typical Severity

WARNING to CRITICAL.

---

## F006 — Gear Wear

### Equipment

Gearboxes and geared drives

### Typical Symptoms

- Increasing vibration
- Abnormal noise
- Increasing temperature
- Reduced mechanical efficiency
- Possible speed instability

### Common Causes

- Gear tooth wear
- Poor lubrication
- Excessive load
- Misalignment
- Contamination

### Recommended Inspection

- Check gearbox vibration
- Check lubricant condition
- Inspect gear teeth
- Check alignment
- Inspect gearbox housing

### Typical Severity

WARNING to CRITICAL.

---

## F007 — High Temperature

### Equipment

Motors, pumps, compressors, fans, gearboxes

### Typical Symptoms

- Temperature above normal operating range
- Increasing temperature trend
- Possible vibration increase
- Reduced equipment performance

### Common Causes

- Excessive load
- Bearing problems
- Poor lubrication
- Cooling failure
- Mechanical friction

### Recommended Inspection

- Check temperature trend
- Check motor load
- Inspect cooling system
- Check lubrication
- Inspect bearings

### Typical Severity

WARNING to CRITICAL depending on temperature and trend.

---

## F008 — Sensor / Communication Failure

### Equipment

All monitored equipment

### Typical Symptoms

- Missing telemetry
- No sensor update
- Invalid sensor values
- Unexpected constant readings

### Common Causes

- Sensor failure
- Communication interruption
- MQTT connection failure
- PLC communication problem
- Power loss

### Recommended Inspection

- Check sensor connection
- Check PLC communication
- Check MQTT connectivity
- Verify sensor power
- Compare with other available measurements

### Typical Severity

WARNING.

---

## Diagnostic Interpretation Rules

The ProDiag AI system should consider multiple signals together rather than
assigning a fault from a single measurement.

### Pattern 1 — Bearing degradation

Increasing vibration + increasing temperature + degradation trend

→ Possible bearing wear or lubrication problem.

### Pattern 2 — Motor overload

High current + reduced RPM + increasing temperature

→ Possible motor overload or mechanical resistance.

### Pattern 3 — Pump cavitation

Increasing vibration + unstable operation + pump performance reduction

→ Possible cavitation.

### Pattern 4 — Belt misalignment

Increasing vibration + temperature increase + belt-related symptoms

→ Possible belt or pulley misalignment.

### Pattern 5 — Gear wear

Increasing vibration + abnormal noise + gearbox temperature increase

→ Possible gear wear or lubrication problem.

---

## Important Safety Note

Fault identification from this knowledge base is a diagnostic aid.

Maintenance personnel should verify machine condition using applicable
site procedures, safety requirements, and authorized machine documentation
before performing maintenance.
