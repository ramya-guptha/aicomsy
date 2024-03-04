# -*- coding: utf-8 -*-

from odoo import api, fields, models


class IncidentRecord(models.Model):
    _inherit = 'x.incident.record'


    @api.model
    def create(self, vals_list):
        incident = super().create(vals_list)
        return incident

    # ----------------------------------------------------------
    # Fields
    # ----------------------------------------------------------

    legal_compliance_id = fields.Many2one("x.legal.compliance", "Legal Compliance Id")
