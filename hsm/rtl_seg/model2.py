# =============================================================================
# LOAD DEPENDENCIES
# =============================================================================

from modelsandbox import Model
import os, math
import numpy as np
MODEL_PATH = os.path.abspath(os.path.dirname(__file__))
SCHEMA_PATH = os.path.join(MODEL_PATH, 'schemas')


# =============================================================================
# PREPARE MODEL
# =============================================================================

# Initialize the model class
model = Model()

# Add data validation
model.add_validation(os.path.join(SCHEMA_PATH, 'validation.json'))


# =============================================================================
# DEFINE MODEL
# =============================================================================

# -----------------------------------------------------------------------------
# Layer #1: SPF calculations
# -----------------------------------------------------------------------------

with model.add_layer():
    with model.add_sequence():
        # Add SPF parameters
        model.add_schema(os.path.join(SCHEMA_PATH, 'spf.json'), hidden=True)

        # Compute number of crashes
        @model.add_wrapped()
        def n_kabco(aadt, length):
            """
            Based on HSM Equation 10-7.
            """
            # Compute number of crashes
            n = aadt * length * 365 * 10E-6 * math.exp(-0.312)
            return n

        # Compute overdispersion
        @model.add_wrapped()
        def overdispersion(length):
            # Compute overdispersion
            k = 0.236 / length
            return k


# -----------------------------------------------------------------------------
# Layer #2: AF calculations
# -----------------------------------------------------------------------------

with model.root.add_layer() as layer:

    @layer.add_wrapped()
    def af_lane_width(lane_width, aadt):
        # Compute adjustment factor
        if lane_width < 10:
            af = np.clip(1.05 + 2.81e-4 * (aadt - 400), 1.05, 1.50)
        elif lane_width < 11:
            af = np.clip(1.02 + 1.75e-4 * (aadt - 400), 1.02, 1.30)
        elif lane_width < 12:
            af = np.clip(1.01 + 0.25e-4 * (aadt - 400), 1.01, 1.05)
        else:
            af = 1
        return af

    @layer.add_wrapped()
    def af_shoulder_width(shoulder_width, aadt):
        # Compute adjustment factor
        if shoulder_width < 2:
            af = np.clip(1.10 + 2.50e-4 * (aadt - 400), 1.10, 1.50)
        elif shoulder_width < 4:
            af = np.clip(1.07 + 1.43e-4 * (aadt - 400), 1.07, 1.30)
        elif shoulder_width < 6:
            af = np.clip(1.02 + 0.8125e-4 * (aadt - 400), 1.02, 1.15)
        elif shoulder_width < 8:
            af = 1
        else:
            af = np.clip(0.98 + 0.6875e-4 * (aadt - 400), 0.98, 0.87)
        return af

    model.add_schema(os.path.join(SCHEMA_PATH, 'af_shoulder_type.json'))

    @layer.add_wrapped()
    def af_horizontal_curve(curve_length, curve_radius, spiral):
        # Check if provided
        if (curve_length == 0) or (curve_radius == 0):
            return 1.0
        # Process spiral information
        spiral_value = {'both': 1.0, 'one': 0.5, 'neither': 0.0}[spiral]
        # Clip values
        # - Minimum of 100' length if provided
        curve_length = max(curve_length, 100 / 5280)
        # - Minimum of 100' radius if provided
        curve_radius = max(curve_radius, 100)
        # Compute adjustment factor
        af = (
            (1.55 * curve_length) + \
            (80.2 / curve_radius) - \
            (0.012 * spiral_value)
        ) / (1.55 * curve_length)
        return af

    @layer.add_wrapped()
    def af_se_variance(se_variance):
        """
        Based on HSM equation 10-14, 10-15, 10-16.

        NOTE: Future improvement, code AASHTO SE Tables to automatically calculate 
        variance from input superelevation and other values.
        """
        # Compute adjustment factor
        if se_variance < 0.01:
            af = 1.00
        elif se_variance >= 0.02:
            af = 1.06 + (3 * (se_variance - 0.02))
        else:
            af = 1.00 + (6 * (se_variance - 0.01))
        return af

    @layer.add_wrapped()
    def af_grade(grade):
        """
        Based on HSM table 10-11.
        """
        # Enforce positive grade
        grade = math.fabs(grade)
        # "Level Grade"
        if grade <= 3.00:
            af = 1.00
        # "Moderate Terrain"
        elif grade <= 6.00:
            af = 1.10
        # "Steep Terrain"
        else:
            af = 1.16
        return af

    @layer.add_wrapped()
    def af_driveway_density(aadt, length, driveway_density):
        """
        Based on HSM equation 10-17
        """
        # Enforce minimum driveway number
        if driveway_density < 5:
            af = 1.00
        else:
            af = (0.322 + (driveway_density * (0.05 - 0.005 * math.log(aadt)))) / \
                (0.322 + (5 * (0.05 - 0.005 * math.log(aadt))))
        return af

    @layer.add_wrapped()
    def af_rumble_cl(rumble_cl):
        """
        Based on HSM page 10-29
        """
        # Compute binary adjustment factor
        if rumble_cl == 1:
            af = 0.94
        else:
            af = 1.00
        return af

    @layer.add_wrapped()
    def af_passing_lanes(passing_lanes):
        """
        Based on HSM page 10-29
        """
        # Compute adjustment factor based on number of passing lanes present
        if passing_lanes == 0:
            af = 1.00
        elif passing_lanes == 1:
            af = 0.75
        elif passing_lanes == 2:
            af = 0.65
        return af

    @layer.add_wrapped()
    def af_twltl(twltl, length, driveway_density):
        """
        Based on HSM equation 10-18 and 10-19.
        """
        if twltl == 0:
            af = 1.00
        elif driveway_density < 5:
            af = 1.00
        else:
            driveway_prop = ((0.0047 * driveway_density) + (0.0024 * driveway_density ** 2)) / \
                (1.199 + (0.0047 * driveway_density) + (0.0024 * driveway_density ** 2))
            af = 1.0 - (0.7 * driveway_prop * 0.5)
        return af


    @layer.add_wrapped()
    def af_rhr(rhr):
        """
        Based on HSM equation 10-20 and the roadside hazard rating in appendix 13A
        """
        # Compute adjustment factor
        af = math.exp(-0.6869 + (0.0668 * rhr)) / math.exp(-0.4865)
        return af

    @layer.add_wrapped()
    def af_lighting(lighting):
        """
        Based on HSM equation 10-21 and table 10-12.
        """
        # Compute adjustment factor
        if lighting == 1:
            af = 1.0 - ((1.0 - (0.72 * 0.382) - (0.83 * 0.618)) * 0.370)
        else:
            af = 1.00
        return af

    @layer.add_wrapped()
    def af_ase(ase):
        """
        Based on HSM page 10-31.
        """
        # Compute adjustment factor
        if ase == 1:
            af = 0.93
        else:
            af = 1.00
        return af
