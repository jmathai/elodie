from tabulate import tabulate


class Result(object):

    def __init__(self):
        self.records = []
        self.success = 0
        self.error = 0
        self.error_items = []
        self.skipped = 0

    def append(self, row):
        id, status = row

        if status == 'skipped':
            self.skipped += 1
        else:
            if status:
                self.success += 1
            else:
                self.error += 1
                self.error_items.append(id)

    def write(self):
        if self.error > 0:
            error_headers = ["File"]
            error_result = []
            for id in self.error_items:
                error_result.append([id])

            print("****** ERROR DETAILS ******")
            print(tabulate(error_result, headers=error_headers))
            print("\n")

        headers = ["Metric", "Count"]
        result = [
                    ["Success", self.success],
                    ["Error", self.error],
                    ["Skipped", self.skipped],
                 ]

        print("****** SUMMARY ******")
        print(tabulate(result, headers=headers))
