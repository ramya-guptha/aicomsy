# -*- coding: utf-8 -*-

# import from odoo
from odoo import api, fields, models

from datetime import datetime


class IncidentPersonRecord(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.person.record"
    _description = "Persons involved or victims in an Incident"
    _sql_constraints = [
        ('name_incident_uniq', 'unique(person_name, incident_id)', 'Person name must be unique per incident !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    incident_id = fields.Many2one('x.incident.record', required=True)
    person_category = fields.Many2one("x.inc.person.category", required=True)
    selected_category = fields.Char(compute='_compute_selected_category')
    person_name = fields.Char(string='Name', compute='_compute_name', store=True, readonly=True)
    employee = fields.Many2one('hr.employee', string='Employee Name')
    employee_id = fields.Integer(related="employee.id", string='Employee ID')
    visitor_name = fields.Char(string='Visitor Name')
    nationality = fields.Many2one('res.country', "Nationality")
    age = fields.Integer(string="Age", compute="_compute_age")
    # experience = fields.Integer(string="Experience", related="employee.experience")
    job_title = fields.Char(related='employee.job_id.name', string="Job Title")
    involved_victim = fields.Selection(
        string="Involved/ Victim",
        selection=[('involved', "Involved"), ('victim', "Victim"), ('both', 'Both')], required=True)
    person_task = fields.Text(string="Task being done at the time of incident")
    person_employer = fields.Char(string="Employer")
    incident_injured_body_parts = fields.Many2many("x.inc.injured.body.parts", string="Injured Body Part")
    incident_type_of_illness = fields.Many2many("x.inc.injury.type", string="Nature of Injury")
    visited_hospital = fields.Char(string="Name of the Hospital Visited")
    person_days_off = fields.Integer(string="Days Off")
    is_visitor = fields.Boolean(string='Is Visitor', compute='_compute_is_visitor')
    immediate_response = fields.Many2one('x.inc.person.immediate.response', string="Immediate Response")
    oh_incident_classification = fields.Many2one("x.inc.oh.classification", string="OH Incident Classification",
                                                 required=True)
    location = fields.Many2one("x.location", string="Incident Location")
    experience = fields.Integer(string="Experience")

    @api.depends('person_category', 'employee', 'visitor_name')
    def _compute_name(self):
        for person in self:
            if person.person_category.name in ("Employee", "Contractor") and person.employee:
                person.person_name = person.employee.name
                person.nationality = person.employee.country_id
            elif person.person_category.name in ("Visitor", "Others") and person.visitor_name:
                person.person_name = person.visitor_name
            else:
                person.person_name = False

    @api.depends('person_category')
    def _compute_selected_category(self):
        for record in self:
            record.selected_category = record.person_category.name

    @api.onchange('person_category', 'employee', 'visitor_name')
    def _compute_age(self):
        for employees in self:
            if employees.employee is not None:
                dob = employees.employee.birthday
                if dob:
                    dob_datetime = fields.Date.from_string(dob)
                    today = datetime.now().date()
                    employees.age = today.year - dob_datetime.year - (
                            (today.month, today.day) < (dob_datetime.month, dob_datetime.day))
                else:
                    employees.age = False


class IncPersonCategory(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.person.category"
    _description = "Category of the person"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Category must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Person Category")


class IncInjuryType(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.injury.type"
    _description = "Type of Injury"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Injury Type must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Injury Type")


class IncInjuredBodyParts(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.injured.body.parts"
    _description = "Persons involved or victims in an Incident"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Injured Body parts must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Injured Body Parts")


class IncPersonImmediateResponse(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.person.immediate.response"
    _description = "Person Immediate response"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Immediate Response must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Immediate Response")


class IncOHClassification(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.oh.classification"
    _description = "OH Incident classification"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'OH Incident classification must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="OH Incident Classification")

