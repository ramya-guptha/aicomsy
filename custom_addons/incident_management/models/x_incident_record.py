# -*- coding: utf-8 -*-

from odoo import api, fields, models


class IncidentRecord(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.incident.record"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "To Report Incidents"
    _order = "location"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Incident Id must be unique !'),
    ]

    # ---------------------------------------- CRUD METHODS ---------------------------------------

    @api.model
    def create(self, vals_list):
        vals_list['name'] = self.env['ir.sequence'].next_by_code("x.incident.record")
        vals_list['state'] = 'new'
        incident = super().create(vals_list)
        # Call the send_email method
        incident.action_send_email()
        return incident

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Incident Reference", default='New', readonly=True)
    inc_reported_date = fields.Date(string="Date Reported", default=lambda self: fields.Date.today(), required=True)
    inc_date_time = fields.Datetime(string="Date & Time", required=True, tracking=True)
    shift = fields.Many2one("x.inc.shift", required=True, tracking=True)
    type = fields.Many2many("x.inc.type", string="Type of Incident", required=True, tracking=True)
    location = fields.Many2one("x.location", string="Location of Incident", required=True, tracking=True)
    description = fields.Html(string="Description", required=True, tracking=True)
    notified_by = fields.Many2one('hr.employee', string="Notified By")
    notified_by_id = fields.Integer(related="notified_by.id", string="Notified By ID")
    notified_by_type = fields.Selection(related="notified_by.employee_type")
    severity = fields.Many2one("x.inc.severity", string="Severity Classification", required=False)

    incident_person_ids = fields.One2many(
        'x.inc.person.record', 'incident_id', string='People'
    )

    incident_asset_ids = fields.One2many(
        'x.inc.asset.record', 'incident_id', string='Asset Damages'
    )
    incident_spill_ids = fields.One2many(
        'x.inc.material.spill.record', 'incident_id', string='Material Spill'
    )
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("investigation_assigned", "Assigned"),
            ("investigation_in_progress", "In Progress"),
            ("action_review", "Action Review"),
            ("closed", "Inc Closed"),
            ("canceled", "Canceled"),
        ],
        string="Status",

        copy=False,

    )

    def action_send_email(self):
        mail_template = self.env.ref('incident_management.email_template_incident')
        mail_template.send_mail(self.id, force_send=True)

    def assign_team(self):
        return {
            'name': 'Investigation Team',
            'res_model': 'x.inc.investigation',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('incident_management.inc_investigation_view_form').id,

            'context': {
                'default_incident_id': self.id,
            }

        }

    def save(self):
        return True


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


class IncSeverity(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.severity"
    _description = "Severity Classification"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Severities must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Severity Classification")
    notification_ids = fields.One2many('x.inc.notification', 'severity', string='Notification Team')


class NotificationTeam(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = 'x.inc.notification'
    _description = 'Notification Team'

    # --------------------------------------- Fields Declaration ----------------------------------
    name = fields.Char(string='Employee Name', related='officer_id.name', readonly=True)
    severity = fields.Many2one("x.inc.severity", string="Severity Classification", required=True)
    officer_id = fields.Many2one('hr.employee', string="Officer", required=True)
