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
    month = fields.Integer(string='Month (Integer)', store=True)
    year = fields.Integer(string='Year (Integer)', store=True)
    month_selection = fields.Selection(MONTHS, string='Month')

    year_selection = fields.Selection(
        [(str(year), str(year)) for year in range(1990, 2030)],
        string='Year')

    working_days = fields.Integer(string='Working Days')
    hour_worked = fields.Float(string='Hours Worked')
    total_sales = fields.Integer(string='Total Sales')

    @api.onchange('month_selection')
    def _compute_month_integer(self):
        for record in self:
            if record.month_selection is not None:
                record.month = int(record.month_selection)

    @api.onchange('year_selection')
    def _compute_year_integer(self):
        for record in self:
            record.year = int(record.year_selection)

    def _compute_month(self):
        for record in self:
            if record.month is not None:
                record.month_selection = str(record.month)
            else:
                record.month_selection = str(datetime.now().month)

    def _compute_year(self):
        for record in self:
            if record.year is not None and record:
                record.year_selection = str(record.year)
            else:
                record.year_selection = str(datetime.now().year)
