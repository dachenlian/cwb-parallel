from django.shortcuts import render
from django.views.generic import View, TemplateView

from .cqp import Cqp


class IndexView(TemplateView):
    template_name = 'core/index.html'


class ResultsView(View):
    template_name = 'core/results.html'

    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        corpus = self.request.GET.get('corpus')
        alignment = self.request.GET.get('alignment')

        cqp = Cqp(query_cmd=query, corpus=corpus, alignment=alignment)
        if cqp.results:
            context = {
                'data': True
            }
            if alignment:
                context.update({
                    'alignment': True,
                    'len': len(cqp.src),
                    'results': list(zip(cqp.src, cqp.tgt))
                })
            else:
                context.update({
                    'alignment': False,
                    'len': len(cqp),
                    'results': cqp.results,
                })
        else:
            context = {
                'data': False
            }
        return render(self.request, self.template_name, context=context)

