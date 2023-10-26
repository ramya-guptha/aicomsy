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
        return super().create(vals_list)

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(
        string="Investigation", readonly=True, default='New')
    incident_id = fields.Many2one("x.incident.record", string="Incident Id")
    description = fields.Html(related="incident_id.description")
    # description = fields.Html(related="incident_id.description")
    # Investigation Team Details
    hse_officer = fields.Many2one('hr.employee', string="HSE Officer")
    hse_officer_id = fields.Integer(related="hse_officer.id", string="ID Number")
    field_executive = fields.Many2one('hr.employee', string="Field Executive")
    field_executive_id = fields.Integer(related="field_executive.id", string="ID Number")
    hr_administration = fields.Many2one('hr.employee', string="HR / Administration")
    hr_administration_id = fields.Integer(related="hr_administration.id", string="ID Number")
    finance = fields.Many2one('hr.employee', string="Finance")
    finance_id = fields.Integer(related="finance.id", string="ID Number")

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


class IncidentPeopleInterviewed(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = 'x.inc.investigation.people.interview'
    _description = 'People Interviewed for an incident'

    # --------------------------------------- Fields Declaration ----------------------------------
    investigation_id = fields.Many2one('x.inc.investigation', 'Investigation Id', readonly=True)
    # employer_name = fields.Char(string='Employer Name', required=True)
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
    actions_damages = fields.Many2one('x.inc.action.damage', string="Actions/ Damages")
    quantity = fields.Float(string="Quantity")
    unit = fields.Many2one('x.inc.unit', string="Units")
    unit_rate = fields.Float(string="Unit Rate")
    total_cost = fields.Float(string="Total Cost")
    impact = fields.Selection([('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], string="Impact")
    investigation_id = fields.Integer(string="Investigation ID")


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
        ('primary_root_cause_id', 'unique(primary_root_cause_id)', 'Primary Root Cause needs to be unique'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    investigation_id = fields.Many2one("x.inc.investigation")
    primary_root_cause_id = fields.Many2one('x.inc.primary.root.causes', required=True)
    secondary_root_cause_ids = fields.Many2many('x.inc.secondary.root.causes',
                                                domain="[('primary_root_causes_id', '=', primary_root_cause_id)]",
                                                required=True)


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

    # --------------------------------------- Fields Declaration ----------------------------------

    investigation_id = fields.Integer(string="Investigation ID")
    action_number = fields.Integer(string="Action")
    corrective_action = fields.Char(string="Corrective Action")
    root_cause = fields.Text(string="Root Cause")
    action_type = fields.Many2one('x.inc.inv.ca.action.type', string="Action Type")
    hierarchy_of_control = fields.Many2one('x.inc.inv.ca.hierarchy.control', string="Hierarchy of Control")
    action_party = fields.Many2one('hr.employee', string="Action Party")
    target_date = fields.Date(string="Target Date of Completion")
    action_status = fields.Char(string="Action Status")
    remarks = fields.Text(string="Remarks")


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
