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


def translation(request):
    source = request.POST.get('translate-box')
    source = " ".join(list(source))

    print(source)
    data = [{
        'id': 100,
        'src': source
    }]

    data = json.dumps(data, ensure_ascii=False).encode('utf-8')

    r = requests.post('http://140.112.147.125:5000/translator/translate', data=data).json()[0][0]
    target = "".join(r.get('tgt').split(' '))

    context = {
        'target': target
    }
    return render(request, 'core/index.html', context=context)
