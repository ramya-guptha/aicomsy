from odoo import models, fields, api
from datetime import datetime, timedelta

class MonitoringMeasurement(models.Model):
    _name = 'x.monitoring.measurement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Monitoring and Measurement'

    @api.model
    def create(self, values):
        assigned_user = self.env['res.users'].search([('id', '=', values['assign_responsibility'])], limit=1)
        monitoring_record = super(MonitoringMeasurement, self).create(values)
        due_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        if values.get('test_performed_by') != 'third_party':
            self.create_activity(monitoring_record, 'Ready to go legal compliance', 'To Do', assigned_user.id, due_date)

        compliance = {
            "monitoring_measurement_id": monitoring_record.id
        }
        self.env['x.legal.compliance'].create(compliance)



        return monitoring_record

    legal_regulations_id = fields.Many2one('x.legal.regulation', string='legal regulations id', required=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    lr_sno = fields.Char(related='legal_regulations_id.lr_number', string='OPEN LR S.No')
    lr_description = fields.Text(string='LR Description', related='legal_regulations_id.description_lrs')
    lr_requirements = fields.Text(string='LR Requirements', related='legal_regulations_id.lr_requirements')
    title_of_programme = fields.Text(string='Title of Programme', required=True)
    acceptance_criteria = fields.Text(string='Acceptance Criteria', required=True)
    risk_assessment_reference = fields.Char(string='Risk Assessment Reference')
    frequency_of_measurement = fields.Text(string='Frequency of Measurement')
    test_performed_by = fields.Selection(
        [('in_house', 'In-house'),
         ('third_party', 'Third Party Agency')],
        string='Test Performed by', required=True
    )
    select_department = fields.Many2one('hr.department', string='Select Department')
    assign_responsibility = fields.Many2one('res.users', string='Assign Responsibility', domain="[('department_id', '=', select_department )]")
    _rec_name = 'lr_sno'

    def create_activity(self,monitoring_record, summary, activity_type, user_id, date_deadline=None):
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
                'res_model_id': self.env['ir.model']._get('x.monitoring.measurement').id,
                'res_id': monitoring_record.id,
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

    def get_users_with_access_right(self, group_name):
        group_id = self.env.ref(group_name)

        if group_id:
            # Retrieve users who have the specified access right
            users_with_access_right = self.env['res.users'].search([('groups_id', 'in', group_id.id)])
            mail_list = []

            for user in users_with_access_right:
                mail_list.append(user.employee_id.work_email)
            return mail_list
        else:
            return []

    def send_notification(self):
        hse_mail_list = self.get_users_with_access_right('aicomsy_base.access_hse_manager')
        qa_qc_mail_list = self.get_users_with_access_right('aicomsy_base.access_qa_qc_manager')


        managers_mail_list = hse_mail_list + qa_qc_mail_list

        template = self.env.ref('legal_compliance_management.email_template_monitoring_measurement')
        email_values = {
            'email_to': ','.join(str(email) for email in managers_mail_list if isinstance(email, str))

        }

        # Update the context before sending the email
        template.send_mail(self.id, force_send=True, email_values=email_values)




class ComplianceObligation(models.Model):
    _name = 'x.legal.compliance'
    _description = 'Compliance Obligation'

    monitoring_measurement_id = fields.Many2one('x.monitoring.measurement', string='monitoring_measurement_id', required=True)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company, related='monitoring_measurement_id.company_id')
    lr_sno = fields.Char(string='LR S.No.', related='monitoring_measurement_id.lr_sno')
    description_legal_regulation = fields.Text(string='Description of Legal Regulation Standards', related='monitoring_measurement_id.lr_description')
    classification_id = fields.Many2one("x.legal.classification", string="Classification", related='monitoring_measurement_id.legal_regulations_id.classification_id')
    title_of_programme = fields.Text(string='Title of Programme', readonly=True, related='monitoring_measurement_id.title_of_programme')
    test_frequency = fields.Text(string='Test Frequency', readonly=True, related='monitoring_measurement_id.frequency_of_measurement')
    test_performed_by = fields.Selection(
        [('in_house', 'In-house'),
         ('third_party', 'Third Party Agency')],
        string='Test Performed by', readonly=True, related='monitoring_measurement_id.test_performed_by')
    test_performed_on = fields.Datetime(string="Test Performed on", tracking=True)
    test_result = fields.Selection(
        [('pass', 'Pass'),
         ('fail', 'Fail')],
        string='Test Result'
    )
    incident_id = fields.One2many(
        'x.incident.record', 'legal_compliance_id', string='Incident Id'
    )
    test_report = fields.Text(string='Test report')
    attachment_ids = fields.One2many('ir.attachment', 'res_id', string='Upload ', help='Attachment')
    assign_responsibility_id = fields.Many2one('res.users', string='Assign To', related='monitoring_measurement_id.assign_responsibility',
                                            domain="[('department_id', '=', select_department )]")
    is_assign = fields.Boolean(compute="_is_assign")
    def action_open_incident(self):
        return {
            'name': 'All Incident',
            'res_model': 'x.incident.record',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('incident_management.incident_form_view').id,
            'target': 'new',
            'context': {
                'default_description': self.description_legal_regulation,
                'default_inc_date_time': self.date_time,
                'default_legal_compliance_id': self.id

            }
        }

    def get_users_with_access_right(self, group_name):
        group_id = self.env.ref(group_name)

        if group_id:
            # Retrieve users who have the specified access right
            users_with_access_right = self.env['res.users'].search([('groups_id', 'in', group_id.id)])
            mail_list = []

            for user in users_with_access_right:
                mail_list.append(user.employee_id.work_email)
            return mail_list
        else:
            return []

    def send_notification(self):
        hse_mail_list = self.get_users_with_access_right('aicomsy_base.access_hse_manager')
        qa_qc_mail_list = self.get_users_with_access_right('aicomsy_base.access_qa_qc_manager')

        managers_mail_list = hse_mail_list + qa_qc_mail_list

        template = self.env.ref('legal_compliance_management.email_template_legal_compliance')
        email_values = {
            'email_to': ','.join(str(email) for email in managers_mail_list if isinstance(email, str))

        }

        # Update the context before sending the email
        template.send_mail(self.id, force_send=True, email_values=email_values)

    def _is_assign(self):
        self.is_assign = self.env.user == self.assign_responsibility_id
