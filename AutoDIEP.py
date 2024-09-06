from Demos.mmapfile_demo import offset

import trimatic
from tkinter import filedialog

## NOTES: Always duplicate before hollow

from pymatic import find_parts
from threaded_trimatic import create_group, activate_trim, boolean_subtraction, smooth_edge
from trimatic import TrimMethod, SmoothDetail

print('----------------------- Welcome to Keiran\'s DIEP Wizard! ----------------------------\n\n')

# Import files from Mimics (alternatively maybe write code that just asks user to select folder)
filenames = filedialog.askopenfilenames(title="Choose SF, RA_Merged, and Arteries_Merged Mimics files to import")
for i in filenames:
    trimatic.import_project(i)

# Find parts
SF = trimatic.find_parts(regex='.+?SF.+?')
RA_Merged = trimatic.find_parts(regex='.+?RA_Merged.+?')
Arteries_Merged = trimatic.find_parts(regex='.+?Arteries_Merged.+?')

# Get Umbilicus line from user
print('Please select the Umbilicus Line. Press ESC when complete.')
umbilicus_line_point = trimatic.create_point(coords=(0,0,0))
while 1:
    try:
        umbilicus_line_point = trimatic.indicate_coordinate()
        print('Indicated coordinate is: ' + str(umbilicus_line_point))
    except:
        break
print('Umbilicus line point saved as: ' + str(umbilicus_line_point))

# Get Bottom line from user
print('Please select Mimics Bottom. Press ESC when complete.')
bottom_point = trimatic.create_point(coords=(0,0,0))
while 1:
    try:
        bottom_point = trimatic.indicate_coordinate()
        print('Indicated coordinate is: ' + str(bottom_point))
    except:
        break
print('Mimics bottom point saved as: ' + str(bottom_point))

# Create reference planes
standard_section_z = trimatic.create_plane_3_points(point1=(0,0,0),point2=(1,0,0),point3=(0,1,0))
umbilicus_plane = trimatic.create_plane_1_point_parallel_plane(umbilicus_line_point, standard_section_z)
mimics_bottom_plane = trimatic.create_plane_1_point_parallel_plane(bottom_point, standard_section_z)

# Create Top plane
top_plane = trimatic.create_plane_1_point_parallel_plane(point=(umbilicus_line_point.x, umbilicus_line_point.y, umbilicus_line_point.z+25), parallel_plane=standard_section_z)
top_plane.name = "Top"

# Create Bottom plane
bottom_plane = top_plane = trimatic.create_plane_1_point_parallel_plane(point=(umbilicus_line_point.x, umbilicus_line_point.y, umbilicus_line_point.z+25), parallel_plane=standard_section_z)
top_plane.name = "Top"

# Create U-Top plane
u_top_plane = trimatic.create_plane_1_point_parallel_plane(point=(umbilicus_line_point.x, umbilicus_line_point.y, umbilicus_line_point.z+0.5), parallel_plane=standard_section_z)
u_top_plane.name = "U-Top"

# Create U-Bottom plane
u_bottom_plane = trimatic.create_plane_1_point_parallel_plane(point=(umbilicus_line_point.x, umbilicus_line_point.y, umbilicus_line_point.z-0.5), parallel_plane=standard_section_z)
u_bottom_plane.name = "U-Bottom"

# Duplicate SF, RA_Merged and Arteries_Merged and add to Rev group, then hide
duplicated_parts = trimatic.data.duplicate([SF,RA_Merged,Arteries_Merged])
trimatic.create_group("Rev", entities = duplicated_parts)
for part in duplicated_parts:
    part.visible = False

# DIEP SF Trim
print("Trim the SF around the RA_Merged parts, ensuring fillet does not contact the top or bottom of the SF."
      "Click anywhere in the 3D View to start drawing the trimming outline. Press apply to trim the SF. Press ESC when done.")
activate_trim(SF, trim_method = TrimMethod.remove_outer, fillet_radius = 100)
SF_duplicated = trimatic.duplicate(SF)
RA_Merged_duplicated = trimatic.duplicate(RA_Merged)
SF_subtracted = boolean_subtraction(SF_duplicated, RA_Merged_duplicated, clearance = 0.1)
SF_subtracted.name = "SF_Subtracted"
smooth_edge(SF_subtracted, distance = 0.5)
SF.visible = False
SF_subtracted.visible = False
Arteries_Merged.visible = True
RA_Merged.transparency = 0.75


#PLACEHOLDER BECAUSE NO INTERACTIVE FUNCTION FOR MANUAL CONNECTIONS
#Maybe interactively get points then project them onto parts and create cylinders
# print('Click points on RA_Merged for connections. Press ESC when done.')
# connection_points = []
# connection_points[0] = trimatic.create_point(coords=(0,0,0))
# for x in range(4):
#     try:
#         connection_points[x] = trimatic.indicate_coordinate()
#         print('Indicated connection points are:' + str(connection_points))
#     except:
#         break
message = ("Select 'Connections' with settings 'Manual', 'Towards an entity', 'SF_Subtracted' as 'target entity',"
           "'Absolute', 'Radius' 3.1750, 'Convert to Solid' checked and leave the default tolerance.)"
           "Then, select four points on the RA_Merged part that do not overlap to interfere with both"
           "'Arteries_Merged' and the 'Section' lines. Finally, left click Apply and press the OK button on "
           "this dialog box.")
trimatic.message_box(message, "Create Part Connections Manually", with_cancel = True)
cylinder_connections = trimatic.find_part("Cylinder Connections")

# ???? UNSURE HOW MOVE SURFACE SHOULD BEHAVE
# find cylinder top and bottom surfaces by name, then move surfaces
connection_cylinder_tops = cylinder_connections.find_surfaces(regex='Top')
connection_cylinder_bottoms = cylinder_connections.find_surfaces(regex='Bottom')
trimatic.move_surface(connection_cylinder_tops,direction = None, distance = 3.175, solid = True)
trimatic.move_surface(connection_cylinder_bottoms,direction = None, distance = 1.587, solid = True)

# Boolean subtract cylinder connections from SF_subtracted
SF_subtracted.visible = True
SF_subtracted = boolean_subtraction(SF_subtracted, cylinder_connections, clearance = 0.1) # Assuming here we don't need to keep the originals here
SF_subtracted.name = "SF_subtracted"

# Duplicate SF_subtracted because otherwise it will be removed during the hollow step
SF_subtracted_duplicate = trimatic.duplicate(SF_subtracted)
trimatic.hollow(entities = SF_subtracted_duplicate, hollow_type = trimatic.HollowType.Inside, distance = 3.5, smallest_detail = 0.5, smooth_factor = 0.1, reduce = True)

# RA Muscle Umbilicus Line Preparation
Line_ROI = trimatic.duplicate(RA_Merged)
trimatic.activate_trim(Line_ROI, trim_method = TrimMethod.remove_outer, fillet_radius = None)
Line_ROI.name = "Line-ROI"

Line_ROI_duplicated = trimatic.duplicate(Line_ROI)
offset_Line_ROI = trimatic.uniform_offset_preserve_sharp_features(Line_ROI_duplicated, distance= 0.3, solid = False) # Should it have 'remove original' checked or not?
offset_Line_ROI_duplicated = trimatic.duplicate(offset_Line_ROI)
trimatic.hollow(entities = offset_Line_ROI_duplicated, distance = 0.8, smallest_detail = 0.5, smooth_factor = 0.100, reduce = True)

# SF, Arteries and RA Muscle Boundary Cuts
