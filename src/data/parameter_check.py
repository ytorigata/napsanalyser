def are_all_sites_included(parameter):
    """
    Check if all sites are required by the parameter. If 'all' (string) is specified, 
    return True, otherwise return False.
    - input: sites: a list of site ID (int) or 'all' (string)
    - output: bool
    """
    if isinstance(parameter, list):
        return False
    elif isinstance(parameter, str):
        if parameter == 'all':
            return True
        else:
            raise 'Select sites with a list of Site ID (int) or pass "all".'
