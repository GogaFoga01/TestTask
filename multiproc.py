import multiprocessing


def process_profile(profile):
    print(f"Processed profile with id {profile['id']}")


profiles = db.execute("SELECT * FROM cookie_profile").fetchall()

pool = multiprocessing.Pool(processes=5)

results = [pool.apply_async(process_profile, args=(profile,)) for profile in profiles]

for result in results:
    result.wait()
