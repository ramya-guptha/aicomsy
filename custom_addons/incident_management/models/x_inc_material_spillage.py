# -*- coding: utf-8 -*-

# import from odoo
from odoo import api, fields, models


class IncidentMaterialSpillageRecord(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.material.spill.record"
    _description = "Oil, Paint, Chemical Spillage, Environmental Incidents or  incidents"

    # --------------------------------------- Fields Declaration ----------------------------------

    incident_id = fields.Many2one('x.incident.record', required=True)
    material_type = fields.Text(string="Type of Material")
    # spill_rating =
    location = fields.Text(string="Location of Spill")
    quantity = fields.Text(string="Quantity Spilled")
    unit = fields.Many2one('x.inc.spill.unit')
    area = fields.Text(string="Area of Spill")
    area_unit = fields.Many2one('x.inc.spill.unit')
    description = fields.Text(string="Description of Spill")
    env_impact = fields.Many2one('x.inc.spill.env.impact')
    immediate_response = fields.Many2one("x.inc.material.spill.immediate.response")


class IncAssetImmediateResponse(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.material.spill.immediate.response"
    _description = "Immediate response"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Immediate response must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Immediate Response")


class IncSpillDamages(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.spill.env.impact"
    _description = "Environmental Impact"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Spill damages must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Environmental Impact")


class IncSpillUnit(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.spill.unit"
    _description = "Spill Unit"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'unit must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Spill Unit")
