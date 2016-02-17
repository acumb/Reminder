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
import sys
import subprocess
import fcntl
import urwid
import time
import pytz

ACTIVE = True
INACTIVE = False
MOVE_KEYS = ('up', 'down', 'right', 'left', 'pageup', 'pagedown')
LONDON_TIMEZONE = pytz.timezone('Europe/London')
    

def lock_and_write_pickle(pickle_file, prepickle):
    locked = True
    while locked:
        try:
            with open(pickle_file, 'wb') as file:
                fcntl.fcntl(file, fcntl.LOCK_EX)
                pickle.dump(prepickle, file)
                fcntl.fcntl(file, fcntl.LOCK_UN)
                locked = False

        except OSError:
            time.sleep(1)


def lock_and_load_pickle(pickle_file):
    locked = True
    while locked:
        try:
            with open(pickle_file, 'rb') as file:
                fcntl.fcntl(file, fcntl.LOCK_EX)
                pickle_data = pickle.load(file)
                fcntl.fcntl(file, fcntl.LOCK_UN)
                locked = False

        except OSError:
            time.sleep(1)

    return pickle_data

def make_filler_time():
    filler_time = datetime.datetime(2099, 12, 12, hour=23, minute=59, 
        tzinfo=LONDON_TIMEZONE)
    return filler_time

class Reminders():
    """Collection of reminders."""

    def __init__(self):
        self.data_file = 'test.pickle'

        # If data file doesn't exist, create with filler entry
        filler_time = make_filler_time()
        if not os.path.isfile(self.data_file):
            with open(self.data_file, 'wb') as file:
                pickle.dump({'fill': filler_time}, file)

        self.reminder_dict = self.__load_reminders()

    def __iter__(self):
        return iter(self.reminder_dict.items())

    def __len__(self):
        return len(self.reminder_dict)

    def add_reminder(self, name, reminder_time):
        self.reminder_dict[name] = reminder_time

    def update_reminder(self, old_name, new_name, new_time):
        """Update reminder name and time."""

        del self.reminder_dict[old_name]
        self.reminder_dict[new_name] = new_time
        lock_and_write_pickle(self.data_file, self.reminder_dict)

    def update(self):
        self.reminder_dict = self.__load_reminders()

    def delete_reminder(self, name):
        del self.reminder_dict[name]
        lock_and_write_pickle(self.data_file, self.reminder_dict)

    def __load_reminders(self):
        """Load reminders from database."""

        reminder_dict = lock_and_load_pickle(self.data_file)

        return reminder_dict


class Daemon:
    """Background process for checking reminders and spawning popups."""

    state_file = 'reminder_daemon_state.pickle'

    @staticmethod
    def daemon_running():
        if not os.path.isfile(Daemon.state_file):
            daemon_running = False

        else:
            daemon_running = lock_and_load_pickle(Daemon.state_file)

        return daemon_running

    def __init__(self, reminders):
        self.reminders = reminders
        self.daemon_running = True

        if not os.path.isfile(Daemon.state_file):
            with open(Daemon.state_file, 'wb') as file:
                pickle.dump(self.daemon_running, file)
        else:
            self.update_state()

    def start(self):
        # really bad code to make this a background process
        if os.fork():
            sys.exit()
        try:
            while self.daemon_running:
                self.reminders.update()
                self._check_reminders()
                if not Daemon.daemon_running():
                    self.daemon_running = False

                time.sleep(10)
        except:
            self.daemon_running = False
            self.update_state()
            raise

    def _check_reminders(self):
        reminders_to_delete = []
        for reminder, reminder_time in self.reminders:
            if reminder_time <= reminder_time.now(tz=reminder_time.tzinfo):
                self.popup(reminder)
                reminders_to_delete.append(reminder)

        for reminder in reminders_to_delete:
            self.reminders.delete_reminder(reminder)

    def popup(self, name):
        # It automatically detects what screen is current and spawns there
        subprocess.run(['urxvt', '--hold', '-e', 'echo', name])

    def update_state(self):
        lock_and_write_pickle(Daemon.state_file, self.daemon_running)


class Urwid_Interface:
    """Urwid interface for creating/editing reminders.

    Urwid is a python alternative (and optionally wrapper of) ncurses that
    provides an API at a higher level of abstraction.

    Data:

    Methods:

    """

    def __init__(self, reminders):
        """Set up interface."""

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

        table_header_name = urwid.Text(('header', 'Name'), align='left')
        table_header_name_map = urwid.AttrMap(table_header_name, 'header')
        table_header_time = urwid.Text(('header', 'Remind at'), align='left')
        table_header_time_map = urwid.AttrMap(table_header_time, 'header')
        table_header_body = [table_header_name_map, table_header_time_map]
        table_header = urwid.Columns(urwid.SimpleListWalker(table_header_body))

        menu_header = [title_map, divider_map, table_header]
        menu_widget = ReminderMenu(menu_header, reminders)

        # I don't understand why I need to have the pile enscapsulated in a listbox
        encapsulating_listbox = urwid.ListBox(urwid.SimpleFocusListWalker([menu_widget]))
        self.loop = urwid.MainLoop(encapsulating_listbox, palette)

    def run(self):
        """Run reminder editor interface."""

        # Consider adding try except block.
        self.loop.run()


