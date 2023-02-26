import json
import numpy as np
from scipy.optimize import curve_fit


class Regressor:
    """
    A class to perform a multiple linear regression on a given dataset
    using a given polynomial.
    """

    def __init__(self, filename, poly):
        """
        Initialize the regressor.

        Parameters
        ----------
        filename : Path
            The path to the file containing the data set.
        poly : function
            The polynomial to use for the regression.
        """
        self.polynomial = poly
        self.data_set = self._read_data_set(filename)
        self.number_of_samples = self.data_set.shape[0]

        self.optimal_parameters = None
        self.optimal_covariance = None
        self.predicted_y = None

    def _read_data_set(self, filename):
        """
        Read the data set from a given file.

        Parameters
        ----------
        filename : Path
            The path to the file containing the data set.
        """
        data_set = np.genfromtxt(
            filename,
            delimiter=",",
            dtype=[np.uintc, np.uintc, np.uintc, np.double],
            names=["p", "q", "r", "score"],
        )
        return data_set

    def _compute_weights(self):
        """
        Compute the weights for the regression.
        """
        sigma = [1.0 / (p * q) for p, q in zip(self.data_set["p"], self.data_set["q"])]
        return sigma

    def _fit_function(self):
        """
        Fit the polynomial to the data set.
        """
        self.optimal_parameters, self.optimal_covariance = curve_fit(
            self.polynomial,
            (self.data_set["p"], self.data_set["q"], self.data_set["r"]),
            self.data_set["score"],
            sigma=self._compute_weights(),
            absolute_sigma=True,
        )

    def _predict_y(self):
        """
        Predict the values of y for the data set.
        """
        p = lambda x: self.polynomial(x, *self.optimal_parameters)
        x_data = zip(self.data_set["p"], self.data_set["q"], self.data_set["r"])
        self.predicted_y = np.array([p(x) for x in x_data])

    def _compute_mae(self):
        """
        Compute the mean absolute error.

        Returns
        -------
        float
            The mean absolute error of the current regression.
        """
        return np.mean(np.abs(self.predicted_y - self.data_set["score"]))

    def _generate_report(self, filename):
        """
        Generate a report of the regression in JSON format and save it.
        """
        report = {
            "fitted_function": self.polynomial.__name__,
            "coeficients": self.optimal_parameters.tolist(),
            "covariance": self.optimal_covariance.tolist(),
            "mean_absolute_error": self._compute_mae(),
        }
        with open(filename, "w") as f:
            json.dump(report, f, indent=4)

    def regression(self, file_to_save):
        """
        Perform the regression and save the results on a JSON file.

        Parameters
        ----------
        file_to_save : str, optional
            The file path where the results are saved.
        """
        self._fit_function()
        self._predict_y()
        self._generate_report(file_to_save)
