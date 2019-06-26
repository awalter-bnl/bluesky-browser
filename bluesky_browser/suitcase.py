import traitlets
from PyQt5.QtWidgets import (QPushButton, QVBoxLayout, QTabWidget, QWidget,
                             QCheckBox, QFormLayout, QLineEdit)
import suitcase.csv
import suitcase.json_metadata
import suitcase.specfile
import suitcase.tiff_stack
import suitcase.tiff_series
import sys

from .utils import ConfigurableQWidget

class SuitcaseWidget(ConfigurableQWidget):
    '''Widget for entering generic ``suitcase.xyz.export()`` parameters.

    Parameters
    ----------
    *args : args
        args passed down to QWidget
    geometry : tuple
        Tuple giving the (left, top, width, height) required for the window
    **kwargs : kwargs
        kwargs passed down to QWidget

    Configurable Traits
    -------------------
    directory : str
        The directory passed to the ``suitcase.xyz`` exporter
    file_prefix : str
        The file_prefix passed to the ``suitcase.xyz`` exporter
    show : list
        A list of parameters to include in the dialog box
    '''

    file_prefix = traitlets.Unicode('test_data_{start[scan_id]}')
    file_prefix.tag(widget=QLineEdit)
    directory = traitlets.Unicode('test_data')
    directory.tag(widget=QLineEdit)
    show = traitlets.List(['file_prefix', 'directory'])

    def __init__(self, *args, geometry=(10, 10, 400, 140), **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry = geometry
        self.initUI()

    def initUI(self):
        self.setGeometry(*self.geometry)

        self.main_layout = QFormLayout()

        self.enable_checkbox = QCheckBox('enable exporter', self)
        self.main_layout.addRow('', self.enable_checkbox)

        for parameter in self.show:
            trait = self.traits()[parameter]
            setattr(self, f'{parameter}_widget', trait.metadata['widget']())
            getattr(self,
                    f'{parameter}_widget').setText(getattr(self, parameter))
            self.main_layout.addRow(parameter,
                                    getattr(self, f'{parameter}_widget'))

        self.setLayout(self.main_layout)


class json_metadataSuitcaseWidget(SuitcaseWidget):
    '''Widget for entering ``suitcase.json_metatdata.export()`` parameters.
    '''
    ...


class csvSuitcaseWidget(SuitcaseWidget):
    '''Widget for entering ``suitcase.csv.export()`` parameters.

    Parameters
    ----------
    *args : args
        args passed down to QWidget
    geometry : tuple
        Tuple giving the (left, top, width, height) required for the window
    **kwargs : kwargs
        kwargs passed down to QWidget

    Configurable Traits
    -------------------
    directory : str
        The directory passed to the ``suitcase.xyz`` exporter
    file_prefix : str
        The file_prefix passed to the ``suitcase.xyz`` exporter
    show : list
        A list of parameters to include in the dialog box
    seperator : str, default ','
        Str of lenght 1 used as the delimiterfor the output file
    na_rep : str, default ‘’
        Missing data representation.
    float_format : str, default None
        Format string for floating point numbers.
    columns : sequence, optional
        Columns to write.
    header : bool or list of str, default True
        Write out the column names. If a list of strings is given it is assumed
        to be aliases for the column names.
    index : bool, default True
        Write row names (index).
    index_label : str or sequence, or False, default None
        Column label for index column(s) if desired. If None is given, and
        header and index are True, then the index names are used. A sequence
        should be given if the object uses MultiIndex. If False do not print
        fields for index names. Use index_label=False for easier importing in
        R.
    mode : str
        Python write mode, default ‘w’.
    encoding : str, optional
        A string representing the encoding to use in the output file, defaults
        to ‘ascii’ on Python 2 and ‘utf-8’ on Python 3.
    compression : str, default ‘infer’
        Compression mode among the following possible values: {‘infer’, ‘gzip’,
        ‘bz2’, ‘zip’, ‘xz’, None}. If ‘infer’ and path_or_buf is path-like,
        then detect compression from the following extensions: ‘.gz’, ‘.bz2’,
        ‘.zip’ or ‘.xz’. (otherwise no compression).
    line_terminator : string, optional
        The newline character or character sequence to use in the output file.
        Defaults to os.linesep, which depends on the OS in which this method is
        called (‘n’ for linux, ‘rn’ for Windows, i.e.).
    chunksize : int or None
        Rows to write at a time.
    date_format: str, default None
        Format string for datetime objects.
    doublequote : bool, default True
        Control quoting of quotechar inside a field.
    escapechar : str, default None
        String of length 1. Character used to escape sep and quotechar when
        appropriate.
    decimal : str, default ‘.’
        Character recognized as decimal separator. E.g. use ‘,’ for European
        data.
    '''
    seperator = traitlets.Unicode(',')
    seperator.tag(widget=QLineEdit)
    na_rep = traitlets.Unicode('')
    na_rep.tag(widget=QLineEdit)
    float_format = traitlets.Unicode('')
    columns = traitlets.List([])
    header = traitlets.List([])
    index = traitlets.Bool(True)
    index_label = traitlets.List([])
    mode = traitlets.Unicode('a')
    encoding = traitlets.Unicode('ascii')
    compression = traitlets.Unicode('infer')
    line_terminator = traitlets.Unicode('os.lineshape')
    chunksize = traitlets.Int(None, allow_none=True)
    date_format = traitlets.Unicode(None, allow_none=True)
    doublequote = traitlets.Bool(True)
    escapechar = traitlets.Unicode(None, allow_none=True)
    decimal = traitlets.Unicode('.')
    show = traitlets.List(['directory', 'file_prefix', 'seperator'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class export_widget(ConfigurableQWidget):
    ''' Widget for exporting using suitcases.

    Parameters
    ----------
    *args : args
        args passed down to QWidget
    geometry : tuple
        Tuple giving the (left, top, width, height) required for the window
    **kwargs : kwargs
        kwargs passed down to QWidget
    '''
    suitcase_list = traitlets.List(['csv', 'json_metadata'])

    def __init__(self, entries, *args, geometry=(10, 10, 400, 140), **kwargs):
        super().__init__(*args, **kwargs)
        self.entries = entries
        self.geometry = geometry

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
            temp_class = getattr(sys.modules[__name__],
                                 f'{suitcase_type}SuitcaseWidget')
            setattr(self, f'{suitcase_type}_widget', temp_class())
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
                directory = getattr(temp_widget,'directory_widget').text()
                kwargs = {'file_prefix': getattr(temp_widget,
                                                 'file_prefix_widget').text()}
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
