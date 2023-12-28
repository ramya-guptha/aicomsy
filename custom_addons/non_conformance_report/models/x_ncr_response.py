from odoo import models, fields, api
from odoo.exceptions import ValidationError


class NcrResponse(models.Model):
    _name = 'x.ncr.response'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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
    supplier_response = fields.Text(string='Supplier Response', tracking=True)
    prepared_by_id = fields.Many2one('hr.employee', string='Prepared by', required=True, tracking=True)
    reviewed_and_approved_by_id = fields.Many2one('hr.employee', string='Reviewed & Approved by', required=True,
                                                  tracking=True)
    prepared_by_signature_date = fields.Char(string='Signature With Date', help='Maximum 30 character only',
                                             tracking=True)
    reviewed_by_signature_date = fields.Char(string='Signature With Date', help='Maximum 30 character only',
                                             tracking=True)
    prepared_by_title = fields.Char(related='prepared_by_id.job_id.name', string='Title')
    reviewed_by_title = fields.Char(related='reviewed_and_approved_by_id.job_id.name', string='Title')
    total_cost_for_rework = fields.Float(string='Total Cost for Rework', compute='_compute_total_cost_for_rework')
    rca_approver_id = fields.Many2one('hr.employee', string='RCA Approver Name', tracking=True)
    ncr_completion_status = fields.Char(string='NCR Completion Status', compute='_compute_ncr_completion_status')
    total_backcharge_amount = fields.Float(string='Total Backcharge Amount', compute='_compute_total_backcharge',)
    title = fields.Char(related='rca_approver_id.job_id.name', string='Title')
    ncr_closed_date = fields.Date(string='NCR Closed Date', tracking=True)
    ncr_nc_ids = fields.One2many('x.ncr.nc', 'ncr_response_id', string='NCR NC')
    show_approve_button = fields.Boolean("Show Approve Button", default=False, store=False)
    state = fields.Selection(
        selection=[("new", "New"),
                   ("review_in_progress", "Review in Progress"),
                   ("closed", "Closed")
                   ],
        default="new", tracking=True  # Set a default value for the state field
    )

    def save_and_submit(self):
        # Your logic for save_and_submit
        self.write({'state': 'review_in_progress'})
        self.email_report()
        nc_records = self.mapped('ncr_nc_ids')
        for nc in nc_records:
            nc.write({'state': 'received_vendor_response'})

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
            'name': 'Email',
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
        self.write({'state': 'closed'})
        return True

    def action_rca_rejected(self):
        # Additional logic can be added here if needed
        return True

    @api.depends('ncr_nc_ids.nc_part_details_ids.estimated_backcharge_price')
    def _compute_total_backcharge(self):
        for record in self:
            # Your custom logic for computing total backcharge
            record.total_backcharge_amount = sum(
                part.estimated_backcharge_price for part in record.ncr_nc_ids.mapped('nc_part_details_ids')
            )

    @api.depends('ncr_nc_ids.nc_part_details_ids.disposition_cost')
    def _compute_total_cost_for_rework(self):
        for record in self:
            # Your custom logic for computing total cost for rework
            record.total_cost_for_rework = sum(
                part.disposition_cost for part in record.ncr_nc_ids.mapped('nc_part_details_ids')
            )

    @api.depends('ncr_nc_ids.ca_response_id', 'ncr_nc_ids.ca_response_id.name')
    def _compute_ncr_completion_status(self):
        for record in self:
            # Filter NCR NC records where ca_response_id has names "CODE-1" or "CODE-2"
            code_1_2_records = record.ncr_nc_ids.filtered(
                lambda nc: nc.ca_response_id and nc.ca_response_id.name in ["Code-1", "Code-2"]
            )
            # Calculate the total number of nc_s
            total_nc_s_count = len(code_1_2_records)
            # Calculate the percentage
            if len(record.ncr_nc_ids) != 0:
                percentage = (total_nc_s_count / len(record.ncr_nc_ids)) * 100
                # Update the ncr_completion_status field
                record.ncr_completion_status = percentage

                if percentage == 100:
                    record.show_approve_button = True
                else:
                    record.show_approve_button = False
            else:
                record.ncr_completion_status = 0


    @api.constrains('prepared_by_signature_date', 'reviewed_by_signature_date')
    def _check_fields_size(self):
        for record in self:
            if record.prepared_by_signature_date and len(record.prepared_by_signature_date) > 30:
                raise ValidationError("Signature With Date should be at most 30 characters.")
            if record.reviewed_by_signature_date and len(record.reviewed_by_signature_date) > 30:
                raise ValidationError("Signature With Date should be at most 30 characters.")
