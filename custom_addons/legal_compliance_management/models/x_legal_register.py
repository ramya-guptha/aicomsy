from odoo import models, fields, api
from datetime import datetime


class LegalRegister(models.Model):
    _name = "x.legal.register"
    _description = "Legal Register"
    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Legal Register Name and Company Id must be unique !'),
    ]

    @api.model
    def create(self, values):
        print("vals", values, self.env.company)
        values['name'] = 'LR - ' + self.env.company.name + " - "+values['selected_year']
        values['state'] = 'created'
        record = super(LegalRegister, self).create(values)
        self.regulation_standards(record.system_regulations_ids, record.company_id.id, values['selected_year'])
        self.regulation_standards(record.saso_ids, record.company_id.id, values['selected_year'])
        self.regulation_standards(record.mhrs_ids, record.company_id.id, values['selected_year'])
        self.regulation_standards(record.other_legal_regulations_ids, record.company_id.id, values['selected_year'])
        return record

    def write(self, vals):

        old_system_regulations_values = self._origin.system_regulations_ids.ids if self._origin else []

        old_saso_values = self._origin.saso_ids.ids if self._origin else []
        old_mhrs_values = self._origin.mhrs_ids.ids if self._origin else []
        old_other_legal_regulations_values = self._origin.other_legal_regulations_ids.ids if self._origin else []
        result = super(LegalRegister, self).write(vals)
        self.modify_system_regulations(old_system_regulations_values, self.company_id.id, self.selected_year)
        self.modify_saso(old_saso_values, self.company_id.id, self.selected_year)
        self.modify_mhrs(old_mhrs_values, self.company_id.id, self.selected_year)
        self.modify_other_legal_regulations(old_other_legal_regulations_values, self.company_id.id, self.selected_year)

        return result

    def modify_system_regulations(self, old_system_regulations_values, company_id, selected_year):

        new_system_regulations_values = self.system_regulations_ids.ids

        added_records_system_regulations_ids = list(set(new_system_regulations_values) - set(old_system_regulations_values))
        removed_records_system_regulations_ids = list(set(old_system_regulations_values) - set(new_system_regulations_values))

        if added_records_system_regulations_ids:
            regulation_records = self.env['x.legal.environment.regulation'].browse(added_records_system_regulations_ids)

            for record in regulation_records:
                self.regulation_standards(record, company_id, selected_year)
        if removed_records_system_regulations_ids:

            regulation_records = self.env['x.legal.environment.regulation'].browse(removed_records_system_regulations_ids)

            for record in regulation_records:
                print(">>>removed_records_system_regulations_ids in env regulation", record.name)
                search_domain = [('company_id', '=', company_id), ('lr_year', '=', selected_year), ('description_lrs', '=', record.name), ('version', '=', record.version)]
                existing_legal_regulation_records = self.env['x.legal.regulation'].search(search_domain)
                print(">>>>>existing_legal_regulation_records", existing_legal_regulation_records)

    def modify_saso(self, old_saso_values, company_id, selected_year):

        new_saso_values = self.saso_ids.ids

        added_records_saso_ids = list(set(new_saso_values) - set(old_saso_values))
        removed_records_saso_ids = list(set(old_saso_values) - set(new_saso_values))

        legal_regulation_records = []
        if added_records_saso_ids:
            regulation_records = self.env['x.legal.saso'].browse(added_records_saso_ids)
            for record in regulation_records:
                self.regulation_standards(record, company_id, selected_year)

    def modify_mhrs(self, old_mhrs_values, company_id, selected_year):

        new_mhrs_values = self.mhrs_ids.ids

        added_records_mhrs_ids = list(set(new_mhrs_values) - set(old_mhrs_values))
        removed_records_mhrs_ids = list(set(old_mhrs_values) - set(new_mhrs_values))

        legal_regulation_records = []
        if added_records_mhrs_ids:
            regulation_records = self.env['x.legal.mhrs'].browse(added_records_mhrs_ids)
            for record in regulation_records:
                self.regulation_standards(record, company_id, selected_year)

    def modify_other_legal_regulations(self, old_other_legal_regulations_values, company_id, selected_year):

        new_other_legal_regulations_values = self.other_legal_regulations_ids.ids

        added_records_other_legal_regulations_ids = list(set(new_other_legal_regulations_values) - set(old_other_legal_regulations_values))
        removed_records_other_legal_regulations_ids = list(set(old_other_legal_regulations_values) - set(new_other_legal_regulations_values))

        legal_regulation_records = []
        if added_records_other_legal_regulations_ids:
            regulation_records = self.env['x.legal.other'].browse(added_records_other_legal_regulations_ids)
            for record in regulation_records:
                self.regulation_standards(record, company_id, selected_year)

    def regulation_standards(self, regulations, company_id, year):
        records = []
        if regulations:
            sequence_number = "LR"
            for regulation in regulations:
                if regulation.classification_id.name == "Environment System Regulations":
                    sequence_number = self.env['ir.sequence'].next_by_code("x.legal.environment.regulation")
                elif regulation.classification_id.name == "Saudi Standards, Metrology and Quality Organization (SASO)":
                    sequence_number = self.env['ir.sequence'].next_by_code("x.legal.saso")
                elif regulation.classification_id.name == "Ministry of Human Resource and Social Development":
                    sequence_number = self.env['ir.sequence'].next_by_code("x.legal.mhrs")
                elif regulation.classification_id.name == "Other Legal Regulations from Local Bodies & Customers":
                    sequence_number = self.env['ir.sequence'].next_by_code("x.legal.other")
                description_lrs = f"{regulation.name}"
                legal_regulation_model = self.env['x.legal.regulation']
                record = legal_regulation_model.create({
                    'classification_id': regulation.classification_id.id,
                    'description_lrs': description_lrs,
                    'lr_number': sequence_number,
                    'company_id': company_id,
                    'lr_year': year,
                    })
                records.append(record)
        return records

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    system_regulations_ids = fields.Many2many("x.legal.environment.regulation",
                                              string="I Environment System Regulations")
    saso_ids = fields.Many2many("x.legal.saso",
                                string="II Saudi Standards, Metrology and Quality Organization (SASO)")
    mhrs_ids = fields.Many2many("x.legal.mhrs",
                                string="III Ministry of Human Resource and Social Development")
    other_legal_regulations_ids = fields.Many2many("x.legal.other",
                                                   string="IV Other Legal Regulations from Local Bodies & Customers")
    legal_regulation_standards = fields.Text(string="Description of Legal Regulation Standards", store=True)
    name = fields.Char(string="Name", default='New')
    year_selection = [(str(year), str(year)) for year in range(2000, 2031)]
    active = fields.Boolean(default=True)

    # Create the Selection field for years
    selected_year = fields.Selection(
        selection=year_selection,
        string='Select Year for Legal Regulations',
        help='Choose the year from the dropdown.',
        default=lambda self: str(datetime.now().year),
    )
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("created", "Created"),
            ("archived", "Archived")
        ],
        string="Status",
        default="new",
        copy=False,

    )

    def add_system_regulations(self):
        return {
            'name': 'Environment System Regulations',
            'type': 'ir.actions.act_window',
            'res_model': 'x.legal.environment.regulation',
            'view_mode': 'form',
            'target': 'new',
        }

    def add_saso(self):
        return {
            'name': 'Saudi Standards, Metrology and Quality Organization (SASO)',
            'type': 'ir.actions.act_window',
            'res_model': 'x.legal.saso',
            'view_mode': 'form',
            'target': 'new',
        }

    def add_mhrs(self):
        return {
            'name': 'Ministry of Human Resource and Social Development',
            'type': 'ir.actions.act_window',
            'res_model': 'x.legal.mhrs',
            'view_mode': 'form',
            'target': 'new',
        }

    def add_other_legal_regulations(self):
        return {
            'name': 'Other Legal Regulations from Local Bodies & Customers',
            'type': 'ir.actions.act_window',
            'res_model': 'x.legal.other',
            'view_mode': 'form',
            'target': 'new',
        }

    def view_current_company_form_action(self):
        exist = self.sudo().search([["company_id", "=", self.env.company.id]], limit=1)
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "form",
            "res_id": exist.id if exist.id else False
        }

    def change_company(self):
        action = self.env.ref('legal_compliance_management.legal_register_action').read()[0]

        return action
        """ return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "view_mode": "tree",
        }"""


