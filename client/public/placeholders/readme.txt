Most of these SVG files are modifications of material icons with 24x24 size.
The width and height is enlarged to 600x400 (a 3:2 ratio)
and the viewport is "-9 -2 42 28", which also makes 3:2,
but with a margin of 9 left and right and 2 top an bottom
(9+24+9 = 42 and 2+24+2 makes 28).

The coordinates of the vector data is unchanged.

Additionally a fill="#ffffff" was added to make the icons white instead of black.

To create new placeholder images you can basically use a material icon with 24x24 size
and replace the svg tag with one like this:

<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400" viewBox="-9 -2 42 28" fill="#ffffff">
