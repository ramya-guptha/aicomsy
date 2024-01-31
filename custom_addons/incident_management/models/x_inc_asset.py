# -*- coding: utf-8 -*-

# import from odoo
from odoo import api, fields, models


class IncidentAssetRecord(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.asset.record"
    _description = "Asset Damages"

    # --------------------------------------- Fields Declaration ----------------------------------

    incident_id = fields.Many2one('x.incident.record', required=True)
    asset_category = fields.Selection([('equipment', 'Equipment'), ('others', 'Others')], string="Asset Category",
                                      help='Asset Category')
    asset_id = fields.Many2one("maintenance.equipment", string="Asset Title")
    asset_title = fields.Char(related="asset_id.name")
    asset_type = fields.Selection([('owned', 'Owned'), ('rental', 'Rental')], help='Asset Type')
    description = fields.Text(string="Description of the Damage", help='Description of the Damage')
    immediate_response = fields.Many2one("x.inc.asset.immediate.response", help='Immediate Response')
    others_asset_category = fields.Char(string="Others")
    asset_name = fields.Char(string="Asset Name", compute="_compute_asset_name", store=True, help='Asset Name')

    @api.depends('asset_id', 'others_asset_category', 'asset_category')
    def _compute_asset_name(self):
        for record in self:
            if record.asset_category == 'equipment' and record.asset_id:
                record.asset_name = record.asset_id.name
            elif record.asset_category == 'others':
                record.asset_name = record.others_asset_category
            else:
                record.asset_name = False


class IncAssetImmediateResponse(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.asset.immediate.response"
    _description = "Immediate response"

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Immediate Response")
