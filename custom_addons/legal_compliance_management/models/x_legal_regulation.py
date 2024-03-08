from odoo import models, fields


class LegalRegulation(models.Model):
    _name = "x.legal.regulation"
    _description = "Legal Regulation"

    company_id = fields.Many2one('res.company', required=True, readonly=True)
    description_lrs = fields.Text(string="Description of Legal Regulation Standards", store=True)
    classification_id = fields.Many2one("x.legal.classification", string="Classification of Legal Regulations", store=True)
    lr_number = fields.Char(string="LR S.No.")
    lr_requirements = fields.Text(string="LR requirements")
    date = fields.Date(string="Date")
    version = fields.Char(string="Version")
    lr_year = fields.Char(string="Year")
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string='Browse', help='Attachment')
    active = fields.Boolean(default=True)
    _rec_name = 'lr_number'


class LegalClassification(models.Model):
    _name = "x.legal.classification"
    _description = "Legal Classification"

    name = fields.Char(string='Classification', required=True)
