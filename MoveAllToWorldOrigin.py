import trimatic

# Find all parts
all_parts = trimatic.get_parts()

# get part volumes
list_of_volumes = []
for y in all_parts:
    list_of_volumes.append(y.volume)

# Sort parts by volume and get indices of largest two objects
sorted_volume_index = sorted(range(len(list_of_volumes)), reverse=True, key=list_of_volumes.__getitem__)
biggest_part = all_parts[sorted_volume_index[0]]
next_biggest_part = all_parts[sorted_volume_index[1]]

# Create bounding boxes around each part and merge
box1 = trimatic.create_box_around_part(biggest_part)
box2 = trimatic.create_box_around_part(next_biggest_part)
boxes_merged = trimatic.merge([box1, box2])

# Find center of gravity of the merged boxes and invert it
center_of_gravity = trimatic.compute_center_of_gravity(part=boxes_merged, method='Based on mesh')
cog_list = list(center_of_gravity)
for x in range(len(cog_list)):
    cog_list[x] = cog_list[x]*-1
center_of_gravity = tuple(cog_list)

# Switch all objects to WCS and translate by inverted box center of gravity
for i in all_parts:
    print(i)
    trimatic.update_ocs_to_cs(entity=i, method=trimatic.UpdateOCSMethod.WCS)
    trimatic.translate(i, center_of_gravity)

# Remove boxes
trimatic.delete(boxes_merged)

#Reduce triangles
##trimatic.quality_preserving_reduce_triangles(entities=all_parts, number_of_iterations=7)



## Export
##myfilename=r"[filename string]"
##trimatic.export_obj(entities=aorta, filename=myfilename, units=1)
