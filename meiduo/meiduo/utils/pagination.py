from rest_framework.pagination import PageNumberPagination


class SKUListPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'  # 用于接收前端的请求参数 page_size=5， 前端写了这个就会展示5条
    max_page_size = 20