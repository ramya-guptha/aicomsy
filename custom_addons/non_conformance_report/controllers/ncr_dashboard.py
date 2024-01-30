import datetime

from odoo import http
from odoo.http import request


class NCRFilter(http.Controller):

    @http.route('/ncr/filter', auth='public', type='json')
    def ncr_filter(self, **kw):
        """

        Summery:
            transferring data to the selection field that works as a filter
        Returns:
            type:list of lists , it contains the data for the corresponding
            filter.


        """
        location_list = []
        source_list = []
        company_id = kw.get('params', {}).get('company_id')
        location_ids = request.env['x.location'].search([('company_id', '=', company_id)])
        ncr_source_ids = request.env['x.ncr.source'].search([('company_id', '=', company_id)])
        # getting location data
        for location_id in location_ids:
            dic = {'name': location_id.name,
                   'id': location_id.id}
            location_list.append(dic)
        # getting location data
        for ncr_source_id in ncr_source_ids:
            dic = {'name': ncr_source_id.name,
                   'id': ncr_source_id.id}
            source_list.append(dic)
        return [location_list, source_list]

