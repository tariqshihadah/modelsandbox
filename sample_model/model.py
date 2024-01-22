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
# DEFINE MODEL LAYERS
# =============================================================================

# -----------------------------------------------------------------------------
# Layer #1: SPF calculations
# -----------------------------------------------------------------------------
model.add_layer('SPF calculations')

@model.add_wrapped(tags=['spf'])
def n_kabco(aadt, length):
    # Compute number of crashes
    n = aadt * length * 365 * 10E-6 * math.exp(-0.312)
    return n

@model.add_wrapped(tags=['spf'])
def overdispersion(length):
    # Compute overdispersion
    k = 0.236 / length
    return k


# -----------------------------------------------------------------------------
# Layer #2: AF calculations
# -----------------------------------------------------------------------------
model.add_layer('AF calculations')

@model.add_wrapped(tags=['af'])
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

@model.add_wrapped(tags=['af'])
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

model.add_schema(
    os.path.join(SCHEMA_PATH, 'af_shoulder_type.json'),
    tags=['af']
)

@model.add_wrapped(tags=['af'])
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


# -----------------------------------------------------------------------------
# Layer #3: AF aggregation
# -----------------------------------------------------------------------------
model.add_layer('AF aggregation')

@model.add_wrapped()
def af_total(__af):
    return np.prod(list(__af.values()))


# -----------------------------------------------------------------------------
# Layer #4: Crash prediction
# -----------------------------------------------------------------------------
model.add_layer('Crash prediction')

@model.add_wrapped()
def predicted_kabco(n_kabco, af_total):
    return n_kabco * af_total


# -----------------------------------------------------------------------------
# Layer #5: Empirical-Bayes
# -----------------------------------------------------------------------------
model.add_layer('Empirical-Bayes')

@model.add_wrapped()
def expected_kabco(observed_kabco, predicted_kabco, overdispersion):
    # Compute predicted crash weighting
    weight = 1 / (1 + overdispersion * (predicted_kabco))
    # Apply weighting between predicted and observed
    return weight * predicted_kabco + (1 - weight) * observed_kabco