class EnvironmentSystemRegulations(models.Model):
    _name = "x.legal.environment.regulation"
    _description = "Environment System Regulations"
    _sql_constraints = [
        ('unique_name_version', 'unique(name,version)', 'Name and Version must be unique!'),
    ]

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    date = fields.Date(string="Date")
    version = fields.Char(string="Version")
    classification_id = fields.Many2one("x.legal.classification", string="Classification", default="Environment System Regulations", readonly=True)


class LegalSaso(models.Model):
    _name = 'x.legal.saso'
    _description = 'SASO'
    _sql_constraints = [
        ('unique_name_version', 'unique(name,version)', 'Name and Version must be unique!'),
    ]

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string="Description")
    date = fields.Date(string="Date")
    version = fields.Char(string="Version")
    classification_id = fields.Many2one("x.legal.classification", string="Classification", default=lambda self: self.env['x.legal.classification'].search([('name', '=', 'Saudi Standards, Metrology and Quality Organization (SASO)')], limit=1), readonly=True)


class LegalMhrs(models.Model):
    _name = 'x.legal.mhrs'
    _description = 'MHRS'
    _sql_constraints = [
        ('unique_name_version', 'unique(name,version)', 'Name and Version must be unique!'),
    ]

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string="Description")
    date = fields.Date(string="Date")
    version = fields.Char(string="Version")
    classification_id = fields.Many2one("x.legal.classification", string="Classification", default=lambda self: self.env['x.legal.classification'].search([('name', '=', 'Ministry of Human Resource and Social Development')], limit=1), readonly=True)


class OtherLegalRegulations(models.Model):
    _name = 'x.legal.other'
    _description = 'Other Legal'
    _sql_constraints = [
        ('unique_name_version', 'unique(name,version)', 'Name and Version must be unique!'),
    ]

    @api.model
    def create(self, vals_list):
        result = super(OtherLegalRegulations, self).create(vals_list)
        print(">>> Going to do page relooad")
        return result

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string="Description")
    date = fields.Date(string="Date")
    version = fields.Char(string="Version")
    classification_id = fields.Many2one("x.legal.classification", string="Classification",
                                        default=lambda self: self.env['x.legal.classification'].search([('name', '=', 'Other Legal Regulations from Local Bodies & Customers')], limit=1), readonly=True)
