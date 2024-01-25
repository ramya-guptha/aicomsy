from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class NcrResponse(models.Model):
    _name = 'x.ncr.response'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'NCR Response'
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'NCR Response Id must be unique !'),
    ]

    @api.model
    def create(self, vals_list):
        # Generate a unique name using the sequence
        vals_list['name'] = self.env['ir.sequence'].next_by_code("x.ncr.response")
        # Set default state to 'assigned'
        vals_list['state'] = 'new'
        ncr_id = self.env.context.get('default_ncr_id')
        # Create the NCR response
        response = super().create(vals_list)
        # Change the state of the related incident
        if ncr_id:
            ncr = self.env['x.ncr.report'].browse(ncr_id)
            ncr.write({'state': 'awaiting_vendor_response'})

        response.create_activity('Prepare Response for NCR', 'To Do', response.prepared_by_id.user_id.id, (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'))
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
    manual_total_cost_rework = fields.Float(string='Total Cost for Rework')
    total_cost_for_rework = fields.Float(string='Total Cost for Rework', compute='_compute_total_cost_for_rework', inverse="_inverse_total_cost_rework_editable")
    rca_approver_id = fields.Many2one('hr.employee', string='RCA Approver Name', related="ncr_id.ncr_approver_id", tracking=True)
    ncr_completion_status = fields.Char(string='NCR Completion Status', compute='_compute_ncr_completion_status')
    manual_total_backcharge = fields.Float(string='Total Backcharge Amount')
    total_backcharge_amount = fields.Float(string='Total Backcharge Amount', compute='_compute_total_backcharge', inverse="_inverse_total_backcharge" )
    title = fields.Char(related='rca_approver_id.job_id.name', string='Title')
    ncr_closed_date = fields.Date(string='NCR Closed Date', tracking=True)
    ncr_nc_ids = fields.One2many('x.ncr.nc', 'ncr_response_id', string='NCR NC')
    show_approve_button = fields.Boolean("Show Approve Button", default=False, store=False)
    to_reinspect = fields.Boolean(" Items in Reinspect", default=False, store=False, compute='_compute_to_reinspect')
    to_reject = fields.Boolean(" Items in Reject", default=False, store=False, compute='_compute_to_reject')
    assigned_to_id = fields.Many2one('hr.employee', string='Assigned to', compute='_compute_assignee')
    state = fields.Selection(
        selection=[("draft", "Draft"),
                   ("new", "New"),
                   ("review_in_progress", "Review in Progress"),
                   ("approval_pending", "Approval Pending"),
                   ("review_rejection", "Review Rejection"),
                   ("closed", "Closed")
                   ],
        default="draft", tracking=True  # Set a default value for the state field
    )
    is_approver = fields.Boolean(compute="_is_approver")
    is_preparer = fields.Boolean(compute="_is_preparer")
    is_reviewer = fields.Boolean(compute="_is_reviewer")

    due_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')

    def save_and_submit(self):
        if self.state == 'review_rejection':
            self.mark_activity_as_done("Review Reject Items")
        elif self.state == 'new':
            self.mark_activity_as_done("Prepare Response for NCR")
        # Your logic for save_and_submit
        self.write({'state': 'review_in_progress'})
        # Trigger the email report function
        self.email_report()
        # Update the state of associated Non-Conformance Records to 'received_vendor_response'
        nc_records = self.mapped('ncr_nc_ids')
        self._check_nc_table()
        for nc in nc_records:
            nc.write({'state': 'received_vendor_response'})
        self.create_activity('Review & Approve', 'To Do', self.reviewed_and_approved_by_id.user_id.id, self.due_date)

    def review_approve(self):
        # Your logic for review
        self.write({'state': 'approval_pending'})
        self.create_activity('Approval Pending', 'To Do', self.rca_approver_id.user_id.id, self.due_date)
        self.mark_activity_as_done("Review & Approve")

    def email_report(self):
        # Ensure that this method is called on a single record
        self.ensure_one()
        # Get the email template for NCR response
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
        # Return an action to open the email composition form
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
        ncr_id = self.ncr_id
        nc_records = self.mapped('ncr_nc_ids')
        for nc in nc_records:
            if nc.disposition_action == 'accept':
                nc.write({'state': 'approved'})
            elif nc.disposition_action == 'reinspect':
                nc.write({'state': 'return_for_further_actions'})
            elif nc.disposition_action == 'reject':
                raise ValidationError("NCR Response can\'t be approved when items are in Reject state")

        self.show_approve_button = False
        if self.to_reinspect:
            ncr_id.write({'state': 'return_for_further_actions'})
            ncr_id.create_activity('Reinspect', 'To Do', ncr_id.ncr_initiator_id.user_id.id, ncr_id.due_date)
            self.state = 'closed'
            self.mark_activity_as_done("Approval Pending")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'type': 'success',
                    'message': 'Notification has been sent to Initiator for reinspect.',
                    'next': {'type': 'ir.actions.client',
                             'tag': 'soft_reload', },
                }
            }
        else:
            ncr_id.write({'state': 'closed'})
            self.state = 'closed'
            self.mark_activity_as_done("Approval Pending")


    def action_rca_rejected(self):
        # Additional logic can be added here if needed
        reject_records = self.ncr_nc_ids.filtered(
            lambda nc: nc.disposition_action == 'reject'
        )
        if not reject_records:
            raise ValidationError("NCR Response are in Approved / Reinspect status and can\'t be rejected")
        domain = [
            ('res_name', '=', self.name),
            ('user_id', '=', self.env.user.id),
            ('summary', '=', "Approval Pending"),
        ]

        activity = self.env['mail.activity'].search(domain, limit=1)
        if activity:
            activity.unlink()

        self.state = "review_rejection"
        nc_records = self.mapped('ncr_nc_ids')
        for nc in nc_records:
            if nc.disposition_action == 'reject':
                nc.write({'state': 'rejected'})
        self.create_activity('Review Reject Items', 'To Do', self.rca_approver_id.user_id.id, self.due_date)

    def create_activity(self, summary, activity_type, user_id, date_deadline=None):
        activity_type_id = self.env['mail.activity.type'].search([('name', '=', activity_type)], limit=1).id
        if not activity_type_id:
            # Handle the case where 'To Do' activity type is not found
            return
        else:
            # Create a new activity
            activity = self.env['mail.activity'].create({
                'activity_type_id': activity_type_id,
                'summary': summary,
                'date_deadline': date_deadline,
                'res_model_id': self.env['ir.model']._get('x.ncr.response').id,
                'res_id': self.id,
                'user_id': user_id,
            })

            return activity

    def mark_activity_as_done(self, summary):

        domain = [
            ('res_name', '=', self.name),
            ('user_id', '=', self.env.user.id),
            ('summary', '=', summary),
        ]

        activity = self.env['mail.activity'].search(domain, limit=1)

        if activity:
            # Mark the activity as done
            activity.action_feedback()

    def _compute_rca_approver(self):
        for record in self:
            record.rca_approver_id = record.ncr_id.ncr_approver_id
    def _is_reviewer(self):
        self.is_reviewer = self.env.user == self.reviewed_and_approved_by_id.user_id

    def _is_approver(self):
        self.is_approver = self.env.user == self.rca_approver_id.user_id

    def _is_preparer(self):
        self.is_preparer = self.env.user == self.prepared_by_id.user_id

    @api.depends('manual_total_backcharge', 'ncr_nc_ids.nc_part_details_ids.estimated_backcharge_price')
    def _compute_total_backcharge(self):
        for record in self:
            if record.manual_total_backcharge:
                record.total_backcharge_amount = record.manual_total_backcharge
            elif record.total_backcharge_amount == 0.00:

                # Your custom logic for computing total backcharge
                record.total_backcharge_amount = sum(
                    part.estimated_backcharge_price for part in record.ncr_nc_ids.mapped('nc_part_details_ids')
                )

    def _inverse_total_backcharge(self):
        for record in self:
            record.manual_total_backcharge = record.total_backcharge_amount

    @api.depends('manual_total_cost_rework', 'ncr_nc_ids.nc_part_details_ids.disposition_cost')
    def _compute_total_cost_for_rework(self):
        for record in self:
            if record.manual_total_cost_rework:
                record.total_cost_for_rework = record.manual_total_cost_rework
            elif record.total_cost_for_rework == 0.00:
                # Your custom logic for computing total cost for rework
                record.total_cost_for_rework = sum(
                    part.disposition_cost for part in record.ncr_nc_ids.mapped('nc_part_details_ids')
                )

    def _inverse_total_cost_rework_editable(self):
        for record in self:
            record.manual_total_cost_rework = record.total_cost_for_rework

    @api.depends('ncr_nc_ids.disposition_action')
    def _compute_to_reinspect(self):
        for record in self:
            reinspect_records = record.ncr_nc_ids.filtered(
                lambda nc: nc.disposition_action == 'reinspect'
            )
            record.to_reinspect = False
            if reinspect_records:
                record.to_reinspect = True

    @api.depends('ncr_nc_ids.disposition_action')
    def _compute_to_reject(self):
        for record in self:
            reject_records = record.ncr_nc_ids.filtered(
                lambda nc: nc.disposition_action == 'reject'
            )
            record.to_reject = False
            if reject_records:
                record.to_reject = True

    @api.depends('ncr_nc_ids.disposition_action')
    def _compute_ncr_completion_status(self):
        for record in self:
            # Filter NCR NC records where ca_response_id has names "CODE-1" or "CODE-2"
            accept_reinspect_records = record.ncr_nc_ids.filtered(
                lambda nc: nc.disposition_action == 'accept' or nc.disposition_action == 'reinspect'
            )
            # Calculate the total number of nc_s
            total_nc_s_count = len(accept_reinspect_records)
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
        # Check the size of signature dates and raise validation error if exceeded
        for record in self:
            if record.prepared_by_signature_date and len(record.prepared_by_signature_date) > 30:
                raise ValidationError("Signature With Date should be at most 30 characters.")
            if record.reviewed_by_signature_date and len(record.reviewed_by_signature_date) > 30:
                raise ValidationError("Signature With Date should be at most 30 characters.")

    @api.depends('state')
    def _compute_assignee(self):
        for record in self:
            if record.state == 'new':
                # Set assigned_to_id to the name of the prepared by in the 'new' state
                record.assigned_to_id = record.prepared_by_id.id
            elif record.state == 'review_in_progress':
                # Set assigned_to_id to the name of the reviewer and approver by in the 'review_in_progress' state
                record.assigned_to_id = record.reviewed_and_approved_by_id.id
            elif record.state == 'approval_pending':
                # Set assigned_to_id to the name of the RCA approver in the 'approval_pending' state
                record.assigned_to_id = record.rca_approver_id.id
            else:
                # Set assigned_to_id to None for other states
                record.assigned_to_id = None

    @api.onchange('prepared_by_id')
    def _set_approver_id(self):
        if self.prepared_by_id.parent_id:
            self.reviewed_and_approved_by_id = self.prepared_by_id.parent_id
        else:
            self.reviewed_and_approved_by_id = None

    def _check_nc_table(self):
        for record in self:
            for nc in record.ncr_nc_ids:
                if not(nc.cause_of_nc_id and nc.disposition_type_id and nc.proposed_due_date and nc.immediate_action):
                    raise ValidationError('Mandatory fields - Cause of NC, Disposition Type, Due date and Immediate Action are required')

