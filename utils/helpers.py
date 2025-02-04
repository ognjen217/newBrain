def merge_dicts(a, b):
    """
    Spaja dva rečnika, gde vrednosti iz b prepisuju one iz a.
    
    :param a: Prvi rečnik
    :param b: Drugi rečnik (vrednosti ovde imaju prioritet)
    :return: Novi rečnik koji predstavlja spajanje a i b
    """
    result = a.copy()
    result.update(b)
    return result

def validate_config(config, required_keys):
    """
    Proverava da li zadati konfiguracioni rečnik sadrži sve neophodne ključeve.
    
    :param config: Konfiguracioni rečnik
    :param required_keys: Lista ključeva koji moraju postojati u config-u
    :return: Tuple (bool, missing_keys). Prvi element je True ako su svi ključevi prisutni,
             a drugi je lista nedostajućih ključeva (ako ih ima).
    """
    missing = [key for key in required_keys if key not in config]
    return (len(missing) == 0, missing)
