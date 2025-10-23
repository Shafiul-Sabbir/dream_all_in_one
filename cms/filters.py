from django_filters import rest_framework as filters

from cms.models import *



#Blog
class BlogFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="title", lookup_expr='icontains')

    class Meta:
        model = Blog
        fields = ['title', ]


# BlogComments

class BlogCommentsFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="title", lookup_expr='icontains')

    class Meta:
        model = BlogComments
        fields = ['title', ]
# MetaData
class MetaDataFilter(filters.FilterSet):
    meta_title = filters.CharFilter(field_name="meta_title", lookup_expr='icontains')

    class Meta:
        model = MetaData
        fields = ['meta_title', ]

class TagFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = Tag
        fields = ['name', ]

class BlogCategoryFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = BlogCategory
        fields = ['name', ]