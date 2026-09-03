"""
ProDiag AI V2
Machine API

Provides machine configuration and fleet-level machine information.
"""

from flask import Blueprint, jsonify

from machine_config import (
    MACHINES,
    get_machine,
    get_machines_by_department,
    get_machines_by_line,
    get_machines_by_type,
)


machines_bp = Blueprint(
    "machines",
    __name__,
    url_prefix="/api/machines",
)


# ============================================================
# GET ALL MACHINES
# ============================================================

@machines_bp.route("", methods=["GET"])
def get_all_machines():
    """
    Return the complete industrial asset fleet.
    """

    return jsonify({
        "count": len(MACHINES),
        "machines": MACHINES,
    })


# ============================================================
# GET SINGLE MACHINE
# ============================================================

@machines_bp.route("/<machine_id>", methods=["GET"])
def get_single_machine(machine_id):
    """
    Return configuration for one machine.
    """

    machine = get_machine(machine_id)

    if machine is None:
        return jsonify({
            "error": "Machine not found",
            "machine_id": machine_id,
        }), 404

    return jsonify(machine)


# ============================================================
# GET MACHINES BY DEPARTMENT
# ============================================================

@machines_bp.route("/department/<department>", methods=["GET"])
def get_by_department(department):
    """
    Return machines belonging to a department.
    """

    machines = get_machines_by_department(
        department
    )

    return jsonify({
        "department": department,
        "count": len(machines),
        "machines": machines,
    })


# ============================================================
# GET MACHINES BY PRODUCTION LINE
# ============================================================

@machines_bp.route("/line/<path:production_line>", methods=["GET"])
def get_by_line(production_line):
    """
    Return machines belonging to a production line.
    """

    machines = get_machines_by_line(
        production_line
    )

    return jsonify({
        "production_line": production_line,
        "count": len(machines),
        "machines": machines,
    })


# ============================================================
# GET MACHINES BY TYPE
# ============================================================

@machines_bp.route("/type/<path:machine_type>", methods=["GET"])
def get_by_type(machine_type):
    """
    Return machines of a specific machine type.
    """

    machines = get_machines_by_type(
        machine_type
    )

    return jsonify({
        "machine_type": machine_type,
        "count": len(machines),
        "machines": machines,
    })