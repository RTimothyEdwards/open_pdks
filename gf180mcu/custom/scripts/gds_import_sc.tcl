# Set GDS import styles as needed to deal with the standard cells.
# Set "flatten" to "false" or else the fill cells have so few
# shapes that they get flattened out of existence.  There are no
# instances in the standard cells that could get flattened, anyway.
gds flatten false
# Regenerate implant layers that don't conform to minimum rules
# as mask-hints
gds maskhints on
