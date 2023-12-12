from datetime import datetime

from odoo import models, fields, api


class MonthlyMetrics(models.Model):
    _name = 'x.company.monthly.metrics'
    _description = 'Monthly Metrics'
    _sql_constraints = [
        ('unique_month_year', 'unique(month, year)', 'Monthly metrics for the same month and year already exist.'),
    ]

    MONTHS = [
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    month = fields.Integer(string='Month (Integer)', store=True)
    year = fields.Integer(string='Year (Integer)', store=True)
    month_selection = fields.Selection(MONTHS, string='Month')

    year_selection = fields.Selection(
        [(str(year), str(year)) for year in range(1990, 2050)],
        string='Year')

    working_days = fields.Integer(string='Working Days')
    hour_worked = fields.Float(string='Hours Worked')
    total_sales = fields.Float(string='Total Sales')

    @api.depends('month_selection', 'year_selection')
    def _compute_name(self):
        for record in self:
            if record.month_selection and record.year_selection:
                month_name = dict(record.MONTHS).get(str(record.month_selection))
                record.name = f"{month_name} {record.year_selection}"

    @api.onchange('month_selection')
    def _compute_month_integer(self):
        for record in self:
            if record.month_selection is not None:
                record.month = int(record.month_selection)

    @api.onchange('year_selection')
    def _compute_year_integer(self):
        for record in self:
            record.year = int(record.year_selection)
