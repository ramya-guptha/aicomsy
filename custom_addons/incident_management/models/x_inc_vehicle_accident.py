# -*- coding: utf-8 -*-

# import from odoo
from odoo import api, fields, models


class IncidentMotorVehicleAccidentRecord(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.mva.record"
    _description = "Motor Vehicle Accidents"

    # --------------------------------------- Fields Declaration ----------------------------------

    incident_id = fields.Many2one('x.incident.record', required=True)
    location = fields.Text(string="Location of MVA")
    mva_classification = fields.Text(string="MVA Classification")
    damage = fields.Many2one("x.inc.mva.damage")
    description = fields.Text(string="Description")
    immediate_action = fields.Many2one("x.inc.mva.immediate.action")


class IncMVAImmediateAction(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.mva.immediate.action"
    _description = "Immediate Action"

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Immediate Action")


class IncMVAClassification(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.mva.classification"
    _description = "MVA Classification"

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Classification")


class IncMVADamage(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.mva.damage"
    _description = "MVA Damage"

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Damage")
