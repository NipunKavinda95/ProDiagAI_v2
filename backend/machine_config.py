"""
ProDiag AI V2
Factory Machine Configuration

Single source of truth for the industrial asset fleet.
"""

MACHINES = [
    # =========================================================
    # PRODUCTION LINE A — MIXING & PROCESSING
    # =========================================================

    {
        "machine_id": "MTR-01",
        "machine_name": "Mixer Drive Motor",
        "machine_type": "Electric Motor",
        "department": "Production",
        "production_line": "Production Line A",
        "area": "Mixing",
        "location": "Line A - Mixing Station 01",
        "manufacturer": "ABB",
        "model": "M3BP 160",
        "criticality": "HIGH",
        "production_impact": "HIGH",
        "operating_hours": 12480,
        "fault_type": "bearing_wear",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (35, 50),
            "vibration_mm_s": (0.5, 1.8),
            "current_a": (12, 18),
            "rpm": (1450, 1500),
        },
    },

    {
        "machine_id": "PMP-02",
        "machine_name": "Cooling Water Pump",
        "machine_type": "Centrifugal Pump",
        "department": "Utilities",
        "production_line": "Production Line A",
        "area": "Cooling",
        "location": "Utilities - Cooling Station 01",
        "manufacturer": "Grundfos",
        "model": "NB 50-125",
        "criticality": "HIGH",
        "production_impact": "HIGH",
        "operating_hours": 9850,
        "fault_type": "cavitation",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (30, 45),
            "vibration_mm_s": (0.4, 1.5),
            "current_a": (9, 15),
            "rpm": (1400, 1500),
        },
    },

    {
        "machine_id": "MTR-07",
        "machine_name": "Process Drive Motor",
        "machine_type": "Electric Motor",
        "department": "Production",
        "production_line": "Production Line A",
        "area": "Processing",
        "location": "Line A - Processing Station 02",
        "manufacturer": "Siemens",
        "model": "SIMOTICS GP",
        "criticality": "MEDIUM",
        "production_impact": "MEDIUM",
        "operating_hours": 8750,
        "fault_type": "bearing_wear",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (35, 50),
            "vibration_mm_s": (0.5, 1.8),
            "current_a": (10, 17),
            "rpm": (1400, 1500),
        },
    },

    {
        "machine_id": "GBX-08",
        "machine_name": "Mixer Gearbox",
        "machine_type": "Gearbox",
        "department": "Production",
        "production_line": "Production Line A",
        "area": "Mixing",
        "location": "Line A - Mixer Drive",
        "manufacturer": "SEW-Eurodrive",
        "model": "R87",
        "criticality": "HIGH",
        "production_impact": "HIGH",
        "operating_hours": 11200,
        "fault_type": "gear_wear",
        "sensors": ["temperature", "vibration", "rpm"],
        "normal_range": {
            "temperature_c": (40, 55),
            "vibration_mm_s": (0.8, 2.0),
            "rpm": (900, 1000),
        },
    },

    {
        "machine_id": "FAN-09",
        "machine_name": "Process Extraction Fan",
        "machine_type": "Industrial Fan",
        "department": "Utilities",
        "production_line": "Production Line A",
        "area": "Ventilation",
        "location": "Line A - Extraction System",
        "manufacturer": "FläktGroup",
        "model": "eQ Prime",
        "criticality": "MEDIUM",
        "production_impact": "MEDIUM",
        "operating_hours": 7650,
        "fault_type": "fan_imbalance",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (30, 48),
            "vibration_mm_s": (0.5, 1.8),
            "current_a": (8, 14),
            "rpm": (1400, 1500),
        },
    },

    # =========================================================
    # PRODUCTION LINE B — PACKAGING
    # =========================================================

    {
        "machine_id": "CNV-04",
        "machine_name": "Packaging Conveyor",
        "machine_type": "Conveyor",
        "department": "Production",
        "production_line": "Production Line B",
        "area": "Packaging",
        "location": "Line B - Packaging Conveyor 01",
        "manufacturer": "Dorner",
        "model": "2200 Series",
        "criticality": "HIGH",
        "production_impact": "HIGH",
        "operating_hours": 14300,
        "fault_type": "belt_misalignment",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (30, 45),
            "vibration_mm_s": (0.4, 1.5),
            "current_a": (7, 12),
            "rpm": (880, 950),
        },
    },

    {
        "machine_id": "MTR-10",
        "machine_name": "Packaging Drive Motor",
        "machine_type": "Electric Motor",
        "department": "Production",
        "production_line": "Production Line B",
        "area": "Packaging",
        "location": "Line B - Packaging Drive",
        "manufacturer": "ABB",
        "model": "M2BAX 132",
        "criticality": "HIGH",
        "production_impact": "HIGH",
        "operating_hours": 10600,
        "fault_type": "bearing_wear",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (35, 50),
            "vibration_mm_s": (0.5, 1.8),
            "current_a": (10, 17),
            "rpm": (1400, 1500),
        },
    },

    {
        "machine_id": "GBX-11",
        "machine_name": "Packaging Gearbox",
        "machine_type": "Gearbox",
        "department": "Production",
        "production_line": "Production Line B",
        "area": "Packaging",
        "location": "Line B - Packaging Drive",
        "manufacturer": "Bonfiglioli",
        "model": "VF 86",
        "criticality": "HIGH",
        "production_impact": "HIGH",
        "operating_hours": 9200,
        "fault_type": "gear_wear",
        "sensors": ["temperature", "vibration", "rpm"],
        "normal_range": {
            "temperature_c": (40, 55),
            "vibration_mm_s": (0.8, 2.0),
            "rpm": (850, 950),
        },
    },

    {
        "machine_id": "CNV-12",
        "machine_name": "Product Transfer Conveyor",
        "machine_type": "Conveyor",
        "department": "Production",
        "production_line": "Production Line B",
        "area": "Material Transfer",
        "location": "Line B - Transfer Station",
        "manufacturer": "FlexLink",
        "model": "X85",
        "criticality": "MEDIUM",
        "production_impact": "MEDIUM",
        "operating_hours": 6800,
        "fault_type": "belt_misalignment",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (30, 45),
            "vibration_mm_s": (0.4, 1.5),
            "current_a": (6, 11),
            "rpm": (850, 950),
        },
    },

    # =========================================================
    # UTILITIES — COMPRESSED AIR
    # =========================================================

    {
        "machine_id": "CMP-03",
        "machine_name": "Air Compressor",
        "machine_type": "Air Compressor",
        "department": "Utilities",
        "production_line": "Compressed Air System",
        "area": "Compressor Room",
        "location": "Utilities - Compressor Room 01",
        "manufacturer": "Atlas Copco",
        "model": "GA 75",
        "criticality": "CRITICAL",
        "production_impact": "CRITICAL",
        "operating_hours": 15750,
        "fault_type": "overload",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (45, 60),
            "vibration_mm_s": (0.8, 2.0),
            "current_a": (15, 19),
            "rpm": (2850, 3000),
        },
    },

    {
        "machine_id": "CMP-13",
        "machine_name": "Backup Air Compressor",
        "machine_type": "Air Compressor",
        "department": "Utilities",
        "production_line": "Compressed Air System",
        "area": "Compressor Room",
        "location": "Utilities - Compressor Room 02",
        "manufacturer": "Kaeser",
        "model": "CSD 85",
        "criticality": "HIGH",
        "production_impact": "HIGH",
        "operating_hours": 11300,
        "fault_type": "overload",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (45, 60),
            "vibration_mm_s": (0.8, 2.0),
            "current_a": (15, 20),
            "rpm": (2850, 3000),
        },
    },

    # =========================================================
    # UTILITIES — COOLING & VENTILATION
    # =========================================================

    {
        "machine_id": "FAN-05",
        "machine_name": "Extraction Fan",
        "machine_type": "Industrial Fan",
        "department": "Utilities",
        "production_line": "Ventilation System",
        "area": "Extraction",
        "location": "Utilities - Extraction Unit 01",
        "manufacturer": "Howden",
        "model": "WRV",
        "criticality": "MEDIUM",
        "production_impact": "MEDIUM",
        "operating_hours": 11800,
        "fault_type": "fan_imbalance",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (30, 48),
            "vibration_mm_s": (0.5, 1.8),
            "current_a": (8, 14),
            "rpm": (1400, 1500),
        },
    },

    {
        "machine_id": "FAN-14",
        "machine_name": "Cooling Tower Fan",
        "machine_type": "Cooling Fan",
        "department": "Utilities",
        "production_line": "Cooling System",
        "area": "Cooling Tower",
        "location": "Utilities - Cooling Tower 01",
        "manufacturer": "Baltimore Aircoil",
        "model": "VXI",
        "criticality": "HIGH",
        "production_impact": "HIGH",
        "operating_hours": 13400,
        "fault_type": "fan_imbalance",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (30, 50),
            "vibration_mm_s": (0.5, 1.8),
            "current_a": (10, 17),
            "rpm": (900, 1000),
        },
    },

    {
        "machine_id": "PMP-15",
        "machine_name": "Cooling Circulation Pump",
        "machine_type": "Centrifugal Pump",
        "department": "Utilities",
        "production_line": "Cooling System",
        "area": "Cooling",
        "location": "Utilities - Cooling Station 02",
        "manufacturer": "KSB",
        "model": "Etanorm",
        "criticality": "HIGH",
        "production_impact": "HIGH",
        "operating_hours": 10100,
        "fault_type": "cavitation",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (30, 45),
            "vibration_mm_s": (0.4, 1.5),
            "current_a": (9, 15),
            "rpm": (1400, 1500),
        },
    },

    # =========================================================
    # MATERIAL HANDLING
    # =========================================================

    {
        "machine_id": "GBX-06",
        "machine_name": "Conveyor Gearbox",
        "machine_type": "Gearbox",
        "department": "Material Handling",
        "production_line": "Material Handling",
        "area": "Main Conveyor",
        "location": "Material Handling - Conveyor 01",
        "manufacturer": "SEW-Eurodrive",
        "model": "K97",
        "criticality": "HIGH",
        "production_impact": "HIGH",
        "operating_hours": 12900,
        "fault_type": "gear_wear",
        "sensors": ["temperature", "vibration", "rpm"],
        "normal_range": {
            "temperature_c": (40, 55),
            "vibration_mm_s": (0.8, 2.0),
            "rpm": (900, 1000),
        },
    },

    {
        "machine_id": "CNV-16",
        "machine_name": "Raw Material Conveyor",
        "machine_type": "Conveyor",
        "department": "Material Handling",
        "production_line": "Material Handling",
        "area": "Raw Material",
        "location": "Material Handling - Intake",
        "manufacturer": "Dorner",
        "model": "3200 Series",
        "criticality": "MEDIUM",
        "production_impact": "MEDIUM",
        "operating_hours": 7200,
        "fault_type": "belt_misalignment",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (30, 45),
            "vibration_mm_s": (0.4, 1.5),
            "current_a": (7, 12),
            "rpm": (850, 950),
        },
    },

    {
        "machine_id": "MTR-17",
        "machine_name": "Material Handling Motor",
        "machine_type": "Electric Motor",
        "department": "Material Handling",
        "production_line": "Material Handling",
        "area": "Raw Material",
        "location": "Material Handling - Intake Drive",
        "manufacturer": "Siemens",
        "model": "SIMOTICS SD",
        "criticality": "MEDIUM",
        "production_impact": "MEDIUM",
        "operating_hours": 8450,
        "fault_type": "bearing_wear",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (35, 50),
            "vibration_mm_s": (0.5, 1.8),
            "current_a": (10, 17),
            "rpm": (1400, 1500),
        },
    },

    # =========================================================
    # PRODUCTION LINE C — PROCESSING / FINISHING
    # =========================================================

    {
        "machine_id": "MTR-18",
        "machine_name": "Finishing Line Motor",
        "machine_type": "Electric Motor",
        "department": "Production",
        "production_line": "Production Line C",
        "area": "Finishing",
        "location": "Line C - Finishing Station",
        "manufacturer": "ABB",
        "model": "M3BP 180",
        "criticality": "HIGH",
        "production_impact": "HIGH",
        "operating_hours": 9700,
        "fault_type": "bearing_wear",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (35, 50),
            "vibration_mm_s": (0.5, 1.8),
            "current_a": (13, 19),
            "rpm": (1450, 1500),
        },
    },

    {
        "machine_id": "PMP-19",
        "machine_name": "Process Transfer Pump",
        "machine_type": "Centrifugal Pump",
        "department": "Production",
        "production_line": "Production Line C",
        "area": "Process Transfer",
        "location": "Line C - Transfer Station",
        "manufacturer": "Grundfos",
        "model": "CR 45",
        "criticality": "HIGH",
        "production_impact": "HIGH",
        "operating_hours": 8900,
        "fault_type": "cavitation",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (30, 45),
            "vibration_mm_s": (0.4, 1.5),
            "current_a": (9, 15),
            "rpm": (1400, 1500),
        },
    },

    {
        "machine_id": "FAN-20",
        "machine_name": "Finishing Ventilation Fan",
        "machine_type": "Industrial Fan",
        "department": "Utilities",
        "production_line": "Production Line C",
        "area": "Ventilation",
        "location": "Line C - Finishing Ventilation",
        "manufacturer": "FläktGroup",
        "model": "eQ",
        "criticality": "MEDIUM",
        "production_impact": "MEDIUM",
        "operating_hours": 6300,
        "fault_type": "fan_imbalance",
        "sensors": ["temperature", "vibration", "current", "rpm"],
        "normal_range": {
            "temperature_c": (30, 48),
            "vibration_mm_s": (0.5, 1.8),
            "current_a": (8, 14),
            "rpm": (1400, 1500),
        },
    },
]


def get_machine(machine_id):
    """Return a machine configuration by ID."""
    for machine in MACHINES:
        if machine["machine_id"] == machine_id:
            return machine

    return None


def get_all_machines():
    """Return all configured machines."""
    return MACHINES


def get_machines_by_department(department):
    """Return machines belonging to a department."""
    return [
        machine
        for machine in MACHINES
        if machine["department"] == department
    ]


def get_machines_by_line(production_line):
    """Return machines belonging to a production line."""
    return [
        machine
        for machine in MACHINES
        if machine["production_line"] == production_line
    ]


def get_machines_by_type(machine_type):
    """Return machines of a specific type."""
    return [
        machine
        for machine in MACHINES
        if machine["machine_type"] == machine_type
    ]