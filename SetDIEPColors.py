import trimatic

## Set artery colors
red_parts = trimatic.find_parts(regex=".+?Arteries_EM.+?")
blue_parts = trimatic.find_parts(regex=".+?Arteries_IM.+?")
for z in red_parts:
    z.color = (1,0,0)
for z in blue_parts:
    z.color = (0,0,1)

# ra and shell need to be transparent
RA_parts = trimatic.find_parts(regex=".+?_RA_.+?")
RA_line_parts = trimatic.find_parts(regex=".+?_RA_Line_Label.+?")
shell_parts = trimatic.find_parts(regex=".+?_Shell.+?")
for z in RA_parts:
    z.color = (1, 1, 1)
    z.transparency = 0.75
for z in shell_parts:
    z.color = (1, 1, 1)
    z.transparency = 0.75
for z in RA_line_parts:
    z.color = (0, 0, 0)
    z.transparency = 0
