from django.views import generic

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
        products = Product.objects.all()
        product_variant_price = ProductVariantPrice.objects.filter(product__in=products)

        context['product_variant_price'] = dict()
        for pr in products:
            pvp = product_variant_price.filter(product=pr)
            context['product_variant_price'][pr.id] = list()
            for p in pvp:
                context['product_variant_price'][pr.id].append(p)

        return context