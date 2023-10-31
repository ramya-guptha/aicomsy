# -*- coding: utf-8 -*-

# import from odoo
from odoo import fields, models


class IncidentMaterialSpillageRecord(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.material.spill.record"
    _description = "Oil, Paint, Chemical Spillage, Environmental Incidents or  incidents"

    # --------------------------------------- Fields Declaration ----------------------------------

    incident_id = fields.Many2one('x.incident.record', required=True)
    person_reported = fields.Many2one("hr.employee", string="person_reported", required=True)
    id_number = fields.Integer(related="person_reported.id", string="ID Number")
    task = fields.Text(string="Task being done at the time of incident")
    job_title = fields.Char(related='person_reported.job_id.name', string="Job Title")
    location = fields.Many2one("x.location", string="Incident Location")
    env_incident_classification = fields.Many2one("x.inc.env.classification", string="ENV Incident Classification")
    qty = fields.Integer(string="QTY of Emission / Spill/ Spoilage")
    unit = fields.Many2one("x.inc.unit", string="Unit")
    env_impact = fields.Many2one('x.inc.spill.env.impact')
    immediate_response = fields.Many2one("x.inc.material.spill.immediate.response")
    env_severity_classification = fields.Many2one("x.inc.env.severity.classification",
                                                  string="Severity Classification (ENV)", required=True)
    env_severity_consequence = fields.Many2one("x.inc.env.severity.consequence",
                                               string="Severity Consequence (ENV)", required=True)


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


class ENVSeverityClassification(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.env.severity.classification"
    _description = "ENV Severity classification"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'ENV Severity classification must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Severity Classification (ENV)")


class IncENVSeverityConsequence(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.env.severity.consequence"
    _description = "ENV Severity Consequence"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'ENV Severity Consequence must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Severity Consequence(ENV)")
