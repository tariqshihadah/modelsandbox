from modelsandbox_old.model.model import Model

# FUNCTIONAL APPROACH
model = Model()

# SPF Calculations
model.cursor.add_layer('Layer 1')
model.cursor.add_schema('schema1.json')

# SPF 1
model.cursor.add_sequence()
model.cursor.add_schema('schema2.json', reveal=False)
model.cursor.add_wrapped()
def process(a, b, c, d):
    return a * b + c / d
model.cursor.close()

# WITH APPROACH
model = Model()

# SPF Calculations
with model.root.add_layer('spf_calculations') as layer:
    layer.add_schema('schema1.json')

    # SPF 1
    with layer.add_sequence() as seq:
        seq.add_schema('schema2.json', hidden=True)
        seq.add_wrapped()
        def process(a, b, c, d):
            return a * b + c / d
        
    # SPF 2
    with layer.add_sequence() as seq:
        seq.add_schema('schema3.json', hidden=True)
        seq.add_wrapped()
        def process(a, b, c, d):
            return a * b + c / d

# AF Calculations
with model.root.add_layer('af_calculations') as layer:

    # AF 1
    layer.add_wrapped()
    def af_lane_width(lane_width):
        return lane_width / 12