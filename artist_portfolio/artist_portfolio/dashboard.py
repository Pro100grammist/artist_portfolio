from jet.dashboard.dashboard import Dashboard
from jet.dashboard.modules import AppList, ModelList, RecentActions, LinkList
from django.utils.translation import gettext_lazy as _


class CustomIndexDashboard(Dashboard):
    """
    Dashboard для головної сторінки адмінки
    """
    def init_with_context(self, context):
        # Останні дії
        self.children.append(RecentActions(_('Recent actions'), limit=10))

        # AppList для Store management
        self.children.append(AppList(
            _('Store management'),
            models=('orders.*', 'products.*'),
        ))

        # Моделі користувачів
        self.children.append(ModelList(
            _('Users'),
            models=('users.UserProfile',),
        ))

        # Швидкі дії
        self.children.append(LinkList(
            _('Quick actions'),
            layout='inline',
            draggable=False,
            deletable=False,
            collapsible=False,
            children=[
                {'title': _('Create product'), 'url': '/admin/products/product/add/', 'external': False},
                {'title': _('Look over the order'), 'url': '/admin/orders/order/', 'external': False},
            ]
        ))
