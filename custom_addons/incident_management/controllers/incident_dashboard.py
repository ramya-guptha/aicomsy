import datetime

from odoo import http
from odoo.http import request


class IncidentFilter(http.Controller):

    @http.route('/incident/filter', auth='public', type='json')
    def incident_filter(self):
        """

        Summery:
            transferring data to the selection field that works as a filter
        Returns:
            type:list of lists , it contains the data for the corresponding
            filter.


        """
        location_list = []
        location_ids = request.env['x.location'].search([])
        # getting location data
        for location_id in location_ids:
            dic = {'name': location_id.name,
                   'id': location_id.id}
            location_list.append(dic)
        return [location_list]

    @http.route('/incident/filter-apply', auth='public', type='json')
    def incident_filter_apply(self, **kw):
        """
        Summery:
            transferring data after filter 9is applied
        Args:
            kw(dict):This parameter contain value of selection field
        Returns:
            type:dict, it contains the data for the corresponding
            filter.

        and transferring data to ui after filtration.


        """
        data = kw['data']
        # checking the employee selected or not
        employee_id = request.env['hr.employee'].search(
            [('user_id', '=', data['uid'])]).id
        if data['location'] == 'null':
            loc_selected = [location.id for location in
                            request.env['x.location'].search([])]
        else:
            loc_selected = [int(data['location'])]
        start_date = data['start_date']
        end_date = data['end_date']
        incidents = data['incidents']
        uid = data['uid']
        incidents_in_location = request.env['x.incident.record'].search(
                [
                    ('location', 'in', loc_selected),
                    ]
        )
        incidents_in_location_ids = [incident.id for incident in incidents_in_location]

        if(start_date != 'null' and end_date != 'null'):
            if incidents != 'null':
                incidents_in_location = request.env['x.incident.record'].search(
                    [('location', 'in', loc_selected),
                        ('inc_date_time', '>=', start_date),
                        ('inc_date_time', '<=', end_date),
                        '|',
                        ('notified_by', '=', employee_id),
                        ('create_uid', '=', uid),
                    ]
                )
                incidents_in_location_ids = [incident.id for incident in incidents_in_location]
            else:
                incidents_in_location = request.env['x.incident.record'].search(
                    [
                        ('location', 'in', loc_selected),
                        ('inc_date_time', '>=', start_date),
                        ('inc_date_time', '<=', end_date),
                    ]
                )
                incidents_in_location_ids = [incident.id for incident in incidents_in_location]

        elif start_date != 'null':

            if incidents != 'null':
                incidents_in_location = request.env['x.incident.record'].search(
                    [('location', 'in', loc_selected),
                     ('inc_date_time', '>=', start_date),
                     '|',
                     ('notified_by', '=', employee_id),
                     ('create_uid', '=', uid),
                     ]
                )
                incidents_in_location_ids = [incident.id for incident in incidents_in_location]
            else:
                incidents_in_location = request.env['x.incident.record'].search(
                    [
                        ('location', 'in', loc_selected),
                        ('inc_date_time', '>=', start_date),

                    ]
                )
                incidents_in_location_ids = [incident.id for incident in incidents_in_location]

        elif end_date != 'null':
            if incidents != 'null':
                incidents_in_location = request.env['x.incident.record'].search(
                    [('location', 'in', loc_selected),
                        ('inc_date_time', '<=', end_date),
                        '|',
                        ('notified_by', '=', employee_id),
                        ('create_uid', '=', uid),
                    ]
                )
                incidents_in_location_ids = [incident.id for incident in incidents_in_location]
            else:
                incidents_in_location = request.env['x.incident.record'].search(
                    [
                        ('location', 'in', loc_selected),
                        ('inc_date_time', '<=', end_date),
                    ]
                )
                incidents_in_location_ids = [incident.id for incident in incidents_in_location]
        return {
            'total_locations': loc_selected,
            'total_incidents_ids': incidents_in_location_ids,
        }
