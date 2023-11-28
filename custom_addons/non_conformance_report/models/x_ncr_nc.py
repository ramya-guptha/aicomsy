from odoo import models, fields, api


# Define the NonConformanceModel class
class NonConformanceModel(models.Model):
    _name = 'x.ncr.nc'
    _description = 'Non-Conformance Model'

    # Fields for NonConformanceModel
    ncr_id = fields.Many2one('x.ncr.report', string='NCR Report', required=True)
    nc_s = fields.Char(string='NCS #', required=True)
    source_of_nc = fields.Many2one('x.ncr.source', string='Source of NC')
    nc_description = fields.Text(string='NC Description (Max 400 Characters)', size=400)
    uom = fields.Char(string='Unit of Measure (Max 10 Characters)', size=10)
    quantity = fields.Float(string='Quantity')
    nc_details = fields.Char(string='NC Details')
    attachment_ids = fields.Many2many('ir.attachment', 'res_id', string='Attachments')

    # Define an action for opening the NC Part Details
    @api.model
    def nc_part_details_popup(self):
        return {
            'name': 'NC Part Details',
            'type': 'ir.actions.act_window',
            'res_model': 'x.ncr.part',
            'view_mode': 'tree',
            'view_id': False,
            'view_type': 'tree',
            'target': 'new',
        }

    # Define an onchange method for the 'quantity' field
    @api.onchange('quantity')
    def _onchange_quantity(self):
        pass


# Define YourModelName class
class YourModelName(models.Model):
    _name = 'x.ncr.source'
    _description = 'x NCR Source'

    # Fields for YourModelName
    name = fields.Char(string='Name', required=True)


# Define NcPartDetails class
class NcPartDetails(models.Model):
    _name = 'x.ncr.part'
    _description = 'NC Part Details'

    # Fields for NcPartDetails
    assembly_number = fields.Char(string='Assembly Number')
    part_number = fields.Char(string='Part Number')
    unit_weight = fields.Float(string='Unit Weight')
    affected_part_weight = fields.Float(string='Affected Part Weight')
    completion_percentage = fields.Float(string='% of Completion')
    production_date = fields.Date(string='Production Date')
    quarantine = fields.Boolean(string='Quarantine')
    operator_employee_id = fields.Char(string='Operator / Production Employee ID')
    total_weight = fields.Float(string='Total Weight')
    disposition_priority = fields.Char(string='Disposition Priority')
    disposition_cost = fields.Float(string='Disposition Cost')
    estimated_backcharge_price = fields.Float(string='Estimated Backcharge Price')
    ncr_initiator_name = fields.Char(string='NCR Initiator Name')
    ncr_details_id = fields.Many2one('x.ncr.report', string='NCR Report', ondelete='cascade')

