# Preventive Maintenance Standard Operating Procedure

## Purpose

This simulated SOP provides a general maintenance workflow for industrial
rotating equipment monitored by ProDiag AI V2.

It is intended as a decision-support reference and does not replace
site-specific safety procedures or authorized OEM documentation.

---

## SOP-001 — Routine Machine Inspection

### Before Inspection

1. Review current machine condition.
2. Review active alerts.
3. Review recent vibration, temperature, current and RPM trends.
4. Confirm machine identification.
5. Follow applicable site safety procedures.

### Inspection

Check:

- Bearing condition
- Lubrication condition
- Shaft and coupling alignment
- Belt condition and alignment
- Gearbox condition
- Cooling system
- Electrical connections
- Abnormal noise
- Abnormal vibration
- Temperature condition

### After Inspection

Record:

- Observed condition
- Fault identified
- Corrective action
- Parts used
- Maintenance date
- Technician/team
- Machine operating condition after maintenance

---

## SOP-002 — Warning Condition

### Trigger

Machine condition reaches WARNING.

### Recommended Action

1. Review sensor trends.
2. Review active alerts.
3. Identify probable fault.
4. Inspect the machine during the next appropriate maintenance window.
5. Increase monitoring frequency if required.
6. Record inspection results.

---

## SOP-003 — Critical Condition

### Trigger

Machine condition reaches CRITICAL.

### Recommended Action

1. Notify responsible maintenance personnel.
2. Review ML failure probability.
3. Review anomaly evidence.
4. Identify probable fault.
5. Assess production impact.
6. Determine whether planned intervention is possible.
7. Create a maintenance work order after engineering review.

---

## SOP-004 — Faulted Machine

### Trigger

Machine condition reaches FAULTED.

### Recommended Action

1. Follow applicable equipment isolation and safety procedures.
2. Confirm the machine has stopped.
3. Review fault history.
4. Perform physical inspection.
5. Identify failed component.
6. Perform approved repair.
7. Verify machine condition before restart.
8. Record maintenance outcome.

---

## SOP-005 — Post-Maintenance Restart

### Before Restart

Verify:

- Maintenance work is complete
- Guards and covers are correctly installed
- Tools and foreign objects are removed
- Lubrication is correct
- Connections are secure
- Alignment is acceptable
- Safety requirements are satisfied

### Restart

1. Start the machine according to the applicable operating procedure.
2. Monitor vibration.
3. Monitor temperature.
4. Monitor current.
5. Monitor RPM.
6. Confirm stable operation.

### Completion

Return machine to normal monitoring when stable.

---

## AI Safety Boundary

ProDiag AI provides recommendations and decision support.

The AI must not independently:

- Bypass safety procedures
- Override machine protection systems
- Authorize hazardous work
- Command physical equipment without approved controls
- Confirm a repair without human verification

Final maintenance decisions remain with qualified personnel.
