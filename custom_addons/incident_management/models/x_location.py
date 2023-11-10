# -*- coding: utf-8 -*-

# import from odoo
from odoo import api, fields, models


class Location(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.location"
    _description = "Zones and locations in a facility"
    _parent_name = "location_id"
    _parent_store = True
    _rec_name = 'name'
    _rec_names_search = ['name']
    _check_company_auto = True
    _sql_constraints = [
        ('name_uniq', 'unique(name,location_id)', 'Location name and it\'s parent must be unique !'),
    ]

    # --------------------------------------- Fields Declaration ----------------------------------
    name = fields.Char('Location Name', required=True)
    active = fields.Boolean('Active', default=True,
                            help="By unchecking the active field, you may hide a location without deleting it.")
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True,
        store=True)
    usage = fields.Selection([
        ('supplier', 'Vendor Location'),
        ('view', 'View'),
        ('internal', 'Internal Location'),
        ('customer', 'Customer Location'),
        ('inventory', 'Inventory Loss'),
        ('production', 'Production'),
        ('transit', 'Transit Location'),
        ('others', 'Others')], string='Location Type',
        default='internal', index=True, required=True,
        help="* Vendor Location: Virtual location representing the source location for products coming from your vendors"
             "\n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products"
             "\n* Internal Location: Physical locations inside your own warehouses,"
             "\n* Customer Location: Virtual location representing the destination location for products sent to your customers"
             "\n* Inventory Loss: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)"
             "\n* Production: Virtual counterpart location for production operations: this location consumes the components and produces finished products"
             "\n* Transit Location: Counterpart location that should be used in inter-company or inter-warehouses operations")
    location_id = fields.Many2one(
        'x.location', 'Parent Location', index=True, ondelete='cascade',
        help="The parent location that includes this location. Example : The 'Dispatch Zone' is the 'Gate 1' parent "
             "location.")
    child_ids = fields.One2many('x.location', 'location_id', 'Contains')
    child_internal_location_ids = fields.Many2many(
        'x.location',
        string='Internal locations among descendants',
        compute='_compute_child_internal_location_ids',
        recursive=True,
        help='This location (if it\'s internal) and all its descendants filtered by type=Internal.'
    )
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company, index=True,
        help='Let this field empty if this location is shared between companies')

    location_manager = fields.Many2one('res.users', string="Location Manager")
    location_alternate_1 = fields.Many2one('res.users', string="Alternative Location Manager 1")
    location_alternate_2 = fields.Many2one('res.users', string="Alternative Location Manager 2")
    parent_path = fields.Char(index=True, unaccent=False)

    @api.depends('name', 'location_id.complete_name')
    def _compute_complete_name(self):
        for location in self:
            if location.location_id:
                location.complete_name = '%s / %s' % (location.location_id.complete_name, location.name)
            else:
                location.complete_name = location.name

    @api.depends('child_ids.usage', 'child_ids.child_internal_location_ids')
    def _compute_child_internal_location_ids(self):
        # batch reading optimization is not possible because the field has recursive=True
        for loc in self:
            loc.child_internal_location_ids = self.search([('id', 'child_of', loc.id), ('usage', '=', 'internal')])
