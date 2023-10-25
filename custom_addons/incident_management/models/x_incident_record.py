# -*- coding: utf-8 -*-

from odoo import api, fields, models


class IncidentRecord(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.incident.record"
    _description = "To Report Incidents"
    _order = "location"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Incident Id must be unique !'),
    ]

    # ---------------------------------------- CRUD METHODS ---------------------------------------

    @api.model
    def create(self, vals_list):
        vals_list['name'] = self.env['ir.sequence'].next_by_code("x.incident.record")
        incident = super().create(vals_list)
        # Call the send_email method
        incident.action_send_email()
        return incident

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Incident Reference", default='New')
    inc_reported_date = fields.Date(string="Date Reported", default=lambda self: fields.Date.today())
    inc_date_time = fields.Datetime(string="Date & Time")
    shift = fields.Many2one("x.inc.shift")
    type = fields.Many2many("x.inc.type", string="Type of Incident")
    location = fields.Many2one("x.location", string="Location of Incident")
    description = fields.Html(string="Description")
    notified_by = fields.Many2one('res.users', string="Notified By", default=lambda self: self.env.user)
    notified_by_id = fields.Integer(related="notified_by.id", string="Notified By ID")
    notified_by_type = fields.Selection(related="notified_by.employee_type")

    incident_person_ids = fields.One2many(
        'x.inc.person.record', 'incident_id', string='Person Involved/ Injured'
    )

    incident_asset_ids = fields.One2many(
        'x.inc.asset.record', 'incident_id', string='Asset Damages'
    )
    incident_spill_ids = fields.One2many(
        'x.inc.material.spill.record', 'incident_id', string='Material Spill'
    )
    incident_mva_ids = fields.One2many(
        'x.inc.mva.record', 'incident_id', string='Motor Vehicle Accidents'
    )

    def action_send_email(self):
        mail_template = self.env.ref('incident_management.email_template_incident')
        mail_template.send_mail(self.id, force_send=True)


class IncidentType(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.type"
    _description = "Incident Type"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Incident type must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char("Incident Type", required="True")


class IncidentShift(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.shift"
    _description = "Working Shift"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Shift must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char("Shift", required="True")
