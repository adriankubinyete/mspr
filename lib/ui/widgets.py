# widget parts
from lib.ui.widget.BoxAssign import UIBoxAssign as BoxAssign
from lib.ui.widget.Checkbox import UICheckbox as Checkbox
from lib.ui.widget.ClickAssign import UIClickAssign as ClickAssign
from lib.ui.widget.v2.Entry import UIEntry as Entry
from lib.ui.widget.Radio import UIRadio as Radio
from lib.ui.widget.ToggleableEntry import UIToggleableEntry as ToggleableEntry
from lib.ui.widget.Tooltip import UIToolTip as ToolTip
from lib.ui.widget.InfoButton import UIInfoButton as InfoButton

# modals (put them on buttons)
from lib.ui.modals.Debug import ModalDebug
from lib.ui.modals.ScreenCallibration import ModalScreenCallibration
from lib.ui.modals.Biome import ModalBiomeManager
from lib.ui.modals.RAMWS import ModalRAMWSSettings

# other items (standalone frames)
from lib.ui.MultiAccountPage import MultiAccountPage
from lib.ui.TabManager import TabManagerPage
from lib.ui.pages.Development import DevelopmentPage

"""
This file is basically an easy way to import all widgets.
You can also control which version of widgets is imported from here, through changing the import path.
Example:
from lib.ui.widget.Entry import UIEntry as Entry :: Uses version 1
from lib.ui.widget.v2.Entry import UIEntry as Entry :: Uses version 2 of Entry, through changing the import path.

- ⚠️ 
Be careful with ToolTip, as it is used inside many widgets (not through this import), so if there is ever
a v2.ToolTip, you will need to change inside the widgets that uses it too.
"""