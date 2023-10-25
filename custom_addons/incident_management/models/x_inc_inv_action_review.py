from odoo import fields, models


class ActionReview(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.inv.action.review"
    _description = "Action Review"

    # --------------------------------------- Fields Declaration ----------------------------------

    investigation_id = fields.Many2one("x.inc.investigation")
    corrective_action_id = fields.Many2one("x.inc.inv.corrective.actions")
    reviewer = fields.Many2one('res.users', string="Reviewer")
    review_completion_date = fields.Date(string="Review Completion Date")
    risks_and_opportunities_reviewed = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                        string="Risks and Opportunities Reviewed?")
    job_hazard_analysis_reviewed = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="JHAs Reviewed?",
                                                    help="Job Hazard Analysis reviewed?")
    status = fields.Char(string="Status")
    report_closed_by = fields.Many2one('hr.employee', string="Report Closed by")
    closure_date = fields.Date(string="Closure Date")
    comments = fields.Text(string="Comments")
    action_follow_up_required = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Action Follow-up Required")
    review_by_ceo_vp_gm_required = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                    string="Review by CEO/VP/GM Required")
    justification = fields.Text(string="If no, give justification")
    reviewed_by_ceo_vp_gm = fields.Text(string="Reviewed by CEO/VP/GM")
    reviewed_comments = fields.Text(string="Comments")
    review_date = fields.Date(string="Date")

    def action_close(self):
        self.write({'justification': 'close'})

    def action_return_for_review(self):
        self.write({'justification': 'return_for_review'})

    def action_confirm(self):
        self.write({'justification': 'close'})

    def action_return(self):
        self.write({'justification': 'return'})
