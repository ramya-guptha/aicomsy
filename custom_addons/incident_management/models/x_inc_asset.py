# -*- coding: utf-8 -*-

# import from odoo
from odoo import api, fields, models


class IncidentAssetRecord(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.asset.record"
    _description = "Asset Damages"

    # --------------------------------------- Fields Declaration ----------------------------------

    incident_id = fields.Many2one('x.incident.record', required=True)
    asset_id = fields.Many2one("maintenance.equipment", string="Asset Title")
    asset_title = fields.Char(related="asset_id.name")
    asset_type = fields.Selection([('owned', 'Owned'), ('rental', 'Rental')])
    description = fields.Text(string="Description of the Damage")
    immediate_response = fields.Many2one("x.inc.asset.immediate.response")


class IncAssetImmediateResponse(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.asset.immediate.response"
    _description = "Immediate response"

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Immediate Response")
