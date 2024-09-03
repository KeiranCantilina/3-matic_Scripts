import trimatic

# Find groups
R_group = trimatic.find_group("R_RA")
L_group = trimatic.find_group("L_RA")

# Define exception in case we can't find a group
class CantFindPartException(Exception):
    pass

if (R_group or L_group) is None:
    raise CantFindPartException("Can't find Group")

# Create bounding boxes around each group and merge (assuming biggest part in each group is first)
box1 = trimatic.create_box_around_part(R_group.items[0])
box2 = trimatic.create_box_around_part(L_group.items[0])
boxes_merged = trimatic.merge([box1, box2])

# Find center of gravity of the merged boxes and invert it
center_of_gravity = trimatic.compute_center_of_gravity(part=boxes_merged, method='Based on mesh')
cog_list = list(center_of_gravity)
for x in range(len(cog_list)):
    cog_list[x] = cog_list[x]*-1
center_of_gravity = tuple(cog_list)

# Switch all objects to WCS and translate by inverted box center of gravity
for i in R_group.items:
    print(i)
    trimatic.update_ocs_to_cs(entity=i, method=trimatic.UpdateOCSMethod.WCS)
    trimatic.translate(i, center_of_gravity)

for i in L_group.items:
    print(i)
    trimatic.update_ocs_to_cs(entity=i, method=trimatic.UpdateOCSMethod.WCS)
    trimatic.translate(i, center_of_gravity)

# Rotate

# Remove boxes
trimatic.delete(boxes_merged)

#Reduce triangles
##trimatic.quality_preserving_reduce_triangles(entities=aorta, number_of_iterations=7)

## Set colors somehow (by tags? Parsing anatomical names? User selection?)

## Export
##myfilename=r"[filename string]"
##trimatic.export_obj(entities=aorta, filename=myfilename, units=1)
