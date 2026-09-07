# Bearing Failure Modes

## Purpose

This document provides engineering reference information for identifying common bearing-related problems using industrial machine condition signals.

## 1. Bearing Wear

### Typical indicators

- Increasing vibration
- Gradual increase in temperature
- Increasing vibration trend over time
- Possible increase in mechanical resistance
- Abnormal operating noise

### Typical machine condition

DEGRADING → WARNING → CRITICAL

### Recommended maintenance

- Inspect bearing condition
- Check lubrication
- Check shaft and coupling alignment
- Inspect bearing housing
- Replace bearing if excessive wear is confirmed

---

## 2. Bearing Lubrication Problem

### Typical indicators

- Increasing bearing temperature
- Increased vibration
- Abnormal noise
- Temperature may continue increasing during operation

### Recommended maintenance

- Verify lubricant type
- Check lubrication level
- Inspect lubrication interval
- Inspect bearing condition

---

## 3. Bearing Misalignment

### Typical indicators

- Elevated vibration
- Increasing vibration trend
- Abnormal temperature
- Possible coupling/alignment issues

### Recommended maintenance

- Inspect shaft alignment
- Inspect coupling
- Check mounting condition
- Perform alignment correction

---

## 4. Severe Bearing Failure

### Typical indicators

- Very high vibration
- Rapid temperature increase
- Significant machine instability
- Possible RPM reduction
- High probability of machine failure

### Recommended action

- Stop or isolate equipment according to the applicable safety procedure
- Inspect bearing assembly
- Replace damaged components
- Verify alignment and lubrication before restart

---

## Engineering Interpretation

Increasing vibration combined with increasing temperature is a strong indicator that mechanical degradation may be developing.

The AI system should not make a maintenance decision from a single sensor reading alone. It should consider:

1. Current sensor values
2. Sensor trends
3. Machine condition
4. ML prediction
5. Historical fault information
6. Retrieved maintenance documentation
