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
                   ("review_in_progress", "Review in Progress"),
                   ("closed", "Closed")
                   ],
        default="new",  # Set a default value for the state field
    )

    def save_and_submit(self):
        # Your logic for save_and_submit
        self.write({'state': 'review_in_progress'})
        self.email_report()

    def email_report(self):
        self.ensure_one()
        mail_template = self.env.ref('non_conformance_report.email_template_ncr_response', raise_if_not_found=False)

        ctx = {
            'default_model': 'x.ncr.response',
            'default_res_id': self.id,
            'default_use_template': bool(mail_template),
            'default_template_id': mail_template.id if mail_template else None,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
            'force_email': True,
            'model_description': self.with_context().name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


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
