# import from odoo
from odoo import api, fields, models


class IncidentRootCauses(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.root.causes"
    _description = "Oil, Paint, Chemical Spillage, Environmental Incidents or  incidents"

    # --------------------------------------- Fields Declaration ----------------------------------

    investigation_id = fields.Many2one('x.inc.investigation.team', required=True)
    rc_procedure_policy = fields.Many2many('x.inc.rc.procedure.policy')
    rc_tools_ppe = fields.Many2many('x.inc.rc.tools.ppe')
    rc_physical_capabilities = fields.Many2many('x.inc.rc.physical.capabilities')
    rc_other_party_action = fields.Many2many('x.inc.rc.other.party.action')
    rc_maintenance = fields.Many2many('x.inc.rc.maintenance.repair')


class IncRCProcedure(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.rc.procedure.policy"
    _description = "Procedure / Policy/ Pre-Job Planning"

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Procedure / Policy/ Pre-Job Planning")


class IncRCTools(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.rc.tools.ppe"
    _description = "Tools/ Equipment/ PPE"

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Tools/ Equipment/ PPE")


class IncRCPhysicalCapabilities(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.rc.physical.capabilities"
    _description = "Physical Capabilities/ Condition"

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Physical Capabilities/ Condition")


class IncRCOtherPartyAction(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.rc.other.party.action"
    _description = "Other Party Action"

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Other Party Action")


class IncRCPhysicalCapabilities(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.rc.maintenance.repair"
    _description = "Maintenance/ Repair"

    # --------------------------------------- Fields Declaration ----------------------------------

    name = fields.Char(string="Physical Capabilities/ Condition")
