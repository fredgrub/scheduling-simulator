import numpy as np
from polynomials import lin, qdr, cub, qua, qui, sex
from scipy.optimize import curve_fit

class Regressor:
    def __init__(self, filename, poly):
        self.polynomial = poly
        self.p, self.q, self.r, self.score = self._read_score_data(filename)
        self.number_of_samples = len(self.score)
        
        self.popt = None
        self.pcov = None
        self.predicted_y = None

    def _read_score_data(self, filename):
        p, q, r, score = [[] for _ in range(4)]

        with open(filename) as f:
            for line in f.readlines():
                row = line.split(',')
                p.append(int(row[0]))
                q.append(int(row[1]))
                r.append(int(row[2]))
                score.append(float(row[3]))
        
        return [np.array(element) for element in (p, q, r, score)]

    def _compute_weights(self):
        sigma = np.zeros(self.number_of_samples)
        for i in range(self.number_of_samples):
            sigma[i] = 1.0 / (self.p[i]*self.q[i])
        return sigma

    def _fit_function(self):
        self.popt, self.pcov = curve_fit(self.polynomial, (self.p, self.q, self.r), self.score, sigma=self._compute_weights(), absolute_sigma=True)

    def _predict_y(self):
        y_predict_data = []
        for i in range(self.number_of_samples):
            x = (self.p[i], self.q[i], self.r[i])
            y_predict_data.append(self.polynomial(x, *self.popt))
        self.predicted_y = np.array(y_predict_data)

    def _mae(self, y_true, predictions):
        y_true, predictions = np.array(y_true), np.array(predictions)
        return np.mean(np.abs(y_true - predictions))

    def _compute_mae(self):
        return self._mae(self.predicted_y , self.score)

    def _report(self):
        print("*** REGRESSION REPORT ***\n")
        print(f"Fitted function: {self.polynomial.__name__}")
        print(f"Intercept: {self.popt[0]:E}")
        print(f"Coeficients:\n{self.popt[1:]}\n")
        print(f"Mean Absolute Error: {self._compute_mae():E}")

    def make_regression(self):
        self._fit_function()
        self._predict_y()
        self._report()

if __name__ == '__main__':
    regressor = Regressor("src/regressor/dummy-score.csv", qdr)
    regressor.make_regression()