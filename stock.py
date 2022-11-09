class Stock:
  def __init__(self, name):
    self.ticker = name
    self.beta = 0
    self.exp_return = 0
    self.annual_return = 0
    self.var = 0
    self.std = 0

  def log(self):
    print("Stock " + self.ticker)
    print("Stock " + self.ticker)
        