from tabulate import tabulate


class Result(object):

    def __init__(self):
        self.records = []
        self.success = 0
        self.error = 0
        self.error_items = []
        self.duplicate = 0
        self.duplicate_items = []

    def append(self, row):
        id, status = row

        # status can only be True, False, or None
        if status is True:
            self.success += 1
        elif status is None: # status is only ever None if file checksum matched an existing file checksum and is therefore a duplicate file
            self.duplicate += 1
            self.duplicate_items.append(id)
        else:
            self.error += 1
            self.error_items.append(id)

    def write(self):
        print("\n")
        if self.error > 0:
            error_headers = ["File"]
            error_result = []
            for id in self.error_items:
                error_result.append([id])

            print("****** ERROR DETAILS ******")
            print(tabulate(error_result, headers=error_headers))
            print("\n")

        if self.duplicate > 0:
            duplicate_headers = ["File"]
            duplicate_result = []
            for id in self.duplicate_items:
                duplicate_result.append([id])

            print("****** DUPLICATE (NOT IMPORTED) DETAILS ******")
            print(tabulate(duplicate_result, headers=duplicate_headers))
            print("\n")

        headers = ["Metric", "Count"]
        result = [
                    ["Success", self.success],
                    ["Error", self.error],
                    ["Duplicate, not imported", self.duplicate]
                 ]

        print("****** SUMMARY ******")
        print(tabulate(result, headers=headers))
