import suitcase.csv
import suitcase.json_metadata
import suitcase.specfile
import suitcase.tiff_stack
import suitcase.tiff_series
from PyQt5.QtWidgets import (QPushButton, QVBoxLayout, QTabWidget, QWidget,
                             QCheckBox, QFormLayout, QLineEdit)


class suitcase_params_widget(QWidget):
    '''Widget for entering suitcase export parameters for a given suitcase.

    Parameters
    ----------
    file_type : str
        The name of the suitcase repo that this widget sets params, for e.g.
        'csv' for ``suitcase.csv``
    *args : args
        args passed down to QWidget
    **kwargs : kwargs
        kwargs passed down to QWidget
    default_values : dict
        dictionary giving default values for the input parameters 'directory'
        and 'file_prefix'.
    '''

    def __init__(self, file_type, *args, geometry=(10, 10, 400, 140),
                 default_values={}, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_type = file_type
        self.geometry = geometry
        self.default_values = default_values
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f'Exporter for {self.file_type} files:')
        self.setGeometry(*self.geometry)

        self.main_layout = QFormLayout()

        self.enable_checkbox = QCheckBox('enable exporter', self)
        self.main_layout.addRow('', self.enable_checkbox)

        self.directory = QLineEdit(self)
        self.directory.setText(self.default_values.pop('directory', ''))
        self.main_layout.addRow('directory', self.directory)

        self.file_prefix = QLineEdit(self)
        self.file_prefix.setText(self.default_values.pop('file_prefix', ''))
        self.main_layout.addRow('file_prefix', self.file_prefix)

        self.setLayout(self.main_layout)


class export_widget(QWidget):
    ''' Widget for exporting using suitcases.

    Parameters:
    suitcase_list : list
        List of suitcase repo's that this widget sets params, for e.g.
        'csv' for ``suitcase.csv``
    *args : args
        args passed down to QWidget
    **kwargs : kwargs
        kwargs passed down to QWidget
    '''
    def __init__(self, entries, suitcase_list, *args,
                 geometry=(10, 10, 400, 140), default_values={}, **kwargs):
        super().__init__(*args, **kwargs)
        self.entries = entries
        self.suitcase_list = suitcase_list
        self.geometry = geometry
        self.default_values = default_values
        self.initUI()

    def initUI(self):
        '''generate the layout of the widget.'''
        # set Window parameters
        self.setWindowTitle('export dialog box')
        self.setGeometry(*self.geometry)
        # set the widget layout
        self.layout = QVBoxLayout()

        # add each of the required suitcase tabs
        self.suitcase_tabs = QTabWidget()
        for suitcase_type in self.suitcase_list:
            setattr(self, f'{suitcase_type}_widget',
                    suitcase_params_widget(
                        suitcase_type,
                        default_values=self.default_values[suitcase_type]))
            temp_widget = getattr(self, f'{suitcase_type}_widget')
            setattr(self.suitcase_tabs, f'{suitcase_type}_tab', temp_widget)
            temp_tab = getattr(self.suitcase_tabs, f'{suitcase_type}_tab')
            temp_tab.layout = QVBoxLayout()
            temp_tab.layout.addWidget(temp_widget)
            temp_tab.setLayout(temp_tab.layout)
            self.suitcase_tabs.addTab(temp_tab, suitcase_type)
        # add the tabs to the layout
        self.layout.addWidget(self.suitcase_tabs)
        # add an export button
        self.export_button = QPushButton('export', self)
        self.export_button.clicked.connect(self._export_clicked)
        self.layout.addWidget(self.export_button)
        # add a cancel button
        self.cancel_button = QPushButton('cancel', self)
        self.cancel_button.clicked.connect(self._cancel_clicked)
        self.layout.addWidget(self.cancel_button)

        # set the layout
        self.setLayout(self.layout)

    def _export_clicked(self):
        '''The function run when the export button is clicked.'''
        for suitcase_type in self.suitcase_list:  # step through each suitcase
            temp_widget = getattr(self, f'{suitcase_type}_widget')
            if temp_widget.enable_checkbox.isChecked():
                directory = temp_widget.directory.text()
                kwargs = {'file_prefix': temp_widget.file_prefix.text()}
                export_file(suitcase_type, self.entries, directory, **kwargs)
        self.close()

    def _cancel_clicked(self):
        '''The function run when the cancel button is clicked.'''
        self.close()


def export_file(file_type, entries, directory, **kwargs):
    '''exports the data from 'entries' to the file gieven by 'file_type'.

    parameters
    ----------
    file_type : str
        The name of the suitcase repo to export, e.g 'csv' for ``suitcase.csv``
    entries : list
        A list of ``intake-databroker`` entries associated to export.
    directory : str
        The name of the directory to save the files to.
    **kwargs : dict
        A dictionary of kwargs passed into the export function for the
        ``file_type`` suitcase.
    '''

    for entry in entries:
        docs = entry.read_canonical()
        getattr(suitcase, file_type).export(docs, directory, **kwargs)
