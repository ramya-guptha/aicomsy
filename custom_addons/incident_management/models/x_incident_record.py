# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError

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
        # Check if inc_reported_date is prior to inc_date_time
        if 'inc_reported_date' in vals_list and 'inc_date_time' in vals_list:
            reported_date = fields.Date.from_string(vals_list['inc_reported_date'])
            date_time = fields.Datetime.from_string(vals_list['inc_date_time'])
            if reported_date < date_time.date():
                raise ValidationError("Date Reported cannot be prior to Incident Date & Time")
            if reported_date > fields.Date.today():
                raise ValidationError("Date Reported cannot be greater than today's date")

        vals_list['name'] = self.env['ir.sequence'].next_by_code("x.incident.record")
        vals_list['state'] = 'new'
        incident = super().create(vals_list)
        # Call the send_email method
        incident.action_send_email()
        incident.create_activity('Review & Approve', 'To Do', incident.location.location_manager.id, self.due_date)
        return incident

    def write(self, vals_list):
        # Check if inc_reported_date is prior to inc_date_time
        reported_date = fields.Date.from_string(vals_list.get('inc_reported_date', self.inc_reported_date))
        date_time = fields.Datetime.from_string(vals_list.get('inc_date_time', self.inc_date_time))
        if reported_date < date_time.date():
            raise ValidationError("Date Reported cannot be prior to Incident Date & Time")
        if reported_date > fields.Date.today():
            raise ValidationError("Date Reported cannot be greater than today's date")

        return super().write(vals_list)

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Incident Reference", default='New', readonly=True)
    inc_reported_date = fields.Date(string="Date Reported", default=lambda self: fields.Date.today(), required=True)
    inc_date_time = fields.Datetime(string="Incident Date & Time", required=True, tracking=True)
    shift = fields.Many2one("x.inc.shift", required=True, tracking=True)
    type = fields.Many2many("x.inc.type", string="Type of Incident", required=True, tracking=True)
    location = fields.Many2one("x.location", string="Location of Incident", required=True, tracking=True)
    description = fields.Html(string="Description", required=True, tracking=True)
    notified_by = fields.Many2one('hr.employee', string="Notified By", domain="[('company_id', '=', company_id)]")
    notified_by_id = fields.Integer(related="notified_by.id", string="Notified By ID")
    notified_by_type = fields.Selection(related="notified_by.employee_type")
    severity = fields.Many2one("x.inc.severity", string="Severity Classification", required=False)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
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
            ("reviewed", "Reviewed"),
            ("investigation_assigned", "Assigned"),
            ("investigation_in_progress", "In Progress"),
            ("action_review", "Action Review"),
            ("closed", "Inc Closed"),
            ("canceled", "Canceled"),
        ],
        string="Status",

        copy=False,

    )
    due_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')

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

    def review_approve(self):
        self.state = "reviewed"
        self.mark_activity_as_done("Review & Approve")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': 'The Incident is forwarded to HSE Manager for further Action',
                'sticky': True,
                'next': {'type': 'ir.actions.client',
                         'tag': 'soft_reload', },
            }
        }

    def create_activity(self, summary, activity_type, user_id, date_deadline=None):
        activity_type_id = self.env['mail.activity.type'].search([('name', '=', activity_type)], limit=1).id
        if not activity_type_id:
            # Handle the case where 'To Do' activity type is not found
            return
        else:
            # Create a new activity
            activity = self.env['mail.activity'].create({
                'activity_type_id': activity_type_id,
                'summary': summary,
                'date_deadline': date_deadline,
                'res_model_id': self.env['ir.model']._get('x.incident.record').id,
                'res_id': self.id,
                'user_id': user_id,

            })

            return activity

    def mark_activity_as_done(self, summary):

        domain = [
            ('res_name', '=', self.name),
            ('user_id', '=', self.env.user.id),
            ('summary', '=', summary),
        ]

        activity = self.env['mail.activity'].search(domain, limit=1)

        if activity:
            # Mark the activity as done
            activity.action_feedback()


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
