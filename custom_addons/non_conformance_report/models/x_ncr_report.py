from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


# Define the NcrReport class
class NcrReport(models.Model):
    _name = 'x.ncr.report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'NCR Report'
    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'NCR Id and Company Id must be unique !'),
    ]

    # Override the create method to set default values and generate a unique name
    @api.model
    def create(self, vals_list):
        vals_list['state'] = 'new'
        vals_list['name'] = self.env['ir.sequence'].next_by_code("x.ncr.report")
        report = super().create(vals_list)
        return report

    # Fields for NcrReport
    name = fields.Char(string="NCR Reference", default='New', readonly=True, required=True)
    ncr_type_id = fields.Many2one('x.ncr.type', string='NCR Type', required=True, tracking=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    discipline_id = fields.Many2one('x.ncr.discipline', string='Discipline')
    supplier_name_id = fields.Many2one('res.partner', domain=[('supplier_rank', '>', 0)], string='Supplier Name')
    purchase_order_no = fields.Char(string='Purchase Order No.')
    project_number = fields.Char(string='Project Number', required=True)
    project_name_title = fields.Char(string='Project Name / Title')
    tag_no_location = fields.Many2one("x.location", string="Tag No. / Location", domain="[('company_id', '=', company_id)]", required=True)
    shipment_reference = fields.Char(string='Shipment Reference')
    received_date = fields.Date(string='Received Date')
    inspection_stage = fields.Char(string='Inspection Stage')
    rfi_number = fields.Char(string='RFI Number')
    ncr_initiator_id = fields.Many2one('hr.employee', string='NCR Initiator Name', required=True, default=lambda
        self: self.env.user.employee_id.id if self.env.user.employee_id else False, domain="[('company_id', '=', company_id)]", tracking=True)
    initiator_job_title = fields.Char(related='ncr_initiator_id.job_id.name', string="Job Title")
    ncr_open_date = fields.Date(string='NCR Open Date', required=True, default=fields.Date.context_today, copy=False, tracking=True)
    ncr_approver_id = fields.Many2one('hr.employee', string='NCR Approver Name', store=True, domain="[('company_id', '=', company_id)]", tracking=True)
    approver_job_title = fields.Char(related='ncr_approver_id.job_id.name', string="Job Title", store=True)
    rca_response_due_date = fields.Date(string='RCA Response Due Date', copy=False )
    ncr_category_id = fields.Many2one(comodel_name='x.ncr.category', string='NCR Category', copy=False)
    ncr_type_check = fields.Boolean(string='ncr_type_check', compute='_compute_ncr_type_check')
    ncr_nc_ids = fields.One2many('x.ncr.nc', 'ncr_id', string='NCR NC', required=True)
    ncs_sequence_no = fields.Integer(string="ncs_sequence", default=1, copy=False)
    assigned_to_id = fields.Many2one('hr.employee', string='Assigned to', compute='_compute_assignee')
    is_location_incharge = fields.Boolean(compute="_is_location_incharge")
    is_approver = fields.Boolean(compute="_is_approver")
    is_initiator = fields.Boolean(compute="_is_initiator")
    # State field for the NcrReport
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('approval_pending', 'Approval Pending'),
            ('approved', 'Approved'),
            ('awaiting_vendor_response', 'Awaiting Vendor Response'),
            ('received_vendor_response', 'Received Vendor Response'),
            ('rejected', 'Rejected'),
            ('return_for_further_actions', 'Return for Further Actions'),
            ('closed', 'Closed')
        ], tracking=True, default ='new'
        # Set a default value for the state field
    )

    due_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')

    @api.onchange('ncr_initiator_id')
    def _set_approver_id(self):
        if self.ncr_initiator_id.parent_id:
            self.ncr_approver_id = self.ncr_initiator_id.parent_id
        else:
            self.ncr_approver_id = None

    def _is_location_incharge(self):
        self.is_location_incharge = self.env.user == self.tag_no_location.location_incharge.user_id

    def _is_initiator(self):
        self.is_initiator = self.env.user == self.ncr_initiator_id.user_id

    def _is_approver(self):
        self.is_approver = self.env.user == self.ncr_approver_id.user_id

    def _check_nc_table(self):
        for record in self:
            if not record.ncr_nc_ids:
                raise ValidationError('At least one Non-Conformance record is required in the Table')
    # Compute method to set the value of ncr_list based on the ncr_type
    @api.depends('ncr_type_id')
    def _compute_ncr_type_check(self):
        for record in self:
            record.ncr_type_check = record.ncr_type_id.name in ['Supplier', 'Customer Site Compliant']

    @api.depends('state')
    def _compute_assignee(self):
        for record in self:
            if record.state == 'new':
                record.assigned_to_id = record.ncr_initiator_id.id
            elif record.state == 'approval_pending':
                record.assigned_to_id = record.ncr_approver_id.id
            else:
                record.assigned_to_id = None

    def save_and_forward(self):
        self._check_nc_table()
        if self.ncr_approver_id.user_id.id != False:
            # Your logic for save_and_forward
            self.state = "approval_pending"
            self.create_activity('Approval Pending', 'To Do', self.ncr_approver_id.user_id.id, self.due_date)
        else:
            raise ValidationError('Approver needs to be assigned. Initiator\'s manager is set as the default Approver')

    # Your logic for Approve and Submit
    def approve_and_submit(self):
        # Get the email template for NCR approval
        mail_template = self.env.ref('non_conformance_report.email_template_ncr')
        # Send approval email and force_send=True ensures the email is sent immediately
        mail_template.send_mail(self.id, force_send=True)
        self.mark_activity_as_done("Approval Pending")
        if self.tag_no_location.location_incharge.user_id.id:
            self.create_activity('Assign Response Handler', 'To Do', self.tag_no_location.location_incharge.user_id.id, self.due_date)
        self.write({'state': 'approved'})

        # Update the state of associated Non-Conformance Records to 'ncr_submitted'
        nc_records = self.mapped('ncr_nc_ids')

        for nc in nc_records:
            nc.write({'state': 'ncr_submitted'})


    def reinspect_completed(self):
        nc_records = self.mapped('ncr_nc_ids')
        for nc in nc_records:
            if nc.disposition_action == 'reinspect':
                nc.write({'state': 'ncr_submitted'})
        self.state = "closed"


    def add_supplier(self):
        # Open a form to add a new supplier
        return {
            'name': 'Add Supplier',
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'view_id': self.env.ref('non_conformance_report.res_partner_action_supplier').id,
            # Replace with the actual view ID
            'target': 'new',  # 'new' will open it in a popup
            'views': [(False, 'form')],
            'context': {
                'search_default_supplier': 1,
                'res_partner_search_mode': 'supplier',
                'default_is_company': True,
                'default_supplier_rank': 1
            }

        }

    def assign_incharge(self):
        # Open a form to assign an in-charge for NCR response
        self.mark_activity_as_done("Assign Response Handler")
        return {
            'name': 'NCR response',
            'res_model': 'x.ncr.response',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('non_conformance_report.x_ncr_response_view_form').id,
            'context': {
                'default_ncr_id': self.id,
                'default_ncr_nc_ids': self.ncr_nc_ids.ids
            }
        }

    def email_report(self):
        self.ensure_one()
        mail_template = self.env.ref('non_conformance_report.email_template_ncr_email', raise_if_not_found=False)

        ctx = {
            'default_model': 'x.ncr.report',
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
                'res_model_id': self.env['ir.model']._get('x.ncr.report').id,
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


# Define NcrType class
class NcrType(models.Model):
    _name = 'x.ncr.type'
    _description = 'NCR Type'
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'NCR Type must be unique !'),
    ]

    # Fields for NcrType
    name = fields.Char(string='Name', required=True)


# Define Discipline class
class Discipline(models.Model):
    _name = 'x.ncr.discipline'
    _description = 'Discipline'
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Supplier Discipline Classification  must be unique !'),
    ]
    # Fields for Discipline
    name = fields.Char(string='Name', required=True)


# Define Category class
class Category(models.Model):
    _name = 'x.ncr.category'
    _description = 'Category'
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'NCR Category must be unique !'),
    ]

    # Fields for Category
    name = fields.Char(string='Name', required=True)
