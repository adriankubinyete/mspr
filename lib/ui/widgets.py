# widget parts
from lib.ui.modals.Biome import ModalBiomeManager  # noqa

# modals (put them on buttons)
from lib.ui.modals.Debug import ModalDebug  # noqa
from lib.ui.modals.RAMWS import ModalRAMWSSettings  # noqa
from lib.ui.modals.ScreenCallibration import ModalScreenCallibration  # noqa

# other items (standalone frames)
from lib.ui.MultiAccountPage import MultiAccountPage  # noqa
from lib.ui.pages.Development import DevelopmentPage  # noqa
from lib.ui.TabManager import TabManagerPage  # noqa
from lib.ui.widget.BoxAssign import UIBoxAssign as BoxAssign  # noqa
from lib.ui.widget.Checkbox import UICheckbox as Checkbox  # noqa
from lib.ui.widget.ClickAssign import UIClickAssign as ClickAssign  # noqa
from lib.ui.widget.InfoButton import UIInfoButton as InfoButton  # noqa
from lib.ui.widget.Radio import UIRadio as Radio  # noqa
from lib.ui.widget.ToggleableEntry import UIToggleableEntry as ToggleableEntry  # noqa
from lib.ui.widget.Tooltip import UIToolTip as ToolTip  # noqa
from lib.ui.widget.v2.Entry import UIEntry as Entry  # noqa

"""
This file is basically an easy way to import all widgets.
You can also control which version of widgets is imported from here, through changing the import path.
Example:
from lib.ui.widget.Entry import UIEntry as Entry :: Uses version 1
from lib.ui.widget.v2.Entry import UIEntry as Entry :: Uses version 2 of Entry, through changing the import path.

-
Be careful with ToolTip, as it is used inside many widgets (not through this import), so if there is ever
a v2.ToolTip, you will need to change inside the widgets that uses it too.
"""
