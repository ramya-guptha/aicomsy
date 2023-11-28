from odoo import models, fields, api

# Define the NcrReport class
class NcrReport(models.Model):
    _name = 'x.ncr.report'
    _description = 'NCR Report'

    # Override the create method to set default values and generate a unique name
    @api.model
    def create(self, vals_list):
        vals_list['state'] = 'new'
        vals_list['name'] = self.env['ir.sequence'].next_by_code("x.ncr.report")
        report = super().create(vals_list)
        return report

    # Fields for NcrReport
    name = fields.Char(string="NCR Reference", default='New', readonly=True)
    ncr_type = fields.Many2one('x.ncr.type', string='NCR Type')
    discipline = fields.Many2one('x.ncr.discipline', string='Discipline')
    supplier_name = fields.Char(string='Supplier Name')
    purchase_order_no = fields.Char(string='Purchase Order No.')
    project_number = fields.Char(string='Project Number')
    project_name_title = fields.Char(string='Project Name / Title')
    tag_no_location = fields.Char(string='Tag No. / Location')
    shipment_reference = fields.Char(string='Shipment Reference')
    received_date = fields.Date(string='Received Date')
    inspection_stage = fields.Char(string='Inspection Stage')
    rfi_number = fields.Char(string='RFI Number')
    nc_table = fields.Text(string='NC Table')
    ncr_initiator_name = fields.Char(string='NCR Initiator Name')
    ncr_open_date = fields.Date(string='NCR Open Date')
    ncr_approver_name = fields.Char(string='NCR Approver Name')
    rca_response_due_date = fields.Date(string='RCA Response Due Date')
    title = fields.Char(string='Title')
    ncr_category = fields.Many2one(comodel_name='x.ncr.category', string='NCR Category')
    ncr_list = fields.Boolean(string='ncr_list', compute='_compute_ncr_list')
    ncr_nc_ids = fields.One2many('x.ncr.nc', 'ncr_id', string='NCR NC')
    ncr_part_ids = fields.One2many('x.ncr.part', 'ncr_details_id', string='Part Details')

    # State field for the NcrReport
    state = fields.Selection(
        selection=[("new", "New")])

    # Compute method to set the value of ncr_list based on the ncr_type
    @api.depends('ncr_type')
    def _compute_ncr_list(self):
        for record in self:
            record.ncr_list = record.ncr_type.name in ['Supplier', 'Customer Site Compliant']


# Define NcrType class
class NcrType(models.Model):
    _name = 'x.ncr.type'
    _description = 'NCR Type'

    # Fields for NcrType
    name = fields.Char(string='Name', required=True)


# Define Discipline class
class Discipline(models.Model):
    _name = 'x.ncr.discipline'
    _description = 'Discipline'

    # Fields for Discipline
    name = fields.Char(string='Name', required=True)


# Define Category class
class Category(models.Model):
    _name = 'x.ncr.category'
    _description = 'Category'

    # Fields for Category
    name = fields.Char(string='Name', required=True)
