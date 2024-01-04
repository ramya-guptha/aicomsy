from odoo import models, fields, api
from odoo.exceptions import ValidationError


# Define NonConformanceModel class
class NonConformanceModel(models.Model):
    _name = 'x.ncr.nc'
    _description = 'Non-Conformance Model'

    @api.model
    def create(self, values):
        project_number = ''
        nc_records = ''
        ncr_nc_records = ''
        ncr_resp_id = ''
        ncr_id = ''
        if 'ncr_id' in values:
            ncr_id = self.env['x.ncr.report'].browse(values['ncr_id'])
            project_number = ncr_id.project_number
            ncr_nc_records = self.env['x.ncr.nc'].search(
                [('ncr_id', '=', values['ncr_id']), ('ncr_response_id', '=', False)])
            ncr_resp = self.env['x.ncr.response'].search([('ncr_id', '=', values['ncr_id'])])
            if ncr_resp.exists():
                ncr_resp_id = ncr_resp.id
                values['ncr_response_id'] = ncr_resp_id
        elif 'ncr_response_id' in values:
            ncr_response = self.env['x.ncr.response'].browse(values['ncr_response_id'])
            project_number = ncr_response.ncr_id.project_number
            ncr_id = ncr_response.ncr_id
            values['ncr_id'] = ncr_response.ncr_id.id
            # Update records in x.ncr.nc with the ncr_response_id
            ncr_nc_records = self.env['x.ncr.nc'].search(
                [('ncr_id', '=', ncr_response.ncr_id.id), ('ncr_response_id', '=', False)])
            ncr_resp_id = values['ncr_response_id']
        ncs_sequence_no = ncr_id.ncs_sequence_no
        values['nc_s'] = f'{project_number}{ncs_sequence_no:03d}'

        nc = super().create(values)
        ncr_id.write({'ncs_sequence_no': ncs_sequence_no + 1})
        if ncr_resp_id:
            ncr_nc_records.write({'ncr_response_id': ncr_resp_id})
        return nc

    @api.constrains('nc_description', 'uom')
    def _check_fields_size(self):
        for record in self:
            if record.nc_description and len(record.nc_description) > 400:
                raise ValidationError("NC Description should be at most 400 characters.")
            if record.uom and len(record.uom) > 10:
                raise ValidationError("Unit of Measure should be at most 10 characters.")

    # Fields for NonConformanceModel
    ncr_id = fields.Many2one('x.ncr.report', string='NCR Report', required=True, ondelete='cascade')
    ncr_response_id = fields.Many2one('x.ncr.response', string='NCR Response', ondelete='cascade')
    nc_s = fields.Char(string='NCS #', readonly=True)
    source_of_nc = fields.Many2one('x.ncr.source', string='Source of NC', required=True)
    nc_description = fields.Text(string='NC Description', help="Max 400 Characters", required=True)
    uom = fields.Char(string='Unit of Measure', help="Max 10 Characters", required=True)
    quantity = fields.Float(string='Quantity', required=True)
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string='NC Details')
    cause_of_nc_id = fields.Many2one('x.ncr.cause', string='Cause of NC')
    disposition_type_id = fields.Many2one('x.ncr.disposition.type', string='Disposition Type')
    immediate_action = fields.Text(string='Immediate Action', help='Maximum 400 character only')
    proposed_due_date = fields.Date(string='Proposed Due Date')
    response_attachment_ids = fields.One2many('ir.attachment', 'res_id', string="RCA / CA Response")
    review_comments = fields.Text(string='Review Comments (If Any)', help='Max 400 Characters')
    ca_response_id = fields.Many2one('x.ncr.ca.response', string='RCA Response')
    rca_response_type1 = fields.Char(related='ca_response_id.nam', string="RCA Response Type", store=True)
    disposition_action = fields.Selection(
        [('accept', 'Accept'), ('reject', 'Reject')],
        string='Disposition Action',
    )
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('ncr_submitted', 'NCR Submitted'),
            ('received_vendor_response', 'Received Vendor Response'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('return_for_further_actions', 'Return for Further Actions'),
        ], tracking=True,
        # Set a default value for the state field
        default='new',
    )
    nc_part_details_ids = fields.One2many('x.ncr.part', 'nc_details_id', string="Part Details")

    # Define an action for opening the NC Part Details
    def nc_part_details_popup(self):
        return {
            'name': 'NC Details',
            'type': 'ir.actions.act_window',
            'res_model': 'x.ncr.nc',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
        }


# Define NCRSource class
class NCRSource(models.Model):
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
    quantity = fields.Float(string='Quantity')
    quarantine = fields.Selection([('yes', 'Yes'), ('no', 'No')], string='Quarantine')
    operator_employee_id = fields.Char(string='Operator / Production Employee ID')
    total_weight = fields.Float(string='Total Weight')
    disposition_priority = fields.Char(string='Disposition Priority')
    disposition_cost = fields.Float(string='Disposition Cost')
    estimated_backcharge_price = fields.Float(string='Estimated Backcharge Price')
    nc_details_id = fields.Many2one('x.ncr.nc', string='NCR Details', required=True, ondelete='cascade')
    ncr_id = fields.Many2one(related="nc_details_id.ncr_id")


class NcrCause(models.Model):
    _name = 'x.ncr.cause'
    _description = 'Cause of NC'

    name = fields.Char(string='Cause Name', required=True)


class NcrDispositionType(models.Model):
    _name = 'x.ncr.disposition.type'
    _description = 'Disposition Type'

    name = fields.Char(string='Disposition Type', required=True)


class NcrCaResponse(models.Model):
    _name = 'x.ncr.ca.response'
    _description = 'NCR RCA Response'

    name = fields.Char(string='Name', required=True)
    nam = fields.Char(string='Response Type')
