from odoo import models, fields, api

# Define the NcrReport class
class NcrReport(models.Model):
    _name = 'x.ncr.report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'NCR Report'

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
    discipline_id = fields.Many2one('x.ncr.discipline', string='Discipline')
    supplier_name_id = fields.Many2one('res.partner', domain=[('supplier_rank', '>', 0)], string='Supplier Name')
    purchase_order_no = fields.Char(string='Purchase Order No.')
    project_number = fields.Char(string='Project Number', required=True)
    project_name_title = fields.Char(string='Project Name / Title')
    tag_no_location = fields.Many2one("x.location", string="Tag No. / Location", required=True)
    shipment_reference = fields.Char(string='Shipment Reference')
    received_date = fields.Date(string='Received Date')
    inspection_stage = fields.Char(string='Inspection Stage')
    rfi_number = fields.Char(string='RFI Number')
    ncr_initiator_id = fields.Many2one('hr.employee', string='NCR Initiator Name', required=True, tracking=True)
    initiator_job_title = fields.Char(related='ncr_initiator_id.job_id.name', string="Job Title")
    ncr_open_date = fields.Date(string='NCR Open Date', required=True, tracking=True)
    ncr_approver_id = fields.Many2one('hr.employee', string='NCR Approver Name', related='ncr_initiator_id.parent_id', store=True, tracking=True)
    approver_job_title = fields.Char(related='ncr_approver_id.parent_id.job_id.name', string="Job Title", store=True)
    rca_response_due_date = fields.Date(string='RCA Response Due Date')
    ncr_category_id = fields.Many2one(comodel_name='x.ncr.category', string='NCR Category')
    ncr_type_check = fields.Boolean(string='ncr_type_check', compute='_compute_ncr_type_check')
    ncr_nc_ids = fields.One2many('x.ncr.nc', 'ncr_id', string='NCR NC', required=True)
    ncs_sequence_no = fields.Integer(string="ncs_sequence", default=1)
    # State field for the NcrReport
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('approval_pending', 'Approval Pending'),
            ('assigned_to_vendor', 'Assigned to Vendor'),
            ('received_vendor_response', 'Received Vendor Response'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('return_for_further_actions', 'Return for Further Actions'),
        ], tracking=True
        # Set a default value for the state field
    )

    # Compute method to set the value of ncr_list based on the ncr_type
    @api.depends('ncr_type_id')
    def _compute_ncr_type_check(self):
        for record in self:
            record.ncr_type_check = record.ncr_type_id.name in ['Supplier', 'Customer Site Compliant']

    def save_and_forward(self):
        # Your logic for save_and_forward
        self.state = "approval_pending"
        return True

    # Your logic for Approve and Submit
    def approve_and_submit(self):
        mail_template = self.env.ref('non_conformance_report.email_template_ncr')
        mail_template.send_mail(self.id, force_send=True)
        self.write({'state': 'approved'})

    def add_supplier(self):
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
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


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
