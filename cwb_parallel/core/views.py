import logging
import json
import requests

from django.shortcuts import render, redirect, reverse
from django.views.generic import View, TemplateView

from .cqp import Cqp

logger = logging.getLogger()


class IndexView(TemplateView):
    template_name = 'core/index.html'


class ConcordanceView(View):
    template_name = 'core/results.html'

    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        corpus = self.request.GET.get('corpus')
        alignment = self.request.GET.get('alignment')
        search_mode = self.request.GET.get('search-mode')

        if search_mode == 'simple':
            query = f"""'{query}'"""

        cqp = Cqp(query_cmd=query, corpus=corpus, alignment=alignment)
        if cqp.results:
            context = {
                'data': True,
                'query': query,
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
                'data': False,
                'query': query,
            }
        return render(self.request, self.template_name, context=context)


class TranslationView(View):
    template_name = 'core/translation.html'

    def get(self, request, *args, **kwargs):
        return render(self.request, self.template_name)

    def post(self, request, *args, **kwargs):

        source = self.request.POST.get('translate-src')
        source = " ".join(list(source))
        trans_direction = self.request.POST.get('trans-direction')

        context = {
            'source': self.request.POST.get('translate-src'),
        }
        model_names = ['target_rnn', 'target_transformer']

        if trans_direction == 'tm2mm':
            model_id = [100, 200]
        else:
            model_id = [101, 201]

        print(source)
        for name, model in zip(model_names, model_id):
            data = [{
                'id': model,
                'src': source
            }]

            data = json.dumps(data, ensure_ascii=False).encode('utf-8')

            r = requests.post('http://140.112.147.132:5000/translator/translate', data=data).json()[0][0]
            target = "".join(r.get('tgt').split(' '))

            context.update({name: target})

        return render(request, self.template_name, context=context)
