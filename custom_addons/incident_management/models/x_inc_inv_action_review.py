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
    comments = fields.Text(string="Comments", help='Comments')
    action_follow_up_required = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Action Follow-up Required",
                                                 default="no", help='Action Follow-up Required')
    review_by_ceo_vp_gm_required = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                    string="Review by CEO/VP/GM Required", default="no")
    justification = fields.Text(string="If no, give justification")
    reviewed_by_ceo_vp_gm = fields.Text(string="Reviewed by CEO/VP/GM")
    reviewed_comments = fields.Text(string="Comments")
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
    company_id = fields.Many2one(related="investigation_id.company_id")

    @api.depends('reviewer')
    def _compute_report_closed_by(self):
        for record in self:
            record.report_closed_by = record.reviewer

    def start_review(self):
        self.state = 'review'
        self.investigation_id.incident_id.write({'state': 'action_review'})

    def action_confirm(self):
        self.write({'state': 'followup'})

    def action_return(self):
        self.write({'state': 'review'})
        self.corrective_action_id.write({'state': 'returned'})
        self._return_to_action_party()

    def action_close(self):
        self.write({'state': 'closed'})
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
        self._resubmit_for_review_email()

    def action_return_further_action(self):
        self.write({'state': 'review'})
        self._return_for_further_action_email()

    def action_completion_send_email(self):
        mail_template = self.env.ref('incident_management.email_template_corrective_action_completion')
        mail_template.send_mail(self.id, force_send=True)
        mail_template = self.env.ref('incident_management.email_template_action_review')
        mail_template.send_mail(self.id, force_send=True)

    def _return_to_action_party(self):
        mail_template = self.env.ref('incident_management.email_template_return_to_corrective_action')
        mail_template.send_mail(self.id, force_send=True)

    def _resubmit_for_review_email(self):
        mail_template = self.env.ref('incident_management.email_template_resubmit_for_review')
        mail_template.send_mail(self.id, force_send=True)

    def _return_for_further_action_email(self):
        mail_template = self.env.ref('incident_management.email_template_return_further_action')
        mail_template.send_mail(self.id, force_send=True)

    def action_submit_for_management_review(self):
        self.write({'state': 'management'})
        return True

    def _inv_inc_closure_send_email(self):
        mail_template = self.env.ref('incident_management.email_template_incident_closure')
        mail_template.send_mail(self.id, force_send=True)
