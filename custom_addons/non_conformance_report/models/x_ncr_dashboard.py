# -*- coding: utf-8 -*-
import random
from odoo import api, fields, models, tools
from datetime import datetime


class NCRDashboard(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.ncr.dashboard"
    _description = "NCR Dashboard Charts"
    _auto = False

    @api.model
    def get_ncr_by_location(self, start_date, end_date, location,src, ncr):

        # Your initial query
        base_query = """ SELECT DATE(
                                TO_CHAR(ncr_open_date, 'YYYY') || '-' || 
                                TO_CHAR(ncr_open_date, 'MM') || '-01'
                            ) AS MOM,  loc.name, count(loc.name)
                        FROM x_ncr_report report
                        LEFT JOIN x_location loc on loc.id = report. tag_no_location
                        LEFT JOIN x_ncr_nc as nc on nc.ncr_id = report.id"""

        # Construct the WHERE clause based on conditions
        conditions = []
        if (start_date is not None and start_date != '') and (end_date is not None and end_date != ''):
            conditions.append(f"ncr_open_date BETWEEN '{start_date}'  AND  '{end_date}'")

        elif start_date is not None and start_date != '':
            conditions.append(f"(ncr_open_date >= '{start_date}'")

        elif end_date is not None and end_date != '':
            conditions.append(f"(ncr_open_date <= '{end_date}')")

        if src is not None and src != 'null':
            conditions.append(f"source_of_nc = '{src}'")

        if location is not None and location != 'null':
            conditions.append(f"tag_no_location = '{location}'")

        if ncr is not None and ncr != 'null':
            conditions.append(f"(report.create_uid = '{self.env.uid}' OR report.ncr_initiator_id = '{self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id}' "
                              f" OR report.ncr_approver_id = '{self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id}')")

        where_clause = " AND ".join(conditions)  # Final query with the dynamically constructed WHERE clause
        if where_clause:
            where_clause = f" WHERE {where_clause}"

        final_query = f"{base_query} {where_clause} GROUP BY mom,loc.name ORDER BY MOM"
        self.env.cr.execute(final_query)
        result = self.env.cr.fetchall()

        labels = [record[0] for record in result]
        data = [record[2] for record in result]
        classification = [record[1] for record in result]
        return {'labels': labels, 'data': data, 'classification': classification}

    @api.model
    def get_ncr_source_classification(self, start_date, end_date, location, src, ncr):
        # Your initial query
        base_query = """SELECT  DATE(
                                TO_CHAR(ncr_open_date, 'YYYY') || '-' || 
                                TO_CHAR(ncr_open_date, 'MM') || '-01'
                            ) AS mom,                     
                src.name as ncs_source, count(src.name) as count
                FROM x_ncr_report as report  
                LEFT JOIN x_ncr_nc as nc on nc.ncr_id = report.id
                LEFT JOIN x_ncr_source  as src ON nc.source_of_nc = src.id"""

        # Construct the WHERE clause based on conditions
        conditions = []
        if (start_date is not None and start_date != '') and (end_date is not None and end_date != ''):
            conditions.append(f"ncr_open_date BETWEEN '{start_date}'  AND  '{end_date}'")

        elif start_date is not None and start_date != '':
            conditions.append(f"(ncr_open_date >= '{start_date}'")

        elif end_date is not None and end_date != '':
            conditions.append(f"(ncr_open_date <= '{end_date}')")

        if src is not None and src != 'null':
            conditions.append(f"source_of_nc = '{src}'")

        if location is not None and location != 'null':
            conditions.append(f"tag_no_location = '{location}'")

        if ncr is not None and ncr != 'null':
            conditions.append(
                f"(report.create_uid = '{self.env.uid}' OR report.ncr_initiator_id = '{self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id}' "
                f" OR report.ncr_approver_id = '{self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id}')")

        where_clause = " AND ".join(conditions)  # Final query with the dynamically constructed WHERE clause
        if where_clause:
            where_clause = f" WHERE {where_clause}"

        final_query = f"{base_query} {where_clause} GROUP BY mom,ncs_source"
        print("Final Query",final_query)
        self.env.cr.execute(final_query)
        result = self.env.cr.fetchall()

        labels = [record[0] for record in result]
        data = [record[2] for record in result]
        classification = [record[1] for record in result]

        return {'labels': labels, 'data': data, 'classification': classification}

    @api.model
    def get_cost_of_rework(self, start_date, end_date, location, src, ncr):
        # Your initial query
        base_query = """SELECT  DATE(
                            TO_CHAR(ncr_open_date, 'YYYY') || '-' || 
                            TO_CHAR(ncr_open_date, 'MM') || '-01'
                        ) AS mom, ncr_type.name, sum(disposition_cost) as rework
                    FROM x_ncr_report AS  report
                    LEFT JOIN x_ncr_nc AS nc ON report.id = nc.ncr_id
                    LEFT JOIN x_ncr_type AS ncr_type ON report.ncr_type_id = ncr_type.id
                    LEFT JOIN x_ncr_part AS part ON nc.id = part.nc_details_id"""

        # Construct the WHERE clause based on conditions
        conditions = []
        if (start_date is not None and start_date != '') and (end_date is not None and end_date != ''):
            conditions.append(f"ncr_open_date BETWEEN '{start_date}'  AND  '{end_date}'")

        elif start_date is not None and start_date != '':
            conditions.append(f"(ncr_open_date >= '{start_date}'")

        elif end_date is not None and end_date != '':
            conditions.append(f"(ncr_open_date <= '{end_date}')")

        if src is not None and src != 'null':
            conditions.append(f"source_of_nc = '{src}'")

        if location is not None and location != 'null':
            conditions.append(f"tag_no_location = '{location}'")

        if ncr is not None and ncr != 'null':
            conditions.append(
                f"(report.create_uid = '{self.env.uid}' OR report.ncr_initiator_id = '{self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id}' "
                f" OR report.ncr_approver_id = '{self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id}')")

        where_clause = " AND ".join(conditions)  # Final query with the dynamically constructed WHERE clause
        if where_clause:
            where_clause = f" WHERE {where_clause}"

        final_query = f"{base_query} {where_clause} GROUP BY mom, ncr_type_id, ncr_type.name"
        print("Final Query", final_query)

        self.env.cr.execute(final_query)
        result = self.env.cr.fetchall()

        labels = [record[0] for record in result]
        data = [record[2] for record in result]
        classification = [record[1] for record in result]

        return {'labels': labels, 'data': data, 'classification': classification}

    @api.model
    def get_customer_backcharges(self, start_date, end_date, location, src, ncr):
        # Your initial query
        base_query = """SELECT  DATE(
                                TO_CHAR(ncr_open_date, 'YYYY') || '-' || 
                                TO_CHAR(ncr_open_date, 'MM') || '-01'
                            ) AS mom, project_number, sum(estimated_backcharge_price) as backcharges
                            FROM x_ncr_report AS  report
                            LEFT JOIN x_ncr_nc AS nc ON report.id = nc.ncr_id
                            LEFT JOIN x_ncr_part AS part ON nc.id = part.nc_details_id"""

        # Construct the WHERE clause based on conditions
        conditions = []
        if (start_date is not None and start_date != '') and (end_date is not None and end_date != ''):
            conditions.append(f"ncr_open_date BETWEEN '{start_date}'  AND  '{end_date}'")

        elif start_date is not None and start_date != '':
            conditions.append(f"(ncr_open_date >= '{start_date}'")

        elif end_date is not None and end_date != '':
            conditions.append(f"(ncr_open_date <= '{end_date}')")

        if src is not None and src != 'null':
            conditions.append(f"source_of_nc = '{src}'")

        if location is not None and location != 'null':
            conditions.append(f"tag_no_location = '{location}'")

        if ncr is not None and ncr != 'null':
            conditions.append(
                f"(report.create_uid = '{self.env.uid}' OR report.ncr_initiator_id = '{self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id}' "
                f" OR report.ncr_approver_id = '{self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id}')")

        where_clause = " AND ".join(conditions)  # Final query with the dynamically constructed WHERE clause
        if where_clause:
            where_clause = f" WHERE {where_clause}"
        final_query = f"{base_query} {where_clause} GROUP BY mom, project_number"

        self.env.cr.execute(final_query)
        result = self.env.cr.fetchall()

        labels = [record[0] for record in result]
        data = [record[2] for record in result]
        classification = [record[1] for record in result]

        return {'labels': labels, 'data': data, 'classification': classification}


