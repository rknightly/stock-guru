from StockGuru.translate import translate

class Signal:
    def __init__(self, name, worst, best, default=-1, is_negative_bad=False):
        self.name = name
        self.worst = worst
        self.best = best
        self.default = default
        self.is_negative_bad = is_negative_bad

        self.is_found = False
        self.value_string = ""
        self.numerical_value = default

    def set_value(self, new_value):
        self.numerical_value = new_value
        self.value_string = str(new_value)

        if new_value != self.default:
            self.is_found = True

    def get_scaled_score(self):
        scaled_score = translate(self.numerical_value, self.worst, self.best, 0, 100)
        if self.is_negative_bad and self.numerical_value < 0:
            scaled_score = 0
        return scaled_score

