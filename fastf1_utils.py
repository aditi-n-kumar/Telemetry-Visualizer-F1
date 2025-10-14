import fastf1
from concurrent.futures import ThreadPoolExecutor, as_completed

# Enable FastF1 cache globally
fastf1.Cache.enable_cache('fastf1cache')

# You can control max threads here (try 4–8)
executor = ThreadPoolExecutor(max_workers=6)

def preload_sessions(years, rounds, progress_callback=None, timeout=60):
    """
    Preloads FastF1 sessions in parallel for specified years and rounds.
    Example: preload_sessions([2024], range(1,5))

    progress_callback: optional callable completed, total -> None
    """
    rounds_list = list(rounds)
    total = len(years) * len(rounds_list)
    if total == 0:
        return

    futures = {executor.submit(_load_session, year, rnd): (year, rnd)
               for year in years for rnd in rounds_list}

    completed = 0
    for fut in as_completed(futures):
        yr, rnd = futures[fut]
        try:
            fut.result(timeout=timeout)
        except Exception as e:
            print(f"⚠️ Failed preload {yr} R{rnd}: {e}")
        completed += 1
        if progress_callback:
            try:
                progress_callback(completed, total)
            except Exception:
                # don't let callback failures stop the preload
                pass

def _load_session(year, rnd):
    try:
        sess = fastf1.get_session(year, rnd, 'Race')
        # load only results/metadata to keep it light
        sess.load(laps=False, telemetry=False, weather=False)
        print(f"✅ Cached: {year} Round {rnd}")
    except Exception as e:
        print(f"❌ Error loading {year} Round {rnd}: {e}")
