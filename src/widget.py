"""
_____
Theme

a theme determines the styling and border size of each widget.

______
Layout

Different widgets have different default layout. Some have a fixed size
or a fixed minimum size and some grow to take as much or little space as
is available.

In general by default most of them will set the minimum size to the
size given in the constructor or to the minimum size required for the
contents given in the constructor (like a picture or text) but grow to
use additional space if available.

Containers also have different layout for their children.

A Board will place children at their x/y coordinate and keep their
initial size.

A VBox and HBox instead will distribute the available space to their
children (while growing itself to use all available space).

A Scrolling widget will not change its size but provide scrollbars to
scroll the child.

"""


import widget/gul
import widget/base
import widget/theme
import widget/layout

import widget/box
import widget/container
import widget/scrolling
import widget/widget_list
import widget/mover
import widget/sizer
import widget/button
import widget/panel
import widget/menu
import widget/vbox
import widget/hbox
import widget/book
import widget/edit
import widget/spin
import widget/board
import widget/slider
import widget/text
import widget/checkbox
