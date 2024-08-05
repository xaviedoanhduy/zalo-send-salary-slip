from odoo import models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def send_payslip_via_zalo(self):
        zalo_integration = self.env['zalo.integration'].search([], limit=1)
        if not zalo_integration:
            raise ValueError("Zalo integration not configured")

        for payslip in self:
            # Generate PDF
            pdf_content, _ = self.env.ref('hr_payroll.action_report_payslip').sudo()._render_qweb_pdf([payslip.id])

            # Upload PDF to Zalo
            file_name = f"Payslip_{payslip.employee_id.name}_{payslip.date_from}_{payslip.date_to}.pdf"
            file_token = zalo_integration.upload_file_to_zalo(pdf_content, file_name)

            # Send message with file
            if payslip.employee_id.zalo_id:  # Assuming you have a zalo_id field in res.partner
                message = f"Dear {payslip.employee_id.name}, here is your payslip for the period {payslip.date_from} to {payslip.date_to}."
                zalo_integration.send_zalo_message(payslip.employee_id.zalo_id, message, file_token)
            else:
                raise ValueError(f"No Zalo ID found for employee {payslip.employee_id.name}")
