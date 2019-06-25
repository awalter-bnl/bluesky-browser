import suitcase.json_metadata

def export_file(entries):
    '''exports the file with the uid given by ``uid``.

    parameters
    ----------
    uid : str
        The uid associated with the scan to export.
    '''

    for entry in entries:
        docs = entry.read_canonical()
        suitcase.json_metadata.export(docs, 'test_data', 'test_data_{start[scan_id]}')
