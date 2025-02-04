import threading
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

def run_in_thread(target, name="WorkerThread", args=None, kwargs=None, daemon=True):
    """
    Pokreće zadatu funkciju (target) u zasebnoj niti.
    
    :param target: Funkcija koju treba pokrenuti u niti
    :param name: Ime niti (podrazumevano "WorkerThread")
    :param args: Tuple pozicijskih argumenata za target funkciju
    :param kwargs: Rečnik ključnih argumenata za target funkciju
    :param daemon: Da li je nit daemon (podrazumevano True)
    :return: Kreirana i pokrenuta Thread instanca
    """
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    thread = threading.Thread(target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
    thread.start()
    return thread

def run_in_process(target, name="WorkerProcess", args=None, kwargs=None):
    """
    Pokreće funkciju (target) u zasebnom procesu koristeći modul multiprocessing.
    
    :param target: Funkcija koju treba pokrenuti u procesu
    :param name: Ime procesa (podrazumevano "WorkerProcess")
    :param args: Tuple pozicijskih argumenata za target funkciju
    :param kwargs: Rečnik ključnih argumenata za target funkciju
    :return: Kreirana i pokrenuta Process instanca
    """
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    process = multiprocessing.Process(target=target, name=name, args=args, kwargs=kwargs)
    process.start()
    return process

def run_in_process_pool(target, args_list, max_workers=None):
    """
    Paralelno izvršava funkciju 'target' sa argumentima iz args_list koristeći ProcessPoolExecutor.
    
    :param target: Funkcija koja se izvršava u procesu
    :param args_list: Lista tuple-ova argumenata; svaki tuple se prosleđuje target funkciji
    :param max_workers: Maksimalan broj radnika u pool-u (podrazumevano, executor bira optimalan broj)
    :return: Lista rezultata izvršavanja funkcije
    """
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(lambda args: target(*args), args_list))
    return results

Thread = run_in_thread
