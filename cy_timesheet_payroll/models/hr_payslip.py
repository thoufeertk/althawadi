# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'



    def get_timesheet_hours(self):
        calendar_id = str(self.employee_id.resource_calendar_id.id)
        work_hours = str(self.employee_id.resource_calendar_id.hours_per_day)
        employee_id = str(self.employee_id.id)
        query = """select sum(temp.normal_amount) as normal_day,
                   sum(temp.overtime_amount)as overtime,
                   temp.normal_day as day_val,
                   (sum(temp.normal_amount) + sum(temp.overtime_amount)) as total_hours
                   from (
                   select date,
                   (CASE WHEN (unit_amount - """ + work_hours + """) >= 0
                    THEN """ + work_hours + """ ELSE unit_amount END) as normal_amount,
                   (CASE WHEN (unit_amount - """ + work_hours + """) >= 0
                   THEN (unit_amount - """ + work_hours + """)
                   ELSE 0 END) as overtime_amount,
                   (case when (CAST(extract(isodow from date)-1 AS CHAR) in
                   (select DISTINCT(dayofweek)
                   from resource_calendar_attendance where calendar_id = """ + calendar_id + """ )
                   and
                   (case when (select exists(SELECT resource_calendar_leaves.id
                   from resource_calendar_leaves
                   where resource_calendar_leaves.calendar_id = """ + calendar_id + """ and
                   account_analytic_line.date between resource_calendar_leaves.date_from::date and
                   resource_calendar_leaves.date_to::date and resource_id is Null))
                   then false else true end))
                   then 1 else 0 end) as normal_day,
                   (select exists(SELECT resource_calendar_leaves.id
                   from resource_calendar_leaves
                   where resource_calendar_leaves.calendar_id = """ + calendar_id + """  and
                   account_analytic_line.date between resource_calendar_leaves.date_from::date and
                   resource_calendar_leaves.date_to::date and resource_id is Null)) as leave
                   from account_analytic_line where employee_id= """ + employee_id + """ ) as temp
                   group by temp.normal_day"""
        self._cr.execute(query)
        record = self._cr.dictfetchall()
        normal_day = 0
        overtime = 0
        holiday = 0
        for data in record:
            if data['day_val'] == 1:
                normal_day = data['normal_day']
                overtime = data['overtime']
            if data['day_val'] == 0:
                holiday = data['total_hours']
        self.worked_days_line_ids = None
        self.worked_days_line_ids = [(0,0,{
            'work_entry_type_id': self.env.ref('cy_timesheet_payroll.cy_timesheet_payroll_normal').id,
            'number_of_hours': normal_day,
            'amount': normal_day * self.contract_id.hourly_wage,
        }),
                                     (0,0,{
            'work_entry_type_id': self.env.ref('cy_timesheet_payroll.cy_timesheet_payroll_over_time').id,
            'number_of_hours': overtime,
            'amount': overtime * self.contract_id.normal_overtime_wage,
        }),
                                     (0,0,{
            'work_entry_type_id': self.env.ref('cy_timesheet_payroll.cy_timesheet_payroll_holiday').id,
            'number_of_hours': holiday,
            'amount': holiday * self.contract_id.holiday_overtime_wage,
        })]

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        if self.employee_id:
            self.get_timesheet_hours()
        return