from django.views.generic import TemplateView
from .services import SalesReportService

class SalesReportView(TemplateView):
    template_name = 'reports/sales_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sales_stats'] = SalesReportService.get_sales_stats()
        return context
