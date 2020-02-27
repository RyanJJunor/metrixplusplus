import mpp.api
import re

#TODO done?

class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             mpp.api.Child,
             # reuse by inheriting standard metric facilities
             mpp.api.MetricPluginMixin):
    functions = {}

    methods = {}
    method_id = {}

    def declare_configuration(self, parser):
        parser.add_option("--myext.operators_unique", "--tor_u",
                          action="store_true", default=False,
                          help="Enables collection of operators numbers metric")

    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.operators_unique']

    def initialize(self):
        # TODO finish regex brackets REMOVED OPENING BRACKETS TO COUNT ONLY A SET OF BRACKETS
        # TODO sizeof (object size information)
        # typeid (object type information)
        # static_cast (casting operator)
        # const_cast (casting operator)
        # reinterpret_cast (casting operator)
        # dynamic_cast (casting operator)??????????????????

        pattern_to_search = re.compile(
            '\sdelete\s|\snew\s|--|<<=|<<|<=|<|>>=|>>|>=|->\*|->|>|::|\+\+|\+=|\+|==|!=|\^=|\|=|\?:|&&|&=|&|\*=|%=|/=|-=|=|-|\.\*|\*|/|\)|]|%|\.|\|\||\||,|~|\^|!')
        # declare metric rules
        self.declare_metric(
            self.is_active_numbers,  # to count if active in callback
            self.Field('tor_u', int),  # field name and type in the database
            # TODO metric regex
            (pattern_to_search, self.Counter),  # pattern to search
            marker_type_mask=mpp.api.Marker.T.CODE,  # search in code
            region_type_mask=mpp.api.Region.T.FUNCTION)  # search in all types of regions

        # use superclass facilities to initialize everything from declared fields
        super(Plugin, self).initialize(fields=self.get_fields())

        # subscribe to all code parsers if at least one metric is active
        if self.is_active() == True:
            self.subscribe_by_parents_interface(mpp.api.ICode)

    # This method is used when the matches are being counted, I use to it to only display the count of metrics, ones the
    # entire file has been gone through
    def count_if_active(self, namespace, field, data, alias='*'):
        if self.is_active(field) == False:
            return

        field_data = self._fields[field]
        if alias not in field_data[4].keys():
            if '*' not in field_data[4].keys():
                raise self.AliasError(alias)
            else:
                alias = '*'
        (pattern_to_search, counter_class) = field_data[4][alias]

        if field_data[0]._regions_supported == True:
            for region in data.iterate_regions(filter_group=field_data[5]):
                counter = counter_class(namespace, field, self, alias, data, region)
                if field_data[1] != mpp.api.Marker.T.NONE:
                    for marker in data.iterate_markers(
                            filter_group=field_data[1],
                            region_id=region.get_id(),
                            exclude_children=field_data[2],
                            merge=field_data[3]):
                        counter.count(marker, pattern_to_search)
                count = counter.get_result()
                if count != 0 or field_data[0].non_zero == False:
                    region.set_data(namespace, field, count)

            # Holds the results as a dict of (Function name: Number of operators found)
            results = {}

            # calculates the total number of matches in all methods
            for i in range(len(Plugin.functions.items())):
                metric_count = 0
                results[str(Plugin.functions.items()[i][0])] = 0
                # for each method, sums the number of metric occurrences
                for j in range(len(Plugin.functions.items()[i][1].items())):
                    metric_count += Plugin.functions.items()[i][1].items()[j][1]
                results[Plugin.functions.items()[i][0]] += metric_count

            # Prints the results in a more readable way
            for i in range(len(results)):
                print(results.items()[i])

        else:
            counter = counter_class(namespace, field, self, alias, data, None)
            if field_data[1] != mpp.api.Marker.T.NONE:
                for marker in data.iterate_markers(
                        filter_group=field_data[1],
                        region_id=None,
                        exclude_children=field_data[2],
                        merge=field_data[3]):
                    counter.count(marker, pattern_to_search)
            count = counter.get_result()
            if count != 0 or field_data[0].non_zero == False:
                data.set_data(namespace, field, count)

    class Counter(mpp.api.MetricPluginMixin.IterIncrementCounter):

        func_metric = {}

        # TODO contains logic on when to count a metric
        def increment(self, match):

            # If a method is overloaded, this will append the number of occurrences of the overloaded methods to the end of the name
            id = self.region.get_id()
            name = self.region.get_name()

            # checks if the method's name has already been encountered
            if name not in Plugin.methods:
                Plugin.methods[name] = 1
                Plugin.method_id[id] = 0
                name = str(name) + '.' + str(Plugin.methods[name])
            # Checks if the methods name and id has been encountered before
            elif id not in Plugin.method_id:
                Plugin.methods[name] = Plugin.methods[name] + 1
                Plugin.method_id[id] = 0
                name = str(name) + '.' + str(Plugin.methods[name])
            # if the methods name and id has been encountered before then it is still in the method that it last encountered
            else:
                name = str(name) + '.' + str(Plugin.methods[name])

            # If the region that just contained a match is not currently in the Plugin.functions dict, add it and add
            # the metric to the func_metric and give it a value of one, else if the metric hasn't already been added to
            # the func_metric dict, add it, and give it a value of zero, if it is already in the dict, increment it by
            # one.
            if name not in Plugin.functions:
                self.func_metric = {match.group(): 1}
                Plugin.functions[name] = self.func_metric
            else:
                if match.group() not in self.func_metric:
                    self.func_metric[match.group()] = 1


            # print(self.region.get_id())
            # print(self.region.get_name())
            # print(Plugin.functions)
            # print(self.test2)
            return 1
