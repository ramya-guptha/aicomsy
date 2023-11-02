# -*- coding: utf-8 -*-

from odoo import api, fields, models


class IncInvestigation(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.investigation"
    _description = "Investigation"

    # ---------------------------------------- CRUD METHODS ---------------------------------------

    @api.model
    def create(self, vals_list):
        vals_list['name'] = self.env['ir.sequence'].next_by_code("x.inc.investigation")
        incident_id = self.env.context.get('default_incident_id')
        vals_list['state'] = 'assigned'
        investigation = super().create(vals_list)
        # Change the state of the related incident
        if incident_id:
            incident = self.env['x.incident.record'].browse(incident_id)
            incident.write({'state': 'investigation_assigned'})
        return investigation

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(
        string="Investigation", readonly=True, default='New')
    incident_id = fields.Many2one("x.incident.record", string="Incident Id")
    description = fields.Html(related="incident_id.description")
    # description = fields.Html(related="incident_id.description")
    # Investigation Team Details
    hse_officer = fields.Many2one('res.users', string="HSE Officer", required=True)
    hse_officer_id = fields.Integer(related="hse_officer.id", string="ID Number")
    field_executive = fields.Many2one('hr.employee', string="Field Executive", required=True)
    field_executive_id = fields.Integer(related="field_executive.id", string="ID Number")
    hr_administration = fields.Many2one('hr.employee', string="HR / Administration", required=True)
    hr_administration_id = fields.Integer(related="hr_administration.id", string="ID Number")
    finance = fields.Many2one('hr.employee', string="Finance", required=True)
    finance_id = fields.Integer(related="finance.id", string="ID Number")
    investigation_team = fields.One2many("x.inc.investigation.team", "investigation_id",
                                         string="Investigation Team", required=True)

    # Investigation Details Tab
    investigation_details = fields.Text(string='Investigation Details')
    people_interviewed_ids = fields.One2many("x.inc.investigation.people.interview", "investigation_id",
                                             string="People Interviewed")
    # Consequences Tab
    consequences_ids = fields.One2many("x.inc.consequences", "investigation_id", string="Consequences")

    # Root Causes Tab
    root_causes_ids = fields.One2many("x.inc.root.causes", "investigation_id", string="Root Causes")

    # Corrective Actions Tab
    corrective_actions_ids = fields.One2many("x.inc.inv.corrective.actions", "investigation_id",
                                             string="Corrective Actions")

    # Related field to fetch attachments from corrective actions
    corrective_action_attachments = fields.One2many('ir.attachment', compute='_compute_corrective_action_attachments',
                                                    string='Related Attachments')

    # Actions Review & Closure Tab
    actions_review_ids = fields.One2many("x.inc.inv.action.review", "investigation_id", string="Action Review & Closure ")
    state = fields.Selection(
        selection=[
            ("assigned", "Assigned"),
            ("in_progress", "In Progress"),
            ("closed", "Closed"),
        ],
        string="Status",

        copy=False,

    )

    def start_investigation(self):
        self.write({'state': 'in_progress'})
        incident_id = self.incident_id
        incident_id.write({'state': 'investigation_in_progress'})

    # Computed field to gather attachments from corrective actions
    def _compute_corrective_action_attachments(self):
        for investigation in self:
            print("In for lopp>>>>>")
            print(investigation.corrective_actions_ids.ids)
            attachments = self.env['ir.attachment'].search([('res_model', '=', 'x.inc.inv.corrective.actions')])
            print(attachments)
            print(investigation.corrective_action_attachments)
            investigation.corrective_action_attachments = [(6, 0, attachments.ids)]
            print(investigation.corrective_action_attachments)


class InvestigationTeam(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = 'x.inc.investigation.team'
    _description = 'Investigation Team'

    # --------------------------------------- Fields Declaration ----------------------------------
    investigation_id = fields.Many2one('x.inc.investigation', 'Investigation Id', readonly=True)
    employee = fields.Many2one('hr.employee', string='Team Members')


class IncidentPeopleInterviewed(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = 'x.inc.investigation.people.interview'
    _description = 'People Interviewed for an incident'

    # --------------------------------------- Fields Declaration ----------------------------------
    investigation_id = fields.Many2one('x.inc.investigation', 'Investigation Id', readonly=True)
    employee = fields.Many2one('hr.employee', string='Employee Name')
    employee_id = fields.Integer(related="employee.id", string='ID Number')
    person_employer = fields.Char(string='If Contractor,Name of the Employer')
    # relation_to_incident = fields.Char(string='Relation to Incident')
    relation_to_incident = fields.Selection(string='Relation to Incident',
                                            selection=[('involved', "Involved"), ('affected', "Affected"),
                                                       ('others', 'Others'), ('witness', 'Witness')])
    details_of_interview = fields.Text(string='Details of Interview(If Required)')
    remarks = fields.Text(string='Remarks')
    person_category = fields.Many2one("x.inc.person.category", required="True")
    selected_category = fields.Char(compute='_compute_selected_category')
    person_name = fields.Char(string='Name', compute='_compute_name', store=True, readonly="True")
    visitor_name = fields.Char(string='Visitor Name')

    @api.depends('person_category', 'employee', 'visitor_name')
    def _compute_name(self):
        for person in self:
            if person.person_category.name in ("Employee", "Contractor") and person.employee:
                person.person_name = person.employee.name
                # person.nationality = person.employee.country_id
            elif person.person_category.name in ("Visitor", "Others") and person.visitor_name:
                person.person_name = person.visitor_name
            else:
                person.person_name = False

    @api.depends('person_category')
    def _compute_selected_category(self):
        for record in self:
            record.selected_category = record.person_category.name


class IncidentConsequences(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------
    _name = "x.inc.consequences"
    _description = "Consequences of Incidents"

    # --------------------------------------- Fields Declaration ----------------------------------
    actions_damages = fields.Many2one('x.inc.action.damage', string="Actions/ Damages", required=True)
    quantity = fields.Float(string="Quantity")
    unit = fields.Many2one('x.inc.unit', string="Units")
    unit_rate = fields.Float(string="Unit Rate")
    total_cost = fields.Float(string="Total Cost", compute='_compute_total_cost', store=True)
    impact = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], string="Impact")
    investigation_id = fields.Many2one("x.inc.investigation")

    @api.depends('quantity', 'unit_rate')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = record.quantity * record.unit_rate


class ActionDamage(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------
    _name = "x.inc.action.damage"
    _description = "Actions/Damages for Incidents"

    # --------------------------------------- Fields Declaration ----------------------------------
    name = fields.Char(string="Action/Damage")


class IncidentRootCauses(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.root.causes"
    _description = "Root Causes for an Incident"
    _sql_constraints = [
        ('primary_root_cause_id', 'unique(investigation_id, primary_root_cause_id)',
         'Primary Root Cause needs to be unique'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    investigation_id = fields.Many2one("x.inc.investigation")
    primary_root_cause_id = fields.Many2one('x.inc.primary.root.causes', required=True)
    secondary_root_cause_ids = fields.Many2many('x.inc.secondary.root.causes',
                                                domain="[('primary_root_causes_id', '=', primary_root_cause_id)]",
                                                required=True)
    comments = fields.Text(string="Comments")

    def corrective_action(self):
        existing_record = self.env['x.inc.inv.corrective.actions'].search([
            ('investigation_id', '=', self.investigation_id.id),
            ('primary_root_cause_id', '=', self.primary_root_cause_id.id)]
        )
        if existing_record:
            return {
                'name': 'Corrective Action',
                'res_model': 'x.inc.inv.corrective.actions',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_id': existing_record.id,
                'target': 'new',
            }
        else:
            return {
                'name': 'Corrective Action',
                'res_model': 'x.inc.inv.corrective.actions',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'view_id': self.env.ref('incident_management.corrective_action_form_view').id,
                'target': 'new',

                'context': {
                    'default_investigation_id': self.investigation_id.id,
                    'default_action_party': self.investigation_id.incident_id.location.location_manager.id,
                    'default_primary_root_cause_id': self.primary_root_cause_id.id,
                    'default_secondary_root_cause_ids': self.secondary_root_cause_ids.ids,
                    'default_state': 'new'
                },
            }


class IncidentPrimaryRootCauses(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.primary.root.causes"
    _description = "Primary Root Causes for an Incident"
    _sql_constraints = [
        ('name', 'unique(name)', 'Primary Root Cause needs to be unique'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char('Primary Root Causes', required=True)


class IncidentSecondaryRootCauses(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.secondary.root.causes"
    _description = "Secondary Root Causes for an Incident"
    _sql_constraints = [
        ('secondary_root_cause_uniq', 'unique(name, primary_root_causes_id)',
         'Secondary Root Cause needs to be unique'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------
    primary_root_causes_id = fields.Many2one("x.inc.primary.root.causes", string="Primary Root Cause")
    name = fields.Char('Secondary Root Causes', required=True)


class CorrectiveAction(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------
    _name = "x.inc.inv.corrective.actions"
    _description = "Corrective Actions"

    _sql_constraints = [
        ('corrective_action_uniq', 'unique(investigation_id, primary_root_cause_id)',
         'Corrective action already exists'),
    ]

    # ---------------------------------------- CRUD METHODS ---------------------------------------

    @api.model
    def create(self, vals_list):
        vals_list['name'] = self.env['ir.sequence'].next_by_code("x.inc.inv.corrective.actions")
        corrective_action = super().create(vals_list)
        # Call the send_email method
        corrective_action.action_send_email()
        return corrective_action

    # --------------------------------------- Fields Declaration ----------------------------------
    name = fields.Char(string="Corrective Action", default='New', readonly=True)
    investigation_id = fields.Many2one("x.inc.investigation")
    primary_root_cause_id = fields.Many2one('x.inc.primary.root.causes', required=True, readonly=True)
    secondary_root_cause_ids = fields.Many2many('x.inc.secondary.root.causes',
                                                domain="[('primary_root_causes_id', '=', primary_root_cause_id)]",
                                                required=True, readonly=True)
    action_type = fields.Many2one('x.inc.inv.ca.action.type', string="Action Type")
    hierarchy_of_control = fields.Many2one('x.inc.inv.ca.hierarchy.control', string="Hierarchy of Control")
    action_party = fields.Many2one('res.users', string="Action Party")
    target_date = fields.Date(string="Target Date of Completion")
    remarks = fields.Text(string="Remarks")
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string="Attachments")
    proposed_action = fields.Text(string="Proposed Action", required=True)
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("in_progress", "In Progress"),
            ("returned", "Returned"),
            ("completed", "Completed"),
        ],
        string="Status",
        copy=False,
    )

    def action_send_email(self):
        mail_template = self.env.ref('incident_management.email_template_corrective_action')
        mail_template.send_mail(self.id, force_send=True)

    def start_action(self):
        self.state = 'in_progress'

    def review_action(self):
        return {
            'name': 'Action Review & Closure',
            'res_model': 'x.inc.inv.action.review',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('incident_management.action_review_form_view').id,
            'target': 'new',
            'context': {
                'default_investigation_id': self.investigation_id.id,
                'default_corrective_action_id': self.id,
                'default_reviewer': self.investigation_id.hse_officer.id
            },

        }


class ActionType(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------
    _name = "x.inc.inv.ca.action.type"
    _description = "Action Types"

    # --------------------------------------- Fields Declaration ----------------------------------
    name = fields.Char(string="Action Type", required=True)


class HierarchyOfControl(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------
    _name = "x.inc.inv.ca.hierarchy.control"
    _description = "Hierarchy of Control"

    # --------------------------------------- Fields Declaration ----------------------------------
    name = fields.Char(string="Hierarchy of Control", required=True)
