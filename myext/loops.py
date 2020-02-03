import mpp.api
import re


class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             mpp.api.Child,
             # reuse by inheriting standard metric facilities
             mpp.api.MetricPluginMixin):

    def declare_configuration(self, parser):
        parser.add_option("--myext.loops", "--loops",
                          action="store_true", default=False,
                          help="Enables collection of magic numbers metric [default: %default]")

    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.loops']

    def initialize(self):
        # declare metric rules
        self.declare_metric(
            self.is_active_numbers,  # to count if active in callback
            self.Field('loops', int),  # field name and type in the database
            re.compile('(\swhile[\s(])|(\sfor[\s(])'),  # pattern to search
            marker_type_mask=mpp.api.Marker.T.CODE,  # search in code
            region_type_mask=mpp.api.Region.T.FUNCTION)  # search in all types of regions

        # use superclass facilities to initialize everything from declared fields
        super(Plugin, self).initialize(fields=self.get_fields())

        # subscribe to all code parsers if at least one metric is active
        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)