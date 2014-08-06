# -*- coding: utf-8 -*-
from django_select2.widgets import (AutoHeavySelect2MultipleWidget,
                                    AutoHeavySelect2Widget,
                                    AutoHeavySelect2TagWidget)

class TagWithSpaceWidget(AutoHeavySelect2TagWidget):

    def __init__(self, *args, **kwargs):
        super(TagWithSpaceWidget, self).__init__(*args, **kwargs)
        self.options['tokenSeparators'] = [',']

class MultipleLookupWidget(AutoHeavySelect2MultipleWidget):

    def __init__(self, *args, **kwargs):
        super(MultipleLookupWidget, self).__init__(*args, **kwargs)
        self.options['minimumInputLength'] = 0

class LookupWidget(AutoHeavySelect2Widget):

    def __init__(self, *args, **kwargs):
        super(LookupWidget, self).__init__(*args, **kwargs)
        self.options['minimumInputLength'] = 0
