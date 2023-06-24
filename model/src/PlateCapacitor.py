class PlateCapacitor:
    def __init__(self, area, separation):
        self.area = area
        self.separation = separation
        self.epsilon_0 = 8.854e-12

    def capacitance(self, permittivity):
        return (self.epsilon_0 * permittivity * self.area) / self.separation