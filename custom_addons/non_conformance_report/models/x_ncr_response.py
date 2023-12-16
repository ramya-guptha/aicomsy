from odoo import models, fields, api
from odoo.exceptions import ValidationError


class NcrResponse(models.Model):
    _name = 'x.ncr.response'
    _description = 'NCR Response'

    @api.model
    def create(self, vals_list):
        # Generate a unique name using the sequence
        vals_list['name'] = self.env['ir.sequence'].next_by_code("x.ncr.response")
        # Set default state to 'assigned'
        vals_list['state'] = 'new'

        # Create the NCR response
        response = super().create(vals_list)

        return response

    name = fields.Char(string="NCR Reference", default='New', readonly=True)
    ncr_type_id = fields.Many2one('x.ncr.type', related="ncr_id.ncr_type_id", string='NCR Type')
    ncr_id = fields.Many2one("x.ncr.report", string='NCR No.')
    project_number = fields.Char(related="ncr_id.project_number", string='Project Number')
    project_name_title = fields.Char(related="ncr_id.project_name_title", string='Project Name / Title')
    supplier_response = fields.Text(string='Supplier Response')
    prepared_by_id = fields.Many2one('hr.employee', string='Prepared by')
    reviewed_and_approved_by_id = fields.Many2one('hr.employee', string='Reviewed & Approved by')
    prepared_by_signature_date = fields.Char(string='Signature With Date', help='Maximum 30 character only')
    reviewed_by_signature_date = fields.Char(string='Signature With Date', help='Maximum 30 character only')
    prepared_by_title = fields.Char(related='prepared_by_id.job_id.name', string='Title')
    reviewed_by_title = fields.Char(related='reviewed_and_approved_by_id.job_id.name', string='Title')
    total_cost_for_rework = fields.Float(string='Total Cost for Rework')
    rca_approver_id = fields.Many2one('hr.employee', string='RCA Approver Name')

    ncr_completion_status = fields.Char(string='NCR Completion Status')
    total_backcharge_amount = fields.Float(string='Total Backcharge Amount')
    title = fields.Char(related='rca_approver_id.job_id.name', string='Title')
    ncr_closed_date = fields.Date(string='NCR Closed Date')
    ncr_nc_ids = fields.One2many('x.ncr.nc', 'ncr_response_id', string='NCR NC')

    state = fields.Selection(
        selection=[("new", "New"),
                   ("closed", "Closed")
                   ],
        default="new",  # Set a default value for the state field
    )

    def save_and_submit(self):
        # Your logic for save_and_submit
        self.write({'state': 'closed'})
        return True

    def approve_and_forward(self):
        # Your logic for approve_and_forward
        return True

    def action_rca_rejected(self):
        # Additional logic can be added here if needed
        return True

    @api.constrains('signature_with_date_1', 'signature_with_date_2', 'title_1', 'title_2')
    def _check_fields_size(self):
        for record in self:
            if record.prepared_by_signature_date and len(record.prepared_by_signature_date) > 30:
                raise ValidationError("Signature With Date should be at most 30 characters.")
            if record.reviewed_by_signature_date and len(record.reviewed_by_signature_date) > 30:
                raise ValidationError("Signature With Date should be at most 30 characters.")
            if record.prepared_by_title and len(record.prepared_by_title) > 30:
                raise ValidationError("Title should be at most 30 characters.")
            if record.reviewed_by_title and len(record.reviewed_by_title) > 30:
                raise ValidationError("Title (2) should be at most 30 characters.")
