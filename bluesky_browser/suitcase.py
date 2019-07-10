import traitlets
from PyQt5.QtWidgets import (QPushButton, QVBoxLayout, QTabWidget, QCheckBox,
                             QFormLayout, QLineEdit, QSpinBox)
import suitcase.csv
import suitcase.json_metadata
import suitcase.specfile
import suitcase.tiff_stack
import suitcase.tiff_series

from .utils import (ConfigurableQWidget, QStrListEdit, QIntListEdit, QBoolBox,
                    QBoolNoneBox)


class SuitcaseWidget(ConfigurableQWidget):
    '''Widget for entering generic ``suitcase.xyz.export()`` parameters.

    Parameters
    ----------
    *args : args
        args passed down to QWidget
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
    # Add the two required traits for the parameters file_prefix and directory
    file_prefix = traitlets.Unicode('test_data_{start[scan_id]}')
    directory = traitlets.Unicode('test_data')

    # Add the list of parameters for which the input widget should be displayed
    parameters = traitlets.List(['file_prefix', 'directory'])
    # Tuple giving the (left, top, width, height) size of the required window
    geometry = traitlets.Tuple((10, 10, 600, 200))


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initGUI()
        self.show_parameters()

    def initGUI(self):
        '''Initialize the widget defined by this class'''
        # set the layout and define the shape of the suitcase widget.
        self.setGeometry(*self.geometry)
        self.main_layout = QFormLayout()

        # add an 'enable exporter' checkbox.
        self.enable_checkbox = QCheckBox('enable exporter', self)
        self.main_layout.addRow('', self.enable_checkbox)

        # set the trait widgets for `file_prefix` and `directory`.
        self._create_trait_widget('directory', QLineEdit, 'setText',
                                  'textChanged')
        self._create_trait_widget('file_prefix', QLineEdit, 'setText',
                                  'textChanged')

    def show_parameters(self, parameters=[]):
        '''Walks through ``parameters`` then ``self.parameters`` showing the
           widgets.'''

        # add any parameters from self.parameters, if they are unique.
        for parameter in self.parameters:
            if parameter not in parameters: parameters.append(parameter)

        # step through each parameter and add the widget to the layout.
        for parameter in parameters:
            # collect the trait and widget_type objects.
            trait_widget = getattr(self, f'{parameter}_widget')
            self.main_layout.addRow(parameter, trait_widget)

        # set ``self.main_layout`` as the layout
        self.setLayout(self.main_layout)

    def _create_trait_widget(self, trait_name, widget_type, slot_name,
                             signal_name):
        '''Creates an input widget for a trait based on the input parameters.

        This creates an input widget for the trait specified by ``trait_name``
        using ``widget_type`` as the type. It also ensures that the current
        value of ``trait_name`` is set to the widgets ``slot_name`` and that
        ``trait_name`` is connected to the widgets ``signal_name``.

        Parameters
        ----------
        trait_name : str
            The name of the trait as a string, i.e. the trait is found at
            ``self.trait_name``.
        widget_type : obj
            The pyqt5 widget class that is to be used to create the input
            widget, e.g. ``PyQt5.QtWidgets.QLineEdit``
        slot_name : str
            The name of the ``PyQt5.QtCore.pyqtSlot from ``widget_type`` to set
            the current value too, e.g. ``PyQt5.QtWidget.QlineEdit.setText``.
        signal_name : str
            The name of the ``PyQt5.QtCore.pyqtSignal from ``widget_type`` to
            connect the trait too, e.g. ``PyQt5.QtWidget.QlineEdit.setText``.
        '''

        # reference the trait and create the trait widget
        trait = getattr(self, trait_name)
        setattr(self, f'{trait_name}_widget', widget_type())
        trait_widget = getattr(self, f'{trait_name}_widget')
        # write the value of the trait to the widget
        if trait is not None:  # ignore if it is "None"
            getattr(trait_widget, slot_name)(trait)
        # Connect the output of the widget to the file_prefix trait.
        getattr(trait_widget, signal_name).connect(
            lambda output: setattr(self, trait_name, output))


class json_metadataSuitcaseWidget(SuitcaseWidget):
    '''Widget for entering ``suitcase.json_metatdata.export()`` parameters.
    '''
    ...


class csvSuitcaseWidget(SuitcaseWidget):
    '''Widget for entering ``suitcase.csv.export()`` parameters.

    This widget adds the ``suitcase.csv`` specific traits, one for each of the
    args/kwargs in ``suitcase.csv.export`` and for each of the kwargs in
    ``pandas.dataframe.to_csv``.

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
    index_label : str or None, default None
        Column label for index column(s) if desired. If None is given, and
        header and index are True, then the index names are used
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
    # Add all of the csv specific parameter traits.
    seperator = traitlets.Unicode(',')
    na_rep = traitlets.Unicode('')
    float_format = traitlets.Unicode('')
    columns = traitlets.List([])
    header = traitlets.List([])
    index = traitlets.Bool(True)
    index_label = traitlets.Bool(None, allow_none=True)
    mode = traitlets.Unicode('a')
    encoding = traitlets.Unicode('ascii')
    compression = traitlets.Unicode('infer')
    line_terminator = traitlets.Unicode('os.lineshape')
    chunksize = traitlets.Int(None, allow_none=True)
    date_format = traitlets.Unicode(None, allow_none=True)
    doublequote = traitlets.Bool(True)
    escapechar = traitlets.Unicode(None, allow_none=True)
    decimal = traitlets.Unicode('.')

    # Add the list of parameters for which the input widget should be displayed
    parameters = traitlets.List(['directory', 'file_prefix', 'seperator'])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def initGUI(self):
        super().initGUI()  # ensures directory and file_prefix are at the top.

        # set all of the unique traits widgets
        self._create_trait_widget('seperator', QLineEdit, 'setText',
                                  'textChanged')
        self._create_trait_widget('na_rep', QLineEdit, 'setText',
                                  'textChanged')
        self._create_trait_widget('float_format', QLineEdit, 'setText',
                                  'textChanged')
        self._create_trait_widget('columns', QIntListEdit, 'setList',
                                  'listChanged')
        self._create_trait_widget('header', QStrListEdit, 'setList',
                                  'listChanged')
        self._create_trait_widget('index', QBoolBox, 'setBool',
                                  'boolChanged')
        self._create_trait_widget('index_label', QBoolNoneBox, 'setBool',
                                  'boolChanged')
        self._create_trait_widget('mode', QLineEdit, 'setText',
                                  'textChanged')
        self._create_trait_widget('encoding', QLineEdit, 'setText',
                                  'textChanged')
        self._create_trait_widget('compression', QLineEdit, 'setText',
                                  'textChanged')
        self._create_trait_widget('line_terminator', QLineEdit, 'setText',
                                  'textChanged')
        self._create_trait_widget('chunksize', QSpinBox, 'setValue',
                                  'valueChanged')
        self._create_trait_widget('date_format', QLineEdit, 'setText',
                                  'textChanged')
        self._create_trait_widget('doublequote', QBoolBox, 'setBool',
                                  'boolChanged')
        self._create_trait_widget('escapechar', QLineEdit, 'setText',
                                  'textChanged')
        self._create_trait_widget('decimal', QLineEdit, 'setText',
                                  'textChanged')

    def show_parameters(self, parameters = []):
        '''Walks through ``parameters`` then ``super().parameters`` showing the
        widgets.

        NOTE: This modified version is required for all child classes. The call
        to ``super().parameters`` from inside ``super().show_parameters()``
        does not find any parameters.
        '''
        # add any parent parameters first if they exist.
        try:
            # add any parameters from super.parameters, if they are unique.
            for parameter in super().parameters:
                if parameter not in parameters: parameters.append(parameter)
        except AttributeError:
            ...

        super().show_parameters(parameters=parameters)


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
    # A dict mapping suitcases to labels'
    suitcase_dict = {'json_metadata': json_metadataSuitcaseWidget,
                     'csv': csvSuitcaseWidget}
    # A list of suitcase 'labels' to show
    suitcases = traitlets.List(['json_metadata', 'csv'])
    # Tuple giving the (left, top, width, height) size of the required window
    geometry = traitlets.Tuple((10, 10, 600, 200))

    def __init__(self, entries, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entries = entries
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
        for suitcase_label in self.suitcases:
            temp_class = self.suitcase_dict[suitcase_label]
            setattr(self, f'{suitcase_label}_widget', temp_class())
            temp_widget = getattr(self, f'{suitcase_label}_widget')
            setattr(self.suitcase_tabs, f'{suitcase_label}_tab', temp_widget)
            temp_tab = getattr(self.suitcase_tabs, f'{suitcase_label}_tab')
            temp_tab.layout = QVBoxLayout()
            temp_tab.layout.addWidget(temp_widget)
            self.suitcase_tabs.addTab(temp_tab, suitcase_label)
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
        for suitcase_label in self.suitcases:  # step through each suitcase
            temp_widget = getattr(self, f'{suitcase_label}_widget')
            if temp_widget.enable_checkbox.isChecked():
                directory = getattr(temp_widget, 'directory_widget').text()
                kwargs = {'file_prefix': getattr(temp_widget,
                                                 'file_prefix_widget').text()}
                export_file(suitcase_label, self.entries, directory, **kwargs)
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
