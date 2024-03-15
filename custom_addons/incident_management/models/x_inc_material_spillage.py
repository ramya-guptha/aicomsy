# -*- coding: utf-8 -*-

# import from odoo
from odoo import fields, models


class IncidentMaterialSpillageRecord(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.material.spill.record"
    _description = "Oil, Paint, Chemical Spillage, Environmental Incidents or  incidents"

    # --------------------------------------- Fields Declaration ----------------------------------
    incident_id = fields.Many2one('x.incident.record', required=True)
    env_incident_classification_id = fields.Many2one("x.inc.env.classification", string="ENV Incident Classification", help='ENV Incident Classification')
    qty = fields.Integer(string="QTY of Emission / Spill/ Spoilage")
    unit_id = fields.Many2one("x.inc.unit", string="Unit", help='Unit')
    env_impact_id = fields.Many2one('x.inc.spill.env.impact', help='Environmental Impact')
    immediate_response_id = fields.Many2one("x.inc.material.spill.immediate.response", help='Immediate Response')
    env_severity_consequence_id = fields.Many2one("x.inc.env.severity.consequence",
                                               string="Severity Consequence", required=True, help='Severity Consequence')


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


class IncEnvClassification(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.env.classification"
    _description = "Environmental Classification"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Environmental Classification must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Environmental Classification")


class Unit(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------
    _name = "x.inc.unit"
    _description = "Units for Incidents"

    # --------------------------------------- Fields Declaration ----------------------------------
    name = fields.Char(string="Unit")

class IncENVSeverityConsequence(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.env.severity.consequence"
    _description = "ENV Severity Consequence"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'ENV Severity Consequence must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Severity Consequence(ENV)")
