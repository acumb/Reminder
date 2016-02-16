#!/usr/env python

"""A program for storing and displaying reminders.

Classes:
    Daemon
    Curses_Interface
    Reminder
    Popup

"""

import argparse
import pickle
import datetime
import os
import fcntl
import urwid

ACTIVE = True
INACTIVE = False
MOVE_KEYS = ('up', 'down', 'right', 'left', 'pageup', 'pagedown')
    

class Reminder:
    """Abstract data-type for reminders.

    Data:

    Methods:

    """

    def __init__():
        """ 

        Arguments:

        """

class Daemon:
    """Background process for checking reminders and spawning popups.

    Data:

    Methods:

    """

    def __init__():
        """

        Arguments:

        """

class Popup:
    pass

class Urwid_Interface:
    """Urwid interface for creating/editing reminders.

    Urwid is a python alternative (and optionally wrapper of) ncurses that
    provides an API at a higher level of abstraction.

    Data:

    Methods:

    """

    def __init__(self):
        """Set up interface."""

        # Set test data, will be replaced with reminder objects data
        reminder_names = ['Test1', 'Test2']
        reminder_times = ['Time1', 'Time2']

        palette = [
            (None,  '', ''),
            ('title', 'white', 'dark gray'),
            ('divider', '', ''),
            ('header', 'white', 'dark gray'),
            ('options', 'white', 'black'),
            ('options_fill', 'white', 'black'),
            ('focus', 'black', 'white')]

        title = urwid.Text(('title', 'Reminder editor'), align='left')
        title_map = urwid.AttrMap(title, 'title')

        divider = urwid.Divider()
        divider_map = urwid.AttrMap(divider, 'divider')

        list_header_name = urwid.Text(('header', 'Name'), align='left')
        list_header_name_map = urwid.AttrMap(list_header_name, 'header')
        list_header_time = urwid.Text(('header', 'Remind at'), align='left')
        list_header_time_map = urwid.AttrMap(list_header_time, 'header')
        list_header_body = [list_header_name_map, list_header_time_map]
        list_header = urwid.Columns(urwid.SimpleListWalker(list_header_body))

        list_body = self.__load_reminders()
        list_widget = urwid.Pile(list_body)
        top_body = [title_map, divider_map, list_header, list_widget]
        top_widget = InteractiveListBox(urwid.SimpleFocusListWalker(top_body))
        top_widget = InteractivePile(top_body)
        encapsulating_listbox = urwid.ListBox(urwid.SimpleFocusListWalker([top_widget]))
        # I don't understand why I need to have the pile enscapsulated in a listbox
        loop = urwid.MainLoop(encapsulating_listbox, palette)

        loop.run()

    def add_reminder(self, reminder_name, reminder_time):
        """Add reminder.

        Arguments:
            reminder_name -- Reminder text
            reminder_time -- Time to remind

        """

    def update_reminder(self, reminder_name, reminder_time):
        """Update reminder."""

    def delete_reminder(self, reminder_name):
        """Delete reminder.

        Arguments:
            reminder_name -- 

        """

    def run_interface(self):
        """Run reminder editor interface."""

        # Consider adding try except block.
        self.loop.run()

    def __load_reminders(self):
        """Load pickled reminders"""
        for name, time in zip(reminder_names, reminder_times):


class SwitchableEdit(urwid.Edit):
    """Modify Edit widget so editing only between ENTER key presses"""

    def __init__(self, caption='', edit_text=''):
        """Passes emtpy string as caption."""
        self.state = INACTIVE
        super(SwitchableEdit, self).__init__(caption, edit_text=edit_text)

    def keypress(self, size, key):
        # Should also update the datastructure
        empty_key = ''
        if self.state == ACTIVE:
            if key == 'enter':
                self.state = INACTIVE
                key = empty_key
            elif key in MOVE_KEYS:
                key = empty_key
            else:
                pass
        else:
            if key == 'enter':
                self.state = ACTIVE
                key = empty_key
            elif key not in MOVE_KEYS:
                key = empty_key
        return super(SwitchableEdit, self).keypress(size, key)

class InteractivePile(urwid.Pile):
    """Provide single keystroke global options."""

    def keypress(self, size, key):
        """Decorator to catch custom global option keystrokes"""

        if key == 'q':
            self.quit()
        elif key == 'n':
            self.add_reminder()
        return super(InteractivePile, self).keypress(size, key)

    def quit():
        """Clean quit."""

        raise urwid.ExitMainLoop()

    def add_reminder()
        """Update menu and datastructure"""

            list_entry_name = SwitchableEdit(edit_text=name)
            list_entry_name_map = urwid.AttrMap(list_entry_name, 'options_fill', 'focus')
            list_entry_time = SwitchableEdit(edit_text=time)
            list_entry_time_map = urwid.AttrMap(list_entry_time, 'options_fill', 'focus')
            list_entry_body = [list_entry_name_map, list_entry_time_map]
            list_entry = urwid.Columns(urwid.SimpleFocusListWalker(list_entry_body))
            list_body.append(list_entry)
        list_entry_name = SwitchableEdit(edit_text='Fill in.')
        list_entry_time = SwitchableEdit(edit_text='Fill in.')
        list_entry_body = [list_entry_name, list_entry_time]
        list_entry = urwid.Columns(urwid.SimpleFocusListWalker(list_entry_body))
        self.contents[4][0].contents.append((list_entry, self.options()))
        
def main():
    """Check flags and act accordingly."""


#    Urwid_Interface()

if __name__ == '__main__':
    main()
