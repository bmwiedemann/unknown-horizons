# ###################################################
# Copyright (C) 2009 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

import pychan

import horizons.main
from horizons.entities import Entities

from horizons.i18n import load_xml_translated
from horizons.util import livingProperty, LivingObject, PychanChildFinder, Rect, Point
from horizons.gui.mousetools import BuildingTool, SelectionTool
from horizons.gui.tabs import TabWidget, BuildTab
from horizons.gui.widgets import Minimap, MessageWidget
from horizons.constants import RES

class IngameGui(LivingObject):
	"""Class handling all the ingame gui events."""

	gui = livingProperty()
	tabwidgets = livingProperty()
	message_widget = livingProperty()

	def __init__(self, session, gui):
		super(IngameGui, self).__init__()
		self.session = session
		self.main_gui = gui
		self.gui = {}
		self.tabwidgets = {}
		self.settlement = None
		self.resource_source = None
		self.resources_needed, self.resources_usable = {}, {}
		self._old_menu = None

		self.gui['cityInfo'] = load_xml_translated('city_info.xml')
		self.gui['cityInfo'].stylize('cityInfo')
		self.gui['cityInfo'].child_finder = PychanChildFinder(self.gui['cityInfo'])
		self.gui['cityInfo'].position = (
			horizons.main.fife.settings.getScreenWidth()/2 - self.gui['cityInfo'].size[0]/2 - 10,
			5
		)

		# self.gui['minimap'] is the guichan gui around the acctual minimap, which is saved
		# in self.minimap
		self.gui['minimap'] = load_xml_translated('minimap.xml')
		self.gui['minimap'].position = (
				horizons.main.fife.settings.getScreenWidth() - self.gui['minimap'].size[0] -20,
			4
		)
		self.gui['minimap'].show()
		self.gui['minimap'].mapEvents({
			'zoomIn' : self.session.view.zoom_in,
			'zoomOut' : self.session.view.zoom_out,
			'rotateRight' : self.session.view.rotate_right,
			'rotateLeft' : self.session.view.rotate_left,
			'speedUp' : self.session.speed_up,
			'speedDown' : self.session.speed_down
		})
		self.minimap = Minimap(Rect(Point(self.gui['minimap'].position[0]+77, 55), 120, 120), \
													 self.session, self.session.view.renderer['GenericRenderer'])
		minimap_overlay = self.gui['minimap'].findChild(name='minimap_overlay_image')
		self.minimap.use_overlay_icon(minimap_overlay)

		self.gui['menuPanel'] = load_xml_translated('menu_panel.xml')
		self.gui['menuPanel'].position = (
			horizons.main.fife.settings.getScreenWidth() - self.gui['menuPanel'].size[0] +15,
			149)
		self.gui['menuPanel'].show()
		self.gui['menuPanel'].mapEvents({
			'destroy_tool' : self.session.destroy_tool,
			'build' : self.show_build_menu,
			'helpLink' : self.main_gui.on_help,
			'gameMenuButton' : self.main_gui.show_pause
		})

		self.gui['tooltip'] = load_xml_translated('tooltip.xml')
		self.gui['tooltip'].hide()

		self.gui['status'] = load_xml_translated('status.xml')
		self.gui['status'].stylize('resource_bar')
		self.gui['status'].child_finder = PychanChildFinder(self.gui['status'])
		self.gui['status_extra'] = load_xml_translated('status_extra.xml')
		self.gui['status_extra'].stylize('resource_bar')
		self.gui['status_extra'].child_finder = PychanChildFinder(self.gui['status_extra'])

		self.message_widget = MessageWidget(self.gui['cityInfo'].position[0] + self.gui['cityInfo'].size[0], 5)

		self.gui['status_gold'] = load_xml_translated('status_gold.xml')
		self.gui['status_gold'].stylize('resource_bar')
		self.gui['status_gold'].show()
		self.gui['status_gold'].child_finder = PychanChildFinder(self.gui['status_gold'])
		self.gui['status_extra_gold'] = load_xml_translated('status_extra_gold.xml')
		self.gui['status_extra_gold'].stylize('resource_bar')
		self.gui['status_extra_gold'].child_finder = PychanChildFinder(self.gui['status_extra_gold'])

		self.gui['change_name'] = load_xml_translated("change_name_dialog.xml")
		self.gui['change_name'].stylize('book')
		self.gui['change_name'].findChild(name='headline').stylize('headline')

		# map button names to build functions calls with the building id
		callbackWithArguments = pychan.tools.callbackWithArguments
		self.callbacks_build = { # keys are settler levels
			0: {
				'store-1' : callbackWithArguments(self._build, 2),
				'church-1' : callbackWithArguments(self._build, 5),
				'main_square-1' : callbackWithArguments(self._build, 4),
				'lighthouse-1' : callbackWithArguments(self._build, 6),
				'resident-1' : callbackWithArguments(self._build, 3),
				'hunter-1' : callbackWithArguments(self._build, 9),
				'fisher-1' : callbackWithArguments(self._build, 11),
				'weaver-1' : callbackWithArguments(self._build, 7),
				'boat_builder-1' : callbackWithArguments(self._build, 12),
				'lumberjack-1' : callbackWithArguments(self._build, 8),
				'tree-1' : callbackWithArguments(self._build, 17),
				'potatofield-1' : callbackWithArguments(self._build, 19),
				'herder-1' : callbackWithArguments(self._build, 20),
				'pasture-1' : callbackWithArguments(self._build, 18),
				'tower-1' : callbackWithArguments(self._build, 13),
				#'wall-1' : callbackWithArguments(self._build, 14),
				'street-1' : callbackWithArguments(self._build, 15),
				#'bridge-1' : callbackWithArguments(self._build, 16)
		},
			1: {
		    'school-1' : callbackWithArguments(self._build, 21),
		    'sugarfield-1' : callbackWithArguments(self._build, 22)
		},
			2: {
		},
			3: {
		},
			4: {
		}
		}

	def end(self):
		self.gui['menuPanel'].mapEvents({
			'destroy_tool' : None,
			'build' : None,
			'helpLink' : None,
			'gameMenuButton' : None
		})

		self.gui['minimap'].mapEvents({
			'zoomIn' : None,
			'zoomOut' : None,
			'rotateRight' : None,
			'rotateLeft' : None
		})

		for w in self.gui.itervalues():
			if w.parent is None:
				w.hide()
		self.message_widget = None
		self.tabwidgets = None
		self.hide_menu()
		super(IngameGui, self).end()

	def update_gold(self):
		first = str(self.session.world.player.inventory[RES.GOLD_ID])
		lines = []
		show = False
		if self.resource_source is not None and self.resources_needed.get(RES.GOLD_ID, 0) != 0:
			show = True
			lines.append('- ' + str(self.resources_needed[RES.GOLD_ID]))
		self.status_set('gold', first)
		self.status_set_extra('gold',lines)
		self.set_status_position('gold')
		if show:
			self.gui['status_extra_gold'].show()
		else:
			self.gui['status_extra_gold'].hide()

	def status_set(self, label, value):
		"""Sets a value on the status bar (available res of the settlement).
		@param label: str containing the name of the label to be set.
		@param value: value the Label is to be set to.
		"""
		if isinstance(value,list):
			value = value[0]
		gui = self.gui['status_gold'] if label == 'gold' else self.gui['status']
		foundlabel = gui.child_finder(label + '_1')
		foundlabel._setText(unicode(value))
		foundlabel.resizeToContent()
		gui.resizeToContent()

	def status_set_extra(self,label,value):
		"""Sets a value on the extra status bar. (below normal status bar, needed res for build)
		@param label: str containing the name of the label to be set.
		@param value: value the Label is to be set to.
		"""
		if not value:
			foundlabel = (self.gui['status_extra_gold'] if label == 'gold' else self.gui['status_extra']).child_finder(label + '_' + str(2))
			foundlabel.text = u''
			foundlabel.resizeToContent()
			self.gui['status_extra_gold'].resizeToContent() if label == 'gold' else self.gui['status_extra'].resizeToContent()
			return
		if isinstance(value, str):
			value = [value]
		#for i in xrange(len(value), 3):
		#	value.append("")
		for i in xrange(0,len(value)):
			foundlabel = (self.gui['status_extra_gold'] if label == 'gold' else self.gui['status_extra']).child_finder(name=label + '_' + str(i+2))
			foundlabel._setText(unicode(value[i]))
			foundlabel.resizeToContent()
		if label == 'gold':
			self.gui['status_extra_gold'].resizeToContent()
		else:
			self.gui['status_extra'].resizeToContent()

	def cityinfo_set(self, settlement):
		"""Sets the city name at top center

		Show/Hide is handled automatically
		To hide cityname, set name to ''
		@param settlement: Settlement class providing the information needed
		"""
		if settlement is self.settlement:
			return
		if self.settlement is not None:
			self.settlement.remove_change_listener(self.update_settlement)
		self.settlement = settlement
		if settlement is None:
			self.gui['cityInfo'].hide()
		else:
			self.gui['cityInfo'].show()
			self.update_settlement()
			settlement.add_change_listener(self.update_settlement)

	def resourceinfo_set(self, source, res_needed = {}, res_usable = {}, res_from_ship = False):
		city = source if not res_from_ship else None
		self.cityinfo_set(city)
		if source is not self.resource_source:
			if self.resource_source is not None:
				self.resource_source.remove_change_listener(self.update_resource_source)
			if source is None:
				self.gui['status'].hide()
				self.gui['status_extra'].hide()
				self.resource_source = None
				self.update_gold()
		if source is not None:
			if source is not self.resource_source:
				source.add_change_listener(self.update_resource_source)
			self.resource_source = source
			self.resources_needed = res_needed
			self.resources_usable = res_usable
			self.update_resource_source()
			self.gui['status'].show()

	def update_settlement(self):
		self.gui['cityInfo'].mapEvents({'city_name': pychan.tools.callbackWithArguments( \
			self.show_change_name_dialog, self.settlement)})
		foundlabel = self.gui['cityInfo'].child_finder('city_name')
		foundlabel._setText(unicode(self.settlement.name))
		foundlabel.resizeToContent()
		foundlabel = self.gui['cityInfo'].child_finder('city_inhabitants')
		foundlabel.text = unicode(' '+str(self.settlement.inhabitants))
		foundlabel.resizeToContent()
		self.gui['cityInfo'].resizeToContent()

	def update_resource_source(self):
		"""Sets the values for resource status bar as well as the building costs"""
		self.update_gold()
		for res_id, res_name in {3 : 'textiles', 4 : 'boards', 5 : 'food', 6 : 'tools', 7 : 'bricks'}.iteritems():
			first = str(self.resource_source.inventory[res_id])
			lines = []
			show = False
			if self.resources_needed.get(res_id, 0) != 0:
				show = True
				lines.append('- ' + str(self.resources_needed[res_id]))
			self.status_set(res_name, first)
			self.status_set_extra(res_name,lines)
			self.set_status_position(res_name)
			if show:
				self.gui['status_extra'].show()

	def ship_build(self, ship):
		"""Calls the Games build_object class."""
		self._build(1, ship)

	def minimap_to_front(self):
		self.gui['minimap'].hide()
		self.gui['minimap'].show()
		self.gui['menuPanel'].hide()
		self.gui['menuPanel'].show()

	def show_ship(self, ship):
		self.gui['ship'].findChild(name='buildingNameLabel').text = \
				unicode(ship.name+" (Ship type)")

		size = self.gui['ship'].findChild(name='chargeBar').size
		size = (size[0] - 2, size[1] - 2)
		self.gui['ship'].findChild(name='chargeBarLeft').size = (int(0.5 + 0.75 * size[0]), size[1])
		self.gui['ship'].findChild(name='chargeBarRight').size = (int(0.5 + size[0] - 0.75 * size[0]), size[1])

		pos = self.gui['ship'].findChild(name='chargeBar').position
		pos = (pos[0] + 1, pos[1] + 1)
		self.gui['ship'].findChild(name='chargeBarLeft').position = pos
		self.gui['ship'].findChild(name='chargeBarRight').position = (int(0.5 + pos[0] + 0.75 * size[0]), pos[1])
		self.gui['ship'].mapEvents({
			'foundSettelment' : ychan.tools.callbackWithArguments(self.ship_build, ship)
		})
		self.show_menu('ship')

	def show_build_menu(self):
		self.session.cursor = SelectionTool(self.session) # set cursor for build menu
		self.deselect_all()
		btabs = [BuildTab(index, self.callbacks_build[index]) for index in
			range(0, self.session.world.player.settler_level+1)]
		tab = TabWidget(tabs=btabs)
		self.show_menu(tab)

	def deselect_all(self):
		for instance in self.session.selected_instances:
			instance.deselect()
		self.session.selected_instances = set()

	def _build(self, building_id, unit = None):
		"""Calls the games buildingtool class for the building_id.
		@param building_id: int with the building id that is to be built.
		@param unit: weakref to the unit, that builds (e.g. ship for branch office)"""
		self.hide_menu()
		self.deselect_all()
		cls = Entities.buildings[building_id]
		if hasattr(cls, 'show_build_menu'):
			cls.show_build_menu()
		self.session.cursor = BuildingTool(self.session, cls, None if unit is None else unit())


	def _get_menu_object(self, menu):
		"""Returns pychan object if menu is a string, else returns menu
		@param menu: str with the guiname or pychan object.
		"""
		if isinstance(menu, str):
			menu = self.gui[menu]
		return menu

	def get_cur_menu(self):
		"""Returns menu that is currently displayed"""
		return self._old_menu

	def show_menu(self, menu):
		"""Shows a menu
		@param menu: str with the guiname or pychan object.
		"""
		if self._old_menu is not None:
			self._old_menu.hide()

		self._old_menu = self._get_menu_object(menu)
		if self._old_menu is not None:
			self._old_menu.show()
			self.minimap_to_front()

	def hide_menu(self):
		self.show_menu(None)

	def toggle_menu(self, menu):
		"""Shows a menu or hides it if it is already displayed.
		@param menu: parameter supported by show_menu().
		"""
		if self.get_cur_menu() == self._get_menu_object(menu):
			self.hide_menu()
		else:
			self.show_menu(menu)

	def build_load_tab(self, num):
		"""Loads a subcontainer into the build menu and changes the tabs background.
		@param num: number representing the tab to load.
		"""
		tab1 = self.gui['build'].findChild(name=('tab'+str(self.active_build)))
		tab2 = self.gui['build'].findChild(name=('tab'+str(num)))
		activetabimg, nonactiveimg= tab1._getImage(), tab2._getImage()
		tab1._setImage(nonactiveimg)
		tab2._setImage(activetabimg)
		contentarea = self.gui['build'].findChild(name='content')
		contentarea.removeChild(self.gui['build_tab'+str(self.active_build)])
		contentarea.addChild(self.gui['build_tab'+str(num)])
		contentarea.adaptLayout()
		self.active_build = num

	def set_status_position(self, resource_name):
		for i in xrange(1, 4):
			icon_name = resource_name + '_icon'
			plusx = 0
			if i > 1:
				# increase x position for lines greater the 1
				plusx = 20
			if resource_name == 'gold':
				self.gui['status_gold'].child_finder(resource_name + '_' + str(i)).position = (
					self.gui['status_gold'].child_finder(icon_name).position[0] + 33 - self.gui['status_gold'].findChild(name = resource_name + '_' + str(i)).size[0]/2,
					41 + 10 * i + plusx
				)
			else:
				self.gui['status'].child_finder(resource_name + '_' + str(i)).position = (
					self.gui['status'].child_finder(icon_name).position[0] + 24 - self.gui['status'].child_finder(resource_name + '_' + str(i)).size[0]/2,
					41 + 10 * i + plusx
				)

	def save(self, db):
		self.message_widget.save(db)

	def load(self, db):
		self.message_widget.load(db)

		self.minimap.draw() # update minimap to new world

	def show_change_name_dialog(self, instance):
		"""Shows a dialog where the user can change the name of a NamedObject.
		The game gets paused while the dialog is executed."""
		self.session.speed_pause()
		events = {
			'okButton': pychan.tools.callbackWithArguments(self.change_name, instance),
			'cancelButton': self.hide_change_name_dialog
		}
		self.on_escape = self.hide_change_name_dialog
		self.gui['change_name'].mapEvents(events)
		self.gui['change_name'].show()

	def hide_change_name_dialog(self):
		"""Escapes the change_name dialog"""
		self.session.speed_unpause()
		self.on_escape = self.show_pause
		self.gui['change_name'].hide()

	def change_name(self, instance):
		"""Applies the change_name dialogs input and hides it"""
		new_name = self.gui['change_name'].collectData('new_name')
		self.gui['change_name'].findChild(name='new_name').text = u''
		instance.set_name(new_name)
		self.hide_change_name_dialog()

