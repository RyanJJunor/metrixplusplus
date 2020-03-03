import csv
import re

import mpp.api


class Plugin(mpp.api.Plugin,
             mpp.api.IConfigurable,
             mpp.api.Child,
             # reuse by inheriting standard metric facilities
             mpp.api.MetricPluginMixin):
    functions = {}

    methods = {}
    method_id = {}

    def declare_configuration(self, parser):
        parser.add_option("--myext.loops", "--loops",
                          action="store_true", default=False,
                          help="Enables collection of loops metric [default: %default]")

    def configure(self, options):
        self.is_active_numbers = options.__dict__['myext.loops']

    def initialize(self):
        # declare metric rules
        pattern_to_search = re.compile(
            '(\swhile[\s(])|(\sfor[\s(])')  # 44??
        # declare metric rules
        self.declare_metric(
            self.is_active_numbers,  # to count if active in callback
            self.Field('loops', int),  # field name and type in the database    a + b + c
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
            #for i in range(len(results)):
                #print(results.items()[i])

            default = 0
            column = 4
            rows = []
            line = 0

            with open('C:/Users/ryanj/Documents/Honours_Project/functions.csv', 'r') as read_obj:
                with open('C:/Users/ryanj/Documents/Honours_Project/loops.csv', 'wb') as write_obj:

                    csv_reader = csv.reader(read_obj)
                    csv_writer = csv.writer(write_obj)

                    # for each row in the csv file
                    for row in csv_reader:
                        if line == 0:
                            line += 1
                            csv_writer.writerow(
                                [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
                                 row[10], row[11], row[12], row[13]])
                            continue
                        for i in range(len(results)):
                            if row[2] in results.items()[i]:
                                row.append(results.items()[i][1])
                                continue
                            elif len(row) < column and i + 1 == len(results):
                                row.append(default)
                        line += 1
                        rows.append(row)
                    csv_writer.writerows(rows)

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
            # the func_metric dict, add it, and give it a value of one, if it is already in the dict, increment it by
            # one.

            if name not in Plugin.functions:
                self.func_metric = {match.group(): 1}
                Plugin.functions[name] = self.func_metric
            else:
                if match.group() not in self.func_metric:
                    self.func_metric[match.group()] = 1
                else:
                    self.func_metric[match.group()] += 1

            return 1
