import mpp.api
import re


class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             mpp.api.Child,
             # reuse by inheriting standard metric facilities
             mpp.api.MetricPluginMixin):

    def declare_configuration(self, parser):
        parser.add_option("--myext.operators_total", "--op_t",
                          action="store_true", default=False,
                          help="Enables collection of operators numbers metric")

    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.operators_total']

    def initialize(self):
        pattern_to_search = re.compile('\+\+|\+|-|\*|\/')
        # declare metric rules
        self.declare_metric(
            self.is_active_numbers,  # to count if active in callback
            self.Field('op_t', int),  # field name and type in the database
            # TODO metric regex
            (pattern_to_search, self.Counter),  # pattern to search
            marker_type_mask=mpp.api.Marker.T.CODE,  # search in code
            region_type_mask=mpp.api.Region.T.FUNCTION)  # search in all types of regions

        '''pattern_to_search = re.compile('\+\+')
        self.declare_metric(
            self.is_active_numbers,  # to count if active in callback
            self.Field('op_r', int),  # field name and type in the database
            # TODO metric regex
            (pattern_to_search, self.Counter),  # pattern to search
            marker_type_mask=mpp.api.Marker.T.CODE,  # search in code
            region_type_mask=mpp.api.Region.T.FUNCTION)'''

        # use superclass facilities to initialize everything from declared fields
        super(Plugin, self).initialize(fields=self.get_fields())

        # subscribe to all code parsers if at least one metric is active
        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)

    class Counter(mpp.api.MetricPluginMixin.IterIncrementCounter):

        functions = {}
        test2 = {}
        func = {}

        def increment(self, match):

            if self.region.get_name() not in self.functions:
                self.func = {match.group(): 1}
                self.functions[self.region.get_name()] = self.func
            else:
                if match.group() not in self.func:
                    self.func[match.group()] = 1
                else:
                    self.func[match.group()] += 1

            # print(self.region.get_id())
            # print(self.region.get_name())
            print(self.functions)
            # print(self.test2)
            return 1
