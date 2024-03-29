import json
import pathlib
import numpy as np
from scipy.optimize import curve_fit
from polynomials import *

DATA_DIR = pathlib.Path(__file__).parent.parent.parent / "data"
SCORE_DISTRIBUTION = DATA_DIR / "scores" / "lublin-256-final-score.csv"
REPORT_FILE = DATA_DIR / "regression_report.json"
FUNCTIONS = [lin, qdr, cub, qua, qui, sex]


class Regressor:
    """
    A class to perform a multiple linear regression on a given dataset
    using a set of functions.
    """

    def __init__(self, data_file, functions):
        """
        Initialize the regressor.

        Parameters
        ----------
        data_file : str
            The path to the file containing the data set.
        functions : list
            The list of functions to use for the regression.
        """
        self.functions = functions
        self.data_set = self._read_data_set(data_file)
        self.number_of_samples = self.data_set.shape[0]

    def _read_data_set(self, filename):
        """
        Read the data set from a given file.

        Parameters
        ----------
        filename : str
            The path to the file containing the data set.

        Returns
        -------
        array
            The data set.
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

    def _fit_function(self, function):
        """
        Fit a given function to the data set using scipy.optimize.curve_fit.

        Parameters
        ----------
        function : function
            The function to fit.

        Returns
        -------
        tuple
            The optimal parameters and the covariance matrix.
        """
        optimal_parameters, optimal_covariance = curve_fit(
            function,
            (self.data_set["p"], self.data_set["q"], self.data_set["r"]),
            self.data_set["score"],
            sigma=self._compute_weights(),
            absolute_sigma=True,
        )

        return optimal_parameters, optimal_covariance

    def _predict_y(self, function, optimal_parameters):
        """
        Predict the values of y for the data set.

        Parameters
        ----------
        function : function
            The function to fit.
        optimal_parameters : array
            The optimal parameters of the function.

        Returns
        -------
        array
            The predicted values of y.
        """
        p = lambda x: function(x, *optimal_parameters)
        x_data = zip(self.data_set["p"], self.data_set["q"], self.data_set["r"])
        predicted_y = np.array([p(x) for x in x_data])

        return predicted_y

    def _compute_mae(self, predicted_y):
        """
        Compute the mean absolute error.

        Parameters
        ----------
        predicted_y : array
            The predicted values of y.

        Returns
        -------
        float
            The mean absolute error of the current regression.
        """
        return np.mean(np.abs(predicted_y - self.data_set["score"]))

    def _generate_report(
        self,
        function,
        optimal_parameters,
        optimal_covariance,
        predicted_y,
        include_covariance,
    ):
        """
        Generate a report of the regression for a given function.

        Parameters
        ----------
        function : function
            A function used for the regression.
        optimal_parameters : array
            The optimal parameters of the function.
        optimal_covariance : array
            The covariance matrix of the function.
        predicted_y : array
            The predicted values of y.
        include_covariance : bool
            Whether to include the covariance matrix in the report.

        Returns
        -------
        dict
            The report of the regression.
        """
        report = {
            "fitted_function": function.__name__,
            "coeficients": optimal_parameters.tolist(),
            "mean_absolute_error": self._compute_mae(predicted_y),
        }

        if include_covariance:
            report["covariance"] = optimal_covariance.tolist()

        return report

    def regression(self, output_file, include_covariance=False):
        """
        Perform the regression on the data set and write the report to a file.

        Parameters
        ----------
        output_file : str
            The path to the file where the report will be written.
        include_covariance : bool, optional
            Whether to include the covariance matrix in the report.
        """
        reports = []
        for function in self.functions:
            optimal_parameters, optimal_covariance = self._fit_function(function)
            predicted_y = self._predict_y(function, optimal_parameters)
            report = self._generate_report(
                function,
                optimal_parameters,
                optimal_covariance,
                predicted_y,
                include_covariance,
            )
            reports.append(report)

        with open(output_file, "w") as f:
            json.dump(reports, f, indent=4)


if __name__ == "__main__":
    print("Performing the regression...")
    regressor = Regressor(SCORE_DISTRIBUTION, FUNCTIONS)
    regressor.regression(REPORT_FILE)
    print("Done!")
    print("Regression report saved to '{}'".format(REPORT_FILE))
