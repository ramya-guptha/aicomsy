from datetime import datetime, timedelta

from odoo import fields, models, api


class ActionReview(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.inv.action.review"
    _description = "Action Review"
    _sql_constraints = [
        ('action_review_uniq', 'unique(investigation_id, corrective_action_id)',
         'Review already exist'),
    ]

    # ---------------------------------------- CRUD METHODS ---------------------------------------

    @api.model
    def create(self, vals_list):
        corrective_action_id = self.env.context.get('default_corrective_action_id')

        action_review = super().create(vals_list)
        # Change the state of the related incident
        if corrective_action_id:
            corrective_action = self.env['x.inc.inv.corrective.actions'].browse(corrective_action_id)
            corrective_action.write({'state': 'completed'})
            self.action_completion_send_email()
        action_review.investigation_id.create_activity('Action Review & Closure: %s' % action_review.corrective_action_id.name, 'To Do', action_review.reviewer.id, action_review.due_date)
        return action_review

    def write(self, vals):
        result = super(ActionReview,self).write(vals)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        } if result else {}

    # --------------------------------------- Fields Declaration ----------------------------------

    investigation_id = fields.Many2one("x.inc.investigation")
    corrective_action_id = fields.Many2one("x.inc.inv.corrective.actions")
    reviewer = fields.Many2one('res.users', string="Reviewer", help='Reviewer')
    review_completion_date = fields.Date(string="Review Completion Date")
    risks_and_opportunities_reviewed = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                        string="Risks and Opportunities Reviewed?", help='Risks and Opportunities Reviewed?')
    job_hazard_analysis_reviewed = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="JHAs Reviewed?",
                                                    help="Job Hazard Analysis reviewed?")
    report_closed_by = fields.Many2one('res.users', string="Report Closed by", compute='_compute_report_closed_by',
                                       store=True, help='Report Closed by', domain="[('company_id', '=', company_id)]")
    closure_date = fields.Date(string="Closure Date")

    action_follow_up_required = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Action Follow-up Required",
                                                 default="no", help='Action Follow-up Required')
    review_by_ceo_vp_gm_required = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                    string="Review by CEO/VP/GM Required", default="no")
    justification = fields.Text(string="If no, give justification")
    reviewed_by_ceo_vp_gm = fields.Text(string="Reviewed by CEO/VP/GM")
    management_reviewed_comments = fields.Text(string="Comments")
    closure_comments = fields.Text(string="Closure Comments")
    followup_comments = fields.Text(string="Followup Comments", help='Comments')
    followup_feedback_comments = fields.Text(string="Followup Feedback Comments", help='Comments')
    resend_ca_comments = fields.Text(string="Review CA Comments", help='Comments')
    send_management_comments = fields.Text(string="Comments to Management Team", help='Comments')
    review_date = fields.Date(string="Date")
    state = fields.Selection(
        selection=[
            ("new", "New"),
            ("review", "Review"),
            ("followup", "Followup"),
            ("management", "Management Review"),
            ("closed", "Closed")
        ],
        string="Status",
        copy=False,
        default="new", help='Status'
    )
    next_step = fields.Selection(
        selection=[
            ("close_ca", "Close the Corrective Action"),
            ("return_to_production_manager", " Resend CA to Production Manager"),
            ("followup_quality_control_inspector", "Followup by Quality Control Inspector"),
            ("send_for_management_review", "Send for Management Review")
        ],
        string="Choose the next action")
    job_position_id = fields.Many2one('hr.job', string='Job Position')
    quality_control_user_id = fields.Many2one('res.users', string='Team Members',
                              domain="[('company_id', '=', company_id), ('employee_id.job_id', '=', job_position_id)]")
    company_id = fields.Many2one(related="investigation_id.company_id")
    due_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    consequences_ids = fields.One2many("x.inc.consequences", related="investigation_id.consequences_ids")
    is_followup_adviser = fields.Boolean(string="Is Followup Adviser", compute="_is_followup_adviser")
    is_reviewer = fields.Boolean(string="Is Followup Adviser", compute="_is_reviewer")

    def _is_reviewer(self):
        self.is_reviewer = self.reviewer == self.env.user

    def _is_followup_adviser(self):
        self.is_followup_adviser = self.quality_control_user_id == self.env.user

    @api.depends('reviewer')
    def _compute_report_closed_by(self):
        for record in self:
            record.report_closed_by = record.reviewer

    def start_review(self):
        self.state = 'review'
        self.investigation_id.incident_id.write({'state': 'action_review'})

    def action_submit(self):
        if self.next_step == "close_ca":
            self._action_close()
        if self.next_step == "return_to_production_manager":
            self._action_return()
        if self.next_step == "followup_quality_control_inspector":
            self._action_followup_qualitycontrol()
        if self.next_step == "send_for_management_review":
            self.action_submit_for_management_review()
        self.investigation_id.mark_activity_as_done('Action Review & Closure: %s' % self.corrective_action_id.name)

    def _action_followup_qualitycontrol(self):
        self.write({'state': 'followup'})
        self.investigation_id.create_activity(
            'Guidance & Advice Production Manager on : %s' % self.corrective_action_id.name, 'To Do',
            self.quality_control_user_id.id,
            self.due_date)
        self.investigation_id.add_log_note(self.followup_comments)

    def _action_return(self):
        self.write({'state': 'review'})
        self.investigation_id.add_log_note(self.resend_ca_comments)
        self.corrective_action_id.write({'state': 'returned'})
        self._return_to_action_party()

    def _action_close(self):
        self.write({'state': 'closed'})
        self.investigation_id.add_log_note(self.closure_comments)
        self._update_investigation_state()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': 'The review has been successfully closed',
                'next': {'type': 'ir.actions.client',
                         'tag': 'soft_reload', },
            }
        }

    def _update_investigation_state(self):
        for review in self:
            investigation = review.investigation_id
            all_closed = True
            if investigation:
                if len(investigation.actions_review_ids) != len(investigation.corrective_actions_ids):
                    all_closed = False
                else:
                    for r in investigation.actions_review_ids:
                        if r.state != 'closed':
                            all_closed = False
            if all_closed:
                investigation.state = 'closed'
                investigation.incident_id.state = 'closed'
                self._inv_inc_closure_send_email()

    def action_resubmit_for_review(self):
        self.write({'state': 'review'})
        self.investigation_id.mark_activity_as_done('Guidance & Advice Production Manager on : %s' % self.corrective_action_id.name)
        self.investigation_id.add_log_note(self.followup_feedback_comments)
        self._resubmit_for_review_email()

    def action_return_further_action(self):
        self.write({'state': 'review'})
        self.investigation_id.add_log_note(self.management_reviewed_comments)
        self.investigation_id.create_activity('Action Review & Closure: %s' % self.corrective_action_id.name, 'To Do', self.reviewer.id,
                                          self.due_date)
        self._return_for_further_action_email()

    def action_completion_send_email(self):
        mail_template = self.env.ref('incident_management.email_template_corrective_action_completion')
        mail_template.send_mail(self.id, force_send=True)
        mail_template = self.env.ref('incident_management.email_template_action_review')
        mail_template.send_mail(self.id, force_send=True)

    def _return_to_action_party(self):
        self.investigation_id.create_activity('Review Corrective action again based on comments: %s' % self.corrective_action_id.name, 'To Do',
                                              self.corrective_action_id.assigner.id,
                                              self.due_date)
        mail_template = self.env.ref('incident_management.email_template_return_to_corrective_action')
        mail_template.send_mail(self.id, force_send=True)

    def _resubmit_for_review_email(self):
        mail_template = self.env.ref('incident_management.email_template_resubmit_for_review')
        mail_template.send_mail(self.id, force_send=True)

    def _return_for_further_action_email(self):
        self.investigation_id.mark_activity_as_done('Management Approval: %s' % self.corrective_action_id.name)
        mail_template = self.env.ref('incident_management.email_template_return_further_action')
        mail_template.send_mail(self.id, force_send=True)

    def action_submit_for_management_review(self):
        self.write({'state': 'management'})
        self.investigation_id.add_log_note(self.send_management_comments)
        self.investigation_id.create_activity('Management Approval: %s' % self.corrective_action_id.name, 'To Do', self.investigation_id.hr_administration.id,
                                         self.due_date)
        return True

    def _inv_inc_closure_send_email(self):
        mail_template = self.env.ref('incident_management.email_template_incident_closure')
        mail_template.send_mail(self.id, force_send=True)
