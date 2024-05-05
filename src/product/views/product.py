import math
from django.views import generic
from django.db.models import Count, Q

from product.models import Variant, Product, ProductVariant, ProductVariantPrice


class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context


class ListProductView(generic.TemplateView):
    template_name = 'products/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        title = self.request.GET.get('title', '')
        selected_variant = self.request.GET.get('variant', '')
        price_from = self.request.GET.get('price_from', '')
        price_to = self.request.GET.get('price_to', '')
        selected_date = self.request.GET.get('date', '').split('-')

        if price_from == '':
            price_from_int = 0
        else:
            price_from_int = int(price_from)

        if price_to == '':
            price_to_int = 100000
        else:
            price_to_int = int(price_to)

        page = int(kwargs['page'])
        products = Product.objects.filter(Q(title__icontains=title) &
                                        (Q(productvariantprice__product_variant_one__variant_title__icontains=selected_variant) | 
                                        Q(productvariantprice__product_variant_two__variant_title__icontains=selected_variant) | 
                                        Q(productvariantprice__product_variant_three__variant_title__icontains=selected_variant)) & 
                                        Q(productvariantprice__price__gte=price_from_int) & 
                                        Q(productvariantprice__price__lte=price_to_int)).distinct()
        
        if selected_date[0] != '':
            products = products.filter(Q(created_at__year=selected_date[0]) &
                                        Q(created_at__month=selected_date[1]) &
                                        Q(created_at__day=selected_date[2]))

        count = products.count()
        
        products = products[((page*2)-2):(page*2)]
        product_variant_price = ProductVariantPrice.objects.filter(product__in=list(products))
        
        context['product_variant_price'] = dict()
        for pr in products:
            pvp = product_variant_price.filter(product=pr)
            context['product_variant_price'][pr.id] = list()
            for p in pvp:
                context['product_variant_price'][pr.id].append(p)

        product_variant = ProductVariant.objects.values('variant_title', 'variant__title').annotate(count=Count('variant_title')).order_by('variant__title')
        variant = product_variant.values('variant__title').distinct()

        is_filter = False

        if title!='' or selected_variant!='' or price_from!='' or price_to!='' or selected_date[0]!='':
            is_filter = True

        context['page'] = page
        context['page_range'] = range(1, math.ceil(count/2)+1)
        context['is_filter'] = is_filter
        context['filter_title'] = title
        context['filter_variant'] = selected_variant
        context['filter_price_from'] = price_from
        context['filter_price_to'] = price_to
        context['filter_date'] = self.request.GET.get('date', '')
        context['count'] = count
        context['first'] = (page * 2) - 1
        context['last'] = (page * 2) - 2 + len(products)

        context['variant'] = list(variant)
        context['product_variant'] = list(product_variant)
        
        return context