# Should I make this only the filter for global keys, and decorate another pile to provide an abstraction for the list of reminders?
class ReminderMenu(urwid.Pile):
    """Pile for browsing and editing reminder entries.."""

    def __init__(self, menu_header, reminders):
        self.state = INACTIVE
        self.reminders = reminders
        menu_body = []
        for name, reminder_time in self.reminders:
            time_string = self._time_to_string(reminder_time)
            menu_entry = ReminderEntry(self, name, time_string)
            menu_body.append(menu_entry)
        
        menu_flat = menu_header + menu_body
        return super(ReminderMenu, self).__init__(menu_flat)

    def keypress(self, size, key):
        """Decorator to catch custom global option keystrokes"""

        #print('in menu')
        if self.state == ACTIVE:
            pass
        else:
            if key == 'q':
                self.quit()
            elif key == 'n':
                self.add_reminder()
            elif key == 'd':
                self.delete_reminder()
            elif key == 'k':
                self.kill_daemon()

        return super(ReminderMenu, self).keypress(size, key)

    def quit(self):
        """Clean quit."""

        raise urwid.ExitMainLoop()

    def add_reminder(self):
        """Add reminder.

        Arguments:
            reminder_name -- Reminder text
            reminder_time -- Time to remind

        """
        name = ''
        filler_time = make_filler_time()
        self.reminders.add_reminder(name,filler_time)
        time_string = self._time_to_string(filler_time)
        menu_entry = ReminderEntry(self, name, time_string)
        self.contents.append((menu_entry, self.options()))
        
    def update(self, old_name, new_name, time_string):
        """Update reminder."""

        reminder_datetime = self._string_to_time(time_string)
        self.reminders.update_reminder(old_name, new_name, reminder_datetime)

    def delete_reminder(self):
        """Delete reminder.

        Arguments:
            reminder_name -- 

        """
        reminder_index = self.focus_position
        # contents are tuples, first position contains widget (wrap for better interface)
        name = self.contents[reminder_index][0].name

        if len(self.reminders) == 1:
            pass
            #blank_name = ''
            #blank_time = ''
            #self.update(name, blank_name, blank_time)
        else:
            del self.contents[reminder_index]
            self.reminders.delete_reminder(name)

    def kill_daemon(self):
        daemon_running = False
        lock_and_write_pickle(Daemon.state_file, daemon_running)
        self.quit()

    def _string_to_time(self, datetime_string):
        date_string, time_string = datetime_string.split()
        year, month, day = date_string.split('-')
        hour, minute = time_string.split(':')
        reminder_datetime = datetime.datetime(int(year), int(month), int(day),
            hour=int(hour), minute=int(minute), tzinfo=LONDON_TIMEZONE)
        return reminder_datetime

    def _time_to_string(self, reminder_datetime):
        year = reminder_datetime.year
        month = reminder_datetime.month
        day = reminder_datetime.day
        hour = reminder_datetime.hour
        minute = reminder_datetime.minute
        time_string = '{year}-{month}-{day} {hour}:{minute}'.format(year=year,
            month=month, day=day, hour=hour, minute=minute)
        return time_string


class TableEntry(urwid.Edit):
    """Interface for entries in reminders."""

    name = 0
    reminder_time = 1

    def __init__(self, reminder_entry, reminder_menu, reminder_data, reminder_type):
        assert reminder_type in (TableEntry.name, TableEntry.reminder_time)

        self.reminder_entry = reminder_entry
        self.reminder_menu = reminder_menu
        self.reminder_type = reminder_type
        super(TableEntry, self).__init__(caption='', edit_text=reminder_data)

    @property
    def reminder_data(self):
        reminder_data = self.get_edit_text()
        return reminder_data

    def keypress(self, size, key):
        """Catches keys based on state of table entry."""

        #print('in entry')
        empty_key = ''
        state_switch_key = 'enter'

        if self.reminder_menu.state == ACTIVE:
            if key == state_switch_key:
                self.reminder_menu.state = INACTIVE
                self.reminder_entry.update(self.reminder_data, self.reminder_type)
                key = empty_key
            elif key in MOVE_KEYS:
                key = empty_key
            else:
                pass
        else:
            if key == state_switch_key:
                self.reminder_menu.state = ACTIVE
                key = empty_key
            elif key not in MOVE_KEYS:
                key = empty_key

        return super(TableEntry, self).keypress(size, key)


class ReminderEntry(urwid.Columns):
    """Interface for reminder entries"""

    def __init__(self, reminder_menu, name, time_string):
        self.reminder_menu = reminder_menu
        self.name = name
        self.time_string = time_string

        table_entry_name = TableEntry(self, reminder_menu, name, TableEntry.name)
        table_entry_name_map = urwid.AttrMap(table_entry_name, 'options_fill', 'focus')
        table_entry_time = TableEntry(self, reminder_menu, time_string, TableEntry.reminder_time)
        table_entry_time_map = urwid.AttrMap(table_entry_time, 'options_fill', 'focus')
        table_entry_body = [table_entry_name_map, table_entry_time_map]
        super(ReminderEntry, self).__init__(urwid.SimpleFocusListWalker(table_entry_body))

    def update(self, reminder_data, reminder_type):
        """Update underlying data type for reminders."""
        
        old_name = self.name
        if reminder_type == TableEntry.name:
            old_name = self.name
            self.name = reminder_data
        elif reminder_type == TableEntry.reminder_time:
            self.time_string = reminder_data

        self.reminder_menu.update(old_name, self.name, self.time_string)


def main():
    """Check mode and state and act accordingly."""

    parser = argparse.ArgumentParser()
    parser.add_argument('--daemon', dest='daemon_mode', action='store_true')
    arguments = parser.parse_args()
    
    daemon_running = Daemon.daemon_running()
    reminders = Reminders()

    if arguments.daemon_mode:
        if daemon_running:
            print('\nDaemon already running\n')
            sys.exit()
        daemon = Daemon(reminders)
        daemon.start()

    else:
        if not daemon_running:
            print('\nDaemon not running\n')
            sys.exit()
        interface = Urwid_Interface(reminders)
        interface.run()


if __name__ == '__main__':
    main()
