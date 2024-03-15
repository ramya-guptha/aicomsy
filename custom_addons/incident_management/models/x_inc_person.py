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
    person_category_id = fields.Many2one("x.inc.person.category", required=True, help='Person Category')
    selected_category = fields.Char(compute='_compute_selected_category')
    person_name = fields.Char(string='Name', compute='_compute_name', store=True, readonly=True, help='Name')
    employee_id = fields.Many2one('hr.employee', string='Employee Name', domain="[('company_id', '=', company_id)]")

    visitor_name = fields.Char(string='Visitor Name')
    nationality_id = fields.Many2one('res.country', "Nationality")
    manual_age = fields.Integer(string="Age", default=0)
    age = fields.Integer(string="Age", compute="_compute_age", inverse="_inverse_age")
    # experience = fields.Integer(string="Experience", related="employee.experience")
    job_title = fields.Char(related='employee_id.job_id.name', string="Job Title")
    involved_victim = fields.Selection(
        string="Involved/ Victim",
        selection=[('involved', "Involved"), ('victim', "Victim"), ('both', 'Both')], required=True, help='Involved/ Victim')
    person_task = fields.Text(string="Task being done at the time of incident")
    person_employer = fields.Char(string="Employer")
    incident_injured_body_parts_ids = fields.Many2many("x.inc.injured.body.parts", string="Injured Body Part", help='Injured Body Part')
    incident_type_of_illness_ids = fields.Many2many("x.inc.injury.type", string="Nature of Injury", help='Nature of Injury')
    visited_hospital = fields.Char(string="Name of the Hospital Visited")
    person_days_off = fields.Integer(string="Days Off")
    is_visitor = fields.Boolean(string='Is Visitor', compute='_compute_is_visitor')
    immediate_response_id = fields.Many2one('x.inc.person.immediate.response', string="Immediate Response", help='Immediate Response')
    oh_incident_classification_id = fields.Many2one("x.inc.oh.classification", string="OH Incident Classification",
                                                 required=True, help='OH Incident Classification')
    oh_severity_consequence_id = fields.Many2one("x.inc.oh.severity.consequence",
                                              string="Severity Consequence", required=True, help='Severity Consequence')
    location_id = fields.Many2one("x.location", string="Incident Location")
    experience = fields.Integer(string="Experience")
    company_id = fields.Many2one(related="incident_id.company_id")

    @api.depends('person_category_id', 'employee_id', 'visitor_name')
    def _compute_name(self):
        for person in self:
            if person.person_category_id.name in ("Employee", "Contractor") and person.employee_id:
                person.person_name = person.employee_id.name
                person.nationality_id = person.employee_id.country_id
            elif person.person_category_id.name in ("Visitor", "Others") and person.visitor_name:
                person.person_name = person.visitor_name
            else:
                person.person_name = False

    @api.depends('person_category_id')
    def _compute_selected_category(self):
        for record in self:
            record.selected_category = record.person_category_id.name

    @api.onchange('person_category_id', 'employee_id', 'visitor_name', 'manual_age')
    def _compute_age(self):
        for record in self:
            if record.manual_age != 0:
                record.age = record.manual_age
                record.manual_age = 0
            elif record.employee_id is not None:
                dob = record.employee_id.birthday
                if dob:
                    dob_datetime = fields.Date.from_string(dob)
                    today = datetime.now().date()
                    record.age = today.year - dob_datetime.year - (
                            (today.month, today.day) < (dob_datetime.month, dob_datetime.day))
                else:
                    record.age = False

    def _inverse_age(self):
        for record in self:
            record.manual_age = record.age


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

class IncOHSeverityConsequence(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.oh.severity.consequence"
    _description = "OH Severity Consequence"
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'OH Severity Consequence must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="OH Severity Consequence")
