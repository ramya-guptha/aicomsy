# -*- coding: utf-8 -*-
import random
from odoo import api, fields, models, tools
from datetime import datetime


class Incident(models.Model):
    _inherit = 'x.incident.record'

    @api.model
    def get_tiles_data(self):
        all_incidents = self.env['x.incident.record'].search([])
        all_locations = self.env['x.location'].search([])

        return {
            'total_incidents': len(all_incidents),
            'total_incidents_ids': all_incidents.ids,
            'total_locations': len(all_locations),
            'total_locations_ids': all_locations.ids,
        }


class NormalDays(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.report.normal.days"
    _description = "Normal Days in the month"

    _auto = False

    @api.model
    def get_normal_mom(self, start_date, end_date, location, incident_type):
        start_date_object = None
        end_date_object = None

        if start_date is not None and start_date != '':
            start_date_object = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date is not None and end_date != '':
            end_date_object = datetime.strptime(end_date, "%Y-%m-%d")

        # Extract month and year

        # Your initial query
        base_query = """SELECT MAKE_DATE(year, month, 1),
                        working_days, 
                        working_days - COUNT(DISTINCT DATE(inc_date_time)) as normal_days           
                        FROM x_company_monthly_metrics AS x  
                        LEFT JOIN  x_incident_record ON EXTRACT(MONTH from inc_date_time) = x.month             
                        AND EXTRACT(YEAR from inc_date_time) = x.year 
                        """

        # Construct the WHERE clause based on conditions
        conditions = []
        if (start_date is not None and start_date != '') and (end_date is not None and end_date != ''):
            conditions.append(f"inc_date_time BETWEEN '{start_date}'  AND  '{end_date}'"
                              f" OR Make_date(year, month, 1) BETWEEN Make_date('{start_date_object.year}', '{start_date_object.month}', 1)"
                              f" AND Make_date('{end_date_object.year}', '{end_date_object.month}', 1)"
                              f" AND inc_date_time  is NULL")

        elif start_date is not None and start_date != '':
            conditions.append(
                f"(inc_date_time >= '{start_date}'  OR inc_date_time  is NULL) AND (year  >= '{start_date_object.year}'"
                f" and month >= '{start_date_object.month}')")

        elif end_date is not None and end_date != '':
            conditions.append(
                f"(inc_date_time <= '{end_date}' OR inc_date_time  is NULL) AND (year  <= '{end_date_object.year}'"
                f" and month <= '{end_date_object.month}')  ")

        if location is not None and location != 'null':
            if (len(conditions) > 0):
                conditions.append(f"location = '{location}'")
            else:
                conditions.append(f"(location = '{location}' OR inc_date_time  is NULL) ")

        if incident_type is not None and incident_type != 'null':
            conditions.append(f"(x_incident_record.create_uid = '{self.env.uid}' OR x_incident_record.notified_by = '{self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id}')")

        where_clause = " AND ".join(conditions)  # Final query with the dynamically constructed WHERE clause
        if where_clause:
            where_clause = f" WHERE {where_clause}"
        final_query = f"{base_query} {where_clause} GROUP BY year, month, working_days ORDER BY year, month"

        self.env.cr.execute(final_query)
        result = self.env.cr.fetchall()

        labels = [record[0] for record in result]
        data = [record[2] for record in result]

        return {'labels': labels, 'data': data}

    @api.model
    def get_incident_frequency_rate(self, start_date, end_date, location, incident_type):
        start_date_object = None
        end_date_object = None

        if start_date is not None and start_date != '':
            start_date_object = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date is not None and end_date != '':
            end_date_object = datetime.strptime(end_date, "%Y-%m-%d")

        base_query = """SELECT MAKE_DATE(year,month,1) as inc_month_year,
            CASE 
         WHEN x.hour_worked <> 0 
         THEN COUNT(x_incident_record.name) * 200000 / x.hour_worked 
         ELSE 0 -- or another default value
       END as incident_frequency_rate            
    		from  x_company_monthly_metrics as x
            left join x_incident_record  on EXTRACT(MONTH from inc_date_time) = x.month 
            and EXTRACT(YEAR from inc_date_time) = x.year            
            """

        # Construct the WHERE clause based on conditions
        conditions = []

        if (start_date is not None and start_date != '') and (end_date is not None and end_date != ''):
            conditions.append(f"inc_date_time BETWEEN '{start_date}'  AND  '{end_date}'"
                              f" OR Make_date(year, month, 1) BETWEEN Make_date('{start_date_object.year}', '{start_date_object.month}', 1)"
                              f" AND Make_date('{end_date_object.year}', '{end_date_object.month}', 1)"
                              f" AND inc_date_time  is NULL")

        elif start_date is not None and start_date != '':
            conditions.append(
                f"(inc_date_time >= '{start_date}'  OR inc_date_time  is NULL) AND (year  >= '{start_date_object.year}'"
                f" and month >= '{start_date_object.month}')")

        elif end_date is not None and end_date != '':
            conditions.append(
                f"(inc_date_time <= '{end_date}' OR inc_date_time  is NULL) AND (year  <= '{end_date_object.year}'"
                f" and month <= '{end_date_object.month}')  ")

        if location is not None and location != 'null':
            if (len(conditions) > 0):
                conditions.append(f"location = '{location}'")
            else:
                conditions.append(f"(location = '{location}' OR inc_date_time  is NULL) ")

        if incident_type is not None and incident_type != 'null':
            conditions.append(f"(x_incident_record.create_uid = '{self.env.uid}' OR x_incident_record.notified_by = '{self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id}')")

        where_clause = " AND ".join(conditions)  # Final query with the dynamically constructed WHERE clause

        if where_clause:
            where_clause = f" WHERE {where_clause}"

        final_query = f"{base_query} {where_clause} GROUP BY  x.hour_worked,year,month order by inc_month_year"

        self.env.cr.execute(final_query)
        result = self.env.cr.fetchall()

        labels = [record[0] for record in result]
        data = [record[1] for record in result]

        return {'labels': labels, 'data': data}

    @api.model
    def get_severity_classification(self, start_date, end_date, location, incident_type):
        start_date_object = None
        end_date_object = None

        if start_date is not None and start_date != '':
            start_date_object = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date is not None and end_date != '':
            end_date_object = datetime.strptime(end_date, "%Y-%m-%d")

        base_query = """SELECT MAKE_DATE(year, month, 1) as inc_month_year,                           
                s.name as severity_classification_mom,
                count(s.name) as severity_count from x_company_monthly_metrics as x
                left join x_incident_record  ON EXTRACT(MONTH from inc_date_time) = x.month
                        AND EXTRACT(YEAR from inc_date_time) = x.year              
                left join x_inc_severity as s on s.id = severity

                """

        conditions = []

        if (start_date is not None and start_date != '') and (end_date is not None and end_date != ''):
            conditions.append(f"inc_date_time BETWEEN '{start_date}'  AND  '{end_date}'"
                              f" OR Make_date(year, month, 1) BETWEEN Make_date('{start_date_object.year}', '{start_date_object.month}', 1)"
                              f" AND Make_date('{end_date_object.year}', '{end_date_object.month}', 1)"
                              f" AND inc_date_time  is NULL")

        elif start_date is not None and start_date != '':
            conditions.append(
                f"(inc_date_time >= '{start_date}'  OR inc_date_time  is NULL) AND (year  >= '{start_date_object.year}'"
                f" and month >= '{start_date_object.month}')")

        elif end_date is not None and end_date != '':
            conditions.append(
                f"(inc_date_time <= '{end_date}' OR inc_date_time  is NULL) AND (year  <= '{end_date_object.year}'"
                f" and month <= '{end_date_object.month}')  ")

        if location is not None and location != 'null':
            if (len(conditions) > 0):
                conditions.append(f"location = '{location}'")
            else:
                conditions.append(f"(location = '{location}' OR inc_date_time  is NULL) ")

        if incident_type is not None and incident_type != 'null':
            conditions.append(f"(x_incident_record.create_uid = '{self.env.uid}' OR x_incident_record.notified_by = '{self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id}')")

        where_clause = " AND ".join(conditions)  # Final query with the dynamically constructed WHERE clause

        if where_clause:
            where_clause = f" WHERE {where_clause}"

        final_query = f"{base_query} {where_clause} GROUP BY year, month, s.name order by inc_month_year, s.name"

        self.env.cr.execute(final_query)
        result = self.env.cr.fetchall()
        labels = [record[0] for record in result]
        data = [record[2] for record in result]
        classification = [record[1] for record in result]

        return {'labels': labels, 'data': data, 'classification': classification}

    @api.model
    def get_incident_status(self, start_date, end_date, location, incident_type):
        start_date_object = None
        end_date_object = None

        if start_date is not None and start_date != '':
            start_date_object = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date is not None and end_date != '':
            end_date_object = datetime.strptime(end_date, "%Y-%m-%d")

        base_query = """select count(name),state from x_incident_record  
                """
        conditions = []

        if (start_date is not None and start_date != '') and (end_date is not None and end_date != ''):
            conditions.append(f"inc_date_time BETWEEN '{start_date}'  AND  '{end_date}'")

        elif start_date is not None and start_date != '':
            conditions.append(
                f"inc_date_time >= '{start_date}'")

        elif end_date is not None and end_date != '':
            conditions.append(
                f"(inc_date_time <= '{end_date}') ")

        if location is not None and location != 'null':
            conditions.append(f"location = '{location}'")

        if incident_type is not None and incident_type != 'null':
            conditions.append(f"(x_incident_record.create_uid = '{self.env.uid}' OR x_incident_record.notified_by = '{self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id}')")

        where_clause = " AND ".join(conditions)  # Final query with the dynamically constructed WHERE clause

        if where_clause:
            where_clause = f" WHERE {where_clause}"

        final_query = f"{base_query} {where_clause} GROUP BY state "

        self.env.cr.execute(final_query)
        result = self.env.cr.fetchall()

        labels = [record[1] for record in result]
        data = [record[0] for record in result]

        return {'labels': labels, 'data': data}


class IncidentSeverityRate(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.report.severity.rate"
    _description = "Incident Severity Rate"
    _auto = False

    @api.model
    def get_severity_rate(self, start_date, end_date, location, incident_type):
        start_date_object = None
        end_date_object = None

        if start_date is not None and start_date != '':
            start_date_object = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date is not None and end_date != '':
            end_date_object = datetime.strptime(end_date, "%Y-%m-%d")
        base_query = """SELECT  MAKE_DATE(year, month ,1) as inc_month_year,             
                          round((sum(quantity) * 200000 / x.hour_worked)::numeric,2) as incident_severity_rate
                          FROM x_company_monthly_metrics AS x
    					  LEFT JOIN  x_incident_record inc ON EXTRACT(MONTH FROM inc.inc_date_time) = x.month AND EXTRACT(YEAR FROM inc.inc_date_time) = x.year
                          LEFT JOIN x_inc_investigation inv ON inc.id = inv.incident_id
                          LEFT JOIN x_inc_consequences con ON con.investigation_id = inv.id
                          LEFT JOIN x_inc_action_damage damage ON damage.id = con.actions_damages               

                         """

        conditions = []

        conditions.append(f" (damage.name='Lost Work Days' or damage.name is NULL)")

        if (start_date is not None and start_date != '') and (end_date is not None and end_date != ''):
            conditions.append(f"inc_date_time BETWEEN '{start_date}'  AND  '{end_date}'"
                              f" OR Make_date(year, month, 1) BETWEEN Make_date('{start_date_object.year}', '{start_date_object.month}', 1)"
                              f" AND Make_date('{end_date_object.year}', '{end_date_object.month}', 1)"
                              f" AND inc_date_time  is NULL")

        elif start_date is not None and start_date != '':
            conditions.append(
                f"(inc_date_time >= '{start_date}'  OR inc_date_time  is NULL) AND (year  >= '{start_date_object.year}'"
                f" and month >= '{start_date_object.month}')")

        elif end_date is not None and end_date != '':
            conditions.append(
                f"(inc_date_time <= '{end_date}' OR inc_date_time  is NULL) AND (year  <= '{end_date_object.year}'"
                f" and month <= '{end_date_object.month}')  ")

        if location is not None and location != 'null':
            if (len(conditions) > 0):
                conditions.append(f"location = '{location}'")
            else:
                conditions.append(f"(location = '{location}' OR inc_date_time  is NULL) ")

        if incident_type is not None and incident_type != 'null':
            conditions.append(f"(inc.create_uid = '{self.env.uid}' OR inc.notified_by = '{self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id}')")

        where_clause = " AND ".join(conditions)  # Final query with the dynamically constructed WHERE clause

        if where_clause:
            where_clause = f" WHERE {where_clause}"

        final_query = f"{base_query} {where_clause}  GROUP BY  year, month,x.hour_worked order by inc_month_year "

        self.env.cr.execute(final_query)
        result = self.env.cr.fetchall()

        labels = [record[0] for record in result]
        data = [record[1] for record in result]
        colors = []
        color_code = self.get_color_code()
        for label in labels:
            colors.append(color_code)

        return {'labels': labels, 'data': data, 'color': colors}

    def get_color_code(self):
        """
        Summery:
            the function is for creating the dynamic color code.
        return:
            type:variable containing color code.
        """
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        return color


class IncidentsCostImpact(models.Model):
    # ---------------------------------------- Private Attributes ---------------------------------

    _name = "x.inc.report.cost.impact"
    _description = "Incident Cost Impact"
    _auto = False

    @api.model
    def get_cost_impact(self, start_date, end_date, location, incident_type):
        start_date_object = None
        end_date_object = None

        if start_date is not None and start_date != '':
            start_date_object = datetime.strptime(start_date, "%Y-%m-%d")

        if end_date is not None and end_date != '':
            end_date_object = datetime.strptime(end_date, "%Y-%m-%d")

        # Construct the WHERE clause based on conditions
        conditions = []
        if (start_date is not None and start_date != '') and (end_date is not None and end_date != ''):
            conditions.append(f"inc_date_time BETWEEN '{start_date}'  AND  '{end_date}'"
                              f" OR Make_date(year, month, 1) BETWEEN Make_date('{start_date_object.year}', '{start_date_object.month}', 1)"
                              f" AND Make_date('{end_date_object.year}', '{end_date_object.month}', 1)"
                              f" AND inc_date_time  is NULL")

        elif start_date is not None and start_date != '':
            conditions.append(
                f"(inc_date_time >= '{start_date}'  OR inc_date_time  is NULL) AND (year  >= '{start_date_object.year}'"
                f" and month >= '{start_date_object.month}')")

        elif end_date is not None and end_date != '':
            conditions.append(
                f"(inc_date_time <= '{end_date}' OR inc_date_time  is NULL) AND (year  <= '{end_date_object.year}'"
                f" and month <= '{end_date_object.month}')  ")

        if location is not None and location != 'null':
            if (len(conditions) > 0):
                conditions.append(f"location = '{location}'")
            else:
                conditions.append(f"(location = '{location}' OR inc_date_time  is NULL) ")

        if incident_type is not None and incident_type != 'null':
            conditions.append(f"(inc.create_uid = '{self.env.uid}' OR inc.notified_by = '{self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).id}')")

        where_clause = " AND ".join(conditions)  # Final query with the dynamically constructed WHERE clause

        base_query = """ SELECT Make_date(year, month, 1)          AS start_date,
                           To_char(inc_date_time, 'Mon YYYY') AS inc_month_year,
                           Extract(month FROM inc_date_time)  AS inc_month,
                           Extract(year FROM inc_date_time)   AS inc_year,
                           SUM(total_cost),
                           CASE
                             WHEN SUM(total_cost) IS NULL THEN 0
                             ELSE Round(( ( SUM(total_cost) / total_sales ) * 100 ) :: NUMERIC, 2)
                           END                                AS cost_ratio
                    FROM   x_company_monthly_metrics AS x
                           left join x_incident_record inc
                                  ON Extract(month FROM inc.inc_date_time) =
                                     Cast(x.month AS INTEGER)
                                     AND Extract(year FROM inc.inc_date_time) = Cast(
                                         x.year AS INTEGER)
                           left join x_inc_investigation inv
                                  ON inc.id = inv.incident_id
                           left join x_inc_consequences con
                                  ON con.investigation_id = inv.id
                           left join x_inc_action_damage damage
                                  ON damage.id = con.actions_damages
                     """

        if where_clause:
            where_clause = f" WHERE {where_clause}"
        final_query = (f"{base_query} {where_clause} GROUP  BY Extract(month FROM inc_date_time), "
                       f"Extract(year FROM inc_date_time), To_char(inc_date_time, 'Mon YYYY'), x.total_sales, year, month "
                       f"ORDER  BY start_date")

        self.env.cr.execute(final_query)
        result = self.env.cr.fetchall()

        labels = [record[0] for record in result]
        data = [record[5] for record in result]

        return {'labels': labels, 'data': data}
